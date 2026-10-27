#!/usr/bin/env python3
"""Build the GitHub Pages site (the player's front page) into _site/.

site/index.html is a template; these come from the environment (the Pages workflow sets them
from the release being published, or the latest release):
  VERSION        release tag, e.g. v1.0.0                   (default: latest)
  RELEASE_DATE   ISO date the release was published          (optional)
  ZIP_SIZE       size of Moon-Mission-game.zip in bytes      (optional)
  REPO_URL       https://github.com/OWNER/REPO               (default: this repo)
The Download button always points at that release's Moon-Mission-game.zip.
"""
import os
from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[2]
out = root / '_site'
if out.exists():
    shutil.rmtree(out)
shutil.copytree(root / 'site', out)
repo = os.environ.get('REPO_URL') or 'https://github.com/LesCubistes/Moon-Mission-GWBASIC'
version = os.environ.get('VERSION') or 'latest'
if version == 'latest':
    zip_url = f'{repo}/releases/latest/download/Moon-Mission-game.zip'
    line = 'The latest release. DOS and GW-BASIC not included.'
else:
    zip_url = f'{repo}/releases/download/{version}/Moon-Mission-game.zip'
    parts = [f'Version {version.lstrip("v")}']
    if os.environ.get('RELEASE_DATE'):
        from datetime import datetime
        d = datetime.fromisoformat(os.environ['RELEASE_DATE'].replace('Z', '+00:00'))
        parts.append(f'released {d:%B} {d.day}, {d:%Y}')
    if os.environ.get('ZIP_SIZE'):
        parts.append(f'{int(os.environ["ZIP_SIZE"]) // 1024} KB ZIP')
    line = ', '.join(parts) + '. DOS and GW-BASIC not included.'
page = (out / 'index.html').read_text()
for key, value in {'VERSION': version.upper() if version == 'latest' else version, 'ZIP_URL': zip_url,
                   'RELEASE_LINE': line, 'REPO': repo}.items():
    page = page.replace('{{' + key + '}}', value)
assert '{{' not in page, 'unfilled placeholder in site/index.html'
(out / 'index.html').write_text(page)
(out / '.nojekyll').write_text('')
print(f'Built {out} for {version}: {zip_url}')
