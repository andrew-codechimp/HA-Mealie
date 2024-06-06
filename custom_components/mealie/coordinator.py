"""DataUpdateCoordinator for mealie."""

from __future__ import annotations

from datetime import datetime, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
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
        api: MealieApiClient,
        group_id: str,
    ) -> None:
        """Initialize."""
        self.api = api
        self.group_id = group_id

        self._shopping_lists: dict | None = None
        self.shopping_list_items: dict = {}
        self.meal_plan: dict = {}
        self.last_breakfast_image = None
        self.last_breakfast_image_update = None
        self.last_lunch_image = None
        self.last_lunch_image_update = None
        self.last_dinner_image: datetime | None = None
        self.last_dinner_image_update: datetime | None = None
        self.last_side_image: datetime | None = None
        self.last_side_image_update: datetime | None = None

        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=10),
        )

    def todays_breakfast(self) -> str | None:
        """Return today's breakfast."""
        if self.meal_plan:
            for plan in self.meal_plan:
                if plan.get("entryType") == "breakfast":
                    if plan["recipeId"]:
                        return plan["recipe"]["name"]
                    else:
                        return plan["title"]
        return None

    def todays_lunch(self) -> str | None:
        """Return today's lunch."""
        if self.meal_plan:
            for plan in self.meal_plan:
                if plan.get("entryType") == "lunch":
                    if plan["recipeId"]:
                        return plan["recipe"]["name"]
                    else:
                        return plan["title"]
        return None

    def todays_dinner(self) -> str | None:
        """Return today's dinner."""
        if self.meal_plan:
            for plan in self.meal_plan:
                if plan.get("entryType") == "dinner":
                    if plan["recipeId"]:
                        return plan["recipe"]["name"]
                    else:
                        return plan["title"]
        return None

    def todays_side(self) -> str | None:
        """Return today's side."""
        if self.meal_plan:
            for plan in self.meal_plan:
                if plan.get("entryType") == "side":
                    if plan["recipeId"]:
                        return plan["recipe"]["name"]
                    else:
                        return plan["title"]
        return None

    def todays_breakfast_image(self) -> str | None:
        """Return today's breakfast image."""
        if self.meal_plan:
            for plan in self.meal_plan:
                if plan.get("entryType") == "breakfast":
                    if plan["recipeId"]:
                        url = self.api.async_get_recipe_image_url(plan["recipeId"])
                        if url != self.last_breakfast_image:
                            self.last_breakfast_image = url
                            self.last_breakfast_image_update = dt_util.now()
                        return url
        if self.last_breakfast_image != None:
            self.last_breakfast_image = None
            self.last_breakfast_image_update = dt_util.now()
        return None

    def todays_lunch_image(self) -> str | None:
        """Return today's lunch."""
        if self.meal_plan:
            for plan in self.meal_plan:
                if plan.get("entryType") == "lunch":
                    if plan["recipeId"]:
                        url = self.api.async_get_recipe_image_url(plan["recipeId"])
                        if url != self.last_lunch_image:
                            self.last_lunch_image = url
                            self.last_lunch_image_update = dt_util.now()
                        return url
        if self.last_lunch_image != None:
            self.last_lunch_image = None
            self.last_lunch_image_update = dt_util.now()
        return None

    def todays_dinner_image(self) -> str | None:
        """Return today's dinner image."""
        if self.meal_plan:
            for plan in self.meal_plan:
                if plan.get("entryType") == "dinner":
                    if plan["recipeId"]:
                        url = self.api.async_get_recipe_image_url(plan["recipeId"])
                        if url != self.last_dinner_image:
                            self.last_dinner_image = url
                            self.last_dinner_image_update = dt_util.now()
                        return url
        if self.last_dinner_image != None:
            self.last_dinner_image = None
            self.last_dinner_image_update = dt_util.now()
        return None

    def todays_side_image(self) -> str | None:
        """Return today's side image."""
        if self.meal_plan:
            for plan in self.meal_plan:
                if plan.get("entryType") == "side":
                    if plan["recipeId"]:
                        url = self.api.async_get_recipe_image_url(plan["recipeId"])
                        if url != self.last_side_image:
                            self.last_side_image = url
                            self.last_side_image_update = dt_util.now()
                        return url
        if self.last_side_image != None:
            self.last_side_image = None
            self.last_side_image_update = dt_util.now()
        return None

    async def async_get_shopping_lists(self) -> dict:
        """Return shopping lists  fetched at most once."""
        if self._shopping_lists is None:

            result = await self.api.async_get_shopping_lists(self.group_id)

            self._shopping_lists = result.get("items")
        return self._shopping_lists

    async def async_get_shopping_lists_items(self, shopping_list_id) -> dict:
        """Return shopping lists  fetched at most once."""
        result = await self.api.async_get_shopping_list_items(
            self.group_id, shopping_list_id
        )

        items = result.get("items")
        return items

    async def _async_update_data(self):
        """Update data."""

        # Today's meal plan

        try:
            result = await self.api.async_get_meal_plans_today(self.group_id)

            if self.api.error:
                raise ConfigEntryAuthFailed(
                    "Unable to login, please re-login."
                ) from None

            self.meal_plan = result

        except Exception as exception:
            raise UpdateFailed(exception) from exception

        # Shopping lists

        if not self._shopping_lists:
            return
        try:

            for value in self._shopping_lists:
                shopping_list_id = value.get("id")
                result = await self.api.async_get_shopping_list_items(
                    self.group_id, shopping_list_id
                )

                if self.api.error:
                    raise ConfigEntryAuthFailed(
                        "Unable to login, please re-login."
                    ) from None

                items = result.get("items")
                self.shopping_list_items.update({shopping_list_id: items})

        except Exception as exception:
            raise UpdateFailed(exception) from exception
