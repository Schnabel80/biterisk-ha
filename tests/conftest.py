"""Test configuration for BiteRisk."""

import pathlib

import pytest


@pytest.fixture
def hass_config_dir() -> str:
    """Return project root so HA loader finds custom_components/biterisk."""
    return str(pathlib.Path(__file__).parent.parent)
