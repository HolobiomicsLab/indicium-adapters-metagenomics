"""Behavioural contract for ``MetagenomicsAdapter.enrich_claim``."""

from __future__ import annotations

from indicium_adapters_metagenomics import _edam


def test_enrich_claim_is_pure(adapter):
    claim = {"subject": "Metagenomics", "qualifier": "sampled_from", "object": "human gut"}
    before = dict(claim)
    adapter.enrich_claim(claim)
    assert claim == before, "enrich_claim mutated its input"


def test_known_label_resolves_to_an_edam_curie(adapter):
    out = adapter.enrich_claim({"subject": "Metagenomics"})
    assert out["ontology_terms"]["subject"].startswith("edam:")
    assert out["ontology_term_justifications"]["subject"] == "semapv:LexicalMatching"


def test_lookup_is_case_and_whitespace_insensitive(adapter):
    spaced = adapter.enrich_claim({"subject": "  mEtAgEnOmIcS  "})
    exact = adapter.enrich_claim({"subject": "Metagenomics"})
    assert spaced["ontology_terms"]["subject"] == exact["ontology_terms"]["subject"]


def test_unresolved_text_is_recorded_not_silently_dropped(adapter):
    out = adapter.enrich_claim({"subject": "a phrase that is not an EDAM concept"})
    assert out["ontology_terms_unmatched"]["subject"] == "a phrase that is not an EDAM concept"
    assert "ontology_terms" not in out


def test_substring_of_a_concept_does_not_resolve(adapter):
    """A prefix of a real index entry must not pick that entry up -- a wrong
    CURIE is worse than no CURIE. Both strings below are proper substrings of
    concepts the shipped index does carry, so the test fails if matching ever
    loosens; a string absent from the index altogether would prove nothing."""
    for prefix in ("microbial", "metagenomic"):
        assert adapter.enrich_claim({"subject": prefix}).get("ontology_terms") is None


def test_an_already_resolved_slot_is_left_to_its_owner(adapter):
    claim = {"subject": "Metagenomics", "ontology_terms": {"subject": "NCBITaxon:2"}}
    out = adapter.enrich_claim(claim)
    assert out["ontology_terms"]["subject"] == "NCBITaxon:2"


def test_empty_and_non_string_slots_are_skipped(adapter):
    out = adapter.enrich_claim({"subject": "", "object": None, "qualifier": 42})
    assert "ontology_terms" not in out
    assert "ontology_terms_unmatched" not in out


def test_a_declared_qualifier_can_still_resolve_if_it_is_also_an_edam_label(adapter):
    """The qualifier slot is enriched like any other -- unlike the genomics
    sibling, none of this adapter's own qualifier strings collide with an EDAM
    label, so there is nothing to special-case; this test pins that fact."""
    out = adapter.enrich_claim({"qualifier": "sampled_from"})
    assert _edam.lookup("sampled_from") is None
    assert out.get("ontology_terms_unmatched", {}).get("qualifier") == "sampled_from"


def test_a_claim_with_all_three_slots_resolving_populates_every_map(adapter):
    out = adapter.enrich_claim(
        {"subject": "Metagenomics", "qualifier": "Microbial ecology", "object": "Metabarcoding"}
    )
    assert set(out["ontology_terms"]) == {"subject", "qualifier", "object"}
    assert set(out["ontology_term_justifications"]) == {"subject", "qualifier", "object"}
    assert "ontology_terms_unmatched" not in out
