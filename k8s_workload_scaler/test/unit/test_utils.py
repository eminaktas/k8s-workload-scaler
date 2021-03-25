from unittest import TestCase
from k8s_workload_scaler.utils import Dict


class UtilsTest(TestCase):
    def test_dict(self):
        example = Dict({"key": "value"})
        self.assertEqual(example["key"], example.key)
