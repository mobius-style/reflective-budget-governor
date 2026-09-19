"""Re-run a local mathematical pilot, including calibrated acceptance and Lean controls."""
from pathlib import Path
import copy, datetime, hashlib, json, os, re, subprocess, sys, tempfile

ROOT=Path(__file__).resolve().parent
DEFAULT_LEAN=Path('/home/happy/.elan/toolchains/leanprover--lean4---v4.32.2/bin/lean')
LEAN=Path(os.environ.get('PILOT_LEAN',str(DEFAULT_LEAN)))

def run(cmd, log, timeout=120):
    p=subprocess.run(cmd,cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=timeout)
    (ROOT/'results'/log).write_text(p.stdout)
    return p

def acceptance(v,e,r,p,l):
    errors=[]
    if v.get('status')!='PASS' or v.get('source_drift')!=[]: errors.append('source/test status')
    if v.get('exact_positive_compositions')!=255 or v.get('label_triples')!=64: errors.append('finite coverage')
    if v.get('repetition_equalities')!=10160: errors.append('repetition coverage')
    if len(e.get('rows',[]))!=8 or sum(x['ordered_histograms'] for x in e['rows'])!=255: errors.append('histogram coverage')
    if e.get('calibration')!='PASS' or p.get('calibration')!='PASS': errors.append('negative controls')
    if set(r)!= {'12b','26b'}: errors.append('model coverage')
    for tag in ['12b','26b']:
        x=r.get(tag,{})
        if x.get('tasks')!=500 or x.get('generation_rows')!=4000: errors.append(tag+' incomplete')
        if x.get('stop_and_reason_and_token_mismatches')!=0 or x.get('boolean_stop_mismatches')!=0: errors.append(tag+' mismatch')
    if l.get('pilot_returncode')!=0 or l.get('t1_returncode')!=0 or not l.get('fresh_olean_bytes',0)>0: errors.append('Lean compilation')
    if set(l.get('negative_mutants_rejected',[])) != {'coverage','threshold','enumeration'}: errors.append('Lean mutant calibration')
    if l.get('forbidden_tokens') or l.get('unapproved_axioms'): errors.append('Lean trust scope')
    return errors

def finalize():
    args=[json.loads((ROOT/'results'/f).read_text()) for f in ['verification.json','entropy.json','replay.json','repetition.json','lean_checks.json']]
    failures=acceptance(*args)
    if failures: raise RuntimeError(failures)
    compiled=args[-1]
    if hashlib.sha256((ROOT/'lean/Pilot.lean').read_bytes()).hexdigest()!=compiled.get('pilot_source_sha256'):
        raise RuntimeError('Lean source changed since compilation')
    if hashlib.sha256((ROOT/'lean/Pilot.olean').read_bytes()).hexdigest()!=compiled.get('olean_sha256'):
        raise RuntimeError('Lean output changed since compilation')
    manifest=json.loads((ROOT/'sources/manifest.json').read_text())
    for rec in manifest['files']:
        for file in [ROOT/'sources'/rec['name'],Path(rec['original'])]:
            if hashlib.sha256(file.read_bytes()).hexdigest()!=rec['sha256']:
                raise RuntimeError('Source drift: '+str(file))
    broken=copy.deepcopy(args); broken[2]['12b']['generation_rows']=3999
    if not acceptance(*broken): raise RuntimeError('Acceptance failed to reject missing input')
    broken2=copy.deepcopy(args); broken2[4]['unapproved_axioms']=['sorryAx']
    if not acceptance(*broken2): raise RuntimeError('Acceptance failed to reject proof hole')
    review_paths=['review/independent_math.md','review/boundary.md','review/final_integration.md']
    reviews={f:(ROOT/f).is_file() and (ROOT/f).stat().st_size>0 for f in review_paths}
    complete=lambda rs: bool(rs) and len(rs)==3 and all(rs.values())
    assert complete(dict.fromkeys(review_paths,True))
    assert not complete({**dict.fromkeys(review_paths,True),review_paths[-1]:False})
    if not complete(reviews): raise RuntimeError('Review files incomplete: '+str(reviews))
    for f in ['NOTE.md','PROTOCOL.md','LITERATURE.md','README_JA.md']:
        if not (ROOT/f).is_file() or (ROOT/f).stat().st_size==0: raise RuntimeError('Missing deliverable '+f)
    final={'status':'PASS','finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'acceptance_positive_control':'PASS','acceptance_missing_input_control':'REJECTED',
        'acceptance_proof_hole_control':'REJECTED','acceptance_missing_review_control':'REJECTED','review_files':reviews,
        'claims':'local exploratory pilot, not new-math priority or end-to-end formal verification'}
    (ROOT/'results/acceptance.json').write_text(json.dumps(final,indent=2)+'\n')
    print(json.dumps(final,indent=2))

def main():
    if not __debug__: raise RuntimeError('Assertions must be enabled')
    p=run([sys.executable,'verify.py'],'verify.log')
    if p.returncode: raise RuntimeError(p.stdout)
    version=subprocess.check_output([str(LEAN),'--version'],text=True).strip()
    if '4.32.2' not in version: raise RuntimeError('Expected pinned Lean 4.32.2, got '+version)
    text=(ROOT/'lean/Pilot.lean').read_text()
    stripped=re.sub(r'/\-[\s\S]*?\-/','',text)
    stripped=re.sub(r'--[^\n]*','',stripped)
    bad=re.findall(r'\b(?:sorry|admit|axiom|native_decide)\b',stripped)
    checks={'lean_version':version,'forbidden_tokens':bad,'negative_mutants_rejected':[]}
    with tempfile.TemporaryDirectory(prefix='rhl_rbg_lean_') as tmp:
        tmp=Path(tmp)
        out=tmp/'Pilot.olean'
        p=run([str(LEAN),'-o',str(out),'lean/Pilot.lean'],'lean.log',60)
        checks['pilot_returncode']=p.returncode
        checks['fresh_olean_bytes']=out.stat().st_size if out.exists() else 0
        checks['olean_sha256']=hashlib.sha256(out.read_bytes()).hexdigest() if out.exists() else None
        checks['pilot_source_sha256']=hashlib.sha256((ROOT/'lean/Pilot.lean').read_bytes()).hexdigest()
        axioms=set()
        for group in re.findall(r'depends on axioms: \[([^\]]*)\]',p.stdout):
            axioms.update(x.strip() for x in group.split(',') if x.strip())
        checks['axioms']=sorted(axioms)
        checks['unapproved_axioms']=sorted(axioms-{'propext','Quot.sound'})
        if p.returncode or bad or checks['unapproved_axioms']: raise RuntimeError(p.stdout)
        (ROOT/'lean/Pilot.olean').write_bytes(out.read_bytes())
        t1=run([str(LEAN),'-o',str(tmp/'T1.olean'),'sources/T1.lean'],'t1.log',60)
        checks['t1_returncode']=t1.returncode
        checks['t1_fresh_olean_bytes']=(tmp/'T1.olean').stat().st_size if (tmp/'T1.olean').exists() else 0
        if t1.returncode or not checks['t1_fresh_olean_bytes']: raise RuntimeError(t1.stdout)
        mutants={
          'coverage':('hcover : q+L-1 ≤ M','hcover : q+L-2 ≤ M'),
          'threshold':('cs.length^(3*n)','cs.length^(10*n)'),
          'enumeration':('[1::cs, incrementHead cs]','[1::cs]'),
        }
        for label,(old,new) in mutants.items():
            assert text.count(old)==1,(label,'mutation site')
            m=tmp/(label+'.lean'); m.write_text(text.replace(old,new))
            attempt=run([str(LEAN),str(m)],'lean_mutant_'+label+'.log',60)
            if attempt.returncode==0: raise RuntimeError('Mutant survived: '+label)
            checks['negative_mutants_rejected'].append(label)
    (ROOT/'results/lean_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    finalize()

if __name__=='__main__':
    if '--finalize-only' in sys.argv: finalize()
    else: main()
