import pydantic
import datetime
import typing

simpledate = typing.Annotated[
    datetime.time,
    pydantic.PlainSerializer(
        lambda x: x.isoformat('seconds'),
        str
    )
]


class A(pydantic.BaseModel):
    d: datetime.date
    t: simpledate


now = datetime.datetime.now()

a = A(d=now.date(), t=now.time())
print(a.model_dump_json())
