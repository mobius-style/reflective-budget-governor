/- Finite integer certificates only. The log/exponent bridge and universal
   support-monotonicity argument are prose proofs in ../NOTE.md. -/
set_option maxRecDepth 100000
set_option maxHeartbeats 10000000

def envelopeFires (n k p q : Nat) : Bool :=
  decide (n ^ (q*n) ≤ k ^ ((q-p)*n) * (n-k+1) ^ (q*(n-k+1)))

def mixedSmallWindows : Bool :=
  ((List.range 17).map (· + 2)).all fun n =>
    ((List.range (n-1)).map (· + 2)).all fun k =>
      !envelopeFires n k 7 10

theorem all_153_small_envelopes : mixedSmallWindows = true := by decide
theorem binary_18_below :
    18^180 > 17^170 * 2^54 := by decide
theorem binary_19_above :
    19^190 < 18^180 * 2^57 := by decide

#print axioms all_153_small_envelopes
#print axioms binary_18_below
#print axioms binary_19_above
