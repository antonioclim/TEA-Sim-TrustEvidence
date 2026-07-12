# Finite bounded executable checks

`bounded_model_check.py` systematically explores the declared finite domain `{0,1,2}` over ordered histories of length zero through five. It checks append monotonicity, inclusion reconstruction, controlled tamper rejection, canonicalisation determinism, receipt binding, payload non-disclosure, same-size root comparison and prefix consistency.

The retained output reports 29,105 checks and zero failures for that finite domain. This is executable bounded evidence, not an unbounded theorem or mechanised formal proof.
