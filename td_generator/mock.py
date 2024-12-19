import os

from td_generator.generate import things_list
from td_generator.td import ThingDescription


def log_message(topic, message, retain, file):
    file.write(
        f"topic: '{topic}'; payload: '{message}'; retain: '{str(retain).lower()}'\n"
    )


count = 0


def mock_thing(td: ThingDescription):
    global count

    if not os.path.exists("logs"):
        os.mkdir("logs")

    message_log_file = open(f"logs/Message_log_{count}_{td.type}.txt", "w")
    count += 1
    props = td.properties
    events = td.events
    actions = td.actions
    if props is not None:
        for prop, attr in props.items():
            messages = attr.forms[0].mock(
                attr.type, attr.minimum, attr.maximum, attr.enum, prop
            )

            for m in messages:
                log_message(
                    attr.forms[0].topic, m, attr.forms[0].retain, message_log_file
                )

    if events is not None:
        for event, attr in events.items():
            messages = attr.forms[0].mock(
                attr.data.type,
                attr.data.minimum,
                attr.data.maximum,
                attr.data.enum,
                event,
            )
            for m in messages:
                log_message(
                    attr.forms[0].topic, m, attr.forms[0].retain, message_log_file
                )

    if actions is not None:
        for action, attr in actions.items():
            messages = attr.forms[0].mock(
                attr.input.type,
                attr.input.minimum,
                attr.input.maximum,
                attr.input.enum,
                action,
            )
            for m in messages:
                log_message(
                    attr.forms[0].topic, m, attr.forms[0].retain, message_log_file
                )

    message_log_file.flush()
    message_log_file.close()


def mock_thing_str(td: ThingDescription):
    props = td.properties
    events = td.events
    actions = td.actions

    s = ""

    if props is not None:
        for prop, attr in props.items():
            messages = attr.forms[0].mock(
                attr.type, attr.minimum, attr.maximum, attr.enum, prop
            )

            for m in messages:
                s += f"topic: '{attr.forms[0].topic}'; payload: '{m}'; retain: '{str(attr.forms[0].retain).lower()}'\n"

    if events is not None:
        for event, attr in events.items():
            messages = attr.forms[0].mock(
                attr.data.type,
                attr.data.minimum,
                attr.data.maximum,
                attr.data.enum,
                event,
            )
            for m in messages:
                s += f"topic: '{attr.forms[0].topic}'; payload: '{m}'; retain: '{str(attr.forms[0].retain).lower()}'\n"

    if actions is not None:
        for action, attr in actions.items():
            messages = attr.forms[0].mock(
                attr.input.type,
                attr.input.minimum,
                attr.input.maximum,
                attr.input.enum,
                action,
            )
            for m in messages:
                s += f"topic: '{attr.forms[0].topic}'; payload: '{m}'; retain: '{str(attr.forms[0].retain).lower()}'\n"

    return s


def generate_message_logs():
    for thing in things_list:
        mock_thing(thing.td())


if __name__ == "__main__":
    generate_message_logs()
