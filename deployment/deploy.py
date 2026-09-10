import json
import os
import re
import subprocess
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

def main():
    image = os.environ['COFFEE_IMAGE']
    owner = os.environ.get('GITHUB_REPOSITORY_OWNER', '8exgh').lower()
    pattern = rf'ghcr\.io/{re.escape(owner)}/dynamics-365-coffee-shop(?:@sha256:[a-f0-9]{{64}}|:sha-[a-f0-9]{{40}})'
    if not re.fullmatch(pattern, image):
        raise SystemExit('Deployment requires an immutable coffee shop image from the expected GHCR owner.')
    container = 'sean-web-dynamics-365-coffee-shop'
    candidate = container + '-candidate'
    previous = container + '-previous'
    root = Path('/opt/dynamics-365-coffee-shop')
    port = '3067'
    required = ['COFFEE_ADMIN_PASSWORD', 'COFFEE_SESSION_SECRET']
    settings = {
        'COFFEE_ADMIN_USER': os.getenv('COFFEE_ADMIN_USER', 'manager'),
        'COFFEE_ADMIN_PASSWORD': os.getenv('COFFEE_ADMIN_PASSWORD', ''),
        'COFFEE_SESSION_SECRET': os.getenv('COFFEE_SESSION_SECRET', ''),
        'COFFEE_CASHIER_PASSWORD': os.getenv('COFFEE_CASHIER_PASSWORD', ''),
        'COFFEE_TIMEZONE': 'America/Edmonton',
        'COFFEE_SECURE_COOKIES': os.getenv('COFFEE_SECURE_COOKIES', 'true'),
        'BC_TENANT_ID': os.getenv('BC_TENANT_ID', ''),
        'BC_ENVIRONMENT': os.getenv('BC_ENVIRONMENT') or 'Sandbox',
        'BC_COMPANY_ID': os.getenv('BC_COMPANY_ID', ''),
        'BC_CLIENT_ID': os.getenv('BC_CLIENT_ID', ''),
        'BC_CLIENT_SECRET': os.getenv('BC_CLIENT_SECRET', ''),
        'BC_WEB_URL': os.getenv('BC_WEB_URL') or 'https://businesscentral.dynamics.com',
        'BC_ALLOW_WRITES': os.getenv('BC_ALLOW_WRITES', 'false'),
    }
    if any(not settings[key] for key in required):
        raise SystemExit('Set COFFEE_ADMIN_PASSWORD and COFFEE_SESSION_SECRET repository secrets.')
    if len(settings['COFFEE_ADMIN_PASSWORD']) < 12 or len(settings['COFFEE_SESSION_SECRET']) < 32:
        raise SystemExit('Admin password requires 12 characters and the session secret requires 32.')
    if any('\n' in value or '\r' in value for value in settings.values()):
        raise SystemExit('Environment settings must be single-line values.')


    def docker(*args, check=True):
        result = subprocess.run(['docker', *args], text=True, capture_output=True)
        if check and result.returncode:
            raise RuntimeError(result.stderr.strip() or 'Docker operation failed.')
        return result.stdout.strip()


    def exists(name):
        return bool(docker('ps', '-a', '--filter', f'name=^/{name}$', '--format', '{{.Names}}'))


    def healthy(url):
        for attempt in range(30):
            try:
                with urllib.request.urlopen(url, timeout=3) as response:
                    if json.load(response).get('status') == 'ok':
                        return True
            except Exception:
                pass
            time.sleep(2)
        return False


    def remove(name):
        if exists(name):
            docker('rm', '-f', name)


    for holder in docker('ps', '--filter', f'publish={port}', '--format', '{{.Names}}').splitlines():
        if holder != container:
            raise SystemExit(f'Port {port} belongs to {holder}; deployment stopped.')
    print('Pulling the immutable image.', flush=True)
    docker('pull', image)
    setup = 'install -d -m 0750 -o "$1" -g "$2" /state /state/config /state/backups; install -d -m 0750 -o 1000 -g 1000 /state/data'
    docker('run', '--rm', '--user', '0:0', '--network', 'none', '--read-only', '-v', f'{root}:/state', '--entrypoint', 'sh', image, '-eu', '-c', setup, 'setup', str(os.getuid()), str(os.getgid()))
    config = root / 'config' / 'runtime.env'
    temporary = config.with_suffix('.tmp')
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w') as output:
        output.write(''.join(f'{key}={value}\n' for key, value in settings.items()))
    os.replace(temporary, config)
    remove(candidate)
    common = ['--env-file', str(config), '--read-only', '--tmpfs', '/tmp:size=64m,mode=1777', '--cap-drop=ALL', '--security-opt=no-new-privileges:true', '--init', '--log-opt', 'max-size=10m', '--log-opt', 'max-file=3']
    try:
        docker('run', '-d', '--name', candidate, *common, '-e', 'COFFEE_DATABASE=/tmp/smoke.db', '-p', '127.0.0.1::3000', image)
        candidate_port = docker('port', candidate, '3000/tcp').split(':')[-1]
        if not healthy(f'http://127.0.0.1:{candidate_port}/api/health'):
            raise RuntimeError('Candidate image failed its health check; current service was preserved.')
    finally:
        remove(candidate)
    remove(previous)
    had_previous = exists(container)
    if had_previous:
        backup_name = f"coffee-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.db"
        program = "import sqlite3,sys; s=sqlite3.connect('/app/data/coffee.db'); t=sqlite3.connect(':memory:'); s.backup(t); sys.stdout.buffer.write(t.serialize()); t.close(); s.close()"
        backup = root / 'backups' / backup_name
        fd = os.open(backup, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            with os.fdopen(fd, 'wb') as output:
                subprocess.run(['docker', 'exec', container, 'python', '-c', program], stdout=output, check=True)
        except Exception:
            backup.unlink(missing_ok=True)
            raise
        docker('stop', '--time', '20', container)
        docker('rename', container, previous)
    try:
        docker('run', '-d', '--name', container, '--restart', 'unless-stopped', *common, '-p', f'{port}:3000', '-v', f'{root / "data"}:/app/data', image)
        if not healthy(f'http://127.0.0.1:{port}/api/health'):
            raise RuntimeError('New service failed its health check.')
    except Exception:
        remove(container)
        if had_previous:
            docker('rename', previous, container)
            docker('start', container)
            if not healthy(f'http://127.0.0.1:{port}/api/health'):
                raise RuntimeError('Deployment and rollback health checks failed. Inspect the service on Server7.')
            print('Restored the previous service.', flush=True)
        raise
    (root / 'deployed-image.txt').write_text(image + '\n')
    print(f'Coffee shop is healthy on Server7 port {port}.', flush=True)


if __name__ == '__main__':
    main()
