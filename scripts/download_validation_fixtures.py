"""Download public test photographs; verify content and keep outside the repository.

Astronaut/chelsea: scikit-image sample data (astronaut is NASA public-domain).
Bus: Ultralytics example image. Sources/hashes are in test_fixtures.json.
These are test inputs only and are not included in the production image.
"""
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen
root = Path(__file__).resolve().parents[1]
target = Path('/tmp/agrivision-validation')
target.mkdir(exist_ok=True)
for name, spec in json.loads((root / 'models/validation/test_fixtures.json').read_text()).items():
    with urlopen(spec['url'], timeout=30) as response:
        content = response.read(5 * 1024 * 1024)
    if hashlib.sha256(content).hexdigest() != spec['sha256']:
        raise ValueError(f'Fixture checksum mismatch: {name}')
    (target / name).write_bytes(content)
print('Verified independent test photos:', target)
