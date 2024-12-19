import random
from enum import Enum
from random import sample
from typing import Optional, List, Any, Callable

from pydantic import (
    BaseModel,
    Field,
)
from pydantic.json_schema import SkipJsonSchema

# This implementation is based on the WoT TD Specification and the WoT TD MQTT Binding Template
# WoT TD Specification: https://www.w3.org/TR/wot-thing-description11/
# WoT MQTT Binding Template: https://w3c.github.io/wot-binding-templates/bindings/protocols/mqtt/index.html

MESSAGE_NUM = 5


# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)


def eq_logger(t1, t2):
    # s = ""
    # if t1 == t2:
    #     for val1, val2 in zip(t1, t2):
    #         if val1 != val2:
    #             s = f"{s} | {val1} != {val2}"
    #         # else:
    #         #     s = f"{s} | {val1} == {val2}"
    #     logger.debug(s)
    pass


class AttributeType(str, Enum):
    string = "string"
    boolean = "boolean"
    integer = "integer"
    object = "object"
    null = "null"
    number = "number"


def default_mock(type=AttributeType.null, min=None, max=None, enum=None, name=None):
    if min is None:
        min = 0
    if max is None:
        max = 250
    if type is AttributeType.null:
        return [""] * MESSAGE_NUM
    elif type == "string":
        if enum is not None:
            return enum
    elif type == "integer":
        return sample(range(min, max), MESSAGE_NUM)
    elif type == "number":
        msg = []
        for i in range(0, MESSAGE_NUM):
            msg.append(round(random.uniform(min, max), 3))
        return msg
    elif type == "boolean":
        return ["true", "false"] * int(MESSAGE_NUM / 2)

    raise NotImplementedError(f"The default mock does not work for {name}: {type}")


class Forms(BaseModel):
    href: str
    contentType: Optional[str] = None
    topic: str = Field(
        alias="mqv:topic", description="The MQTT topic of the affordance"
    )
    retain: bool = Field(
        alias="mqv:retain",
        default=False,
        description="Indicates if the topic is retained or not",
    )
    op: List[str] = Field(default_factory=list, description="")
    mock: SkipJsonSchema[Optional[Callable]] = Field(exclude=True, default=default_mock)

    def __eq__(self, other):
        t1 = (self.topic, self.retain)
        t2 = (other.topic, other.retain)
        eq_logger(t1, t2)
        return t1 == t2

    def __str__(self):
        return f"topic='{self.topic}' retain='{self.retain}'"


class BaseProperty(BaseModel):
    title: Optional[str] = Field(default="", description="The title of the property")
    description: Optional[str] = Field(
        default="", description="The description of the property"
    )
    observable: Optional[bool] = None
    type: AttributeType = AttributeType.null
    minimum: Optional[int] = None
    maximum: Optional[int] = None
    enum: Optional[List[str]] = Field(
        default=None,
        description="A list of string values that the property may have. This only applicable it the affordance is of type string",
    )
    properties: dict[str, "BaseProperty"] = Field(
        default_factory=dict,
        description="If the property is of type 'object', 'properties' further describes how the 'object' "
                    "is structured",
    )

    def __eq__(self, other):
        if other is None:
            # logger.debug("other is None")
            return False

        try:
            s1 = set(self.enum)
        except:
            s1 = set()
        t1 = (
            self.type,
            s1,
            self.properties,
        )

        try:
            s2 = set(other.enum)
        except:
            s2 = set()
        t2 = (
            other.type,
            s2,
            other.properties,
        )
        eq_logger(t1, t2)
        return t1 == t2

    def __str__(self):
        return f"type='{self.type}' enum='{self.enum}' properties='{self.properties}'"


class Property(BaseProperty, BaseModel):
    forms: List[Forms] = Field(default_factory=list)

    def __eq__(self, other):

        if other is None:
            # logger.debug("other is None")
            return False
        try:
            s1 = set(self.enum)
        except:
            s1 = set()
        t1 = (
            self.type,
            s1,
            self.forms,
            self.properties,
        )
        try:
            s2 = set(other.enum)
        except:
            s2 = set()
        t2 = (
            other.type,
            s2,
            other.forms,
            other.properties,
        )
        eq_logger(t1, t2)

        return t1 == t2

    def __str__(self):
        return f"type='{self.type}' enum='{self.enum}' forms='{self.forms}' properties='{self.properties}'"


class Action(BaseModel):
    title: Optional[str] = Field(
        default="",
        description="The title of the action. An action is an interactive affordance",
    )
    description: Optional[str] = Field(
        default="",
        description="Describes the action",
    )
    input: Optional[BaseProperty] = BaseProperty()
    output: Optional[BaseProperty] = BaseProperty()
    forms: List[Forms]

    def __eq__(self, other):
        if other is None:
            # logger.debug("other is None")
            return False

        t1 = (self.input, self.output, self.forms)
        t2 = (
            other.input,
            other.output,
            other.forms,
        )

        eq_logger(t1, t2)
        return t1 == t2

    def __str__(self):
        return f"{self.input}"


class Event(BaseModel):
    title: Optional[str] = Field(default="", description="The title of the event")
    description: Optional[str] = Field(default="", description="Describes the event")
    data: BaseProperty = Field(
        default=BaseProperty(), description="The data produced by the event"
    )
    forms: List[Forms]

    def __eq__(self, other):
        t1 = (self.data, self.forms)
        t2 = (other.data, other.forms)

        self.eq_logger(t1, t2)
        return t1 == t2

    def to_property(self):
        return Property(
            title=self.title + " " + str(self.data.title),
            description=self.description + " " + self.data.description,
            observable=self.data.observable,
            type=self.data.type,
            minimum=self.data.minimum,
            maximum=self.data.maximum,
            enum=self.data.enum,
            forms=self.forms,
            properties=self.data.properties,
        )


class ThingDescription(BaseModel):
    context: List[str] = Field(
        alias="@context",
        default=["https://www.w3.org/2022/wot/td/v1.1"],
    )
    type: str = Field(
        alias="@type",
        description="Is the type of the Thing that the Thing Description models",
    )
    title: str = Field(description="A short title that describes the Thing")
    id: str = Field(description="A URN")
    securityDefinitions: Optional[dict[str, Any]] = Field(
        default={"nosec_sc": {"scheme": "nosec"}}
    )
    security: Optional[List[str]] = Field(default=["nosec_sc"])
    description: str = Field(description="A short description of the Thing")
    properties: dict[str, Property] = Field(
        default_factory=dict,
        description="All affordances of the Thing that can " "be described as property",
    )
    events: dict[str, Event] = Field(
        default_factory=dict,
        description="All affordances of the Thing that can be described as event",
    )
    actions: dict[str, Action] = Field(
        default_factory=dict,
        description="All affordances of the Thing that can be described as action/command",
    )

    def __eq__(self, other):
        return (self.actions, self.events, self.properties) == (
            other.actions,
            other.events,
            other.properties,
        )

    # Example of how an external tool could be used for further validation
    # @model_validator(mode="after")
    # def call_td_validator(self):
    #     res = subprocess.run(
    #         [
    #             "node",
    #             "./node_modules/@thing-description-playground/cli/index.js",
    #             "--no-tm-conformance",
    #             "--no-defaults",
    #             "-i",
    #             f"/dev/fd/0",  # STDIN
    #         ],
    #         cwd="/home/max/PycharmProjects/edgellm/",
    #         input=self.model_dump_json(by_alias=True, exclude_none=True).encode(),
    #         capture_output=True,
    #     )
    #     report = res.stdout.decode()
    #     okay = report.split("\n")[0]
    #     logger.debug(okay)
    #     if "okay" in okay.lower():
    #         # return self
    #         raise ValueError(report)
    #     else:
    #         raise ValidationError(report)


class AffordanceType(str, Enum):
    property = "property"
    event = "event"
    action = "action"
