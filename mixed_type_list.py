################################################################################
# Example of a mixed type list.
################################################################################
import typing
import pydantic
import unittest


def test_val(x: typing.Any) -> str:
    return x if x != '' else None


TestType = typing.Annotated[
    str,
    pydantic.BeforeValidator(test_val)
]


class A (pydantic.BaseModel):
    a: int


class B (pydantic.BaseModel):
    b: int


class C (pydantic.BaseModel):
    a: int | None = None
    b: int | None = None


# -------------------------------------------------------------------------------
# Testing
# -------------------------------------------------------------------------------


class Test(unittest.TestCase):

    def test(self):
        # The order of the types in Union is important because if uses the first match
        # approach.
        adapter1 = pydantic.TypeAdapter(list[typing.Union[int, float, A, B]])

        l = adapter1.validate_json('[1, 1.2, {"a": 1}, {"b": 2}]')
        print(l)
        self.assertEqual([1, 1.2, A(a=1), B(b=2)], l)

        # Because an integer is always a valid float and both A and B are valid
        # C instances, int, A and B will never be parsed.
        adapter2 = pydantic.TypeAdapter(
            list[typing.Union[float, int, C, A, B]])
        l = adapter2.validate_json('[1, 1.2, {"a": 1}, {"b": 2}]')
        print(l)
        self.assertEqual([1.0, 1.2, C(a=1), C(b=2)], l)


if __name__ == '__main__':
    unittest.main()
