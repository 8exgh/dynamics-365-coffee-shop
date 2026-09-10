import io
import json
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

feed = 'https://dynamicssmb2.pkgs.visualstudio.com/DynamicsBCPublicFeeds/_packaging/MSSymbols/nuget/v3/index.json'
version = '28.5.54151.54365'
target = Path(__file__).resolve().parents[1] / 'business-central' / '.alpackages'
target.mkdir(parents=True, exist_ok=True)
lock = json.loads((target.parent / 'symbols.lock.json').read_text())
with urllib.request.urlopen(feed, timeout=60) as response:
    index = json.load(response)
base = next(r['@id'] for r in index['resources'] if r['@type'].startswith('PackageBaseAddress'))
seen = set()


def download(package, requested):
    package = package.lower()
    requested = requested.strip('[]()').split(',')[0].strip()
    requested = lock[package]
    if (package, requested) in seen:
        return
    seen.add((package, requested))
    print(f'Downloading {package} {requested}', flush=True)
    url = f'{base}{package}/{requested}/{package}.{requested}.nupkg'
    with urllib.request.urlopen(url, timeout=120) as response:
        archive = zipfile.ZipFile(io.BytesIO(response.read()))
    for filename in archive.namelist():
        if filename.endswith('.app'):
            (target / Path(filename).name).write_bytes(archive.read(filename))
    manifest = ET.fromstring(archive.read(next(n for n in archive.namelist() if n.endswith('.nuspec'))))
    for dependency in manifest.iter():
        if dependency.tag.endswith('dependency'):
            download(dependency.attrib['id'], dependency.attrib['version'])


download('Microsoft.Application.symbols', version)
print(f'Symbols ready in {target}')
