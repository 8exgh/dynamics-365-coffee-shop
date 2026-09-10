import io
import json
import subprocess

import pytest

from deployment import deploy


@pytest.fixture
def simulation(tmp_path, monkeypatch):
    image = 'ghcr.io/8exgh/dynamics-365-coffee-shop@sha256:' + 'a' * 64
    monkeypatch.setenv('COFFEE_IMAGE', image)
    monkeypatch.setenv('COFFEE_ADMIN_PASSWORD', 'deployment-test-password')
    monkeypatch.setenv('COFFEE_SESSION_SECRET', 'deployment-test-secret-at-least-32-characters')
    monkeypatch.setenv('GITHUB_REPOSITORY_OWNER', '8exgh')
    for folder in ['config', 'data', 'backups']:
        (tmp_path / folder).mkdir()
    monkeypatch.setattr(deploy, 'Path', lambda value: tmp_path)
    monkeypatch.setattr(deploy.time, 'sleep', lambda value: None)
    name = 'sean-web-dynamics-365-coffee-shop'
    state = {'containers': {name: 'old-image'}, 'calls': [], 'fail_new': False, 'occupied': False}
    def run(command, **kwargs):
        state['calls'].append(command)
        args = command[1:]
        output = ''
        if args[0] == 'ps':
            query = args[args.index('--filter') + 1]
            if query.startswith('publish='):
                output = 'unrelated-app' if state['occupied'] else name
            else:
                candidate = query.removeprefix('name=^/').removesuffix('$')
                output = candidate if candidate in state['containers'] else ''
        elif args[0] == 'run':
            state['containers'][args[args.index('--name') + 1]] = args[-1]
        elif args[0] == 'rm':
            state['containers'].pop(args[-1], None)
        elif args[0] == 'rename':
            state['containers'][args[2]] = state['containers'].pop(args[1])
        elif args[0] == 'port':
            output = '127.0.0.1:45678'
        elif args[0] == 'exec':
            kwargs['stdout'].write(b'SQLite test backup')
        return subprocess.CompletedProcess(command, 0, stdout=output, stderr='')
    def response(url, **kwargs):
        if ':3067/' in url and state['fail_new'] and state['containers'].get(name) != 'old-image':
            raise OSError('Simulated failed startup')
        return io.BytesIO(json.dumps({'status': 'ok'}).encode())
    monkeypatch.setattr(deploy.subprocess, 'run', run)
    monkeypatch.setattr(deploy.urllib.request, 'urlopen', response)
    return state, tmp_path, name, image


def test_deployment_preserves_backup_and_previous_container(simulation):
    state, root, name, image = simulation
    deploy.main()
    assert state['containers'][name] == image
    assert state['containers'][name + '-previous'] == 'old-image'
    assert name + '-candidate' not in state['containers']
    assert (root / 'deployed-image.txt').read_text().strip() == image
    assert len(list((root / 'backups').glob('*.db'))) == 1
    assert (root / 'config/runtime.env').stat().st_mode & 0o777 == 0o600


def test_failed_deployment_restores_previous_service(simulation):
    state, root, name, image = simulation
    state['fail_new'] = True
    with pytest.raises(RuntimeError, match='New service failed'):
        deploy.main()
    assert state['containers'] == {name: 'old-image'}
    assert ['docker', 'start', name] in state['calls']
    assert not (root / 'deployed-image.txt').exists()


def test_port_conflict_never_removes_another_application(simulation):
    state, root, name, image = simulation
    state['occupied'] = True
    with pytest.raises(SystemExit, match='Port 3067 belongs to unrelated-app'):
        deploy.main()
    assert not any(call[1] in {'rm', 'stop', 'pull', 'run'} for call in state['calls'])
