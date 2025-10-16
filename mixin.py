################################################################################
# Test how Pydantic handle mixins.
################################################################################
import pydantic
import unittest


class Mixin1:
    m1: str = '1'


class Mixin2:
    m2: str = '2'


class Mixin3(pydantic.BaseModel):
    m3: str = '2'


class A(pydantic.BaseModel, Mixin2, Mixin1):
    a: int = 3


class B(Mixin3, Mixin2, Mixin1):
    b: int = 3


class C(A):
    c: int = 3


# -------------------------------------------------------------------------------
# Testing
# -------------------------------------------------------------------------------


class Test(unittest.TestCase):

    def test(self):
        a = A()
        print(a.model_dump())
        self.assertEqual({'a': 3, 'm1': '1', 'm2': '2'}, a.model_dump())

        b = B()
        print(b.model_dump())
        self.assertEqual({'b': 3, 'm1': '1', 'm2': '2',
                         'm3': '2'}, b.model_dump())

        c = C()
        print(c.model_dump())
        self.assertEqual({'a': 3, 'c': 3, 'm1': '1',
                         'm2': '2'}, c.model_dump())


if __name__ == '__main__':
    unittest.main()
