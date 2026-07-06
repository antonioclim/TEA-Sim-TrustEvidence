# Security considerations

An EvidenceAnchor is not a proof by itself. A2 non-equivocation requires witness, gossip or checkpoint comparison. A3 finality requires a concrete quorum/finality assumption. Implementations must protect transport, authenticate users and clients, restrict audit access and preserve retained verifier state.
