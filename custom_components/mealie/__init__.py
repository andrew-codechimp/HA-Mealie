"""Custom integration to integrate mealie with Home Assistant.

For more details about this integration, please refer to
https://github.com/andrew-codechimp/HA-Mealie
"""

from __future__ import annotations

from awesomeversion.awesomeversion import AwesomeVersion

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import config_validation as cv
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.const import __version__ as HA_VERSION  # noqa: N812

from homeassistant.const import (
    CONF_HOST,
    CONF_TOKEN,
)

from .api import MealieApiClient
from .const import DOMAIN, LOGGER, MIN_HA_VERSION
from .coordinator import MealieDataUpdateCoordinator

PLATFORMS: list[Platform] = [
    Platform.TODO,
]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(
    hass: HomeAssistant,  # pylint: disable=unused-argument
    config: ConfigType,  # pylint: disable=unused-argument
) -> bool:
    """Integration setup."""

    if AwesomeVersion(HA_VERSION) < AwesomeVersion(MIN_HA_VERSION):  # pragma: no cover
        msg = (
            "This integration requires at least HomeAssistant version "
            f" {MIN_HA_VERSION}, you are running version {HA_VERSION}."
            " Please upgrade HomeAssistant to continue use this integration."
        )
        LOGGER.critical(msg)
        return False

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    hass.data.setdefault(DOMAIN, {})

    session = async_get_clientsession(hass)

    if CONF_HOST not in entry.data or CONF_TOKEN not in entry.data:
        raise ConfigEntryAuthFailed("Unable to login, please re-login.") from None

    if entry.data[CONF_HOST] == "" or entry.data[CONF_TOKEN] == "":
        raise ConfigEntryAuthFailed("Unable to login, please re-login.") from None

    client = MealieApiClient(
        session=session,
        host=entry.data[CONF_HOST],
        token=entry.data[CONF_TOKEN],
    )

    result = await client.async_get_groups()

    print(result)

    # conn, errorcode = await client.connection_test()

    # if conn is False:
    #     raise ConfigEntryAuthFailed("Unable to login, please re-login.") from None

    hass.data[DOMAIN][entry.entry_id] = coordinator = MealieDataUpdateCoordinator(
        hass=hass,
        client=client,
    )

    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    if unloaded := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


@callback
async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)
