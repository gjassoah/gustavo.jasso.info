#!/usr/bin/env python3
"""Install a verified Pandoc 3.6.4 binary locally (Linux x86_64 only)."""
from pathlib import Path
import hashlib
import io
import platform
import tarfile
import urllib.request

VERSION = '3.6.4'
SHA256 = '5def6e1ff535e397becce292ee97767a947306150b9fb1488003b67ac3417c5e'
ROOT = Path(__file__).resolve().parents[1]
if platform.system() != 'Linux' or platform.machine() not in ('x86_64', 'AMD64'):
    raise SystemExit('Install Pandoc 3.6.4 for your platform from https://pandoc.org/installing.html')
url = f'https://github.com/jgm/pandoc/releases/download/{VERSION}/pandoc-{VERSION}-linux-amd64.tar.gz'
with urllib.request.urlopen(url) as response:
    archive = response.read()
if hashlib.sha256(archive).hexdigest() != SHA256:
    raise SystemExit('Pandoc archive checksum mismatch')
with tarfile.open(fileobj=io.BytesIO(archive), mode='r:gz') as tar:
    binary = tar.extractfile(f'pandoc-{VERSION}/bin/pandoc').read()
target = ROOT / '.tools/pandoc/bin/pandoc'
target.parent.mkdir(parents=True, exist_ok=True)
target.write_bytes(binary)
target.chmod(0o755)
print(f'Installed Pandoc {VERSION} at {target}')
