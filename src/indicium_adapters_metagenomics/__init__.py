"""Metagenomics DomainAdapter for the indicium ecosystem.

Exposes :class:`MetagenomicsAdapter` via the ``indicium.adapters`` entry point,
so ``indicium_adapters.discover_adapters()`` finds it on install and ASB's
classification vocabulary picks up ``primary_domain="metagenomics"``.
"""

from .metagenomics import MetagenomicsAdapter

__all__ = ["MetagenomicsAdapter", "__version__"]

__version__ = "0.1.0"
