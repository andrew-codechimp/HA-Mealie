"""Mealie API Client."""

import aiohttp
from asyncio import timeout

from .const import LOGGER

HEADERS = {"Content-type": "application/json; charset=UTF-8"}


class MealieApiClient:
    """API for Mealie."""

    def __init__(self, host: str, token: str, session: aiohttp.ClientSession) -> None:
        """Initialize."""
        self._host = host
        self._token = token
        self._session = session

        self._connected = False
        self._error = ""

    def _get_auth_headers(self) -> dict[str, str]:
        # headers = HEADERS
        # headers["Authorization"] = f"bearer {self._token}"
        return {"Authorization": f"bearer {self._token}"}

    async def async_get_groups(self) -> dict:
        """Get current users group."""
        return await self.api_wrapper("get", "/api/groups/self")

    async def async_get_shopping_lists(self, group_id: str) -> dict:
        """Get all shopping lists for our group."""
        params = {"group_id": group_id}
        return await self.api_wrapper("get", "/api/groups/shopping/lists", data=params)

    async def async_get_shopping_list_items(
        self, group_id: str, shopping_list_id: str
    ) -> dict:
        """Get all shopping list items."""

        params = {"orderBy": "position", "orderDirection": "asc", "perPage": "1000"}
        params["group_id"] = group_id
        params["queryFilter"] = f"shopping_list_id={shopping_list_id}"

        return await self.api_wrapper("get", "/api/groups/shopping/items", data=params)

    async def async_add_shopping_list_item(
        self, shopping_list_id: str, summary: str, position: int
    ) -> dict:
        """Add a shopping list item."""

        data = {"isFood": "False", "checked": "False"}
        data["note"] = summary
        data["shoppingListId"] = shopping_list_id
        data["position"] = position

        return await self.api_wrapper("post", "/api/groups/shopping/items", data=data)

    async def async_update_shopping_list_item(
        self, shopping_list_id: str, item_id: str, item: dict
    ) -> dict:
        """Update a shopping list item."""

        return await self.api_wrapper(
            "put", f"/api/groups/shopping/items/{item_id}", data=item
        )

    async def async_reorder_shopping_list_item(
        self, shopping_list_id: str, item: dict, position: int
    ) -> dict:
        """Update a shopping list item position."""

        data = {}
        data["shoppingListId"] = shopping_list_id
        data["item_id"] = item["id"]
        data["position"] = position
        data["isFood"] = item["isFood"]
        data["quantity"] = item["quantity"]
        data["labelId"] = item["labelId"]
        data["note"] = item["note"]

        if item["isFood"]:
            data["foodId"] = item["foodId"]
            data["unitId"] = item["unitId"]

        return await self.api_wrapper(
            "put", f"/api/groups/shopping/items/{item["id"]}", data=data
        )

    async def async_delete_shopping_list_item(self, item_id: str) -> dict:
        """Delete a shopping list item."""

        data = {}
        data["item_id"] = item_id

        return await self.api_wrapper(
            "delete", f"/api/groups/shopping/items/{item_id}", data=data
        )

    async def async_get_meal_plans(self, group_id: str, start_date: str, end_date: str) -> dict:
        """Get all meal plans for our group."""
        params = {"orderBy": "date", "orderDirection": "asc", "perPage": "1000"}
        params["group_id"] = group_id
        params["start_date"] = start_date
        params["end_date"] = end_date

        return await self.api_wrapper("get", "/api/groups/mealplans", data=params)

    async def async_get_meal_plans_today(self, group_id: str) -> dict:
        """Get today's meal plans for our group."""
        params = {"orderBy": "date", "orderDirection": "asc", "perPage": "1000"}
        params["group_id"] = group_id

        return await self.api_wrapper("get", "/api/groups/mealplans/today", data=params)

    async def api_wrapper(self, method: str, service: str, data: dict = {}) -> any:
        """Get information from the API."""

        self._connected = False
        error = False

        url = self.http_normalize_slashes(service)

        try:
            async with timeout(10):
                if method == "get":
                    response = await self._session.get(
                        url=url,
                        params=data,
                        headers={"Authorization": f"bearer {self._token}"},
                    )

                    if response.status == 200:
                        data = await response.json()
                        LOGGER.debug(
                            "%s query response: %s",
                            f"{self._host}{service}",
                            data,
                        )
                    else:
                        error = True

                elif method == "put":
                    response = await self._session.put(
                        url=url,
                        json=data,
                        headers={
                            "accept": "application/json",
                            "Content-Type": "application/json",
                            "Authorization": f"bearer {self._token}",
                        },
                    )

                    if response.status == 200:
                        data = await response.json()
                        LOGGER.debug(
                            "%s query response: %s",
                            f"{self._host}{service}",
                            data,
                        )
                    else:
                        error = True

                elif method == "post":
                    response = await self._session.post(
                        url=url,
                        json=data,
                        headers={
                            "accept": "application/json",
                            "Content-Type": "application/json",
                            "Authorization": f"bearer {self._token}",
                        },
                    )

                    if response.status == 201:
                        data = await response.json()
                        LOGGER.debug(
                            "%s query response: %s",
                            f"{self._host}{service}",
                            data,
                        )
                    else:
                        error = True

                elif method == "delete":
                    response = await self._session.delete(
                        url=url,
                        json=data,
                        headers={"Authorization": f"bearer {self._token}"},
                    )

                    if response.status == 200:
                        data = await response.json()
                        LOGGER.debug(
                            "%s query response: %s",
                            f"{self._host}{service}",
                            data,
                        )
                    else:
                        error = True

                else:
                    error = True
        except Exception:  # pylint: disable=broad-exception-caught
            error = True

        if error:
            try:
                errorcode = response.status
            except Exception:  # pylint: disable=broad-exception-caught
                errorcode = "no_connection"

            LOGGER.warning(
                "%s unable to fetch data %s (%s)",
                self._host,
                service,
                errorcode,
            )

            self._error = errorcode
            return None

        self._connected = True
        self._error = ""

        return data

    @property
    def error(self):
        """Return error."""
        return self._error

    def http_normalize_slashes(self, service):
        """Fix slashes between host and service."""

        url = f"{self._host}{service}"
        segments = url.split("/")
        correct_segments = []
        for segment in segments:
            if segment != "":
                correct_segments.append(segment)
        first_segment = str(correct_segments[0])
        if first_segment.find("http") == -1:
            correct_segments = ["http:"] + correct_segments
        correct_segments[0] = correct_segments[0] + "/"
        normalized_url = "/".join(correct_segments)
        return normalized_url
