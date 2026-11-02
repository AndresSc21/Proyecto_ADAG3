import json
import tempfile
import unittest
from pathlib import Path

from scripts.run_case import build_result


class RunCaseTests(unittest.TestCase):
    def test_build_result_is_json_serializable_and_verifies_constraints(self):
        case = {
            "name": "prueba",
            "budget": 4,
            "stages": [
                {"name": "S1", "duration": 10, "cost": 4, "reduction": 3}
            ],
            "risks": ["datos"],
            "interactions": [
                {"name": "I1", "risks": ["datos"], "cost": 2}
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "caso.json"
            path.write_text(json.dumps(case), encoding="utf-8")
            result = build_result(str(path))

        json.dumps(result)
        self.assertGreaterEqual(result["elapsed_seconds"], 0)
        self.assertTrue(result["verification"]["acceleration_budget_respected"])
        self.assertTrue(result["verification"]["audit_covers_all_risks"])
        self.assertTrue(result["verification"]["weighted_audit_covers_all_risks"])
