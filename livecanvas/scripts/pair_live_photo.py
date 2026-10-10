#!/usr/bin/env python3
"""Pair rendered JPEG + silent H.264 as Apple Live Photo on any desktop OS.
Requires Python >=3.10, Pillow >=10,<12, ffmpeg and ffprobe on PATH.
Never imports into Photos. Use verify_live_photo.swift for optional Apple validation.
"""
import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import tempfile
import uuid

from PIL import Image
from portable_live_photo.apple import write_live_jpeg, write_live_mov, inspect_live_jpeg, inspect_live_mov


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest() if hasattr(hashlib, 'file_digest') else hashlib.sha256(stream.read()).hexdigest()


def probe(path):
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)], check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def check_inputs(photo, movie, seconds, fps):
    if not all(math.isfinite(n) for n in (seconds, fps)) or not 0 < fps <= 240:
        raise ValueError('Invalid cover time/fps')
    info = probe(movie)
    streams = info['streams']
    videos = [s for s in streams if s['codec_type'] == 'video']
    if len(videos) != 1 or videos[0]['codec_name'] != 'h264':
        raise ValueError('Expected one H.264 video stream')
    if any(s['codec_type'] == 'audio' for s in streams):
        raise ValueError('Silent-only input required; audio must not be silently discarded')
    video = videos[0]
    duration = float(video.get('duration', info['format']['duration']))
    if not math.isfinite(duration) or not 0 <= seconds or seconds + 1/fps > duration + 0.0001:
        raise ValueError('Cover time outside video')
    if abs(float(Fraction(video['avg_frame_rate'])) - fps) > 0.01 or abs(seconds*fps-round(seconds*fps)) > 0.0001:
        raise ValueError('FPS mismatch or cover time not aligned to frame')
    if abs(float(video.get('start_time', 0))) > 0.0001:
        raise ValueError('Expected zero-based render timeline')
    if any(float(d.get('rotation', 0)) != 0 for d in video.get('side_data_list', [])):
        raise ValueError('Render rotation into pixels before pairing')
    with Image.open(photo) as cover:
        if cover.format != 'JPEG' or cover.size != (video['width'], video['height']):
            raise ValueError('Expected JPEG matching video dimensions')
        if cover.getexif().get(274, 1) != 1:
            raise ValueError('Render EXIF orientation into pixels first')
        cover.load()
    return duration


def verify_pair(directory, manifest):
    directory = Path(directory).resolve()
    paths = []
    for key in ('photo', 'video'):
        path = (directory / manifest[key]).resolve()
        if path.parent != directory or not path.is_file():
            raise ValueError('Invalid pair resource path')
        if manifest.get('sha256', {}).get(key) != digest(path):
            raise ValueError('Pair hash mismatch: ' + key)
        paths.append(path)
    photo, movie = paths
    identifier = inspect_live_jpeg(photo)
    metadata = inspect_live_mov(movie)
    if identifier != manifest['identifier'] or metadata.asset_id != identifier or metadata.sample_value != 0:
        raise ValueError('Live Photo identifier or signed metadata sample mismatch')
    if abs(metadata.still_time - manifest['coverTime']) > 1/60000:
        raise ValueError('Timed metadata position mismatch')
    # Independent FFmpeg demuxer must find the metadata sample at the same timestamp.
    packets = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'd', '-show_packets', '-of', 'json', str(movie)], check=True, capture_output=True, text=True).stdout)['packets']
    if len(packets) != 1 or abs(float(packets[0]['pts_time']) - manifest['coverTime']) > 1/60000:
        raise ValueError('FFprobe timed sample readback failed')
    if abs(float(packets[0]['duration_time']) - 1/manifest['fps']) > 2/60000:
        raise ValueError('Timed sample duration mismatch')
    check_inputs(photo, movie, manifest['coverTime'], manifest['fps'])
    subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(movie), '-map', '0:v:0', '-f', 'null', '-'], check=True, capture_output=True)
    return metadata


def pair(photo, movie, output, seconds, fps):
    photo, movie, output = Path(photo).resolve(), Path(movie).resolve(), Path(output).absolute()
    if output.exists():
        raise ValueError('Output already exists; choose a new directory')
    duration = check_inputs(photo, movie, seconds, fps)
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix='.livecanvas-pair-', dir=output.parent))
    try:
        identifier = str(uuid.uuid4()).upper()
        raw = staging / 'remux.mov'
        subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-i', str(movie), '-map', '0:v:0', '-map_metadata', '-1', '-c:v', 'copy', '-movie_timescale', '60000', str(raw)], check=True, capture_output=True)
        write_live_jpeg(photo, staging / 'live.jpg', identifier)
        write_live_mov(raw, staging / 'live.mov', identifier, seconds, duration, fps)
        raw.unlink()
        manifest = {'identifier': identifier, 'photo': 'live.jpg', 'video': 'live.mov', 'coverTime': seconds, 'duration': duration, 'fps': fps,
                    'backend': 'portable-python', 'metadataVerified': False, 'localPHLivePhotoLoad': 'not_available',
                    'localLoadReason': 'Portable backend does not invoke Apple PhotoKit', 'iPhonePlayback': 'not_tested',
                    'photosImport': 'not_requested', 'wallpaper': 'not_tested', 'importedIntoPhotos': False,
                    'sha256': {'photo': digest(staging/'live.jpg'), 'video': digest(staging/'live.mov')}}
        actual = verify_pair(staging, manifest)
        manifest.update(metadataVerified=True, readbackStillTime=actual.still_time)
        (staging/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
        if output.exists():
            raise ValueError('Output appeared during generation; refusing to replace it')
        staging.rename(output)
        return manifest
    finally:
        if staging.exists():
            shutil.rmtree(staging)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('photo')
    parser.add_argument('movie')
    parser.add_argument('output')
    parser.add_argument('cover_seconds', type=float)
    parser.add_argument('fps', type=float)
    args = parser.parse_args()
    print(json.dumps(pair(args.photo, args.movie, args.output, args.cover_seconds, args.fps), indent=2))
