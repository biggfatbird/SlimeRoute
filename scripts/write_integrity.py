"""Write checksums for distributable files, excluding transient execution caches."""
from pathlib import Path
import hashlib
ROOT=Path(__file__).resolve().parents[1]
SKIP={'.git','__pycache__','.pytest_cache','.matplotlib-cache','.venv'}
files=sorted(p for p in ROOT.rglob('*') if p.is_file() and not SKIP.intersection(p.relative_to(ROOT).parts) and p.name not in ('INTEGRITY.sha256','.DS_Store'))
(ROOT/'INTEGRITY.sha256').write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT).as_posix()}\n' for p in files))
print(f'Checksummed {len(files)} files')
