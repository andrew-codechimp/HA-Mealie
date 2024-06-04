"""Constants for mealie."""

import json
from logging import Logger, getLogger
from pathlib import Path
import voluptuous as vol

from homeassistant.helpers import config_validation as cv

LOGGER: Logger = getLogger(__package__)

MIN_HA_VERSION = "2024.3"

manifestfile = Path(__file__).parent / "manifest.json"
with open(file=manifestfile, encoding="UTF-8") as json_file:
    manifest_data = json.load(json_file)

DOMAIN = manifest_data.get("domain")
NAME = manifest_data.get("name")
VERSION = manifest_data.get("version")
ISSUEURL = manifest_data.get("issue_tracker")
MANUFACTURER = "@Andrew-CodeChimp"

DOMAIN_CONFIG = "config"
COORDINATOR = "coordinator"

SERVICE_ADD_SHOPPING_LIST_ITEM = "add_shopping_list_item"

CONF_GROUP_ID = "group_id"

CONF_BREAKFAST_START = "breakfast_start"
CONF_BREAKFAST_END = "breakfast_end"
CONF_LUNCH_START = "lunch_start"
CONF_LUNCH_END = "lunch_end"
CONF_DINNER_START = "dinner_start"
CONF_DINNER_END = "dinner_end"

ATTR_SHOPPING_LIST_ID = "shopping_list_id"
