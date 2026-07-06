
---- MODULE TrustEvidenceLog ----
EXTENDS Naturals, Sequences
VARIABLES log, roots
Init == log = << >> /\ roots = [0 |-> "empty"]
Append(e) == /\ log' = Append(log, e)
             /\ roots' = [roots EXCEPT ![Len(log')] = "root"]
Next == \E e \in Nat : Append(e)
TypeOK == log \in Seq(Nat)
AppendMonotone == Len(log') >= Len(log)
====
