"""A Mealie calendar platform."""

from __future__ import annotations

from datetime import datetime, timedelta
import logging

from homeassistant.components.calendar import (
    CalendarEntity,
    CalendarEvent,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
)

from .entity import MealieEntity
from .coordinator import MealieDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=1)

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Mealie calendar platform config entry."""
    coordinator: MealieDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([MealieCalendarEntity(coordinator, entry.entry_id)])


class MealieCalendarEntity(
    MealieEntity, CalendarEntity
):
    """A device for getting the next Task from a Todoist Project."""

    def __init__(
        self,
        coordinator: MealieDataUpdateCoordinator,
        config_entry_id: str,
    ) -> None:
        """Create the Mealie Calendar Entity."""
        super().__init__(entity_description=None, coordinator=coordinator)
        self._attr_name = None
        self.entity_id = f"calendar.mealie"
        self._attr_unique_id = f"{config_entry_id}-mealplans"
        self._attr_has_entity_name = True

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.todays_meal_plan = self.coordinator.meal_plan
        super()._handle_coordinator_update()

    @property
    def breakfast_start(self) -> datetime:
        """Return breakfast start today."""
        return dt_util.now().replace(hour=7, minute=0, second=0)

    @property
    def breakfast_end(self) -> datetime:
        """Return breakfast end today."""
        return dt_util.now().replace(hour=11, minute=0, second=0)

    @property
    def lunch_start(self) -> datetime:
        """Return lunch start today."""
        return dt_util.now().replace(hour=11, minute=30, second=0)

    @property
    def lunch_end(self) -> datetime:
        """Return lunch end today."""
        return dt_util.now().replace(hour=14, minute=30, second=0)

    @property
    def dinner_start(self) -> datetime:
        """Return dinner start today."""
        return dt_util.now().replace(hour=16, minute=0, second=0)

    @property
    def dinner_end(self) -> datetime:
        """Return dinner end today."""
        return dt_util.now().replace(hour=21, minute=0, second=0)


    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""

        if self.breakfast_start <= dt_util.now() <= self.breakfast_end:
            if self.coordinator.todays_breakfast():
                return CalendarEvent(start=self.breakfast_start, end=self.breakfast_end, summary=self.coordinator.todays_breakfast())

        if self.lunch_start <= dt_util.now() <= self.lunch_end:
            if self.coordinator.todays_lunch():
                return CalendarEvent(start=self.lunch_start, end=self.lunch_end, summary=self.coordinator.todays_lunch())

        if self.dinner_start <= dt_util.now() <= self.dinner_end:
            if self.coordinator.todays_dinner():
                return CalendarEvent(start=self.dinner_start, end=self.dinner_end, summary=self.coordinator.todays_dinner())

        return None

    @property
    def state(self) -> str:
        """Return the state of the calendar event."""
        if (event := self.event) is None:
            return STATE_OFF

        now = dt_util.now()

        if event.start_datetime_local <= now < event.end_datetime_local:
            return STATE_ON

        return STATE_OFF

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._attr_name

    async def async_update(self) -> None:
        """Update Mealie Calendars."""
        await super().async_update()
        # self.data.update()

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Get all events in a specific time frame."""

        mealie_start_date = f"{start_date:%Y-%m-%d}"
        mealie_end_date = f"{end_date:%Y-%m-%d}"

        plans = await self.coordinator.api.async_get_meal_plans(
            self.coordinator.group_id, mealie_start_date, mealie_end_date
        )

        events: list[CalendarEvent] = []

        for plan in plans["items"]:
            if plan["entryType"] == "breakfast":
                start_time = "7:00:00"
                end_time = "11:00:00"
            elif plan["entryType"] == "lunch":
                start_time = "11:30:00"
                end_time = "14:30:00"
            elif plan["entryType"] == "dinner":
                start_time = "16:00:00"
                end_time = "21:00:00"
            else:
                start_time = "16:00:00"
                end_time = "21:00:00"

            mealie_start_dt = f"{plan["date"]} {start_time}"
            mealie_end_dt = f"{plan["date"]} {end_time}"
            start = datetime.strptime(mealie_start_dt, "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(mealie_end_dt, "%Y-%m-%d %H:%M:%S")

            start = start.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE)
            end = end.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE)

            # start = start.replace(tzinfo=dt_util.get_time_zone(self.hass.config.time_zone))
            # end = end.replace(tzinfo=dt_util.get_time_zone(self.hass.config.time_zone))

            # start_utc = dt_util.as_utc(start)
            # end_utc = dt_util.as_utc(end)

            # start_utc = start_utc.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE)
            # end_utc = end_utc.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE)

            # start = start.replace(tzinfo=dt_util.get_time_zone(self.hass.config.time_zone))
            # end = end.replace(tzinfo=dt_util.get_time_zone(self.hass.config.time_zone))

            if plan["recipeId"]:
                summary = plan["recipe"]["name"]
            else:
                summary = plan["title"]

            event = CalendarEvent(start=start, end=end, summary=summary, uid=plan["id"])

            events.append(event)

        return events
