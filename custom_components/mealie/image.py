"""Image platform for Mealie."""

from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass
from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.image import (
    ImageEntity,
    ImageEntityDescription,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import UNDEFINED

from .const import DOMAIN, COORDINATOR, MEALIE_LOGO
from .entity import MealieEntity
from .coordinator import MealieDataUpdateCoordinator


ENTITY_DESCRIPTIONS = (
    ImageEntityDescription(
        key="todays_breakfast",
        translation_key="todays_breakfast",
    ),
    ImageEntityDescription(
        key="todays_lunch",
        translation_key="todays_lunch",
    ),
    ImageEntityDescription(
        key="todays_dinner",
        translation_key="todays_dinner",
    ),
    ImageEntityDescription(
        key="todays_side",
        translation_key="todays_side",
    ),
)


@dataclass
class Image:
    """Represent an image."""

    content_type: str
    content: bytes


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator: MealieDataUpdateCoordinator = hass.data[DOMAIN][COORDINATOR]

    async_add_entities(
        MealieImage(
            entity_description=entity_description,
            coordinator=coordinator,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class MealieImage(MealieEntity, ImageEntity):
    """Mealie Image class."""

    entity_description: ImageEntityDescription
    current_image: bytes | None = None

    def __init__(
        self,
        entity_description: ImageEntityDescription,
        coordinator: MealieDataUpdateCoordinator,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(entity_description, coordinator)
        ImageEntity.__init__(self, coordinator.hass)

        self._attr_should_poll = False
        self.entity_id = f"image.mealie_{entity_description.key}"
        self._attr_unique_id = f"mealie_{entity_description.key}_image".lower()
        self.entity_description = entity_description
        self.coordinator = coordinator
        self._attr_has_entity_name = True
        self.current_image = None

    async def async_added_to_hass(self) -> None:
        """Handle added to Hass."""
        await super().async_added_to_hass()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        self._cached_image = None

        if self.entity_description.key == "todays_breakfast":
            self._attr_image_url = self.coordinator.todays_breakfast_image()
            self._attr_image_last_updated = self.coordinator.last_breakfast_image_update
        if self.entity_description.key == "todays_lunch":
            self._attr_image_url = self.coordinator.todays_lunch_image()
            self._attr_image_last_updated = self.coordinator.last_lunch_image_update
        if self.entity_description.key == "todays_dinner":
            self._attr_image_url = self.coordinator.todays_dinner_image()
            self._attr_image_last_updated = self.coordinator.last_dinner_image_update
        if self.entity_description.key == "todays_side":
            self._attr_image_url = self.coordinator.todays_side_image()
            self._attr_image_last_updated = self.coordinator.last_side_image_update

        super()._handle_coordinator_update()

    async def _async_load_image_from_url(self, url: str) -> Image | None:
        """Load an image by url."""
        if response := await self._fetch_url(url):
            return Image(
                content_type="image/webp",
                content=response.content,
            )
        return None

    def image(self) -> bytes | None:
        """Return bytes of image."""

        return self.current_image

    async def async_image(self) -> bytes | None:
        """Return bytes of image."""

        mealie_logo_path = Path(__file__).parent / MEALIE_LOGO

        if self._cached_image:
            return self._cached_image.content

        if (url := self.image_url) is not UNDEFINED:
            if not url or (image := await self._async_load_image_from_url(url)) is None:
                self.current_image = await self.hass.async_add_executor_job(
                    mealie_logo_path.read_bytes
                )
                self._attr_content_type = "image/png"
                return self.current_image
            self._cached_image = image
            self.current_image = image
            self._attr_content_type = "image/webp"
            return image.content
        self.current_image = await self.hass.async_add_executor_job(
            mealie_logo_path.read_bytes
        )
        self._attr_content_type = "image/png"
        return self.current_image
