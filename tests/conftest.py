"""Shared pytest fixtures."""

from __future__ import annotations

import pytest

from indicium_adapters_metagenomics import MetagenomicsAdapter


@pytest.fixture
def adapter() -> MetagenomicsAdapter:
    """The adapter with whatever EDAM index the installation ships."""
    return MetagenomicsAdapter()
