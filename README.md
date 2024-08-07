# Home Assistant Mealie Integration

This integration has now been retired.

With the 2024.8 release of Home Assistant the official Mealie integration has been enhanced to include shopping lists and a lot more, now meeting feature parity with this custom integration.

How do you remove the custom integration and move to core?
* Within Settings, Devices & Services, Integrations, open Mealie.
* Use the 3 dots to choose Delete
* Then within HACS find Mealie, and choose Delete to remove the custom integration.
* Restart HA
* Go to Settings, Devices & Services, Integrations and click Add Integration
* Search for Mealie and follow the integration steps.

While things are a little different, particularly with the meal plan sensors, I have added an example template sensor in the [documentation](https://www.home-assistant.io/integrations/mealie/) to get you started.  The bonus here is you could create sensors for today, tomorrow etc and it will also cope with multiple dishes.

Thanks to everyone who supported this integration.

