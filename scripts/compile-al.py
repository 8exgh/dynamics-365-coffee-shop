import io
import subprocess
import urllib.request
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
version = '17.0.34.45391'
tools = root / 'artifacts' / 'al-tools'
compiler = tools / 'tools' / 'net8.0' / 'any' / 'alc.dll'
if not compiler.exists():
    package = f'https://api.nuget.org/v3-flatcontainer/microsoft.dynamics.businesscentral.development.tools/{version}/microsoft.dynamics.businesscentral.development.tools.{version}.nupkg'
    with urllib.request.urlopen(package, timeout=120) as response:
        archive = zipfile.ZipFile(io.BytesIO(response.read()))
    tools.mkdir(parents=True, exist_ok=True)
    archive.extractall(tools)
cache = root / 'business-central' / '.alpackages'
if len(list(cache.glob('*.app'))) < 5:
    subprocess.run(['python3', str(root / 'scripts' / 'download-symbols.py')], check=True)
for project, filename in [('business-central', 'EightExamplesCoffee.app'), ('business-central-tests', 'EightExamplesCoffeeTests.app')]:
    subprocess.run(['dotnet', str(compiler), f'/project:{root / project}', f'/packagecachepath:{cache};{root / "artifacts"}', f'/out:{root / "artifacts" / filename}'], check=True)
