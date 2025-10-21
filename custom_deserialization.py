################################################################################
# Example of a custom deserialization of a complex object.
################################################################################
import unittest
import pydantic
import typing
import decimal

SAMPLE = [
    {
        "cvssV4_0": {
            "version": "4.0",
            "baseScore": decimal.Decimal('5.1'),
            "vectorString": "CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N/E:P",
            "baseSeverity": "MEDIUM"
        }
    },
    {
        "cvssV3_1": {
            "version": "3.1",
            "baseScore": decimal.Decimal('4.7'),
            "vectorString": "CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:L/E:P/RL:X/RC:R",
            "baseSeverity": "MEDIUM"
        }
    },
    {
        "cvssV3_0": {
            "version": "3.0",
            "baseScore": decimal.Decimal('4.7'),
            "vectorString": "CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:L/E:P/RL:X/RC:R",
            "baseSeverity": "MEDIUM"
        }
    },
    {
        "cvssV2_0": {
            "version": "2.0",
            "baseScore": decimal.Decimal('5.8'),
            "vectorString": "AV:N/AC:L/Au:M/C:P/I:P/A:P/E:POC/RL:ND/RC:UR",
            "baseSeverity": None
        }
    }
]
"""
Example of a custom list with mixed objects from the CVE REST API.
"""

JSON_SAMPLE = [
    """{
        "cvssV4_0": {
            "version": "4.0",
            "baseScore": 5.1,
            "vectorString": "CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N/E:P",
            "baseSeverity": "MEDIUM"
        }
    }""",
    """{
        "cvssV3_1": {
            "version": "3.1",
            "baseScore": 4.7,
            "vectorString": "CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:L/E:P/RL:X/RC:R",
            "baseSeverity": "MEDIUM"
        }
    }""",
    """{
        "cvssV3_0": {
            "version": "3.0",
            "baseScore": 4.7,
            "vectorString": "CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:L/E:P/RL:X/RC:R",
            "baseSeverity": "MEDIUM"
        }
    }""",
    """{
        "cvssV2_0": {
            "version": "2.0",
            "baseScore": 5.8,
            "vectorString": "AV:N/AC:L/Au:M/C:P/I:P/A:P/E:POC/RL:ND/RC:UR"
        }
    }"""
]
"""
Same as SAMPLE but as JSON.
"""


_CVSS_VERSION_ATTR_MAP = {
    "4.0": "cvssV4_0",
    "3.1": "cvssV3_1",
    "3.0": "cvssV3_0",
    "2.0": "cvssV2_0",
}


class CVSSEntry(pydantic.BaseModel):

    version: typing.Literal['2.0', '3.0', '3.1', '4.0']
    base_score: decimal.Decimal = pydantic.Field(alias='baseScore')
    vector_string: str = pydantic.Field(alias='vectorString')
    base_severity: None | typing.Literal[
        'NONE', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'] = pydantic.Field(alias='baseSeverity', default=None)

    @pydantic.model_serializer(mode='wrap')
    def serialize_model(self, handler: pydantic.SerializerFunctionWrapHandler) -> dict[str, object]:
        body = handler(self)
        if field_name := _CVSS_VERSION_ATTR_MAP.get(self.version, None):
            h = {field_name: body}
            return h
        else:
            raise ValueError(
                'Missing version.' if not self.version else f'Unsupported version ')

    @pydantic.model_validator(mode='wrap')
    @classmethod
    def check_card_number_not_present(cls, data: typing.Any, handler: pydantic.ModelWrapValidatorHandler[typing.Self]) -> typing.Any:
        if not isinstance(data, dict):
            raise ValueError('Invalid')
        # Try the default validator first if version is present...
        if 'version' in data:
            return handler(data)
        # Try to decode the JSON object wrapped with cvssVx_x...
        for version, root in _CVSS_VERSION_ATTR_MAP.items():
            if d := data.get(root, None):
                dec = handler(d)
                if dec.version != version:
                    raise ValueError(
                        f'{dec.version} is not a valid version for {root}.')
                return dec
        raise ValueError('Unknown/invalid CVSS.')


# -------------------------------------------------------------------------------
# Testing
# -------------------------------------------------------------------------------


class Test(unittest.TestCase):

    def test_serialization(self):

        for s in SAMPLE:
            for root in _CVSS_VERSION_ATTR_MAP.values():
                if values := s.get(root, None):
                    sample = {root: values}
                    break
            p = dict(values)
            p['baseScore'] = decimal.Decimal(f'{p['baseScore']:.1f}')
            c = CVSSEntry.model_validate(values)
            print(c.model_dump())
            m = c.model_dump(by_alias=True, )
            self.assertEqual(sample, m)

    def test_deserialization(self):
        for i, s in zip(range(len(JSON_SAMPLE)), JSON_SAMPLE):
            m = CVSSEntry.model_validate_json(s)
            m2 = CVSSEntry.model_validate(SAMPLE[i])
            self.assertEqual(m, m2)

        # Root doesn't match the inner version.
        with self.assertRaises(pydantic.ValidationError):
            INVALID = {'cvssV3_1': {'version': '3.0', 'baseScore': decimal.Decimal(
                '4.7'), 'vectorString': 'CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:L/E:P/RL:X/RC:R', 'baseSeverity': 'MEDIUM'}}
            CVSSEntry.model_validate(INVALID)

        # Unknown root
        with self.assertRaises(pydantic.ValidationError):
            INVALID = {'cvssV1_0': {'version': '1.0', 'baseScore': decimal.Decimal(
                '4.7'), 'vectorString': 'CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:L/E:P/RL:X/RC:R', 'baseSeverity': 'MEDIUM'}}
            CVSSEntry.model_validate(INVALID)


if __name__ == '__main__':
    unittest.main()
