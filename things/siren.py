from td_generator.td import ThingDescription


def td():
    return ThingDescription(
        **{
            "@type": "AlarmSiren",
            "title": "Garage Alarm Siren",
            "id": "urn:uuid:be84eecd-42dc-4409-b30c-3bfa046f0e95",
            "description": "MQTT activated alarm sirem, (caution loud)",
            "securityDefinitions": {"nosec_sc": {"scheme": "nosec"}},
            "security": ["nosec_sc"],
            "properties": {
                "availability": {
                    "title": "Siren Availability",
                    "description": "The availability of the sire",
                    "observable": True,
                    "type": "string",
                    "enum": ["ONLINE", "OFFLINE"],
                    "forms": [
                        {
                            "href": "192.168.0.100:1883",
                            "mqv:topic": "garage/siren/availability",
                            "mqv:retain": True,
                            "op": ["observeproperty", "readproperty"],
                        }
                    ],
                },
            },
            "events": {
                "activated": {
                    "title": "Siren Activated",
                    "description": "The siren was activated",
                    "data": {
                        "observable": False,
                        "type": "string",
                        "enum": ["activated"],
                    },
                    "forms": [
                        {
                            "href": "192.168.0.100:1883",
                            "mqv:topic": "garage/siren/activate/result",
                            "mqv:retain": False,
                            "op": ["subscribeevent", "unsubscribeevent"],
                        }
                    ],
                },
                "testActivated": {
                    "title": "Siren Test Activated",
                    "description": "The test alarm was activated (silent)",
                    "data": {
                        "observable": False,
                        "type": "string",
                        "enum": ["activated"],
                    },
                    "forms": [
                        {
                            "href": "192.168.0.100:1883",
                            "mqv:topic": "garage/siren/test/result",
                            "mqv:retain": False,
                            "op": ["subscribeevent", "unsubscribeevent"],
                        }
                    ],
                },
            },
            "actions": {
                "activate": {
                    "title": "Activate Siren (Hot)",
                    "description": "activate Siren",
                    "input": {
                        "observable": True,
                        "type": "boolean",
                    },
                    "forms": [
                        {
                            "href": "192.168.0.100:1883",
                            "mqv:topic": "garage/siren/activate",
                            "mqv:retain": False,
                            "op": ["invokeaction"],
                        }
                    ],
                },
                "test": {
                    "title": "Activate Siren (Silent)",
                    "description": "silently test activation of the siren",
                    "input": {
                        "observable": True,
                        "type": "boolean",
                    },
                    "forms": [
                        {
                            "href": "192.168.0.100:1883",
                            "mqv:topic": "garage/siren/test",
                            "mqv:retain": False,
                            "op": ["invokeaction"],
                        }
                    ],
                },
            },
        }
    )
