/-
Core-only Lean 4.32.2. No sorry, native_decide, or added axioms.
Periodic finite-window representation and feature-only non-identifiability.
The whitespace/Python interface and logarithm-to-integer bridge are prose proofs.
-/
namespace Pilot

def gram {α : Type} (u : Nat → α) (L q i : Nat) : List α :=
  (List.range q).map (fun j => u ((i+j)%L))

def seen {α : Type} (u : Nat → α) (L q M : Nat) (w : List α) : Prop :=
  ∃ i, i+q ≤ M ∧ w = gram u L q i

def phase {α : Type} (u : Nat → α) (L q : Nat) (w : List α) : Prop :=
  ∃ r, r < L ∧ w = gram u L q r

theorem gram_mod {α : Type} (u : Nat → α) (L q i : Nat) :
    gram u L q (i%L) = gram u L q i := by
  simp only [gram, Nat.add_mod, Nat.mod_mod]

/-- Once a finite periodic prefix contains a full period of starts, all grams appear. -/
theorem seen_iff_phase {α : Type} (u : Nat → α) {L q M : Nat}
    (hL : 0 < L) (hcover : q+L-1 ≤ M) (w : List α) :
    seen u L q M w ↔ phase u L q w := by
  constructor
  · rintro ⟨i, _, hw⟩
    exact ⟨i%L, Nat.mod_lt i hL, hw.trans (gram_mod u L q i).symm⟩
  · rintro ⟨r, hr, hw⟩
    exact ⟨r, by omega, hw⟩

/-- Universal repetition stabilization: gram presence is independent of copy count. -/
theorem repetition_stability {α : Type} (u : Nat → α) {L q m n : Nat}
    (hL : 0 < L) (hm : q+L-1 ≤ m*L) (hn : q+L-1 ≤ n*L) (w : List α) :
    seen u L q (m*L) w ↔ seen u L q (n*L) w := by
  exact (seen_iff_phase u hL hm w).trans (seen_iff_phase u hL hn w).symm

/-- Any deterministic observer factoring through a feature cannot split a feature collision. -/
theorem feature_collision {X F Y : Type} (feature : X → F) (observer : F → Y)
    {x y : X} (h : feature x = feature y) :
    observer (feature x) = observer (feature y) := congrArg observer h

/-- An injective desired label cannot factor through a non-injective feature. -/
theorem cannot_recover {X F Y : Type} (feature : X → F) (label : X → Y)
    {x y : X} (hsame : feature x = feature y) (hdiff : label x ≠ label y) :
    ¬ ∃ observer : F → Y, ∀ z, observer (feature z) = label z := by
  rintro ⟨observer, h⟩
  apply hdiff
  calc
    label x = observer (feature x) := (h x).symm
    _ = observer (feature y) := feature_collision feature observer hsame
    _ = label y := h y

/-- Positive compositions: add a new first cell or increment the current first cell. -/
def incrementHead : List Nat → List Nat
  | [] => [1]
  | a::as => (a+1)::as

def compositions : Nat → List (List Nat)
  | 0 => [[]]
  | 1 => [[1]]
  | n+2 => (compositions (n+1)).flatMap (fun cs => [1::cs, incrementHead cs])

/-- The finite certificate's generator covers every positive integer histogram. -/
theorem compositions_complete (n : Nat) : ∀ cs : List Nat,
    cs.sum = n → (∀ c ∈ cs, 0 < c) → cs ∈ compositions n := by
  induction n using Nat.strongRecOn with
  | ind n ih =>
    intro cs hs hp
    cases n with
    | zero =>
      cases cs with
      | nil => simp [compositions]
      | cons c rest =>
        have hc := hp c (by simp)
        simp only [List.sum_cons] at hs
        omega
    | succ t =>
      cases t with
      | zero =>
        cases cs with
        | nil => simp at hs
        | cons c rest =>
          have hc := hp c (by simp)
          cases rest with
          | nil =>
            simp only [List.sum_cons, List.sum_nil, Nat.add_zero] at hs
            subst c
            simp [compositions]
          | cons d tail =>
            have hd := hp d (by simp)
            simp only [List.sum_cons] at hs
            omega
      | succ t =>
        cases cs with
        | nil => simp at hs
        | cons c rest =>
          have hc := hp c (by simp)
          have hrest : ∀ d ∈ rest, 0 < d := by
            intro d hd
            exact hp d (by simp [hd])
          simp only [List.sum_cons] at hs
          by_cases heq : c = 1
          · subst c
            have hr : rest.sum = t+1 := by omega
            have hmem := ih (t+1) (by omega) rest hr hrest
            simp only [compositions, List.mem_flatMap]
            exact ⟨rest, hmem, by simp⟩
          · have hpred : 0 < c-1 := by omega
            have hsum : ((c-1)::rest).sum = t+1 := by
              simp only [List.sum_cons]
              omega
            have hpos : ∀ d ∈ (c-1)::rest, 0 < d := by
              intro d hd
              simp only [List.mem_cons] at hd
              rcases hd with hd | hd
              · simpa [hd] using hpred
              · exact hrest d hd
            have hmem := ih (t+1) (by omega) ((c-1)::rest) hsum hpos
            simp only [compositions, List.mem_flatMap]
            refine ⟨(c-1)::rest, hmem, ?_⟩
            have he : c-1+1 = c := by omega
            simp [incrementHead, he]

def exactSat (cs : List Nat) : Bool :=
  if cs.length == 1 then true else
    let n := cs.sum
    decide (n^(10*n) ≤ cs.length^(3*n) * (cs.map (fun c => c^(10*c))).prod)

def allSmallChecks : Bool :=
  ((List.range 8).map (·+1)).all (fun n =>
    (compositions n).all (fun cs => exactSat cs == (cs.length == 1)))

set_option maxRecDepth 100000
set_option maxHeartbeats 0

/-- Exact finite arithmetic certificate over the generated positive histograms n=1..8. -/
theorem exact_small_certificate : allSmallChecks = true := by decide

/-- Universal over all positive lists in the stated finite-sum domain. -/
theorem exact_small_unanimity (cs : List Nat) (hpos : ∀ c ∈ cs, 0 < c)
    (hlo : 1 ≤ cs.sum) (hhi : cs.sum ≤ 8) :
    exactSat cs = (cs.length == 1) := by
  have hn : cs.sum ∈ (List.range 8).map (·+1) := by
    apply List.mem_map.mpr
    refine ⟨cs.sum-1, List.mem_range.mpr (by omega), by omega⟩
  have hall := List.all_eq_true.mp exact_small_certificate
  have hcs := List.all_eq_true.mp (hall cs.sum hn)
  have he := hcs cs (compositions_complete cs.sum cs rfl hpos)
  exact beq_iff_eq.mp he

/-- Exact squared cosine threshold at the worst-case two added trigrams. -/
theorem cosine_098_boundary :
    10000*49 ≥ 98^2*(49+2) ∧ ¬ 10000*48 ≥ 98^2*(48+2) := by decide

theorem cosine_097_boundary :
    10000*32 ≥ 97^2*(32+2) ∧ ¬ 10000*31 ≥ 97^2*(31+2) := by decide

/-- Integer certificate after squaring the nonnegative d_R threshold expression. -/
theorem dr_boundary :
    23*27^2 ≥ 274*27*2+361*2^2 ∧
    ¬ 23*26^2 ≥ 274*26*2+361*2^2 := by decide

#print axioms repetition_stability
#print axioms cannot_recover
#print axioms exact_small_certificate
#print axioms exact_small_unanimity
#print axioms cosine_098_boundary
#print axioms cosine_097_boundary
#print axioms dr_boundary
end Pilot
