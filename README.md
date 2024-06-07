# Home Assistant Mealie Integration

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![Downloads][download-latest-shield]](Downloads)
[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]


**Early beta, use at own risk**

Mealie integration for Home Assistant

*Please :star: this repo if you find it useful*  
*If you want to show your support please*

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/yellow_img.png)](https://www.buymeacoffee.com/codechimp)

## Features
**To-do lists**  
Mirrors your Mealie shopping lists.  
Given that Home Assistant To-do items are more simplistic, if you edit a Mealie food item within Home Assistant it will be converted to a note type item within Mealie.

**Calendar**  
Creates a Mealie calendar within Home Assistant, this is read only and creates appropriate time slots for breakfast, lunch and dinner (see below for how to change the time slots.)

**Sensors**  
Sensors for today's breakfast, lunch, dinner and side are created for easy use on dashboards.  
An attribute recipe_url provides a link to the recipe.

**Images**  
Images for today's breakfast, lunch, dinner and side, if a meal is a note or the recipe does not have an image the Mealie logo is displayed and the state becomes Unknown, allowing you to conditionally show/hide the image.  
An attribute recipe_url provides a link to the recipe.

## Installation

### HACS

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=andrew-codechimp&repository=HA-Mealie&category=Integration)

Restart Home Assistant  

In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Mealie"  

You will need to provide your Mealie host name (e.g. `http://SERVERIP:PORT`) and an API token that is available from your user account section within Mealie.  Your Mealie user must be an administrator and have advanced features turned on to see this.

### Manual Installation

<details>
<summary>Show detailed instructions</summary>

Installation via HACS is recommended, but a manual setup is supported.

1. Manually copy custom_components/mealie folder from latest release to custom_components folder in your config folder.
1. Restart Home Assistant.
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Mealie"

</details>



## Calendar meal times
If you want to modify the default meal times displayed in the calendar you can add the following to your `configuration.yaml`

```
mealie:
  breakfast_start: "07:00"
  breakfast_end: "11:00"
  lunch_start: "11:30"
  lunch_end: "14:00"
  dinner_start: "16:00"
  dinner_end: "21:00"
```

## Translations

You can help by adding missing translations when you are a native speaker. Or add a complete new language when there is no language file available.

Mealie uses Crowdin to make contributing easy.

<details>
<summary>Show detailed instructions</summary>

### Changing or adding to existing language

First register and join the translation project

- If you don’t have a Crowdin account yet, create one at [https://crowdin.com](https://crowdin.com)
- Go to the [HA-Mealie Crowdin project page](https://crowdin.com/project/ha-mealie)
- Click Join.

Next translate a string

- Select the language you want to contribute to from the dashboard.
- Click Translate All.
- Find the string you want to edit, missing translation are marked red.
- Fill in or modify the translation and click Save.
- Repeat for other translations.

GitHub will automatically pull in latest changes to translations every day and create a Pull Request. After that is reviewed by a maintainer it will be included in the next release of Mealie.

### Adding a new language

Create an [Issue](https://github.com/andrew-codechimp/HA-Mealie/issues/new?template=new_language_request.yml&title=New+Language) requesting a new language. We will do the necessary work to add the new translation to the integration and Crowdin site, when it's ready for you to contribute we'll comment on the issue you raised.
</details>


***

[commits-shield]: https://img.shields.io/github/commit-activity/y/andrew-codechimp/HA-Mealie.svg?style=for-the-badge
[commits]: https://github.com/andrew-codechimp/HA-Mealie/commits/main
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge
[exampleimg]: example.png
[license-shield]: https://img.shields.io/github/license/andrew-codechimp/HA-Mealie.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/andrew-codechimp/HA-Mealie.svg?style=for-the-badge
[releases]: https://github.com/andrew-codechimp/HA-Mealie/releases
[download-latest-shield]: https://img.shields.io/github/downloads/andrew-codechimp/HA-Mealie/latest/total?style=for-the-badge

