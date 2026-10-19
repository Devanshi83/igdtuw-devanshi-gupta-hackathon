"""Check local package requirements; --strict also requires a YouTube link."""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


def check(strict=False):
    errors=[]
    required=['README.md','LICENSE','requirements.txt','app.py','docs/presentation.pdf',
              'docs/architecture.png','data/synthetic_portfolio.csv','data/scenarios.json',
              'data/sample_news.json','data/sample_social_posts.json','data/market_data/price_cache.csv',
              'data/manifest.json','results/real_data/metrics.json','results/demo/bank_credit_audit.json']
    for name in required:
        if not (ROOT/name).is_file() or (ROOT/name).stat().st_size == 0:
            errors.append(f'Missing/empty: {name}')
    readme=(ROOT/'README.md').read_text()
    if 'devanshi034bteceai24@igdtuw.ac.in' not in readme:
        errors.append('College email missing')
    for match in re.finditer(r'\]\(([^)]+)\)', readme):
        target=match.group(1)
        if not target.startswith(('https://','http://','#')) and not (ROOT/target).exists():
            errors.append(f'Broken local README link: {target}')
    manifest_path=ROOT/'data/manifest.json'
    if manifest_path.exists():
        for item in json.loads(manifest_path.read_text())['files']:
            file=ROOT/item['path']
            if not file.exists() or hashlib.sha256(file.read_bytes()).hexdigest()!=item['sha256']:
                errors.append(f'Data checksum mismatch: {item["path"]}')
    metrics_path=ROOT/'results/real_data/metrics.json'
    if metrics_path.exists():
        metrics=json.loads(metrics_path.read_text())
        actual=hashlib.sha256((ROOT/'src/nlp/analyzer.py').read_bytes()).hexdigest()
        if metrics.get('provenance',{}).get('analyzer_sha256') != actual:
            errors.append('Sentiment metrics do not match the current analyzer source; rerun evaluation')
    video=bool(re.search(r'https://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[\w-]+', readme))
    if not video:
        print('ACTION REQUIRED: record/upload an unlisted YouTube demo and add its URL to README.')
        if strict: errors.append('Required demo video URL missing')
    print('MANUAL CHECKS: original case alignment, official deadline, public playback, final form submission.')
    for error in errors: print('FAIL:',error)
    if not errors: print('Local package checks passed.' + (' External/manual checks remain.' if strict else ' This does not certify submission readiness.'))
    return 1 if errors else 0

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--strict',action='store_true')
    sys.exit(check(parser.parse_args().strict))
