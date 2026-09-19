import ast, math, json
from pathlib import Path
p=Path('/home/happy/デスクトップ/mobius_ai/MOBIUS_MMV/experiments/rbg_pilot_20260815/analyze.py')
names={'trigrams','cosine','novelty','change_type','saturation','compute_stops'}
ns={'math':math,'MAX_ITERS':8,'B_SIM_STOP':.98,'DR_EPS':.05,'LOOP_SIM':.95,'SAT_THRESHOLD':.70,'W_EMBED':.6,'W_NOVEL':.4}
exec(compile(ast.Module(body=[n for n in ast.parse(p.read_text()).body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(p),'exec'),ns)
rows=[]
for a in (26,27,31,32,48,49):
 u=''.join(chr(0x4e00+i) for i in range(a+2))
 A=ns['trigrams'](u);T=ns['trigrams'](u*2)
 assert len(A)==a and len(T-A)==2
 stable=ns['compute_stops']([u]+[u*2]*8)
 growth=ns['compute_stops']([u]+[u*2**i for i in range(1,9)])
 assert stable==growth
 rows.append({'a':a,'extra':len(T-A),'d_r':.6*(1-math.sqrt(a/(a+2)))+.8/(a+2),'dr_exact_pass':144*a*(a+2)>=(11*a+38)**2,'sim97_exact_pass':10000*a>=9409*(a+2),'sim98_exact_pass':10000*a>=9604*(a+2),'trace_equal':True,'B':stable['B'],'C':stable['C'],'C_reason':stable['C_reason']})
p=Path(__file__).with_suffix('.json');p.write_text(json.dumps(rows,indent=2));print(p.read_text())
