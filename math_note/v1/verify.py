"""Offline exact checks and production-source replay. No inference or writes to sources."""
from pathlib import Path
from collections import Counter, defaultdict
from itertools import product
from unittest.mock import patch
import datetime, hashlib, importlib.util, json, math, sys, types

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
SRC = HERE / 'sources'

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

def dump(name, data):
    (HERE / 'results' / name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

def compositions(n):
    if n == 0:
        yield ()
    else:
        for c in range(1,n+1):
            for rest in compositions(n-c):
                yield (c,)+rest

def sat(cs):
    n, k = sum(cs), len(cs)
    return 1.0 if k == 1 else 1+sum((c/n)*math.log(c/n) for c in cs)/math.log(k)

def exact_sat(cs, a=7, b=10):
    """S >= a/b. Positive integer histogram, observed-support normalization."""
    assert cs and all(c>0 for c in cs) and 0 <= a <= b
    n,k=sum(cs),len(cs)
    return True if k == 1 else n**(b*n) <= k**((b-a)*n)*math.prod(c**(b*c) for c in cs)

def grams(s, q):
    return {s[i:i+q] for i in range(max(0,len(s)-q+1))}

def main():
    mf=json.loads((SRC/'manifest.json').read_text())
    for rec in mf['files']:
        assert hashlib.sha256((SRC/rec['name']).read_bytes()).hexdigest()==rec['sha256']
    rbg=load('pilot_rbg',SRC/'analyze.py')
    pkg=types.ModuleType('pilotkernel'); pkg.__path__=[]
    ledger=types.ModuleType('pilotkernel.ledger')
    sys.modules['pilotkernel']=pkg; sys.modules['pilotkernel.ledger']=ledger
    rhl=load('pilotkernel.detectors',SRC/'detectors.py')
    rows=[]
    # All 2^(n-1) ordered positive compositions, not only chosen mutants.
    for n in range(1,9):
        histograms=list(compositions(n)); mixed=[c for c in histograms if len(c)>1]
        best=max(mixed,key=sat) if mixed else None
        for cs in histograms:
            assert exact_sat(cs)==(len(cs)==1)
            assert (sat(cs)>=.7)==exact_sat(cs)
            labels=[str(i) for i,c in enumerate(cs) for _ in range(c)]
            proposals=[{'value_axis':x} for x in labels]
            with patch.object(rhl,'_recent_proposals',lambda window=8: proposals[-window:]):
                actual=rhl.saturation_score()
            assert (actual>=rhl.SATURATION_THRESHOLD)==(n>=5 and len(cs)==1)
        rows.append({'n':n,'ordered_histograms':len(histograms),'max_mixed_histogram':best,
                     'max_mixed_score':sat(best) if best else None})
    all_types=['no_change','expand','compress','rewrite']
    for labels in product(all_types,repeat=3):
        assert (rbg.saturation(labels)>=rbg.SAT_THRESHOLD)==(len(set(labels))==1)
    # Edge cases and calibration: controls must fail the intended false assertion.
    for n in range(3):
        assert rbg.saturation(['expand']*n)==0
    assert not exact_sat((2,1)) and exact_sat((3,))
    assert exact_sat((2,1),0,1)  # mutant threshold 0: unanimity equivalence fails
    assert grams('abc',3)!=grams('abcabc',3)  # faulty first-copy invariance killed
    assert grams('abcabc',3)==grams('abcabcabc',3)  # good case
    fixed_k=1+sum((c/8)*math.log(c/8) for c in [7,1])/math.log(8)
    assert fixed_k>=.7 and not exact_sat((7,1))  # fixed-vs-observed support mutant
    first_nonunanimous=None
    for n in range(2,65):
        # Convexity reduces maximum to k-1 singleton cells; see NOTE.md proof.
        candidates=[(n-k+1,)+(1,)*(k-1) for k in range(2,n+1)]
        good=[cs for cs in candidates if exact_sat(cs)]
        if good:
            first_nonunanimous={'n':n,'histogram':good[0],'score':sat(good[0])}
            break
    same_max=[(910,89,1),(910,45,45)]
    assert max(same_max[0])==max(same_max[1]) and sum(same_max[0])==sum(same_max[1])
    assert exact_sat(same_max[0]) and not exact_sat(same_max[1])
    dump('entropy.json',{'rows':rows,'rbg_label_triples':64,'first_nonunanimous_by_envelope':first_nonunanimous,
                         'fixed_alphabet_mutant_score':fixed_k,'calibration':'PASS',
                         'same_max_counterexample_tau_07':[{'counts':cs,'score':sat(cs),'exact_fires':exact_sat(cs)} for cs in same_max]})

    # All binary words of lengths 1..7, q=1..8, repetitions through bound+4.
    repeat_checks=0
    for L in range(1,8):
        for bits in product('ab',repeat=L):
            u=''.join(bits)
            for q in range(1,9):
                bound=(q+L-2)//L+1
                target=grams(u*bound,q)
                for m in range(bound,bound+5):
                    assert grams(u*m,q)==target
                    repeat_checks+=1
    # Sharpness witnesses with distinct symbols at each phase (q>=2).
    sharp=[]
    for L in range(1,9):
        u=''.join(chr(65+i) for i in range(L))
        for q in range(2,9):
            bound=(q+L-2)//L+1
            assert grams(u*(bound-1),q)!=grams(u*bound,q)
            sharp.append([L,q,bound])
    # Actual full governor, including raw length branch precedence.
    benign=['abc'*2]*9
    growing=['abc'*(2**(i+1)) for i in range(9)]
    a,b=rbg.compute_stops(benign),rbg.compute_stops(growing)
    assert a==b and a['B']==1 and a['C']==2 and a['C_reason']=='equilibrium_d_r'
    assert all(x['type']=='no_change' and x['d_r']==0 for x in a['trace'])
    assert rbg.trigrams('')=={''} and rbg.trigrams('a')!={}
    assert rbg.trigrams('a')!=rbg.trigrams('aa')!=rbg.trigrams('aaa')
    assert rbg.trigrams('a b c'*2)==rbg.trigrams('abc'*2)
    # Quantified one-copy boundary disturbance; worst-case b<=q-1.
    boundary_checks=0
    for L in range(3,8):
        for bits in product('ab',repeat=L):
            u=''.join(bits)
            for q in range(1,L+1):
                A,B=grams(u,q),grams(u*2,q)
                assert A<=B and len(B-A)<=q-1
                assert math.isclose(len(A&B)/math.sqrt(len(A)*len(B)),math.sqrt(len(A)/len(B)))
                boundary_checks+=1
    # d_R<=1/20 is equivalent to -23a^2+274ab+361b^2<=0 for r=a/(a+b).
    dr_exact=lambda a,b: -23*a*a+274*a*b+361*b*b<=0
    assert dr_exact(27,2) and not dr_exact(26,2)
    assert 10000*32 >= 97**2*(32+2) and not 10000*31>=97**2*(31+2)
    assert 10000*49 >= 98**2*(49+2) and not 10000*48>=98**2*(48+2)
    u=''.join(chr(0x400+i) for i in range(51))  # 49 internal triples, 2 new boundary triples
    assert len(rbg.trigrams(u))==49 and len(rbg.trigrams(u*2)-rbg.trigrams(u))==2
    schedules=[[1]+[2]*8,[1]+[2**i for i in range(1,9)]]
    boundary_traces=[rbg.compute_stops([u*m for m in ms]) for ms in schedules]
    assert boundary_traces[0]==boundary_traces[1]
    assert boundary_traces[0]['B']==1 and boundary_traces[0]['C']==2
    dump('repetition.json',{'exhaustive_equalities':repeat_checks,'sharpness_witnesses':sharp,
        'first_copy_counterexample':{'u':'abc','G1':sorted(grams('abc',3)),'G2':sorted(grams('abcabc',3))},
        'indistinguishable_full_governor':a,'benign_lengths':list(map(len,benign)),
        'growing_lengths':list(map(len,growing)),'calibration':'PASS',
        'one_copy_boundary_checks':boundary_checks,'threshold_cardinalities':{'d_r_005':27,'type_097':32,'arm_b_098':49},
        'one_copy_trace_witness':boundary_traces[0]})

    # Complete real data and per-chain replay. Full pre-existing artifacts stay intact.
    task_list=json.loads((SRC/'tasks_n500.json').read_text())
    tasks={t['id']:t for t in task_list}; assert len(tasks)==len(task_list)==500
    replay={}
    original_sat=rbg.saturation
    boolean_sat=lambda ts: 1.0 if len(ts)>=3 and len(set(ts[-3:]))==1 else 0.0
    for tag in ['12b','26b']:
        chains=defaultdict(dict); rowcount=0
        for line in (SRC/f'rollouts_n500_{tag}.jsonl').read_text().splitlines():
            rec=json.loads(line); tid,it=rec['task_id'],rec['iteration']
            assert tid in tasks and it not in chains[tid]
            chains[tid][it]=rec; rowcount+=1
        assert set(chains)==set(tasks) and rowcount==4000
        saved=json.loads((SRC/f'stops_{tag}.json').read_text())
        assert set(saved)==set(tasks)
        reasons=Counter(); hist=Counter(); witness={}; selected=[]
        for tid,t in tasks.items():
            iters=chains[tid]; assert set(iters)==set(range(1,9))
            seq=[t['seed']]+[iters[i]['output'] for i in range(1,9)]
            baseline=rbg.compute_stops(seq)
            with patch.object(rbg,'saturation',boolean_sat):
                changed=rbg.compute_stops(seq)
            for key in ['A','B','C','C_reason']:
                assert baseline[key]==changed[key],(tag,tid,key)
            for key in ['A','B','C']:
                assert baseline[key]==saved[tid]['stops'][key],(tag,tid,key,'saved')
                tokens=sum(iters[i]['prompt_tokens']+iters[i]['eval_tokens'] for i in range(1,baseline[key]+1))
                assert tokens==saved[tid]['tokens'][key]
            assert baseline['C_reason']==saved[tid]['C_reason']
            kinds=[]
            for row in baseline['trace']:
                kinds.append(row['type'])
                score=original_sat(kinds)
                assert (score>=.7)==(len(kinds)>=3 and len(set(kinds[-3:]))==1)
                if len(kinds)>=3: hist[str(tuple(sorted(Counter(kinds[-3:]).values(),reverse=True)))]+=1
            reasons[baseline['C_reason']]+=1
            if baseline['C_reason']=='saturation': selected.append(tid)
            if tid=='hr_027':
                witness={'lengths':list(map(len,seq)),'baseline':baseline}
        replay[tag]={'tasks':len(chains),'generation_rows':rowcount,'compared_steps':rowcount,
                     'stop_and_reason_and_token_mismatches':0,'boolean_stop_mismatches':0,
                     'reasons':dict(reasons),'three_step_histograms':dict(hist),'hr_027':witness,
                     'saturation_selected_tasks':selected}
        dump('replay.json',replay)
    # No original implementation or source data changed during the run.
    drift=[]
    for rec in mf['files']:
        if hashlib.sha256(Path(rec['original']).read_bytes()).hexdigest()!=rec['sha256']:
            drift.append(rec['original'])
    assert not drift,drift
    dump('verification.json',{'status':'PASS','finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'source_files':len(mf['files']),'source_drift':drift,'exact_positive_compositions':sum(2**(n-1) for n in range(1,9)),
        'label_triples':64,'repetition_equalities':repeat_checks,'real_chains':1000,'generation_rows':8000,
        'scope':'exact finite tests + source replay; universal proofs in NOTE.md; no performance inference'})
    print(json.dumps(json.loads((HERE/'results/verification.json').read_text()),indent=2))

if __name__=='__main__': main()
