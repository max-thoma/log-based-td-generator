# Introduction

This repository hold the prototypical implementation of the proposed methodology for the
paper “Utilizing Large Language Models for Log-Based Automated Thing Description Generation”
submitted to the ESWC 2025.

# Basic Usage

It is recommended to us [poetry](https://python-poetry.org) and the `pyproject.toml` file to install the dependencies of this project.

The main implementation can be found in `experiment.py`.
In order to execute the experiment you have to set the following variables in the 
`experiment.py`

At the top of the file make sure these global variables are set accordingly:
1. `RUNS_PER_TD`: How many TD candidates should be generated
2. `MODEL`: Which LLM model should be used to conduct the experiment
3. `NUMBER_OF_RETRIES`: How many retries does the LLM get to fix a TD
4. `TEMPERATURE`: Temperature parameter of the LLM

In the main function use one of the example AI backends and set the `base_url` and `api_key` accordingly.
The script generates a report of the experiment as JSON file.
This report includes some metadata about the experiment, the reference TDs paired with a list of the LLM generated artifacts.

# Result Analysis

The script `functional_equivalence.py` generates the report of the functional performance metrics
and the script `desriptive_equivalence.py` generates the report of the descriptive performance metrics.

For both scripts you have to set the path to the output file of the `experiment.py`.
For the `desriptive_equivalence.py` script you also have to set the `api_key` for the text embedding analysis.

Our results used in paper can be found in the `out/` directory.

# Reference TD

The `things` module holds all our reference TD.

For General inspiration we consulted the following sources

| Project                        | Link                                                                           |
|--------------------------------|--------------------------------------------------------------------------------|
| HomeAssistant Integration      | https://www.home-assistant.io/integrations/                                    |
| EVCC documentation             | https://evcc.io                                                                |
| SmartDataModels                | https://smartdatamodels.org                                                    |
| WoT TD Specification           | https://www.w3.org/TR/wot-thing-description11/                                 |
| WoT MQTT Binding Specification | https://w3c.github.io/wot-binding-templates/bindings/protocols/mqtt/index.html |
| Eclipse ThingWeb               | https://thingweb.io                                                            |
| Wikipedia SAE J1772 Article    | https://en.wikipedia.org/wiki/SAE_J1772                                        |
| WebThings                      | https://webthings.io                                                           |
| Tasmota                        | https://github.com/arendst/Tasmota                                             |



See the table down below for to see what was the main source of inspiration for each TD-

| Thing Description        | Main source of inspiration                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
|--------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Alarm Control Panel      | https://www.home-assistant.io/integrations/alarm_control_panel.mqtt/                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Alarm Siren              | https://www.home-assistant.io/integrations/siren.mqtt/                                                                                                                                                                                                                                                                                                                                                                                                                                |
| Binary Window Contact    | https://www.home-assistant.io/integrations/binary_sensor.mqtt/                                                                                                                                                                                                                                                                                                                                                                                                                        |
| Button                   | https://www.home-assistant.io/integrations/button.mqtt/                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Ceiling Fan              | https://www.home-assistant.io/integrations/fan.mqtt/                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Door Lock                | https://www.home-assistant.io/integrations/lock.mqtt/                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| Doorbell                 | N/A                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| Electric Vehicle         | https://docs.evcc.io/docs/devices/vehicles                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| Electric Vehicle Charger | https://docs.evcc.io/docs/devices/chargers                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| Humidifier               | https://www.home-assistant.io/integrations/humidifier.mqtt/                                                                                                                                                                                                                                                                                                                                                                                                                           |
| HVAC Unit                | https://www.home-assistant.io/integrations/climate.mqtt/                                                                                                                                                                                                                                                                                                                                                                                                                              |
| Illuminance Sensor       | https://w3c.github.io/wot-binding-templates/bindings/protocols/mqtt/index.html#conformance,  <br/>https://www.w3.org/TR/wot-thing-description11/#example-69                                                                                                                                                                                                                                                                                                                           |
| Lawn Mower               | https://www.home-assistant.io/integrations/lawn_mower.mqtt/                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Lightbulb (RGB)          | https://www.home-assistant.io/integrations/light.mqtt/, <br/>https://www.w3.org/TR/wot-thing-description11/                                                                                                                                                                                                                                                                                                                                                                           |
| Lightbulb (Single Color) | https://www.home-assistant.io/integrations/light.mqtt/, <br/>https://www.w3.org/TR/wot-thing-description11/                                                                                                                                                                                                                                                                                                                                                                           |
| Location Tracker (GPS)   | https://www.home-assistant.io/integrations/device_tracker.mqtt/                                                                                                                                                                                                                                                                                                                                                                                                                       |
| Photovoltaic Inverter    | https://github.com/smart-data-models/dataModel.GreenEnergy/tree/master/PhotovoltaicMeasurement,  <br/>https://swagger.lab.fiware.org/?url=https://smart-data-models.github.io/dataModel.GreenEnergy/PhotovoltaicDevice/swagger.yaml,  <br/>https://swagger.lab.fiware.org/?url=https://smart-data-models.github.io/dataModel.S4BLDG/SolarDevice/swagger.yaml,  <br/>https://swagger.lab.fiware.org/?url=https://smart-data-models.github.io/dataModel.Energy/SolarEnergy/swagger.yaml |
| Photovoltaic Panel       | https://github.com/smart-data-models/dataModel.GreenEnergy/tree/master/PhotovoltaicMeasurement,  <br/>https://swagger.lab.fiware.org/?url=https://smart-data-models.github.io/dataModel.GreenEnergy/PhotovoltaicDevice/swagger.yaml,  <br/>https://swagger.lab.fiware.org/?url=https://smart-data-models.github.io/dataModel.S4BLDG/SolarDevice/swagger.yaml,  <br/>https://swagger.lab.fiware.org/?url=https://smart-data-models.github.io/dataModel.Energy/SolarEnergy/swagger.yaml |
| Smart Meter              | https://docs.evcc.io/docs/devices/meters                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| Switch                   | https://www.home-assistant.io/integrations/switch.mqtt/                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Vacuum Cleaner           | https://www.home-assistant.io/integrations/vacuum.mqtt/                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Window Cover             | https://www.home-assistant.io/integrations/cover.mqtt/                                                                                                                                                                                                                                                                                                                                                                                                                                |

See the table down below to see which licenses these project use

| Project                        | License                                                       |
|--------------------------------|---------------------------------------------------------------|
| HomeAssistant Integration      | Attribution-NonCommercial-ShareAlike 4.0 International        |
| EVCC documentation             | MIT License                                                   |
| SmartDataModels                | Creative Commons Attribution 4.0 International Public License |
| WoT TD Specification           | Software and Document license - 2023 version                  |
| WoT MQTT Binding Specification | Software and Document license - 2015 version                  |





