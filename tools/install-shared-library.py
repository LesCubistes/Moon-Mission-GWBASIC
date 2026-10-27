#!/usr/bin/env python3
"""Install the shared developer build and optionally update an existing Steam tile."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from steam_client import evaluate

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--library', type=Path, required=True)
p.add_argument('--runtime', type=Path, help='Your existing compatible GWBASIC.EXE')
p.add_argument('--appid', type=int, help='Existing local non-Steam shortcut ID; never synced to other machines')
a = p.parse_args()
root = Path(__file__).resolve().parents[1]
a.library = a.library.expanduser().resolve()
a.library.mkdir(parents=True, exist_ok=True)
runtime = a.library / 'runtime/GWBASIC.EXE'
source = a.runtime or (root / 'dos/GWBASIC.EXE' if (root / 'dos/GWBASIC.EXE').is_file() else runtime)
if not source.is_file() or source.read_bytes()[:2] != b'MZ':
    p.error('Supply --runtime with your compatible DOS BASIC executable')
runtime.parent.mkdir(exist_ok=True)
if source.resolve() != runtime.resolve():
    shutil.copy2(source, runtime)
for src, dest in [('shared-library.py', 'launch.py'), ('steam_client.py', 'steam_client.py')]:
    shutil.copy2(root / 'tools' / src, a.library / dest)
launcher = a.library / 'desktop-play.sh'
launcher.write_text('''#!/usr/bin/env bash
set -euo pipefail
base=$(cd "$(dirname "$0")" && pwd)
exec python3 "$base/launch.py" play --library "$base" "$@"
''')
launcher.chmod(0o755)
shutil.copy2(launcher, a.library / 'play.sh')
subprocess.run([sys.executable, str(a.library / 'launch.py'), 'update', '--library', str(a.library)], check=True)
if a.appid:
    if a.appid <= 0:
        p.error('appid must be positive')
    for method, value in [('SetShortcutExe', f'"{launcher}"'), ('SetShortcutStartDir', f'"{a.library}"'), ('SetShortcutLaunchOptions', '')]:
        evaluate(f'SteamClient.Apps.{method}({a.appid},{json.dumps(value)})')
    state = Path(os.environ.get('XDG_STATE_HOME', Path.home() / '.local/state')) / 'moon-mission'
    state.mkdir(parents=True, exist_ok=True)
    (state / 'steam.json').write_text(json.dumps({'appid': a.appid, 'launcher': str(launcher)}, indent=2) + '\n')
    spec = importlib.util.spec_from_file_location('moon_shared', root / 'tools/shared-library.py')
    shared = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(shared)
    os.environ['SteamAppId'] = str(a.appid)
    shared.apply_artwork(a.library, state)
print(f'Shared library ready: {launcher}')
