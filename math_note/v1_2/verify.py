#!/usr/bin/env python3
"""Reproduce exact decisions, symbolic identities, scoped source audit and Lean."""
import sys
sys.dont_write_bytecode = True
import ast
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import subprocess
import tempfile
from envelope import certificate, envelope_fires, minimum_window, binary_score

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
RESULTS = HERE / 'results'
LEAN = Path('/home/happy/.elan/toolchains/leanprover--lean4---v4.32.2/bin/lean')


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def verify_inputs():
    manifest = json.loads((HERE/'INPUT_MANIFEST.json').read_text())
    for row in manifest['files']:
        b = (PARENT/row['path']).read_bytes()
        require(len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256'],row['path'])
    source_manifest = json.loads((PARENT/'sources/manifest.json').read_text())
    for row in source_manifest['files']:
        b = (PARENT/'sources'/row['name']).read_bytes()
        require(len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256'],row['name'])
    return len(manifest['files'])


def source_audit():
    # Extract ONLY pure functions/constants; do not import network/judge paths.
    module = ast.parse((PARENT/'sources/analyze.py').read_text())
    names = {'trigrams','cosine','novelty','change_type','saturation','compute_stops'}
    nodes = [node for node in module.body if isinstance(node,ast.FunctionDef) and node.name in names]
    scope = {'math':math, 'MAX_ITERS':8,'B_SIM_STOP':.98,'DR_EPS':.05,
             'LOOP_SIM':.95,'SAT_THRESHOLD':.70,'W_EMBED':.6,'W_NOVEL':.4}
    # Assert the parameters really are those of this pinned source.
    for node in module.body:
        if isinstance(node,ast.Assign):
            try:
                value = ast.literal_eval(node.value)
            except (ValueError,TypeError):
                continue
            for target in node.targets:
                if isinstance(target,ast.Name) and target.id in scope:
                    require(scope[target.id]==value,'source constant mismatch')
                elif isinstance(target,ast.Tuple):
                    for item,v in zip(target.elts,value):
                        if isinstance(item,ast.Name) and item.id in scope:
                            require(scope[item.id]==v,'source weight mismatch')
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'pinned_pure_source','exec'),scope)
    same = scope['compute_stops'](['abcdef']*9)
    loop = scope['compute_stops'](['abcdef','uvwxyz']*4+['abcdef'])
    require(same['C']==2 and same['C_reason']=='equilibrium_d_r','equilibrium witness')
    require(loop['C']==2 and loop['C_reason']=='loop','loop witness')
    require(same['trace'][1]['saturation']==0 and same['trace'][2]['saturation']==1,'sat warmup')
    rolls = [json.loads(s) for s in (PARENT/'sources/rollouts_n500_26b.jsonl').read_text().splitlines()]
    seq = {r['iteration']:r['output'] for r in rolls if r['task_id']=='hr_027'}
    u,v = (''.join(seq[i].split()) for i in (5,6))
    a,b = scope['trigrams'](seq[5]),scope['trigrams'](seq[6])
    require((len(a),len(b-a),len(a-b))==(589,5,0),'hr027 trigram counts')
    sim = scope['cosine'](a,b)
    # For this history, novelty is rederived from the seed and all iterations.
    tasks = json.loads((PARENT/'sources/tasks_n500.json').read_text())
    seed = next(t['seed'] for t in tasks if t['id']=='hr_027')
    history = [scope['trigrams'](seed)] + [scope['trigrams'](seq[i]) for i in range(1,6)]
    novel = scope['novelty'](seq[6],history)
    require(math.isclose(novel,5/594,abs_tol=1e-15),'history novelty')
    require(math.isclose(sim,math.sqrt(589/594),abs_tol=1e-15),'nested set formula')
    require(len(v)%len(u)!=0,'literal-power counterexample')
    return {'equilibrium_earliest_witness':same['C'],'loop_earliest_witness':loop['C'],
            'saturation_first_available':3,'source_network_calls':0,
            'hr027':{'a':len(a),'added':len(b-a),'removed':len(a-b),
            'new_vs_all_history':len(b-set().union(*history)),
            'sim':sim,'novelty':novel,'d_r':.6*(1-sim)+.4*novel,
            'raw_lengths':[len(seq[5]),len(seq[6])], 'normalized_lengths':[len(u),len(v)],
            'pure_power_of_previous':False,'max_two_boundary_theorem_applicable':False}}


def main():
    RESULTS.mkdir(exist_ok=True)
    input_count = verify_inputs()
    # Calibrate our assertion gate itself on known-good and known-broken input.
    require(True,'good')
    try:
        require(False,'intentional negative control')
    except AssertionError:
        pass
    else:
        raise RuntimeError('assertion gate failed to reject broken input')
    rows = [certificate(Fraction(t)) for t in ['.1','.25','.5','.7','.8','.9','.95','.98','.99']]
    require(next(r for r in rows if r['threshold']=='7/10')['n_star']==19,'nstar .7')
    all_k = [{'n':n,'k':k,'fires':envelope_fires(n,k,Fraction(7,10))}
             for n in range(2,26) for k in range(2,n+1)]
    require(len(all_k)==300,'all k count')
    require(all(not r['fires'] for r in all_k if r['n']<=18),'all supports n<=18')
    require(any(r['fires'] for r in all_k if r['n']==19),'n19 witness')
    # Independent direct entropy score checks, comfortably away from equality.
    numeric_checks = 0
    for q in range(2,16):
        for p in range(1,q):
            tau = Fraction(p,q)
            for n in range(2,31):
                for k in range(2,n+1):
                    counts = [n-k+1]+[1]*(k-1)
                    s = 1+sum((c/n)*math.log(c/n) for c in counts)/math.log(k)
                    require(envelope_fires(n,k,tau)==(s>=float(tau)),'exact/float mismatch')
                    numeric_checks += 1
    # Equality direction controls (binary uniform S=0) and strict-domain checks.
    require(envelope_fires(2,2,Fraction(0)),'>= equality boundary')
    require(not envelope_fires(19,2,Fraction(1)),'tau1 never reached')
    rejected = 0
    for thunk in [lambda:minimum_window(Fraction(0)),lambda:minimum_window(Fraction(1)),
                  lambda:minimum_window(Fraction(7,10),max_n=18),
                  lambda:minimum_window(Fraction(7,10),max_bits=1),
                  lambda:envelope_fires(10,2.0,Fraction(7,10))]:
        try:
            thunk()
        except ValueError:
            rejected += 1
    require(rejected==5,'input/resource negative controls')
    # Symbolic algebra verifies identities, not the real-analysis sign proof.
    import sympy as sp
    n,x = sp.symbols('n x',positive=True)
    r = n+1-x
    A = n*sp.log(n)-r*sp.log(r)
    F = A/(n*sp.log(x))
    D = x*sp.log(x)*(sp.log(r)+1)-A
    B = sp.log(r)+1-x/r
    identities = [sp.diff(F,x)-D/(n*x*sp.log(x)**2),
                  sp.diff(D,x)-sp.log(x)*B,sp.diff(B,x)+2/r+x/r**2,
                  D.subs(x,1),D.subs(x,n)]
    require(all(sp.simplify(e)==0 for e in identities),'symbolic identities')
    audit = source_audit()
    (RESULTS/'hr027_audit.json').write_text(json.dumps(audit['hr027'],indent=2)+'\n')
    lean_source = HERE/'lean/Envelope.lean'
    good = subprocess.run([str(LEAN),str(lean_source)],capture_output=True,text=True,timeout=60)
    (RESULTS/'lean.log').write_text(good.stdout+good.stderr)
    require(good.returncode==0 and good.stdout.count('does not depend on any axioms')==3,'Lean certs')
    mutant_results = []
    text = lean_source.read_text()
    for old,new in [('List.range 17','List.range 18'),('!envelopeFires n k 7 10','!envelopeFires n k 0 10')]:
        require(old in text,'mutation anchor')
        with tempfile.TemporaryDirectory(dir=RESULTS) as tmp:
            path = Path(tmp)/'Mutant.lean'
            path.write_text(text.replace(old,new))
            bad = subprocess.run([str(LEAN),str(path)],capture_output=True,text=True,timeout=60)
            require(bad.returncode!=0 and 'decide' in bad.stdout,'mutant rejection must be mathematical')
            mutant_results.append({'mutation':new,'rejected':True,'compiler_output':bad.stdout})
    verify_inputs()
    out = {'status':'PASS','original_hashes_verified':input_count,
           'threshold_table':rows,'all_support_cases':all_k,
           'finite_float_crosschecks':numeric_checks,'symbolic_identities':len(identities),
           'invalid_input_controls_rejected':rejected,'source_audit':audit,
           'lean_version':subprocess.check_output([str(LEAN),'--version'],text=True).strip(),
           'lean_mutants':mutant_results,
           'universal_theorem_lean_formalized':False,
           'universal_proof':'NOTE.md; independent prose review review/general_envelope.md'}
    (RESULTS/'verification.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ['all_support_cases','lean_mutants','source_audit']},indent=2))


if __name__=='__main__':
    main()
