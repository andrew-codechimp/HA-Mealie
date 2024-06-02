"""MealieEntity class."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.helpers.entity import DeviceInfo, EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, NAME, VERSION, MANUFACTURER
from .coordinator import MealieDataUpdateCoordinator


class MealieEntity(CoordinatorEntity):
    """MealieEntity class."""

    _attr_has_entity_name = True

    def __init__(
        self,
        entity_description: EntityDescription | None,
        coordinator: MealieDataUpdateCoordinator,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = coordinator.config_entry.entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.unique_id)},
            name=NAME,
            model=VERSION,
            manufacturer=MANUFACTURER,
        )

        if entity_description:
            self.entity_description = entity_description
