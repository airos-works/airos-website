#!/usr/bin/env python3
"""Lay out air/OS's package repositories in dist/repo/<arch>/.

HaikuPorts has no arm64 repository, so air/OS serves one: HaikuPorts' arm64
build packages (gcc, binutils, make, ...), which HaikuDepot and pkgman on
arm64 machines install from https://airos.works/repo/arm64/ (the address in
the images' repository configuration, airos-works/haiku#118).

CI (airos-ci images/package-repo.py) keeps the files as assets of the GitHub
release repo-<arch> of airos-works/haiku, with index.json naming each file's
path in the repository, size and SHA-256. This script downloads what it does
not have yet into .cache/repo (kept between runs), checks every file against
index.json and copies the set into dist. When the release cannot be read, or
a file is missing or damaged (CI changing the release while this runs), the
last complete set stays: the site never serves a repository whose index names
packages it does not have. Run after build.py.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / 'content/project.json').read_text())
OWNER = CONFIG['owner']
CACHE = ROOT / '.cache/repo'
OUT = ROOT / 'dist/repo'
ARCHITECTURES = ['arm64']
TOKEN = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')


def token():
    global TOKEN
    if not TOKEN:
        TOKEN = subprocess.check_output(['gh', 'auth', 'token'], text=True).strip()
    return TOKEN


def get(url, api=False):
    headers = {'User-Agent': 'airos-website'}
    if api:
        headers.update({'Authorization': 'Bearer ' + token(),
            'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'})
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers),
            timeout=600) as response:
        return response.read()


def sha256(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def fetch_index(arch):
    """The release's index, with the download address of each file; None when
    the release or one of its files cannot be had intact."""
    try:
        release = json.loads(get(f'https://api.github.com/repos/{OWNER}/haiku/releases/tags/repo-{arch}', api=True))
        assets = {a['name']: a['browser_download_url'] for a in release['assets']
            if a['state'] == 'uploaded'}
        index = json.loads(get(assets['index.json']))
    except (urllib.error.URLError, KeyError, ValueError) as error:
        print(f'repo-{arch}: no index ({error})')
        return None
    for entry in index['files']:
        cached = CACHE / entry['sha256']
        if cached.exists():
            continue
        name = os.path.basename(entry['path'])
        if name not in assets:
            print(f'repo-{arch}: {name} is not in the release')
            return None
        temporary = cached.with_suffix('.part')
        try:
            temporary.write_bytes(get(assets[name]))
        except urllib.error.URLError as error:
            print(f'repo-{arch}: {name}: {error}')
            return None
        if temporary.stat().st_size != entry['size'] or sha256(temporary) != entry['sha256']:
            temporary.unlink()
            print(f'repo-{arch}: {name} does not match index.json')
            return None
        temporary.replace(cached)
    return index


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    keep = set()
    for arch in ARCHITECTURES:
        saved = CACHE / f'{arch}.json'
        index = fetch_index(arch)
        if index is not None:
            saved.write_text(json.dumps(index, indent=1) + '\n')
        elif saved.exists():
            index = json.loads(saved.read_text())
            print(f'repo-{arch}: serving the last complete repository')
        if index is None or not all((CACHE / e['sha256']).exists() for e in index['files']):
            print(f'repo-{arch}: no repository to serve')
            continue
        target = OUT / arch
        if target.exists():
            shutil.rmtree(target)
        for entry in index['files']:
            path = target / entry['path']
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(CACHE / entry['sha256'], path)
            keep.add(entry['sha256'])
        packages = sum(1 for e in index['files'] if e['path'].startswith('packages/'))
        size = sum(e['size'] for e in index['files'])
        print(f'repo-{arch}: {packages} packages ({size / 1048576:.0f} MiB) in {target}')
    for cached in CACHE.iterdir():
        if cached.suffix not in ('.json',) and cached.name not in keep:
            cached.unlink()


if __name__ == '__main__':
    main()
