import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parents[1]
folder = root / 'artifacts' / 'backups'
folder.mkdir(parents=True, exist_ok=True)
filename = f"coffee-{datetime.now(timezone.utc):%Y%m%dT%H%M%S%fZ}.db"
target = folder / filename
program = "import sqlite3,sys; source=sqlite3.connect('/app/data/coffee.db'); target=sqlite3.connect(':memory:'); source.backup(target); sys.stdout.buffer.write(target.serialize()); target.close(); source.close()"
fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
try:
    with os.fdopen(fd, 'wb') as output:
        subprocess.run(['docker', 'compose', 'exec', '-T', 'coffee', 'python', '-c', program], cwd=root, stdout=output, check=True)
except Exception:
    target.unlink(missing_ok=True)
    raise
print(target)
