import ast, itertools, math, json
from pathlib import Path
p=Path('/home/happy/デスクトップ/mobius_ai/MOBIUS_MMV/experiments/rbg_pilot_20260815/analyze.py')
t=ast.parse(p.read_text()); names={'trigrams','cosine','novelty','change_type','saturation','compute_stops'}
ns={'math':math,'MAX_ITERS':8,'B_SIM_STOP':.98,'DR_EPS':.05,'LOOP_SIM':.95,'SAT_THRESHOLD':.70,'W_EMBED':.6,'W_NOVEL':.4}
exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(p),'exec'),ns)
def parts(n,lo=1):
 if n==0: yield ()
 for c in range(lo,n+1):
  for tail in parts(n-c,c):yield(c,)+tail
rows=[]
for n in range(3,9):
 vals=[]
 for c in parts(n):
  k=len(c)
  if k==1:continue
  score=1+sum(x/n*math.log(x/n) for x in c)/math.log(k)
  exact=n**(10*n)<= k**(3*n)*math.prod(x**(10*x) for x in c)
  assert not exact
  assert score<.7
  vals.append((score,c))
 rows.append({'n':n,'max_mixed':max(vals)})
checks=0
for L in range(1,8):
 for letters in itertools.product('ab',repeat=L):
  u=''.join(letters)
  for n in range(1,10):
   m=(n+L-2)//L+1
   grams=lambda s:{s[i:i+n] for i in range(len(s)-n+1)}
   assert grams(u*m)==grams(u*(m+3))
   checks+=1
stable=ns['compute_stops'](['abab']*9)
growing=ns['compute_stops'](['ab'*(2**(i+1)) for i in range(9)])
assert stable==growing
out={'entropy':rows,'binary_word_checks':checks,'stable_equals_growing':stable==growing,'stable_stops':{k:v for k,v in stable.items() if k!='trace'},'empty_trigrams':list(ns['trigrams']('')),'space_example_type':ns['change_type']('ab ab','ab ab'*100),'short_sequence_error':None}
try:ns['compute_stops'](['abab']*8)
except Exception as e:out['short_sequence_error']=type(e).__name__
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
