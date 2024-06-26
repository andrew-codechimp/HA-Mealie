"""A Mealie todo platform."""

from homeassistant.components.todo import (
    TodoItem,
    TodoItemStatus,
    TodoListEntity,
    TodoListEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, LOGGER, COORDINATOR, ATTR_SHOPPING_LIST_ID
from .entity import MealieEntity
from .coordinator import MealieDataUpdateCoordinator


TODO_STATUS_MAP = {
    False: TodoItemStatus.NEEDS_ACTION,
    True: TodoItemStatus.COMPLETED,
}
TODO_STATUS_MAP_INV = {v: k for k, v in TODO_STATUS_MAP.items()}


def _convert_api_item(item: dict[str, str]) -> TodoItem:
    """Convert tasks API items into a TodoItem."""

    return TodoItem(
        summary=item["display"],
        uid=item["id"],
        status=TODO_STATUS_MAP.get(
            item.get("checked", False),
            TodoItemStatus.NEEDS_ACTION,
        ),
        due=None,
        description=None,
    )


def _convert_todo_item(item: TodoItem) -> dict[str, str | None]:
    """Convert TodoItem dataclass items to dictionary of attributes the tasks API."""

    result: dict[str, str | None] = {}
    result["display"] = item.summary
    if item.status is not None:
        result["checked"] = TODO_STATUS_MAP_INV[item.status]
    else:
        result["checked"] = TodoItemStatus.NEEDS_ACTION
    return result


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the mealie todo platform."""

    coordinator: MealieDataUpdateCoordinator = hass.data[DOMAIN][COORDINATOR]

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


class MealieTodoListEntity(MealieEntity, TodoListEntity):
    """A To-do List representation of a Mealie Shopping List."""

    _unrecorded_attributes = frozenset({ATTR_SHOPPING_LIST_ID})

    _attr_supported_features = (
        TodoListEntityFeature.CREATE_TODO_ITEM
        | TodoListEntityFeature.UPDATE_TODO_ITEM
        | TodoListEntityFeature.DELETE_TODO_ITEM
        | TodoListEntityFeature.MOVE_TODO_ITEM
    )

    def __init__(
        self,
        coordinator: MealieDataUpdateCoordinator,
        config_entry_id: str,
        list_id: str,
        name: str,
    ) -> None:
        """Initialize LocalTodoListEntity."""
        super().__init__(entity_description=None, coordinator=coordinator)

        self._attr_should_poll = False
        self._attr_name = name
        self._attr_has_entity_name = False
        self.entity_id = f"todo.mealie_{name}"
        self._attr_unique_id = f"{config_entry_id}-{list_id}"
        self._shopping_list_id = list_id
        self._attr_icon = "mdi:basket"

    @property
    def todo_items(self) -> list[TodoItem] | None:
        """Get the current set of To-do items."""

        if self._shopping_list_id in self.coordinator.shopping_list_items:
            return [
                _convert_api_item(item)
                for item in self.coordinator.shopping_list_items[self._shopping_list_id]
            ]

        return []

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass update state from existing coordinator data."""
        await super().async_added_to_hass()

        await self.coordinator.async_refresh()

        self._handle_coordinator_update()

    async def async_create_todo_item(self, item: TodoItem) -> None:
        """Add an item to the list."""

        position = 0
        if len(self.coordinator.shopping_list_items[self._shopping_list_id]) > 0:
            position = (
                self.coordinator.shopping_list_items[self._shopping_list_id][-1].get(
                    "position"
                )
                + 1
            )

        await self.coordinator.api.async_add_shopping_list_item(
            self._shopping_list_id, item.summary, position
        )
        await self.coordinator.async_refresh()

    async def async_update_todo_item(self, item: TodoItem) -> None:
        """Update an item on the list."""

        list_items = self.coordinator.shopping_list_items[self._shopping_list_id]

        for list_item in list_items:
            if list_item["id"] == item.uid:
                position = list_item["position"]
                break

        list_items = self.coordinator.shopping_list_items[self._shopping_list_id]
        for list_item in list_items:
            if list_item["id"] == item.uid:
                if list_item["display"] == item.summary:
                    list_item["checked"] = item.status == TodoItemStatus.COMPLETED
                else:
                    list_item["note"] = item.summary
                    list_item["position"] = position
                    list_item["isFood"] = "False"
                    list_item["foodId"] = None
                    list_item["quantity"] = "0.0"
                    list_item["checked"] = item.status == TodoItemStatus.COMPLETED

                await self.coordinator.api.async_update_shopping_list_item(
                    self._shopping_list_id, item.uid, list_item
                )
                await self.coordinator.async_refresh()
                return

        LOGGER.error(
            "Item %s not found in shopping list %s", item.uid, self._shopping_list_id
        )

    async def async_delete_todo_items(self, uids: list[str]) -> None:
        """Delete items from the list."""
        for uid in uids:
            await self.coordinator.api.async_delete_shopping_list_item(uid)

        await self.coordinator.async_refresh()

    async def async_move_todo_item(
        self, uid: str, previous_uid: str | None = None
    ) -> None:
        """Re-order an item on the list."""

        list_items = self.coordinator.shopping_list_items[self._shopping_list_id]

        old_uid_index = None
        previous_uid_index = None

        for item in list_items:
            if item["id"] == uid:
                old_uid_index = list_items.index(item)
                item_to_move = item
            if previous_uid and item["id"] == previous_uid:
                previous_uid_index = list_items.index(item)
            if old_uid_index and previous_uid_index:
                break

        if previous_uid is None:
            previous_uid_index = -1

        if previous_uid_index < old_uid_index:
            previous_uid_index += 1

        list_items.pop(old_uid_index)
        list_items.insert(previous_uid_index, item_to_move)

        position = 0
        for item in list_items:
            await self.coordinator.api.async_reorder_shopping_list_item(
                self._shopping_list_id, item, position
            )
            position += 1
        await self.coordinator.async_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        items = []

        if self._shopping_list_id in self.coordinator.shopping_list_items:

            for item in self.coordinator.shopping_list_items[self._shopping_list_id]:
                todo_item = _convert_api_item(item)
                items.append(todo_item)

        self._attr_todo_items = items

        super()._handle_coordinator_update()

    @property
    def extra_state_attributes(self) -> dict[str, str] | None:
        """Return the state attributes of the shopping list."""

        attrs = {
            ATTR_SHOPPING_LIST_ID: self._shopping_list_id,
        }

        super_attrs = super().extra_state_attributes
        if super_attrs:
            attrs.update(super_attrs)
        return attrs
