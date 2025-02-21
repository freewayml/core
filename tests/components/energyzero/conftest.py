"""Fixtures for EnergyZero integration tests."""
from collections.abc import Generator
import json
from unittest.mock import AsyncMock, MagicMock, patch

from energyzero import Electricity, Gas
import pytest

from homeassistant.components.energyzero.const import DOMAIN
from homeassistant.core import HomeAssistant

from tests.common import MockConfigEntry, load_fixture


@pytest.fixture
def mock_setup_entry() -> Generator[AsyncMock, None, None]:
    """Mock setting up a config entry."""
    with patch(
        "homeassistant.components.energyzero.async_setup_entry", return_value=True
    ) as mock_setup:
        yield mock_setup


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return the default mocked config entry."""
    return MockConfigEntry(
        title="energy",
        domain=DOMAIN,
        data={},
        unique_id="unique_thingy",
    )


def apply_energyzero_mock(energyzero_mock):
    """Apply mocks to EnergyZero client."""
    client = energyzero_mock.return_value
    client.energy_prices.return_value = Electricity.from_dict(
        json.loads(load_fixture("today_energy.json", DOMAIN))
    )
    client.gas_prices.return_value = Gas.from_dict(
        json.loads(load_fixture("today_gas.json", DOMAIN))
    )
    return client


@pytest.fixture
def mock_energyzero() -> Generator[MagicMock, None, None]:
    """Return a mocked EnergyZero client."""
    with patch(
        "homeassistant.components.energyzero.coordinator.EnergyZero", autospec=True
    ) as energyzero_mock:
        yield apply_energyzero_mock(energyzero_mock)


@pytest.fixture
def mock_energyzero_service() -> Generator[MagicMock, None, None]:
    """Return a mocked EnergyZero client."""
    with patch(
        "homeassistant.components.energyzero.EnergyZero", autospec=True
    ) as energyzero_mock:
        yield apply_energyzero_mock(energyzero_mock)


@pytest.fixture
async def init_integration(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_energyzero: MagicMock,
    mock_energyzero_service: MagicMock,
) -> MockConfigEntry:
    """Set up the EnergyZero integration for testing."""
    mock_config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    return mock_config_entry
