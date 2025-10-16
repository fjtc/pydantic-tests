################################################################################
# Defines an annotation that add a property called list_adapter that is a
# pydantic.TypeAdapter for a list of the given type.
################################################################################
import typing
import pydantic
import unittest


class ListAdapterMixin:
    """
    This Mixin adds the class method get_list_adapter() that returns a 
    pydantic.TypeAdapter for a list of instances of the class.
    """

    @classmethod
    def get_list_adapter(cls) -> pydantic.TypeAdapter[typing.List[typing.Self]]:
        """
        Returns a pydantic.TypeAdapter that can be used to serialize/deserialize
        lists of instances of this class.

        The adapter is created on the first call and is reused whenever possible.
        """
        if not hasattr(cls, '_list_adapter'):
            cls._list_adapter = pydantic.TypeAdapter(
                typing.List[cls])
        return cls._list_adapter


class A(pydantic.BaseModel, ListAdapterMixin):
    a: int | None = 1


# -------------------------------------------------------------------------------
# Testing
# -------------------------------------------------------------------------------


class Test(unittest.TestCase):

    def test(self):
        self.assertIsNotNone(A.get_list_adapter())
        self.assertIs(A.get_list_adapter(), A.get_list_adapter())
        ret = A.get_list_adapter().dump_python([A(), A(a=2)])
        print(ret)
        self.assertEqual([{'a': 1}, {'a': 2}], ret)
        l = A.get_list_adapter().validate_json('[{"a": 1}, {"a": 2}]')
        print(l)
        self.assertEqual([A(), A(a=2)], l)


if __name__ == '__main__':
    unittest.main()
