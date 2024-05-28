"""MealieEntity class."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.helpers.entity import DeviceInfo, EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN, NAME, VERSION, MANUFACTURER
from .coordinator import MealieDataUpdateCoordinator


@dataclass
class MealieEntityDescription(EntityDescription):
    """Defines a base Mealie entity description."""

    entity_id: str | None = None
    api_field: str | None = None


class MealieEntity(CoordinatorEntity):
    """MealieEntity class."""

    _attr_attribution = ATTRIBUTION

    entity_description: MealieEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        description: MealieEntityDescription,
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
        self.entity_description = description
        if description.entity_id:
            self.entity_id = description.entity_id
