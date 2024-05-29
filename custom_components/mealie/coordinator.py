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

    def __init__(
        self,
        hass: HomeAssistant,
        client: MealieApiClient,
        group_id: str,
    ) -> None:
        """Initialize."""
        self.client = client
        self.group_id = group_id

        self._shopping_lists: dict | None = None

        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=10),
        )

    async def async_get_shopping_lists(self) -> dict:
        """Return shopping lists  fetched at most once."""
        if self._shopping_lists is None:

            result = await self.client.async_get_shopping_lists(self.group_id)

            self._shopping_lists = result.get("items")
        return self._shopping_lists

    async def _async_update_data(self):
        """Update data."""
        try:
            data = await self.client.async_get_shopping_lists(self.group_id)
            if self.client.error:
                raise ConfigEntryAuthFailed(
                    "Unable to login, please re-login."
                ) from None

            self.shopping_lists = data

        except Exception as exception:
            raise UpdateFailed(exception) from exception

        return self.shopping_lists
