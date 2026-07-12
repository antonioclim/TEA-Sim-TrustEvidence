from trustevidence.commitment import commit_payload, verify_payload_commitment


def test_commitment_binds_payload_nonce_profile_and_context():
    payload = b'{"samples":[101,104]}'
    nonce = bytes.fromhex("00112233445566778899aabbccddeeff")
    kwargs = {"representation_profile": "application/json;te-synthetic-cgm-v1", "commitment_context": "urn:te:object:cgm-day-1"}
    commitment = commit_payload(payload, nonce=nonce, **kwargs)
    assert verify_payload_commitment(commitment, payload, nonce=nonce, **kwargs)
    assert not verify_payload_commitment(commitment, payload + b" ", nonce=nonce, **kwargs)
    assert not verify_payload_commitment(commitment, payload, nonce=bytes(16), **kwargs)


def test_short_nonce_is_rejected():
    import pytest
    with pytest.raises(ValueError):
        commit_payload(b"x", nonce=b"short", representation_profile="binary", commitment_context="test")
