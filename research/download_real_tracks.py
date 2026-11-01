"""Download source full-resolution railway polyline GeoJSON (do not run arbitrary code).

Requires a machine with internet access. The Git-blob SHA is checked against the
exact data inspected for the 2026-10-31 comparison.
"""
from pathlib import Path
import hashlib
import ssl
import certifi
from urllib.request import Request, urlopen

URL='https://raw.githubusercontent.com/datta07/INDIAN-SHAPEFILES/master/INDIA/INDIAN_RAILWAYS.geojson'
EXPECTED_GIT_SHA='63ff14b3f3b62a6d18d4950e9ab4ba99a3c5c16d'
OUT=Path(__file__).resolve().parents[1]/'data'/'INDIAN_RAILWAYS.geojson'


def main():
    print('Downloading 34 MB of line geometry (source: datta07/INDIAN-SHAPEFILES)...')
    req=Request(URL,headers={'User-Agent':'SLIMEROUTE-study/1.0'})
    with urlopen(req, timeout=60, context=ssl.create_default_context(cafile=certifi.where())) as r:
        buf=r.read(70_000_001)
    if len(buf)>70_000_000:
        raise ValueError('Source unexpectedly large; refusing to save')
    actual=hashlib.sha1(f'blob {len(buf)}\0'.encode()+buf).hexdigest()
    if actual != EXPECTED_GIT_SHA:
        raise ValueError(f'Source version changed: git blob {actual}; expected {EXPECTED_GIT_SHA}. Re-audit before using.')
    OUT.write_bytes(buf)
    print(f'Verified SHA {actual}. Saved {OUT}.')

if __name__=='__main__':main()
