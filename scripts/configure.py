import os
import secrets
from pathlib import Path

root = Path(__file__).resolve().parents[1]
target = root / '.env'
if target.exists():
    print('.env already exists; preserved existing credentials.')
else:
    content = (root / '.env.example').read_text()
    content = content.replace('COFFEE_ADMIN_PASSWORD=\n', f'COFFEE_ADMIN_PASSWORD={secrets.token_urlsafe(18)}\n')
    content = content.replace('COFFEE_SESSION_SECRET=\n', f'COFFEE_SESSION_SECRET={secrets.token_urlsafe(48)}\n')
    descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'w') as output:
        output.write(content)
    print('Created .env with unique credentials. Username: manager. Password: COFFEE_ADMIN_PASSWORD in .env.')
