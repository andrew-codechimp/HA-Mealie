"""A Mealie calendar platform."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
import logging
from typing import Any
import uuid

# from todoist_api_python.api_async import TodoistAPIAsync
# from todoist_api_python.endpoints import get_sync_url
# from todoist_api_python.headers import create_headers
# from todoist_api_python.models import Due, Label, Task
import voluptuous as vol

from homeassistant.components.calendar import (
    PLATFORM_SCHEMA,
    CalendarEntity,
    CalendarEvent,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ID, CONF_NAME, CONF_TOKEN, EVENT_HOMEASSISTANT_STOP, STATE_OFF, STATE_ON
from homeassistant.core import Event, HomeAssistant, ServiceCall, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
)
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
    CoordinatorEntity[MealieDataUpdateCoordinator], CalendarEntity
):
    """A device for getting the next Task from a Todoist Project."""

    def __init__(
        self,
        coordinator: MealieDataUpdateCoordinator,
        config_entry_id: str,
    ) -> None:
        """Create the Mealie Calendar Entity."""
        super().__init__(coordinator)
        self._attr_name = "Mealie"
        self._attr_unique_id = f"{config_entry_id}-mealplans"

        # self.data = TodoistProjectData(
        #     coordinator,
        #     config_entry_id=config_entry_id,
        # )

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

        if self.breakfast_start <= dt_util.utcnow() <= self.breakfast_end:
            if self.coordinator.todays_breakfast():
                return CalendarEvent(start=self.breakfast_start, end=self.breakfast_end, summary=self.coordinator.todays_breakfast())

        if self.lunch_start <= dt_util.utcnow() <= self.lunch_end:
            if self.coordinator.todays_lunch():
                return CalendarEvent(start=self.lunch_start, end=self.lunch_end, summary=self.coordinator.todays_lunch())

        if self.dinner_start <= dt_util.utcnow() <= self.dinner_end:
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

    # @property
    # def extra_state_attributes(self) -> dict[str, Any] | None:
    #     """Return the device state attributes."""
    #     if self.data.event is None:
    #         # No tasks, we don't REALLY need to show anything.
    #         return None

    #     return {
    #         DUE_TODAY: self.data.event[DUE_TODAY],
    #         OVERDUE: self.data.event[OVERDUE],
    #         ALL_TASKS: [task[SUMMARY] for task in self.data.all_project_tasks],
    #         PRIORITY: self.data.event[PRIORITY],
    #         LABELS: self.data.event[LABELS],
    #     }


# class TodoistProjectData:
#     """Class used by the Task Entity service object to hold all Todoist Tasks.

#     This is analogous to the GoogleCalendarData found in the Google Calendar
#     component.

#     Takes an object with a 'name' field and optionally an 'id' field (either
#     user-defined or from the Todoist API), a Todoist API token, and an optional
#     integer specifying the latest number of days from now a task can be due (7
#     means everything due in the next week, 0 means today, etc.).

#     This object has an exposed 'event' property (used by the Calendar platform
#     to determine the next calendar event) and an exposed 'update' method (used
#     by the Calendar platform to poll for new calendar events).

#     The 'event' is a representation of a Todoist Task, with defined parameters
#     of 'due_today' (is the task due today?), 'all_day' (does the task have a
#     due date?), 'task_labels' (all labels assigned to the task), 'message'
#     (the content of the task, e.g. 'Fetch Mail'), 'description' (a URL pointing
#     to the task on the Todoist website), 'end_time' (what time the event is
#     due), 'start_time' (what time this event was last updated), 'overdue' (is
#     the task past its due date?), 'priority' (1-4, how important the task is,
#     with 4 being the most important), and 'all_tasks' (all tasks in this
#     project, sorted by how important they are).

#     'offset_reached', 'location', and 'friendly_name' are defined by the
#     platform itself, but are not used by this component at all.

#     The 'update' method polls the Todoist API for new projects/tasks, as well
#     as any updates to current projects/tasks. This occurs every SCAN_INTERVAL minutes.
#     """

#     def __init__(
#         self,
#         project_data: ProjectData,
#         labels: list[Label],
#         coordinator: TodoistCoordinator,
#         due_date_days: int | None = None,
#         whitelisted_labels: list[str] | None = None,
#         whitelisted_projects: list[str] | None = None,
#     ) -> None:
#         """Initialize a Todoist Project."""
#         self.event: TodoistEvent | None = None

#         self._coordinator = coordinator
#         self._name = project_data[CONF_NAME]
#         # If no ID is defined, fetch all tasks.
#         self._id = project_data.get(CONF_ID)

#         # All labels the user has defined, for easy lookup.
#         self._labels = labels
#         # Not tracked: order, indent, comment_count.

#         self.all_project_tasks: list[TodoistEvent] = []

#         # The days a task can be due (for making lists of everything
#         # due today, or everything due in the next week, for example).
#         self._due_date_days: timedelta | None = None
#         if due_date_days is not None:
#             self._due_date_days = timedelta(days=due_date_days)

#         # Only tasks with one of these labels will be included.
#         self._label_whitelist: list[str] = []
#         if whitelisted_labels is not None:
#             self._label_whitelist = whitelisted_labels

#         # This project includes only projects with these names.
#         self._project_id_whitelist: list[str] = []
#         if whitelisted_projects is not None:
#             self._project_id_whitelist = whitelisted_projects

#     @property
#     def calendar_event(self) -> CalendarEvent | None:
#         """Return the next upcoming calendar event."""
#         if not self.event:
#             return None

#         start = self.event[START]
#         if self.event.get(ALL_DAY) or self.event[END] is None:
#             return CalendarEvent(
#                 summary=self.event[SUMMARY],
#                 start=start.date(),
#                 end=start.date() + timedelta(days=1),
#             )

#         return CalendarEvent(
#             summary=self.event[SUMMARY], start=start, end=self.event[END]
#         )

#     def create_todoist_task(self, data: Task):
#         """Create a dictionary based on a Task passed from the Todoist API.

#         Will return 'None' if the task is to be filtered out.
#         """
#         task: TodoistEvent = {
#             ALL_DAY: False,
#             COMPLETED: data.is_completed,
#             DESCRIPTION: f"https://todoist.com/showTask?id={data.id}",
#             DUE_TODAY: False,
#             END: None,
#             LABELS: [],
#             OVERDUE: False,
#             PRIORITY: data.priority,
#             START: dt_util.now(),
#             SUMMARY: data.content,
#         }

#         # All task Labels (optional parameter).
#         task[LABELS] = [
#             label.name for label in self._labels if label.name in data.labels
#         ]
#         if self._label_whitelist and (
#             not any(label in task[LABELS] for label in self._label_whitelist)
#         ):
#             # We're not on the whitelist, return invalid task.
#             return None

#         # Due dates (optional parameter).
#         # The due date is the END date -- the task cannot be completed
#         # past this time.
#         # That means that the START date is the earliest time one can
#         # complete the task.
#         # Generally speaking, that means right now.
#         if data.due is not None:
#             end = dt_util.parse_datetime(
#                 data.due.datetime if data.due.datetime else data.due.date
#             )
#             task[END] = dt_util.as_local(end) if end is not None else end
#             if task[END] is not None:
#                 if self._due_date_days is not None and (
#                     task[END] > dt_util.now() + self._due_date_days
#                 ):
#                     # This task is out of range of our due date;
#                     # it shouldn't be counted.
#                     return None

#                 task[DUE_TODAY] = task[END].date() == dt_util.now().date()

#                 # Special case: Task is overdue.
#                 if task[END] <= task[START]:
#                     task[OVERDUE] = True
#                     # Set end time to the current time plus 1 hour.
#                     # We're pretty much guaranteed to update within that 1 hour,
#                     # so it should be fine.
#                     task[END] = task[START] + timedelta(hours=1)
#                 else:
#                     task[OVERDUE] = False
#         else:
#             # If we ask for everything due before a certain date, don't count
#             # things which have no due dates.
#             if self._due_date_days is not None:
#                 return None

#             # Define values for tasks without due dates
#             task[END] = None
#             task[ALL_DAY] = True
#             task[DUE_TODAY] = False
#             task[OVERDUE] = False

#         # Not tracked: id, comments, project_id order, indent, recurring.
#         return task

#     @staticmethod
#     def select_best_task(project_tasks: list[TodoistEvent]) -> TodoistEvent:
#         """Search through a list of events for the "best" event to select.

#         The "best" event is determined by the following criteria:
#           * A proposed event must not be completed
#           * A proposed event must have an end date (otherwise we go with
#             the event at index 0, selected above)
#           * A proposed event must be on the same day or earlier as our
#             current event
#           * If a proposed event is an earlier day than what we have so
#             far, select it
#           * If a proposed event is on the same day as our current event
#             and the proposed event has a higher priority than our current
#             event, select it
#           * If a proposed event is on the same day as our current event,
#             has the same priority as our current event, but is due earlier
#             in the day, select it
#         """
#         # Start at the end of the list, so if tasks don't have a due date
#         # the newest ones are the most important.

#         event = project_tasks[-1]

#         for proposed_event in project_tasks:
#             if event == proposed_event:
#                 continue

#             if proposed_event[COMPLETED]:
#                 # Event is complete!
#                 continue

#             if proposed_event[END] is None:
#                 # No end time:
#                 if event[END] is None and (proposed_event[PRIORITY] < event[PRIORITY]):
#                     # They also have no end time,
#                     # but we have a higher priority.
#                     event = proposed_event
#                 continue

#             if event[END] is None:
#                 # We have an end time, they do not.
#                 event = proposed_event
#                 continue

#             if proposed_event[END].date() > event[END].date():
#                 # Event is too late.
#                 continue

#             if proposed_event[END].date() < event[END].date():
#                 # Event is earlier than current, select it.
#                 event = proposed_event
#                 continue

#             if proposed_event[PRIORITY] > event[PRIORITY]:
#                 # Proposed event has a higher priority.
#                 event = proposed_event
#                 continue

#             if proposed_event[PRIORITY] == event[PRIORITY] and (
#                 event[END] is not None and proposed_event[END] < event[END]
#             ):
#                 event = proposed_event
#                 continue
#         return event

#     async def async_get_events(
#         self, start_date: datetime, end_date: datetime
#     ) -> list[CalendarEvent]:
#         """Get all tasks in a specific time frame."""
#         tasks = self._coordinator.data
#         if self._id is None:
#             project_task_data = [
#                 task
#                 for task in tasks
#                 if not self._project_id_whitelist
#                 or task.project_id in self._project_id_whitelist
#             ]
#         else:
#             project_task_data = [task for task in tasks if task.project_id == self._id]

#         events = []
#         for task in project_task_data:
#             if task.due is None:
#                 continue
#             start = get_start(task.due)
#             if start is None:
#                 continue
#             event = CalendarEvent(
#                 summary=task.content,
#                 start=start,
#                 end=start + timedelta(days=1),
#             )
#             if event.start_datetime_local >= end_date:
#                 continue
#             if event.end_datetime_local < start_date:
#                 continue
#             events.append(event)
#         return events

#     def update(self) -> None:
#         """Get the latest data."""
#         tasks = self._coordinator.data
#         if self._id is None:
#             project_task_data = [
#                 task
#                 for task in tasks
#                 if not self._project_id_whitelist
#                 or task.project_id in self._project_id_whitelist
#             ]
#         else:
#             project_task_data = [task for task in tasks if task.project_id == self._id]

#         # If we have no data, we can just return right away.
#         if not project_task_data:
#             _LOGGER.debug("No data for %s", self._name)
#             self.event = None
#             return

#         # Keep an updated list of all tasks in this project.
#         project_tasks = []
#         for task in project_task_data:
#             todoist_task = self.create_todoist_task(task)
#             if todoist_task is not None:
#                 # A None task means it is invalid for this project
#                 project_tasks.append(todoist_task)

#         if not project_tasks:
#             # We had no valid tasks
#             _LOGGER.debug("No valid tasks for %s", self._name)
#             self.event = None
#             return

#         # Make sure the task collection is reset to prevent an
#         # infinite collection repeating the same tasks
#         self.all_project_tasks.clear()

#         # Organize the best tasks (so users can see all the tasks
#         # they have, organized)
#         while project_tasks:
#             best_task = self.select_best_task(project_tasks)
#             _LOGGER.debug("Found Todoist Task: %s", best_task[SUMMARY])
#             project_tasks.remove(best_task)
#             self.all_project_tasks.append(best_task)

#         event = self.all_project_tasks[0]
#         if event is None or event[START] is None:
#             _LOGGER.debug("No valid event or event start for %s", self._name)
#             self.event = None
#             return
#         self.event = event
#         _LOGGER.debug("Updated %s", self._name)


# def get_start(due: Due) -> datetime | date | None:
#     """Return the task due date as a start date or date time."""
#     if due.datetime:
#         start = dt_util.parse_datetime(due.datetime)
#         if not start:
#             return None
#         return dt_util.as_local(start)
#     if due.date:
#         return dt_util.parse_date(due.date)
#     return None
