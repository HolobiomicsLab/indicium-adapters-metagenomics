"""MetagenomicsAdapter -- the metagenomics DomainAdapter (api_version=1)."""

from __future__ import annotations

from typing import Final

from . import _edam
from ._namespaces import METAGENOMICS_PREFIXES

# Claim slots worth resolving against the EDAM index. ``qualifier`` is included
# because a qualifier literal sometimes carries a concept name itself
# ("taxonomic profiling"), which is itself an EDAM topic or operation.
_ENRICHABLE_SLOTS: Final[tuple[str, ...]] = ("subject", "object", "qualifier")

# SSSOM justification for a label / synonym string match. Every CURIE this
# adapter emits comes from exact-after-normalisation matching against EDAM, so
# this is the only justification it can honestly claim.
_LEXICAL: Final[str] = "semapv:LexicalMatching"


class MetagenomicsAdapter:
    """Shotgun sequencing of whole microbial communities.

    Owns the tier-3 concerns only (ADR 0001): the classification vocabulary and
    claim/ontology enrichment over already-extracted, already-validated claim
    dicts. It deliberately does **not** recognise repository accessions (SRA,
    ENA, MGnify, IMG) in article text -- those belong to the canonical
    accession table in ``asb-domain-core``, and a second copy of those patterns
    here would be the duplicate-then-drift failure ADR 0001 exists to prevent.
    What this adapter contributes for identifiers is ``ontology_prefixes``, so
    a consumer can expand the CURIEs that tier produces.

    The concept vocabulary is read from EDAM, cut from four roots: Metagenomics
    itself, plus Metagenomic sequencing, Microbial ecology and
    Metatranscriptomics. A shotgun metagenomics paper routinely claims all
    three of the latter, but EDAM files each of them elsewhere in its tree
    (under Sequencing, Ecology and Transcriptomics respectively), so none is
    reachable by walking down from the Metagenomics topic and each has to be
    named as its own root -- see ``data/build_edam_index.py`` for the recorded
    reasoning, the same pattern the genomics sibling uses for
    Metatranscriptomics.

    ``subdomains`` are read off that same EDAM walk rather than hand-listed, so
    the vocabulary is the field's own and moves with an EDAM release.
    ``techniques`` are curated: EDAM models assays as operations and data
    rather than as a technique hierarchy for this domain, so there is nothing
    to derive.

    Every qualifier matches ``^[a-z][a-z0-9_]*$`` (snake_case), required
    because Perspicacite routes adapter qualifiers onto the open
    ``asb:domainQualifier`` slot whose SHACL shape enforces that pattern.
    """

    domain_id = "metagenomics"
    api_version = 1

    # ASB's classification layer reads ``primary_domain`` in preference to
    # ``domain_id`` (see agentic_science_builder.classification._adapter_vocab),
    # and unions it into the controlled vocabulary. Declaring it here is what
    # stops a metagenomics paper classifying as "other".
    primary_domain = "metagenomics"

    qualifiers: frozenset[str] = frozenset(
        {
            # --- Sequencing and assembly ----------------------------------------
            "sequenced_on",  # object is the sequencing platform
            "assembled_with",  # object is the assembler
            "co_assembled_with",  # object is the other samples or read sets co-assembled
            "mapped_to",  # object is the reference or co-assembly the reads were mapped to
            "has_assembly_metric",  # object is a contiguity or completeness value
            # --- Binning and MAG quality ----------------------------------------
            "binned_with",  # object is the binning tool
            "dereplicated_with",  # object is the genome dereplication tool
            "assessed_for_quality_by",  # object is the completeness/contamination tool
            "has_completeness",  # object is the estimated genome completeness value
            "has_contamination",  # object is the estimated genome contamination value
            "has_quality_tier",  # object is the MIMAG quality tier the MAG was assigned
            # --- Taxonomy and function -------------------------------------------
            "classified_by",  # object is the taxonomic classifier or reference database
            "assigned_taxon",  # object is the taxon assigned to the sequence or MAG
            "annotated_against",  # object is the reference database a gene was annotated against
            "predicted_by",  # object is the gene or ORF prediction tool
            "has_functional_annotation",  # object is the functional term or orthologous group
            "resolved_to_strain_by",  # object is the strain-resolution method or tool
            # --- Abundance and ecology --------------------------------------------
            "abundance_estimated_by",  # object is the tool or method used to estimate abundance
            "has_relative_abundance",  # object is the relative abundance value
            "normalized_by",  # object is the normalisation method applied to abundance
            "sampled_from",  # object is the environment or habitat the community was sampled from
            "host_is",  # object is the host organism, when the community is host-associated
            "co_occurs_with",  # object is another taxon or feature it co-occurs with
            "differentially_abundant_in",  # object is the contrast or condition compared
            # --- Validation and identity --------------------------------------------
            "validated_by",  # object is an orthogonal assay confirming the result
            "identifies",  # object is the authority identifier for the subject
        }
    )

    ontology_prefixes: dict[str, str] = dict(METAGENOMICS_PREFIXES)

    @property
    def subdomains(self) -> tuple[str, ...]:
        """EDAM's own sub-topics of the four collected roots, hyphenated."""
        return _edam.subtopics()

    # Curated -- EDAM has no technique hierarchy to read for this domain.
    techniques: tuple[str, ...] = (
        "shotgun-metagenomics",
        "whole-metagenome-sequencing",
        "amplicon-sequencing",
        "16s-rrna-amplicon-sequencing",
        "shallow-shotgun-sequencing",
        "long-read-metagenomics",
        "metagenome-assembly",
        "co-assembly",
        "genome-binning",
        "genome-dereplication",
        "taxonomic-profiling",
        "functional-annotation",
        "strain-resolution",
        "single-amplified-genome-sequencing",
        "hi-c-proximity-ligation",
        "read-based-profiling",
    )

    # ---- protocol methods ---------------------------------------------------

    def extraction_context(self) -> str:
        """Return the domain instructions handed to the extraction model."""
        return (
            "Domain: metagenomics -- shotgun sequencing of whole microbial "
            "communities, assembly, binning, MAGs, functional annotation, "
            "taxonomic profiling and strain resolution. Name subjects and "
            "objects with EDAM terminology where one applies (for example "
            "'metagenomic sequencing', 'community analysis'), using the "
            "singular preferred label rather than a paraphrase. Prefer a "
            "concrete tool, database or environment name over a generic word: "
            "'MetaBAT2' rather than 'the binner', 'CheckM' rather than 'the "
            "quality tool', 'human gut' rather than 'the sample'. Keep a "
            "contig, its predicted gene and the taxon it was assigned to "
            "distinct. Domain qualifiers available in addition to the base "
            "set: " + ", ".join(sorted(self.qualifiers)) + "."
        )

    def enrich_claim(self, claim: dict) -> dict:
        """Attach EDAM CURIEs to the claim slots whose text names an EDAM concept.

        Pure: returns a new dict and never mutates the input or its nested
        maps. Matching is exact after case-folding and whitespace collapse --
        substring and fuzzy matching over an ontology manufacture
        confident-looking wrong CURIEs, and a wrong identifier is worse than no
        identifier. A slot that carries text but resolves to nothing is
        recorded under ``ontology_terms_unmatched`` rather than passed over, so
        "not an EDAM concept" stays distinguishable from "no attempt was made".
        """
        out = dict(claim)
        terms: dict[str, str] = dict(out.get("ontology_terms") or {})
        justifications: dict[str, str] = dict(out.get("ontology_term_justifications") or {})
        unmatched: dict[str, str] = dict(out.get("ontology_terms_unmatched") or {})

        for slot in _ENRICHABLE_SLOTS:
            if slot in terms:
                continue  # another adapter already resolved this slot
            value = out.get(slot)
            if not isinstance(value, str) or not value.strip():
                continue
            curie = _edam.lookup(value)
            if curie:
                terms[slot] = curie
                justifications[slot] = _LEXICAL
                unmatched.pop(slot, None)
            else:
                unmatched[slot] = value

        if terms:
            out["ontology_terms"] = terms
            out["ontology_term_justifications"] = justifications
        if unmatched:
            out["ontology_terms_unmatched"] = unmatched
        return out
