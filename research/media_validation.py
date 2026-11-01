"""Validate published media without silently skipping a missing tool."""
import json
import re
import shutil
import subprocess
from pathlib import Path


def check_media(out):
    ffmpeg = shutil.which('ffmpeg')
    if ffmpeg is None:
        raise RuntimeError('FFmpeg is required for the publication gate')
    video = Path(out) / 'slime_india_final.mp4'
    info = subprocess.run([ffmpeg, '-hide_banner', '-i', str(video)], capture_output=True, text=True).stderr
    duration = re.search(r'Duration: (\d+):(\d+):([\d.]+)', info)
    if not duration:
        raise AssertionError('Cannot read video duration')
    hours, minutes, seconds = map(float, duration.groups())
    assert 26 < hours*3600 + minutes*60 + seconds < 29, info
    assert re.search(r'Video: h264.*1080x1350', info), info
    assert 'Audio:' not in info, 'Expected silent video'
    subprocess.run([ffmpeg, '-v', 'error', '-i', str(video), '-f', 'null', '-'], check=True, capture_output=True)
    from PIL import Image
    from pypdf import PdfReader
    paths = sorted((Path(out)/'carousel').glob('slide_*.png'))
    assert len(paths) == 7
    for path in paths:
        with Image.open(path) as im:
            assert im.size == (1080,1350)
            im.verify()
    assert len(PdfReader(Path(out)/'slimeroute_carousel.pdf').pages) == 7
    manifest = json.loads((Path(out)/'publication_numbers.json').read_text())
    read=lambda name: json.loads((Path(out)/name).read_text())
    assert manifest['seed7']==read('benchmark_metrics.json')['unaffected']['Physarum']
    assert manifest['heuristic']==read('augmented_mst_metrics.json')['metrics']
    assert manifest['preliminary_rail_detour']==read('fullres_rail_analysis.json')['rail_topology']['mean_detour']
    assert manifest['recovery']==read('recovery_v42.json')
    rs=read('resilience_study.json')['results']['150']
    for key,value in manifest['static_150km'].items():
        assert value==rs[key]['fraction_all_pairs_connected']
    assert manifest['scope'] == 'Public v4.2 review branch; main remains v4.1'
