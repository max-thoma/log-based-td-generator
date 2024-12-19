import json
import os

from td_generator.td import AttributeType
from things import (
    allarm_control_panel,
    binary_window_contact,
    button,
    doorbell,
    ev,
    ev_charger,
    fan,
    humidifier,
    hvac,
    illuminance_sensor,
    lawn_mower,
    light_rgb,
    light_simple,
    lock,
    meter_flat,
    meter_nested,
    pv_inverter,
    pv_panel,
    siren,
    switch,
    tracker,
    vacuum,
    window_cover,
)

things_list = [
    allarm_control_panel,
    binary_window_contact,
    button,
    doorbell,
    ev,
    ev_charger,
    fan,
    humidifier,
    hvac,
    illuminance_sensor,
    lawn_mower,
    light_rgb,
    light_simple,
    lock,
    meter_flat,
    meter_nested,
    pv_inverter,
    pv_panel,
    siren,
    switch,
    tracker,
    vacuum,
    window_cover,
]


def thing_list():
    return things_list


def count_entries():
    num = 0
    entries_type = set()
    types = {
        AttributeType.string: 0,
        AttributeType.boolean: 0,
        AttributeType.integer: 0,
        AttributeType.object: 0,
        AttributeType.null: 0,
        AttributeType.number: 0,
    }

    affordances = {
        "action": 0,
        "event": 0,
        "property": 0,
    }

    for thing in things_list:
        td = thing.td()
        entries = {}

        if td.properties is not None:
            len_entries = len(entries)
            len_attr = len(td.properties)
            entries |= td.properties
            affordances["property"] += len_attr
            assert len(entries) == len_entries + len_attr
        if td.events is not None:
            len_entries = len(entries)
            len_attr = len(td.events)
            entries |= td.events
            affordances["event"] += len_attr
            assert len(entries) == len_entries + len_attr
        if td.actions is not None:
            len_entries = len(entries)
            len_attr = len(td.actions)
            entries |= td.actions
            affordances["action"] += len_attr
            assert len(entries) == len_entries + len_attr

        for e in entries.values():
            try:
                t = e.type
            except:
                try:
                    t = e.input.type
                except:
                    t = e.data.type
            types[t] += 1

        num += len(entries)

        print(f"For {len(things_list)} there are {num} entries")
    print(json.dumps(types, indent=4))
    print(affordances)


def generate_tds(num=1):
    count = 0
    for thing in things_list:
        td = thing.td()

        if not os.path.exists("tds"):
            os.mkdir("tds")
        for i in range(0, num):
            with open(f"tds/TD_{count}_{td.type}_{i}.json", "w") as td_file:
                td_content = td.model_dump_json(
                    exclude_none=True,
                    by_alias=True,
                    indent=2,
                    exclude={"properties": {"*": "title"}},
                )
                td_file.write(td_content)
        count += 1
    print(f"Generated {len(things_list)} TDs")


if __name__ == "__main__":
    generate_tds()
    count_entries()
