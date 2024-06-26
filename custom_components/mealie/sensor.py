"""Sensor platform for Mealie."""

from __future__ import annotations

from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, COORDINATOR, ATTR_RECIPE_URL
from .entity import MealieEntity
from .coordinator import MealieDataUpdateCoordinator


ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="todays_breakfast",
        translation_key="todays_breakfast",
    ),
    SensorEntityDescription(
        key="todays_lunch",
        translation_key="todays_lunch",
    ),
    SensorEntityDescription(
        key="todays_dinner",
        translation_key="todays_dinner",
    ),
    SensorEntityDescription(
        key="todays_side",
        translation_key="todays_side",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator: MealieDataUpdateCoordinator = hass.data[DOMAIN][COORDINATOR]

    async_add_entities(
        MealieSensor(
            entity_description=entity_description,
            coordinator=coordinator,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class MealieSensor(MealieEntity, SensorEntity):
    """Mealie Sensor class."""

    entity_description: SensorEntityDescription

    _native_value = None

    def __init__(
        self,
        entity_description: SensorEntityDescription,
        coordinator: MealieDataUpdateCoordinator,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(entity_description, coordinator)

        self._attr_should_poll = False
        self.entity_id = f"sensor.mealie_{entity_description.key}"
        self._attr_unique_id = f"mealie_{entity_description.key}".lower()
        self.entity_description = entity_description
        self.coordinator = coordinator
        self._attr_has_entity_name = True
        self._attr_icon = "mdi:silverware-variant"

    async def async_added_to_hass(self) -> None:
        """Handle added to Hass."""
        await super().async_added_to_hass()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        super()._handle_coordinator_update()

        if self.entity_description.key == "todays_breakfast":
            self._native_value = self.coordinator.todays_breakfast()
        if self.entity_description.key == "todays_lunch":
            self._native_value = self.coordinator.todays_lunch()
        if self.entity_description.key == "todays_dinner":
            self._native_value = self.coordinator.todays_dinner()
        if self.entity_description.key == "todays_side":
            self._native_value = self.coordinator.todays_side()

        self.async_write_ha_state()

    @property
    def native_value(self) -> str | None:
        """Return the native value of the sensor."""
        return self._native_value

    @property
    def extra_state_attributes(self) -> dict[str, str] | None:
        """Return the state attributes."""

        if self.entity_description.key == "todays_breakfast":
            url = self.coordinator.todays_breakfast_recipe_url()
        if self.entity_description.key == "todays_lunch":
            url = self.coordinator.todays_lunch_recipe_url()
        if self.entity_description.key == "todays_dinner":
            url = self.coordinator.todays_dinner_recipe_url()
        if self.entity_description.key == "todays_side":
            url = self.coordinator.todays_side_recipe_url()

        attrs = {
            ATTR_RECIPE_URL: url,
        }

        super_attrs = super().extra_state_attributes
        if super_attrs:
            attrs.update(super_attrs)
        return attrs
