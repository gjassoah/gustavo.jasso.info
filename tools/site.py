#!/usr/bin/env python3
"""Build or preview Hugo, regenerating the BibTeX bibliography first."""
import argparse
import hashlib
import subprocess
import sys
import time
from bibliography import BIBTEX, ROOT, generate


def fingerprint():
    paths = sorted((ROOT / BIBTEX).glob('*.bib')) + sorted((ROOT / 'tools/csl').glob('*.csl'))
    return [(str(p), hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['build', 'serve', 'bibliography'])
    args, hugo_args = parser.parse_known_args()
    if hugo_args[:1] == ['--']:
        hugo_args.pop(0)
    generate()
    if args.command == 'bibliography':
        return
    if args.command == 'build':
        subprocess.run(['hugo', *hugo_args], cwd=ROOT, check=True)
        return
    previous = fingerprint()
    process = subprocess.Popen(['hugo', 'server', *hugo_args], cwd=ROOT)
    try:
        while process.poll() is None:
            time.sleep(0.5)
            current = fingerprint()
            if current != previous:
                previous = current
                try:
                    generate()
                except Exception as error:
                    print(f'Bibliography not updated: {error}', flush=True)
        if process.returncode:
            raise SystemExit(process.returncode)
    except KeyboardInterrupt:
        pass
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait()


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        sys.exit(f'Site update failed: {error}')
