################################################################################
# Very basic ISO 3 letter country code type.
################################################################################
import re
import typing
import unittest

import pydantic

ISO3LETTER_CODE_PATTERN = re.compile(r'^[A-Z]{3}$')


def ISO3LetterCode_validate(x: typing.Any) -> str:
    if isinstance(x, str) and ISO3LETTER_CODE_PATTERN.match(x):
        return x
    else:
        raise ValueError(f'"{x}" is not a valid ISO 3-letter code.')


ISO3LetterCode = typing.Annotated[
    str,
    pydantic.PlainSerializer(
        lambda x: x.upper(),
        str
    ),
    pydantic.PlainValidator(ISO3LetterCode_validate)
]


class A(pydantic.BaseModel):
    a: ISO3LetterCode | None
    b: ISO3LetterCode

# -------------------------------------------------------------------------------
# Testing
# -------------------------------------------------------------------------------


class Test(unittest.TestCase):

    def test(self):
        a = A(a='ABC', b='ABC')
        self.assertEqual('{"a":"ABC","b":"ABC"}', a.model_dump_json())
        print(a.model_dump_json())

        a = A(a=None, b='ABC')
        self.assertEqual('{"a":null,"b":"ABC"}', a.model_dump_json())
        print(a.model_dump_json())

        with self.assertRaises(pydantic.ValidationError):
            A(a='ABC', b=None)

        with self.assertRaises(pydantic.ValidationError):
            A(a='ABC', b='abc')

        with self.assertRaises(pydantic.ValidationError):
            A(a='ABC', b='AB')

        with self.assertRaises(pydantic.ValidationError):
            A(a='ABC', b='ABCD')


if __name__ == '__main__':
    unittest.main()
