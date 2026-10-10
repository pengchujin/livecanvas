# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 杨振
# Modified by LiveCanvas: EXIF sub-IFD, signed zero sample, frame duration,
# exact identifier readback, strict single-mdat input, next track ID.
from __future__ import annotations

import struct
import uuid
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from .iso_bmff import Atom, atom, child_atoms, first_child, parse_atoms, patch_chunk_offsets


CONTENT_KEY = b"com.apple.quicktime.content.identifier"
STILL_TIME_KEY = b"com.apple.quicktime.still-image-time"
TIMED_SAMPLE = b"\x00\x00\x00\x09\x00\x00\x00\x01\x00"


@dataclass(frozen=True, slots=True)
class LiveMovInfo:
    asset_id: str
    still_time: float
    video_track_id: int
    metadata_track_id: int
    video_chunk_offset: int
    metadata_chunk_offset: int
    sample_value: int


def _canonical_asset_id(asset_id: str) -> str:
    try:
        return str(uuid.UUID(asset_id)).upper()
    except (ValueError, AttributeError) as exc:
        raise ValueError("Apple 资产标识必须是标准 UUID") from exc


def apple_maker_note(asset_id: str) -> bytes:
    identifier = _canonical_asset_id(asset_id).encode("ascii")
    return (
        b"Apple iOS\x00\x00\x01MM"
        + b"\x00\x01"
        + b"\x00\x11\x00\x02"
        + struct.pack(">I", len(identifier) + 1)
        + struct.pack(">I", 32)
        + b"\x00\x00\x00\x00"
        + identifier
        + b"\x00"
    )


def _exif_bytes(exif):
    # Pillow serializes an unknown MakerNote byte string as TIFF BYTE (1).
    # ImageIO requires UNDEFINED (7); change the type without moving any data.
    raw = bytearray(exif.tobytes())
    base = 6  # Exif\0\0 prefix, offsets are relative to TIFF header
    order = ">" if raw[base:base+2] == b"MM" else "<"
    ifd0 = struct.unpack_from(order + "I", raw, base+4)[0]
    count = struct.unpack_from(order + "H", raw, base+ifd0)[0]
    for index in range(count):
        entry = base+ifd0+2+12*index
        tag, kind, size, offset = struct.unpack_from(order + "HHII", raw, entry)
        if tag != 0x8769:
            continue
        subcount = struct.unpack_from(order + "H", raw, base+offset)[0]
        for subindex in range(subcount):
            subentry = base+offset+2+12*subindex
            if struct.unpack_from(order + "H", raw, subentry)[0] == 0x927C:
                struct.pack_into(order + "H", raw, subentry+2, 7)
                return bytes(raw)
    raise ValueError("Missing ExifIFD MakerNote")


def write_live_jpeg(source: Path, output: Path, asset_id: str) -> None:
    note = apple_maker_note(asset_id)
    with Image.open(source) as original:
        image = original.convert("RGB")
        exif = original.getexif()
        exif[0x010F] = "Apple"
        exif[0x0110] = "LiveCanvas"
        exif_ifd = exif.get_ifd(0x8769)
        exif_ifd[0x927C] = note
        exif_ifd[0x9000] = b"0232"
        exif_ifd[0xA000] = b"0100"
        exif_ifd[0xA001] = 1
        exif_ifd[0xA002] = image.width
        exif_ifd[0xA003] = image.height
        exif[0x8769] = exif_ifd
        if 0x927C in exif:
            del exif[0x927C]
        save_args: dict[str, object] = {
            "format": "JPEG",
            "quality": 95,
            "subsampling": 0,
            "exif": _exif_bytes(exif),
        }
        if original.info.get("icc_profile"):
            save_args["icc_profile"] = original.info["icc_profile"]
        image.save(output, **save_args)


def inspect_live_jpeg(path: Path) -> str:
    with Image.open(path) as image:
        note = image.getexif().get_ifd(0x8769).get(0x927C)
    if not isinstance(note, bytes) or not note.startswith(b"Apple iOS\x00\x00\x01MM"):
        raise ValueError("JPEG 缺少 Apple MakerNote")
    if len(note) < 69 or note[16:18] != b"\x00\x11" or note[18:20] != b"\x00\x02":
        raise ValueError("Apple MakerNote 缺少内容标识 tag 17")
    count = int.from_bytes(note[20:24], "big")
    offset = int.from_bytes(note[24:28], "big")
    raw = note[offset : offset + count].rstrip(b"\x00")
    try:
        return _canonical_asset_id(raw.decode("ascii"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise ValueError("Apple MakerNote 内容标识无效") from exc


def _fullbox(version: int = 0, flags: int = 0) -> bytes:
    return bytes((version,)) + flags.to_bytes(3, "big")


def _content_identifier_meta(asset_id: str) -> bytes:
    identifier = _canonical_asset_id(asset_id).encode("ascii")
    hdlr = atom(
        b"hdlr",
        _fullbox() + b"\x00" * 4 + b"mdta" + b"\x00" * 12 + b"\x00\x00",
    )
    key_entry = struct.pack(">I4s", 8 + len(CONTENT_KEY), b"mdta") + CONTENT_KEY
    keys = atom(b"keys", _fullbox() + struct.pack(">I", 1) + key_entry)
    data = atom(b"data", struct.pack(">II", 1, 0) + identifier)
    item = atom(b"\x00\x00\x00\x01", data)
    return atom(b"meta", hdlr + keys + atom(b"ilst", item))


def _pascal(text: bytes) -> bytes:
    if len(text) > 255:
        raise ValueError("Pascal 字符串过长")
    return bytes((len(text),)) + text


def _timed_metadata_track(
    track_id: int,
    video_track_id: int,
    timescale: int,
    cover_ticks: int,
    sample_offset: int,
    sample_ticks: int,
) -> bytes:
    track_duration = cover_ticks + sample_ticks
    matrix = struct.pack(
        ">9I",
        0x00010000,
        0,
        0,
        0,
        0x00010000,
        0,
        0,
        0,
        0x40000000,
    )
    tkhd = atom(
        b"tkhd",
        _fullbox(flags=0x0F)
        + struct.pack(">IIIII", 0, 0, track_id, 0, track_duration)
        + b"\x00" * 8
        + struct.pack(">hhhh", 0, 0, 0, 0)
        + matrix
        + struct.pack(">II", 0, 0),
    )

    edits: list[bytes] = []
    if cover_ticks:
        edits.append(struct.pack(">IiHH", cover_ticks, -1, 1, 0))
    edits.append(struct.pack(">IiHH", sample_ticks, 0, 1, 0))
    elst = atom(b"elst", _fullbox() + struct.pack(">I", len(edits)) + b"".join(edits))
    edts = atom(b"edts", elst)
    tref = atom(b"tref", atom(b"cdsc", struct.pack(">I", video_track_id)))

    mdhd = atom(
        b"mdhd",
        _fullbox()
        + struct.pack(">IIII", 0, 0, timescale, sample_ticks)
        + struct.pack(">HH", 0x55C4, 0),
    )
    metadata_name = b"Core Media Metadata"
    hdlr = atom(
        b"hdlr",
        _fullbox()
        + b"mhlrmetaappl"
        + struct.pack(">II", 1, 0)
        + _pascal(metadata_name),
    )

    gmin = atom(
        b"gmin",
        _fullbox() + struct.pack(">H3HHH", 0x0040, 0x8000, 0x8000, 0x8000, 0, 0),
    )
    gmhd = atom(b"gmhd", gmin)
    data_name = b"Core Media Data Handler"
    data_hdlr = atom(
        b"hdlr",
        _fullbox()
        + b"dhlralisappl"
        + struct.pack(">II", 0, 0)
        + _pascal(data_name),
    )
    alias = atom(b"alis", _fullbox(flags=1))
    dref = atom(b"dref", _fullbox() + struct.pack(">I", 1) + alias)
    dinf = atom(b"dinf", dref)

    keyd = atom(b"keyd", b"mdta" + STILL_TIME_KEY)
    dtyp = atom(b"dtyp", _fullbox() + struct.pack(">I", 0x41))
    key_record = struct.pack(">II", 8 + len(keyd) + len(dtyp), 1) + keyd + dtyp
    keys = atom(b"keys", key_record)
    mebx = atom(b"mebx", b"\x00" * 6 + struct.pack(">H", 1) + keys)
    stsd = atom(b"stsd", _fullbox() + struct.pack(">I", 1) + mebx)
    stts = atom(b"stts", _fullbox() + struct.pack(">III", 1, 1, sample_ticks))
    stsc = atom(b"stsc", _fullbox() + struct.pack(">IIII", 1, 1, 1, 1))
    stsz = atom(b"stsz", _fullbox() + struct.pack(">II", 0, 1) + struct.pack(">I", len(TIMED_SAMPLE)))
    if sample_offset <= 0xFFFFFFFF:
        chunk_offsets = atom(b"stco", _fullbox() + struct.pack(">II", 1, sample_offset))
    else:
        chunk_offsets = atom(b"co64", _fullbox() + struct.pack(">IQ", 1, sample_offset))
    stbl = atom(b"stbl", stsd + stts + stsc + stsz + chunk_offsets)
    minf = atom(b"minf", gmhd + data_hdlr + dinf + stbl)
    mdia = atom(b"mdia", mdhd + hdlr + minf)
    return atom(b"trak", tkhd + edts + tref + mdia)


def _movie_timescale(data: bytes, moov: Atom) -> int:
    mvhd = first_child(data, moov, b"mvhd")
    if mvhd is None:
        raise ValueError("MOV 缺少 mvhd")
    version = data[mvhd.payload_start]
    position = mvhd.start + (28 if version == 1 else 20)
    if position + 4 > mvhd.end:
        raise ValueError("MOV mvhd 不完整")
    timescale = int.from_bytes(data[position : position + 4], "big")
    if timescale <= 0:
        raise ValueError("MOV 时间基无效")
    return timescale


def _track_id(data: bytes, trak: Atom) -> int:
    tkhd = first_child(data, trak, b"tkhd")
    if tkhd is None:
        raise ValueError("MOV 轨道缺少 tkhd")
    version = data[tkhd.payload_start]
    position = tkhd.start + (28 if version == 1 else 20)
    return int.from_bytes(data[position : position + 4], "big")


def _track_handler(data: bytes, trak: Atom) -> bytes | None:
    mdia = first_child(data, trak, b"mdia")
    if mdia is None:
        return None
    hdlr = first_child(data, mdia, b"hdlr")
    if hdlr is None or hdlr.start + 20 > hdlr.end:
        return None
    return data[hdlr.start + 16 : hdlr.start + 20]


def _top_required(data: bytes) -> tuple[list[Atom], Atom, Atom, Atom]:
    top = parse_atoms(data)
    try:
        ftyp = next(item for item in top if item.type == b"ftyp")
        mdat = next(item for item in top if item.type == b"mdat")
        moov = next(item for item in top if item.type == b"moov")
    except StopIteration as exc:
        raise ValueError("MOV 必须包含 ftyp、mdat 和 moov") from exc
    return top, ftyp, mdat, moov


def write_live_mov(
    source: Path,
    output: Path,
    asset_id: str,
    still_time: float,
    duration: float,
    fps: float,
) -> None:
    identifier = _canonical_asset_id(asset_id)
    if duration <= 0 or not 0 <= still_time <= duration:
        raise ValueError("Apple 封面时刻必须位于视频片段内")
    data = source.read_bytes()
    top, _ftyp, mdat, moov = _top_required(data)
    if sum(a.type == b"mdat" for a in top) != 1 or any(a.type == b"moof" for a in top):
        raise ValueError("Expected non-fragmented, single-mdat FFmpeg output")
    timescale = _movie_timescale(data, moov)
    tracks = [item for item in child_atoms(data, moov) if item.type == b"trak"]
    ids = [_track_id(data, item) for item in tracks]
    video = next((item for item in tracks if _track_handler(data, item) == b"vide"), None)
    if video is None:
        raise ValueError("MOV 中没有可关联的视频轨")
    video_track_id = _track_id(data, video)
    metadata_track_id = max(ids, default=0) + 1
    cover_ticks = round(still_time * timescale)
    max_tick = max(0, round(duration * timescale) - 1)
    cover_ticks = min(max(0, cover_ticks), max_tick)

    prefix = b"".join(item.raw(data) for item in top if item.type not in {b"mdat", b"moov"})
    old_media = data[mdat.payload_start : mdat.end]
    new_mdat = atom(b"mdat", old_media + TIMED_SAMPLE)
    new_media_start = len(prefix) + (16 if new_mdat[:4] == b"\x00\x00\x00\x01" else 8)
    delta = new_media_start - mdat.payload_start
    sample_offset = new_media_start + len(old_media)

    patched_moov = patch_chunk_offsets(moov.raw(data), delta)
    parsed_patched_moov = parse_atoms(patched_moov)[0]
    patched = bytearray(patched_moov)
    mvhd = first_child(patched, parsed_patched_moov, b"mvhd")
    patched[mvhd.end - 4:mvhd.end] = struct.pack(">I", metadata_track_id + 1)
    original_children = bytes(patched[parsed_patched_moov.payload_start : parsed_patched_moov.end])
    additions = _content_identifier_meta(identifier) + _timed_metadata_track(
        metadata_track_id,
        video_track_id,
        timescale,
        cover_ticks,
        sample_offset,
        max(1, round(timescale / fps)),
    )
    new_moov = atom(b"moov", original_children + additions)
    output.write_bytes(prefix + new_mdat + new_moov)


def _first_chunk_offset(data: bytes, trak: Atom) -> int:
    mdia = first_child(data, trak, b"mdia")
    minf = first_child(data, mdia, b"minf") if mdia else None
    stbl = first_child(data, minf, b"stbl") if minf else None
    if stbl is None:
        raise ValueError("MOV 轨道缺少 sample table")
    table = first_child(data, stbl, b"stco") or first_child(data, stbl, b"co64")
    if table is None:
        raise ValueError("MOV 轨道缺少 chunk offset")
    count = int.from_bytes(data[table.payload_start + 4 : table.payload_start + 8], "big")
    if count < 1:
        raise ValueError("MOV chunk offset 为空")
    width = 4 if table.type == b"stco" else 8
    start = table.payload_start + 8
    return int.from_bytes(data[start : start + width], "big")


def _cover_ticks(data: bytes, trak: Atom) -> int:
    edts = first_child(data, trak, b"edts")
    elst = first_child(data, edts, b"elst") if edts else None
    if elst is None:
        return 0
    version = data[elst.payload_start]
    count = int.from_bytes(data[elst.payload_start + 4 : elst.payload_start + 8], "big")
    position = elst.payload_start + 8
    if count >= 2:
        if version == 0:
            duration = int.from_bytes(data[position : position + 4], "big")
            media_time = int.from_bytes(data[position + 4 : position + 8], "big", signed=True)
        else:
            duration = int.from_bytes(data[position : position + 8], "big")
            media_time = int.from_bytes(data[position + 8 : position + 16], "big", signed=True)
        if media_time == -1:
            return duration
    return 0


def inspect_live_mov(path: Path) -> LiveMovInfo:
    data = path.read_bytes()
    _top, _ftyp, _mdat, moov = _top_required(data)
    timescale = _movie_timescale(data, moov)
    # Parse the generated QuickTime meta instead of matching an unrelated UUID.
    metas = [a for a in child_atoms(data, moov) if a.type == b"meta"]
    values = []
    for meta in metas:
        keys = first_child(data, meta, b"keys")
        ilst = first_child(data, meta, b"ilst")
        if keys is None or ilst is None:
            continue
        expected = _fullbox() + struct.pack(">I", 1) + struct.pack(">I4s", 8 + len(CONTENT_KEY), b"mdta") + CONTENT_KEY
        if data[keys.payload_start:keys.end] != expected:
            continue
        entry = first_child(data, ilst, b"\x00\x00\x00\x01")
        value = first_child(data, entry, b"data") if entry else None
        if value and data[value.payload_start:value.payload_start+8] == struct.pack(">II", 1, 0):
            values.append(_canonical_asset_id(data[value.payload_start+8:value.end].decode("ascii")))
    if len(values) != 1:
        raise ValueError("MOV must contain one exact content identifier")
    identifier = values[0]
    tracks = [item for item in child_atoms(data, moov) if item.type == b"trak"]
    video = next((item for item in tracks if _track_handler(data, item) == b"vide"), None)
    metadata = next(
        (
            item
            for item in tracks
            if _track_handler(data, item) == b"meta"
            and STILL_TIME_KEY in item.raw(data)
        ),
        None,
    )
    if video is None or metadata is None:
        raise ValueError("MOV 缺少视频轨或 still-image-time 元数据轨")
    metadata_offset = _first_chunk_offset(data, metadata)
    if data[metadata_offset : metadata_offset + 8] != TIMED_SAMPLE[:8]:
        raise ValueError("MOV still-image-time sample 结构无效")
    value = struct.unpack("b", data[metadata_offset + 8 : metadata_offset + 9])[0]
    return LiveMovInfo(
        asset_id=identifier,
        still_time=_cover_ticks(data, metadata) / timescale,
        video_track_id=_track_id(data, video),
        metadata_track_id=_track_id(data, metadata),
        video_chunk_offset=_first_chunk_offset(data, video),
        metadata_chunk_offset=metadata_offset,
        sample_value=value,
    )
