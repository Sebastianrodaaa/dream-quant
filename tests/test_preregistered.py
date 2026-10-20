"""Pre-registered family tests."""

from dream_quant.research.preregistered import load_preregistered_family


def test_preregistered_family_size():
    family = load_preregistered_family({"sota_audit": {}})
    assert len(family) <= 10
    assert all("name" in c and "book" in c for c in family)
