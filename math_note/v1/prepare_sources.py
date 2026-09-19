from pathlib import Path
import hashlib, json, datetime, shutil

HERE = Path(__file__).resolve().parent
REPO = Path('/home/happy/デスクトップ/mobius_ai/MOBIUS_MMV')
RBG = REPO / 'experiments/rbg_pilot_20260815'
paths = {
    'analyze.py': RBG / 'analyze.py',
    'analyze_n500.py': RBG / 'analyze_n500.py',
    'detectors.py': REPO / 'addons/secretary/evolution/kernel/detectors.py',
    'guard.py': REPO / 'addons/secretary/evolution/kernel/guard.py',
    'T1.lean': REPO / 'docs/theory_series_2026-08/lean/T1.lean',
    'RBG_PAPER.md': REPO / 'docs/current/RBG_GOVERNOR_PAPER_v1_0_rc.md',
    'CHARTER.md': REPO / 'docs/SECRETARY_EVOLUTION_CHARTER.md',
    **{f: RBG / f for f in ['tasks_n500.json','rollouts_n500_12b.jsonl',
         'rollouts_n500_26b.jsonl','stops_12b.json','stops_26b.json','DESIGN.md','DESIGN_N500.md']},
}
manifest = {'captured_at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'files': []}
for name, src in paths.items():
    raw = src.read_bytes()
    dst = HERE / 'sources' / name
    with dst.open('xb') as f:
        f.write(raw)
    assert dst.read_bytes() == raw
    public = Path('/home/happy/デスクトップ/mobius_ai/reflective-budget-governor') / src.name
    manifest['files'].append({'name':name,'original':str(src),'bytes':len(raw),
        'sha256':hashlib.sha256(raw).hexdigest(),
        'public_checkout_equal':public.read_bytes()==raw if public.is_file() else None})
with (HERE / 'sources/manifest.json').open('x') as f:
    json.dump(manifest,f,indent=2,ensure_ascii=False)
print('snapshotted',len(paths),'files')
