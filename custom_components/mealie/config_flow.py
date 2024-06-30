"""Adds config flow for Mealie."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from homeassistant.const import (
    CONF_HOST,
    CONF_TOKEN,
)

from .api import MealieApiClient

from .const import (
    DOMAIN,
    LOGGER,
)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_TOKEN): str,
    }
)

CONFIG_VERSION = 1


class MealieConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Mealie."""

    VERSION = CONFIG_VERSION

    _reauth_entry: config_entries.ConfigEntry | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user, unless one already exists."""

        errors = {}

        if not self._reauth_entry:
            if self._async_current_entries():
                return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            api = MealieApiClient(
                user_input[CONF_HOST],
                user_input[CONF_TOKEN],
                async_get_clientsession(self.hass),
            )

            await api.async_get_groups()

            if api.error:
                errors["base"] = api.error
                LOGGER.error("Mealie connection error (%s)", api.error)

            # Save instance
            if not errors:
                if self._reauth_entry is None:
                    return self.async_create_entry(title="Mealie", data=user_input)
                else:
                    self.hass.config_entries.async_update_entry(
                        self._reauth_entry, data=user_input
                    )
                    await self.hass.config_entries.async_reload(
                        self._reauth_entry.entry_id
                    )
                    return self.async_abort(reason="reauth_successful")

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_reauth(
        self, user_input=None  # pylint: disable=unused-argument
    ):
        """Perform reauth upon an API authentication error."""
        self._reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        """Dialog that informs the user that reauth is required."""
        if user_input is None:
            return self.async_show_form(
                step_id="reauth_confirm",
                data_schema=vol.Schema({}),
            )
        self._reauth_config = True
        return await self.async_step_user()
