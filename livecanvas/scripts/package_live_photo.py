#!/usr/bin/env python3
"""Wrap a validated Live Photo pair in a macOS .pvt package (no transcoding)."""
import argparse
import hashlib
import json
from pathlib import Path
import plistlib
import shutil
import tempfile


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def package(pair_dir, output):
    pair_dir, output = Path(pair_dir).resolve(), Path(output).absolute()
    manifest = json.loads((pair_dir / 'manifest.json').read_text())
    if manifest.get('metadataVerified') is not True or manifest.get('localPHLivePhotoLoad') != 'passed':
        raise ValueError('Pair must pass metadata and PHLivePhoto validation first')
    if output.suffix.lower() != '.pvt':
        raise ValueError('Output must end in .pvt')
    resources = {}
    for key, suffix in [('photo', '.jpg'), ('video', '.mov')]:
        source = (pair_dir / manifest[key]).resolve()
        if source.parent != pair_dir or not source.is_file():
            raise ValueError('Invalid resource path: ' + str(source))
        resources[output.stem + suffix] = source
    metadata = {'PFVideoComplementMetadataVersionKey': '1'}
    reused = output.exists()
    if reused:
        if not output.is_dir() or set(p.name for p in output.iterdir()) != set(resources) | {'metadata.plist'}:
            raise ValueError('Existing output differs; choose a new name')
        if plistlib.loads((output / 'metadata.plist').read_bytes()) != metadata:
            raise ValueError('Existing metadata differs')
        for name, source in resources.items():
            if digest(output / name) != digest(source):
                raise ValueError('Existing resource differs: ' + name)
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix='.livecanvas-', dir=output.parent))
        try:
            for name, source in resources.items():
                shutil.copyfile(source, staging / name)
                if digest(staging / name) != digest(source):
                    raise ValueError('Copy verification failed')
            (staging / 'metadata.plist').write_bytes(plistlib.dumps(metadata))
            staging.rename(output)
        finally:
            if staging.exists():
                shutil.rmtree(staging)
    return {'package': str(output), 'identifier': manifest['identifier'],
            'resourcesUnchanged': True, 'reused': reused,
            'sha256': {name: digest(output / name) for name in resources},
            'photosImport': 'not_tested', 'iPhonePlayback': 'not_tested'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pair_dir')
    parser.add_argument('output_pvt')
    args = parser.parse_args()
    print(json.dumps(package(args.pair_dir, args.output_pvt), ensure_ascii=False, indent=2))
