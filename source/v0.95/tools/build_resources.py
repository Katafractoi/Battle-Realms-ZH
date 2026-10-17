"""Reconstruct the selected resource snapshot into a fresh offline directory."""
import argparse
import json
from pathlib import Path
from br_review_common import load, save, sha
from resource_delta import apply_patch

ROOT = Path(__file__).resolve().parents[1]

def safe_path(root, relative):
    p = Path(relative.replace('\\', '/'))
    if p.is_absolute() or '..' in p.parts or ':' in relative:
        raise ValueError('Unsafe resource path')
    target = (root / p).resolve()
    target.relative_to(root.resolve())
    return target

def reconstruct(base_root, output, source_map=None):
    base_root, output = base_root.resolve(), output.resolve()
    if output.exists():
        raise FileExistsError(output)
    if output == base_root or base_root in output.parents or output in base_root.parents:
        raise ValueError('Base and output directories must be independent')
    manifest = load(ROOT / 'resources/patch-manifest.json')
    # Check all inputs before creating any output.
    for r in manifest['files']:
        path = Path(source_map[r['path']]) if source_map else safe_path(base_root, r['path'])
        if sha(path.read_bytes()) != r['sourceSha256']:
            raise ValueError('Official base hash mismatch: ' + r['path'])
    output.mkdir(parents=True)
    report = []
    for r in manifest['files']:
        path = Path(source_map[r['path']]) if source_map else safe_path(base_root, r['path'])
        source = path.read_bytes()
        patch = safe_path(ROOT / 'resources', r['patch']).read_bytes()
        if sha(patch) != r['patchSha256']:
            raise ValueError('Patch hash mismatch: ' + r['path'])
        target = apply_patch(source, patch)
        if sha(target) != r['targetSha256'] or len(target) != r['targetBytes']:
            raise ValueError('Reconstruction hash mismatch: ' + r['path'])
        dest = safe_path(output, r['path'])
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(target)
        if sha(dest.read_bytes()) != r['targetSha256']:
            raise ValueError('Output readback mismatch')
        report.append({'path':r['path'], 'sha256':r['targetSha256']})
    save(output / 'snapshot-build.json', {'version':manifest['version'], 'steamBuild':manifest['steamBuild'], 'files':report})
    return report

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base-root', type=Path, required=True, help='Independent copy of official build resources')
    p.add_argument('--output', type=Path, required=True, help='Fresh offline output directory')
    args = p.parse_args()
    print(json.dumps({'verifiedFiles':len(reconstruct(args.base_root, args.output))}))
