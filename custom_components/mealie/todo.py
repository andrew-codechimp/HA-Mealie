"""A Mealie todo platform."""

from typing import cast

from homeassistant.components.todo import (
    TodoItem,
    TodoItemStatus,
    TodoListEntity,
    TodoListEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MealieDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the mealie todo platform."""

    coordinator: MealieDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    shopping_lists = await coordinator.async_get_shopping_lists()

    async_add_entities(
        MealieTodoListEntity(
            coordinator=coordinator,
            config_entry_id=config_entry.entry_id,
            list_id=shopping_list.get("id"),
            name=shopping_list.get("name"),
        )
        for shopping_list in shopping_lists
    )

    # shopping_lists = coordinator.shopping_lists

    # async_add_entities(
    #     (
    #         MealieTodoListEntity(
    #             coordinator,
    #             shopping_list.get("name"),
    #             config_entry.entry_id,
    #             shopping_list.get("id"),
    #         )
    #         for shopping_list in shopping_lists
    #     ),
    #     True,
    # )


class MealieTodoListEntity(
    CoordinatorEntity[MealieDataUpdateCoordinator], TodoListEntity
):
    """A To-do List representation of a Mealie Shopping List."""

    # _attr_has_entity_name = True
    # _attr_should_poll = True
    _attr_supported_features = (
        TodoListEntityFeature.CREATE_TODO_ITEM
        | TodoListEntityFeature.UPDATE_TODO_ITEM
        | TodoListEntityFeature.DELETE_TODO_ITEM
    )

    def __init__(
        self,
        coordinator: MealieDataUpdateCoordinator,
        config_entry_id: str,
        list_id: str,
        name: str,
    ) -> None:
        """Initialize LocalTodoListEntity."""
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = f"{config_entry_id}-{list_id}"
        self._task_list_id = list_id

    @property
    def todo_items(self) -> list[TodoItem] | None:
        """Get the current set of To-do items."""
        # if self.coordinator.data is None:
        #     return None
        # return [_convert_api_item(item) for item in _order_tasks(self.coordinator.data)]
        return []

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass update state from existing coordinator data."""
        await super().async_added_to_hass()
        # self._handle_coordinator_update()

    async def async_create_todo_item(self, item: TodoItem) -> None:
        """Add an item to the To-do list."""

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        # if self.coordinator.data is None:
        # self._attr_todo_items = None
        # else:
        #     items = []
        #     for task in self.coordinator.data:
        #         if task.project_id != self._project_id:
        #             continue
        #         if task.parent_id is not None:
        #             # Filter out sub-tasks until they are supported by the UI.
        #             continue
        #         if task.is_completed:
        #             status = TodoItemStatus.COMPLETED
        #         else:
        #             status = TodoItemStatus.NEEDS_ACTION
        #         due: datetime.date | datetime.datetime | None = None
        #         if task_due := task.due:
        #             if task_due.datetime:
        #                 due = dt_util.as_local(
        #                     datetime.datetime.fromisoformat(task_due.datetime)
        #                 )
        #             elif task_due.date:
        #                 due = datetime.date.fromisoformat(task_due.date)
        #         items.append(
        #             TodoItem(
        #                 summary=task.content,
        #                 uid=task.id,
        #                 status=status,
        #                 due=due,
        #                 description=task.description or None,  # Don't use empty string
        #             )
        #         )
        #     self._attr_todo_items = items

        self._attr_todo_items = []
        super()._handle_coordinator_update()

    #     await self._data.async_add(
    #         item.summary, complete=(item.status == TodoItemStatus.COMPLETED)
    #     )

    # async def async_update_todo_item(self, item: TodoItem) -> None:
    #     """Update an item to the To-do list."""
    #     data = {
    #         "name": item.summary,
    #         "complete": item.status == TodoItemStatus.COMPLETED,
    #     }
    #     try:
    #         await self._data.async_update(item.uid, data)
    #     except NoMatchingShoppingListItem as err:
    #         raise HomeAssistantError(
    #             f"Shopping list item '{item.uid}' was not found"
    #         ) from err

    # async def async_delete_todo_items(self, uids: list[str]) -> None:
    #     """Add an item to the To-do list."""
    #     await self._data.async_remove_items(set(uids))

    # async def async_move_todo_item(
    #     self, uid: str, previous_uid: str | None = None
    # ) -> None:
    #     """Re-order an item to the To-do list."""

    #     try:
    #         await self._data.async_move_item(uid, previous_uid)
    #     except NoMatchingShoppingListItem as err:
    #         raise HomeAssistantError(
    #             f"Shopping list item '{uid}' could not be re-ordered"
    #         ) from err

    # async def async_added_to_hass(self) -> None:
    #     """Entity has been added to hass."""
    #     # Shopping list integration doesn't currently support config entry unload
    #     # so this code may not be used in practice, however it is here in case
    #     # this changes in the future.
    #     self.async_on_remove(self._data.async_add_listener(self.async_write_ha_state))

    # @property
    # def todo_items(self) -> list[TodoItem]:
    #     """Get items in the To-do list."""
    #     results = []
    #     for item in self._data.items:
    #         if cast(bool, item["complete"]):
    #             status = TodoItemStatus.COMPLETED
    #         else:
    #             status = TodoItemStatus.NEEDS_ACTION
    #         results.append(
    #             TodoItem(
    #                 summary=cast(str, item["name"]),
    #                 uid=cast(str, item["id"]),
    #                 status=status,
    #             )
    #         )
    #     return results
