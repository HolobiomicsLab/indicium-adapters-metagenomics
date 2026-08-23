"""Hardcoded CURIE prefix to base-IRI table for the metagenomics adapter.

Nothing here is fetched at runtime: every expansion is pinned in this file, so
changing one changes how every metagenomics claim CURIE expands downstream.

Prefix spellings follow the sibling ``indicium-adapters-genomics`` and
``indicium-adapters-transcriptomics`` tables for every prefix the three share,
so a CURIE minted by any of them expands to the same IRI. One documented
exception: ``edam`` is lower-case here, matching the genomics and proteomics
siblings, because it is the prefix ``_edam.py`` mints.

Two families, and the distinction is load-bearing (ADR 0001):

* **Ontology prefixes** -- the vocabularies claim text is resolved against.
  Expansions are OBO PURLs, or the ontology's own base IRI where it is not an
  OBO library member (EDAM, MIxS).
* **Identifier-authority prefixes** -- expansions for the repository and
  resource accessions that ``asb-domain-core``'s canonical accession_scanner
  mines (ENA, SRA, MGnify, IMG). This table *expands* an accession that some
  other component already recognised; it never recognises one in prose. A
  second accession-detection table here would be the duplicate-then-drift
  failure ADR 0001 exists to prevent.

Database expansions use identifiers.org compact-URI resolution
(``https://identifiers.org/<registry-prefix>:``) where the registry carries the
namespace; MGnify and IMG have no identifiers.org registry entry as of this
writing, so they expand through the resource's own resolvable base URL instead.
"""

from __future__ import annotations

from typing import Final

# --- Ontologies ---------------------------------------------------------------

NCBITAXON: Final[str] = "http://purl.obolibrary.org/obo/NCBITaxon_"
ENVO: Final[str] = "http://purl.obolibrary.org/obo/ENVO_"
OBI: Final[str] = "http://purl.obolibrary.org/obo/OBI_"
GO: Final[str] = "http://purl.obolibrary.org/obo/GO_"
PFAM: Final[str] = "https://identifiers.org/pfam:"
KEGG: Final[str] = "https://identifiers.org/kegg.pathway:"
# Lower-case on purpose: it is the prefix `_edam.py` mints into every CURIE it
# returns. Unlike the genomics/transcriptomics siblings, this package has no
# test pinning that the two stay in sync -- see tests/test_edam_index.py and
# tests/test_protocol_conformance.py for what is actually checked here.
EDAM: Final[str] = "http://edamontology.org/"
# The Genomic Standards Consortium's Minimum Information about any (x)Sequence
# checklist. Terms are published at this base IRI by the MIxS ontology (GSC /
# NMDC), not by identifiers.org.
MIXS: Final[str] = "https://w3id.org/mixs/"

# --- Sequence repositories and resource databases ------------------------------

ENA: Final[str] = "https://identifiers.org/ena.embl:"
SRA: Final[str] = "https://identifiers.org/insdc.sra:"
# EBI's metagenomics resource. No identifiers.org registry entry; expands
# through the resource's own analyses browser, which resolves MGYS (study),
# MGYA (analysis) and ERS/ERR (sample/run) accessions alike.
MGNIFY: Final[str] = "https://www.ebi.ac.uk/metagenomics/"
# JGI's Integrated Microbial Genomes system. No identifiers.org registry entry;
# expands through the resource's own taxon browser.
IMG: Final[str] = "https://img.jgi.doe.gov/"


METAGENOMICS_PREFIXES: Final[dict[str, str]] = {
    # Ontologies.
    "NCBITaxon": NCBITAXON,
    "ENVO": ENVO,
    "OBI": OBI,
    "GO": GO,
    "Pfam": PFAM,
    "KEGG": KEGG,
    "edam": EDAM,
    "MIxS": MIXS,
    # Repositories and resource databases.
    "ENA": ENA,
    "SRA": SRA,
    "MGnify": MGNIFY,
    "IMG": IMG,
}
