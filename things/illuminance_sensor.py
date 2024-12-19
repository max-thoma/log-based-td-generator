import datetime

import td_generator
from td_generator.td import ThingDescription


def _mock(type=None, min=None, max=None, enum=None, name=None):
    msg = []
    now = datetime.datetime.now()
    step = datetime.timedelta(minutes=5)
    for i in range(0, td_generator.td.MESSAGE_NUM):
        msg.append((now + i * step).isoformat())
    return msg


def td():
    return ThingDescription(
        **{
            "@type": "SmartSensor",
            "title": "MyIlluminanceSensor",
            "id": "urn:uuid:f63a9095-ae49-43db-a9ce-f620df21b8a6",
            "description": "An illuminance Sensor",
            "properties": {
                "status": {
                    "title": "Sensor Status",
                    "description": "Status of the Sensor",
                    "observable": True,
                    "type": "string",
                    "enum": ["unknown", "normal", "fault"],
                    "forms": [
                        {
                            "href": "192.168.0.100:1883",
                            "mqv:topic": "application/deviceid/sensor/operation",
                            "mqv:retain": False,
                            "op": ["observeproperty"],
                        }
                    ],
                },
                "uptime": {
                    "title": "Sensor Uptime",
                    "description": "Uptime of the Sensor",
                    "observable": True,
                    "type": "string",
                    "forms": [
                        {
                            "href": "192.168.0.100:1883",
                            "mqv:topic": "application/deviceid/sensor/uptime",
                            "mqv:retain": True,
                            "op": ["observeproperty"],
                            "mock": _mock,
                        }
                    ],
                },
            },
            "events": {
                "illuminance": {
                    "title": "Illuminance measurement",
                    "description": "Illuminance measurement",
                    "data": {"type": "integer"},
                    "forms": [
                        {
                            "href": "192.168.0.100:1883",
                            "contentType": "text/plain",
                            "response": {"contentType": "text/plain"},
                            "mqv:topic": "application/deviceid/sensor/illuminance",
                            "mqv:retain": True,
                            "op": ["subscribeevent", "unsubscribeevent"],
                        }
                    ],
                }
            },
            "actions": {
                "calibrate": {
                    "title": "Calibration",
                    "description": "Calibration",
                    "input": {"observable": True, "type": "integer"},
                    "output": {
                        "observable": True,
                        "type": "string",
                        "enum": ["ok", "error"],
                    },
                    "forms": [
                        {
                            "href": "192.168.0.100:1883",
                            "contentType": "text/plain",
                            "response": {"contentType": "text/plain"},
                            "mqv:topic": "application/deviceid/sensor/calibrate",
                            "mqv:retain": False,
                            "op": ["invokeaction"],
                        }
                    ],
                }
            },
        }
    )
