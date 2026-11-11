# indicium-adapters-metagenomics

A `metagenomics` `DomainAdapter` for the [indicium](https://github.com/HolobiomicsLab/indicium)
ecosystem: EDAM concept enrichment for validated claims, and the classification vocabulary that
lets AgenticScienceBuilder recognise a shotgun metagenomics paper as metagenomics.

## What it does

- **Declares the domain.** `domain_id` and `primary_domain` are `"metagenomics"`. ASB's
  classification layer unions the `primary_domain`, `subdomains` and `techniques` of every
  installed adapter into its controlled vocabulary, so installing this package is what stops a
  metagenomics paper being classified as `other`.
- **Enriches claims with EDAM concepts.** `enrich_claim` attaches an `edam:` CURIE to any
  `subject` / `object` / `qualifier` slot whose text names an EDAM concept, with a
  `semapv:LexicalMatching` justification for downstream SSSOM emitters.
- **Publishes 26 domain qualifiers**, all snake_case, covering the shape of a shotgun
  metagenomics claim: which assembler and binner were used, how a MAG was quality-assessed
  (completeness / contamination), what a contig was annotated against, how abundance was
  estimated, the environment sampled, the host if any, and the co-assembly or reference the
  reads were mapped to.
- **Publishes the prefixes** needed to expand metagenomics CURIEs: `NCBITaxon`, `ENVO`, `OBI`,
  `GO`, `Pfam`, `KEGG`, `edam`, `MIxS`, `ENA`, `SRA`, `MGnify`, `IMG`.

## Where the vocabulary comes from

The concept vocabulary is read from EDAM, never hand-listed. It is cut from four roots recorded
in `data/build_edam_index.py`:

| root | why it is named |
|---|---|
| Metagenomics (`topic_3174`) | the domain root |
| Metagenomic sequencing (`topic_3837`) | filed under *Sequencing*, not reachable from the domain root |
| Microbial ecology (`topic_3697`) | filed under *Ecology*, not reachable from the domain root |
| Metatranscriptomics (`topic_3941`) | filed under *Transcriptomics*, not reachable from the domain root |

A shotgun metagenomics paper routinely claims all three of the latter, but EDAM's own hierarchy
does not put any of them under Metagenomics — the same situation the genomics sibling documents
for Metatranscriptomics, which is why the same topic is named as a root in both packages.

Walking from these four roots (each root plus its direct EDAM subclasses, every preferred label
and every exact synonym) currently yields a small, honest index: EDAM's Metagenomics topic has
no further subclasses of its own beyond what the extra roots contribute.

`subdomains` and `techniques` are curated, not derived. The classification vocabulary comes from
the 2026-08-25 cross-domain audit, which dropped every term two or more sciences both declared —
a term two sciences share cannot tell them apart — and left each domain only the qualified forms
it alone utters. EDAM carries no label or synonym for any of the six subdomains that audit
settled on, so the walk above cannot produce them and there is no further root that would; for
techniques EDAM models assays as operations and data types rather than as a hierarchy to walk.
The EDAM walk still backs claim enrichment and still emits its own sub-topic list as index
provenance.

## Enrichment is exact-match

`enrich_claim` walks the `subject`, `object` and `qualifier` slots and resolves each against the
EDAM index after case-folding and whitespace collapse. Substring and fuzzy matching over an
ontology manufacture confident-looking wrong CURIEs — `"microbial"` inside `"microbial
ecology"` — and a wrong identifier is worse than no identifier. A slot that carries text but
resolves to nothing is recorded under `ontology_terms_unmatched` rather than passed over, so
"this text is not an EDAM concept" stays distinguishable from "no attempt was made". A slot
another adapter already resolved is left untouched.

## What it deliberately does not do

**It does not recognise repository accessions.** Under ADR 0001 those belong to the canonical
accession table in `asb-domain-core`, which is the single source of truth for accession
patterns; a second copy here would be the duplicate-then-drift failure that architecture exists
to prevent. MGnify (`MGYS…`, `MGYA…`), ENA/SRA run and project accessions, and IMG taxon oids all
live there. This package contributes only the prefixes that *expand* those accessions once
something else has recognised them (`ENA`, `SRA`, `MGnify`, `IMG` in `ontology_prefixes`).

**It does not carry an assembler, binner or organism keyword table.** Which tool a paper used is
extraction-heuristic territory, not a controlled vocabulary this adapter owns; a qualifier such
as `assembled_with` or `binned_with` names the *slot*, and the extraction model supplies the
object text.

## Install

The public dependencies are installed from PyPI with the development extra:

```bash
python -m pip install -e ".[dev]"
```

`requires-python >= 3.11`, matching the genomics and astronomy siblings, so this package can be
installed into the AgenticScienceBuilder environment where the classification vocabulary it
feeds is consumed. The `indicium.adapters` entry point makes it discoverable via
`indicium_adapters.discover_adapters()` on install — no configuration.

## Regenerating the bundled index

```bash
python -m indicium_adapters_metagenomics.data.build_edam_index
```

Reads EDAM through EBI OLS4 (network, stdlib only), records the roots it was cut from, and emits
the walk's own sub-topic list as provenance. Regenerate on an EDAM release. Never runs at install
or import time.

## Licence

MIT.
