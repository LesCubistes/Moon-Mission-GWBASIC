#!/usr/bin/env python3
"""Install/play upstream main without changing the developer's worktree.

Sync this file as launch.py plus play.sh, runtime/, artwork/, versions/ and
current.json. Keep Git caches, emulator state and controller IDs local.
"""
import argparse
import base64
import fcntl
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile

URL = 'https://github.com/LesCubistes/Moon-Mission-GWBASIC.git'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write_json(path, data):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, indent=2) + '\n')
    temporary.replace(path)

def complete(version):
    try:
        manifest = json.loads((version / 'manifest.json').read_text())
        return bool(manifest['files']) and all(digest(version / n) == h for n, h in manifest['files'].items())
    except (OSError, KeyError, ValueError):
        return False

def update(library):
    cache = Path(os.environ.get('XDG_CACHE_HOME', Path.home() / '.cache')) / 'moon-mission/upstream.git'
    cache.parent.mkdir(parents=True, exist_ok=True)
    def git(*args):
        return subprocess.run(['git', '--git-dir', str(cache), *args], check=True, capture_output=True, timeout=45).stdout
    if not cache.exists():
        subprocess.run(['git', 'init', '--bare', str(cache)], check=True, capture_output=True)
        git('remote', 'add', 'origin', URL)
    if git('remote', 'get-url', 'origin').decode().strip() != URL:
        raise RuntimeError('Unexpected upstream cache remote')
    git('fetch', '--depth=1', 'origin', 'main')
    commit = git('rev-parse', 'FETCH_HEAD').decode().strip()
    version = library / 'versions' / commit
    if not complete(version):
        (library / 'versions').mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=library / 'versions', prefix='.prepare-') as temporary:
            staged = Path(temporary)
            with tarfile.open(fileobj=io.BytesIO(git('archive', commit))) as archive:
                members = [m for m in archive.getmembers() if m.name.split('/')[0] in {'src', 'assets', 'artwork'}]
                archive.extractall(staged, members=members, filter='data')
            files = {str(f.relative_to(staged)): digest(f) for f in staged.rglob('*') if f.is_file()}
            if not (staged / 'src/MOON.BAS').is_file() or not (staged / 'src/LANDER.BAS').is_file():
                raise RuntimeError('Upstream is missing game programs')
            write_json(staged / 'manifest.json', {'commit': commit, 'files': files, 'upstream': URL})
            # A partial Syncthing arrival can be completed from the exact same Git SHA.
            shutil.copytree(staged, version, dirs_exist_ok=True)
        if not complete(version):
            raise RuntimeError('Incomplete version after installation')
    artwork = version / 'artwork'
    if artwork.is_dir():
        shutil.copytree(artwork, library / 'artwork', dirs_exist_ok=True)
    write_json(library / 'current.json', {'commit': commit, 'upstream': URL, 'channel': 'main-development'})
    print(f'Moon Mission upstream main: {commit[:12]}', flush=True)
    return version

def apply_artwork(library, state):
    appid = os.environ.get('SteamAppId', '')
    if not appid.isdigit():
        return
    hashes = state / 'artwork.json'
    previous = json.loads(hashes.read_text()) if hashes.exists() else {}
    current = dict(previous)
    try:
        from steam_client import evaluate
        for role, kind in [('portrait', 0), ('landscape', 3), ('hero', 1), ('logo', 2), ('icon', None)]:
            path = next((library / 'artwork' / (role + ext) for ext in ['.png', '.jpg'] if (library / 'artwork' / (role + ext)).is_file()), None)
            if path is None or previous.get(appid + '/' + role) == digest(path):
                continue
            if role == 'icon':
                evaluate(f'SteamClient.Apps.SetShortcutIcon({appid},{json.dumps(str(path))})')
            else:
                data = base64.b64encode(path.read_bytes()).decode()
                fmt = 'png' if path.suffix == '.png' else 'jpg'
                evaluate(f'SteamClient.Apps.SetCustomArtworkForApp({appid},{json.dumps(data)},{json.dumps(fmt)},{kind})')
            current[appid + '/' + role] = digest(path)
        write_json(hashes, current)
    except Exception as error:
        print(f'Artwork refresh deferred ({type(error).__name__}); game launch continues.', file=sys.stderr)


def play(library, cycles):
    state = Path(os.environ.get('XDG_STATE_HOME', Path.home() / '.local/state')) / 'moon-mission'
    state.mkdir(parents=True, exist_ok=True)
    with (state / 'play.lock').open('w') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError('Moon Mission is already running on this machine')
        try:
            version = update(library)
        except (OSError, RuntimeError, subprocess.SubprocessError) as error:
            print(f'Update unavailable ({type(error).__name__}); using the existing complete version.', file=sys.stderr)
            current = json.loads((library / 'current.json').read_text())
            version = library / 'versions' / current['commit']
            if not complete(version):
                raise RuntimeError('No complete offline version; allow Syncthing to finish or reconnect')
        apply_artwork(library, state)
        run = state / 'run'
        start, landing = run / 'start', run / 'landing'
        for directory in [start, landing]:
            directory.mkdir(parents=True, exist_ok=True)
        shutil.copytree(version / 'assets', landing, dirs_exist_ok=True)
        for name in ['MOONBG.PIC', 'EARTH.SPR', 'TITLE.SPR', 'CREDIT.SPR', 'ROLL.BIN', 'ROLL.DAT']:
            shutil.copy2(version / 'assets' / name, start / name)
        shutil.copy2(version / 'src/MOON.BAS', start / 'MOON.BAS')
        shutil.copy2(version / 'src/LANDER.BAS', landing / 'LANDER.BAS')
        shutil.copy2(library / 'runtime/GWBASIC.EXE', start / 'GWBASIC.EXE')
        saves = library / 'saves'
        saves.mkdir(exist_ok=True)
        for name in ['LANDHS.DAT', 'HISCORE.DAT']:
            if (saves / name).is_file():
                shutil.copy2(saves / name, start / name)
        config = run / 'dosbox.conf'
        # Both launchers use directory mounts; DOSBox supplies its built-in DOS.
        conf = f'''[sdl]
fullscreen=true
[dosbox]
machine=tandy
memsize=1
[cpu]
core=normal
cputype=8086
[autoexec]
mount a "{start}" -t floppy
mount b "{landing}" -t floppy
a:
gwbasic moon
exit
'''
        modern = shutil.which('flatpak') and subprocess.run(['flatpak', 'info', 'io.github.dosbox-staging'], capture_output=True).returncode == 0
        cpu_option = f'cpu_cycles={cycles}' if modern else f'cycles=fixed {cycles}'
        config.write_text(conf.replace('[autoexec]', cpu_option + '\n[autoexec]'))
        if modern:
            command = ['flatpak', 'run', f'--filesystem={state}', 'io.github.dosbox-staging', '--noprimaryconf', '--conf', str(config)]
        elif shutil.which('dosbox'):
            command = ['dosbox', '-conf', str(config)]
        else:
            raise RuntimeError('Install DOSBox Staging (io.github.dosbox-staging) before playing')
        env = dict(os.environ)
        env.pop('LD_PRELOAD', None)
        try:
            result = subprocess.run(command, env=env)
        finally:
            for name in ['LANDHS.DAT', 'HISCORE.DAT']:
                if (start / name).is_file():
                    temporary = saves / (name + '.tmp')
                    shutil.copy2(start / name, temporary)
                    temporary.replace(saves / name)
        return result.returncode

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['update', 'play'])
    parser.add_argument('--library', type=Path, required=True)
    parser.add_argument('--cycles', type=int, default=1200)
    args = parser.parse_args()
    if not 100 <= args.cycles <= 10000:
        parser.error('cycles must be between 100 and 10000')
    args.library.mkdir(parents=True, exist_ok=True)
    try:
        if args.command == 'update':
            update(args.library)
        else:
            sys.exit(play(args.library, args.cycles))
    except (OSError, RuntimeError, subprocess.SubprocessError, ValueError) as error:
        parser.exit(1, f'Moon Mission: {error}\n')
