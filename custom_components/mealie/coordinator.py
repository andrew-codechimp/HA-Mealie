"""DataUpdateCoordinator for mealie."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.exceptions import ConfigEntryAuthFailed

from .api import MealieApiClient
from .const import DOMAIN, LOGGER


class MealieDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: ConfigEntry

    quota = any

    def __init__(
        self,
        hass: HomeAssistant,
        client: MealieApiClient,
    ) -> None:
        """Initialize."""
        self.client = client
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=30),
        )

    async def _async_update_data(self):
        """Update data."""
        try:
            data = await self.client.query("quota")
            if (
                self.client.error == "Control authorisation failed"
                or self.client.error == "Bad control-login"
            ):
                raise ConfigEntryAuthFailed(
                    "Unable to login, please re-login."
                ) from None

            self.quota = data

        except Exception as exception:
            raise UpdateFailed(exception) from exception

        return self.quota
