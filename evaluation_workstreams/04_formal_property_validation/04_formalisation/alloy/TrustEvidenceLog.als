
module TrustEvidenceLog
sig Evidence {}
sig Log { entries: seq Evidence }
pred append[l,l':Log,e:Evidence] { l'.entries = l.entries.add[e] }
assert AppendMonotone { all l,l':Log,e:Evidence | append[l,l',e] implies #l'.entries = #l.entries.plus[1] }
check AppendMonotone for 4
