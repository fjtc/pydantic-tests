################################################################################
# Implementation of an extension of pydantic.Base64Bytes that are more flexible
# when validating bytes values in multiple ways.
################################################################################
import pydantic
import typing
import base64
import unittest


def b64bytes_validate(x) -> bytes:
    """
    Implements pydantic before validator that can parse multiple formats to
    bytes. It will accept None, '', base64 strings, bytes and bytearray
    """
    match x:
        case '':
            return b''
        case x if isinstance(x, str):
            return base64.b64decode(x, validate=True)
        case x if isinstance(x, bytes):
            return x
        case x if isinstance(x, bytearray):
            return bytes(x)
        case _:
            raise TypeError(f'Unexpected type {type(x)}')


b64bytes = typing.Annotated[
    bytes,
    pydantic.PlainSerializer(
        lambda x: str(base64.b64encode(x), encoding='utf-8') if x else '',
        str
    ),
    pydantic.BeforeValidator(
        b64bytes_validate
    )
]
"""
A variant of pydantic.Base64Bytes that can parse bytes from multiple formats.
"""


class A(pydantic.BaseModel):
    a: b64bytes | None = pydantic.Field(
        min_length=0, max_length=1000, default=None)
    b: pydantic.Base64Bytes | None = None


# -------------------------------------------------------------------------------
# Testing
# -------------------------------------------------------------------------------


class Test(unittest.TestCase):

    def test(self):
        a = A(a=b'A')
        print(a.model_dump())
        self.assertEqual(b'A', a.a)
        self.assertEqual({'a': 'QQ==', 'b': None}, a.model_dump())

        a = A(a='QQ==')
        print(a.model_dump())
        self.assertEqual(b'A', a.a)
        self.assertEqual({'a': 'QQ==', 'b': None}, a.model_dump())

        a = A(a='')
        print(a.model_dump())
        self.assertEqual(b'', a.a)
        self.assertEqual({'a': '', 'b': None}, a.model_dump())
        print(a.model_dump())

        a = A(a=bytearray(b'A'))
        print(a.model_dump())
        self.assertEqual(b'A', a.a)
        self.assertEqual({'a': 'QQ==', 'b': None}, a.model_dump())
        print(a.model_dump())

        a = A(a=None)
        print(a.model_dump())
        self.assertIsNone(a.a)
        self.assertEqual({'a': None, 'b': None}, a.model_dump())


if __name__ == '__main__':
    unittest.main()
