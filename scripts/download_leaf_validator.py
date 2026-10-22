"""Fetch the public offline validator at build time; verify before installation."""
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

root = Path(__file__).resolve().parents[1] / 'models' / 'validation'
metadata = json.loads((root / 'metadata.json').read_text())
target = root / 'vision_model_quantized.onnx'
expected = metadata['sha256'][target.name]
if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != expected:
    temporary = target.with_suffix('.download')
    try:
        digest = hashlib.sha256()
        size = 0
        with urlopen(metadata['vision_url'], timeout=120) as source, temporary.open('wb') as output:
            while block := source.read(1024 * 1024):
                size += len(block)
                if size > 100 * 1024 * 1024:
                    raise ValueError('Validator download exceeds limit')
                digest.update(block)
                output.write(block)
        if digest.hexdigest() != expected:
            raise ValueError('Validator download checksum mismatch')
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)
print('Offline leaf validator verified.')
