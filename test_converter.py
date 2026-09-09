import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("jsonl_to_json.py")


class ConverterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "input.jsonl"
        self.output = self.root / "result.json"

    def run_converter(self, content):
        self.source.write_bytes(content.encode("utf-8"))
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(self.source), str(self.output)],
            capture_output=True, text=True,
        )

    def test_bom_blank_lines_unicode_and_exact_large_id(self):
        result = self.run_converter('\ufeff\n{"id":9007199254740993,"name":"演示"}\n\n')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(self.output.read_text(encoding="utf-8")),
                         [{"id": 9007199254740993, "name": "演示"}])

    def test_escaped_newline_remains_one_record(self):
        result = self.run_converter('{"text":"first\\nsecond"}\n{"id":2}\n')
        self.assertEqual(result.returncode, 0, result.stderr)
        records = json.loads(self.output.read_text(encoding="utf-8"))
        self.assertEqual(records, [{"text": "first\nsecond"}, {"id": 2}])

    def test_invalid_input_reports_physical_line_and_creates_no_output(self):
        result = self.run_converter('{"id":1}\n\n{bad json}\n')
        self.assertEqual(result.returncode, 2)
        self.assertIn("input.jsonl:3:", result.stderr)
        self.assertFalse(self.output.exists())

    def test_existing_output_is_never_overwritten(self):
        self.output.write_text("KEEP THIS", encoding="utf-8")
        result = self.run_converter('{"id":1}\n')
        self.assertEqual(result.returncode, 2)
        self.assertEqual(self.output.read_text(encoding="utf-8"), "KEEP THIS")

    def test_invalid_input_also_preserves_existing_output(self):
        self.output.write_text("KEEP THIS", encoding="utf-8")
        result = self.run_converter('{bad json}\n')
        self.assertEqual(result.returncode, 2)
        self.assertEqual(self.output.read_text(encoding="utf-8"), "KEEP THIS")

    def test_non_json_number_and_non_object_are_rejected(self):
        for content in ['{"score":NaN}\n', '[1,2,3]\n']:
            with self.subTest(content=content):
                result = self.run_converter(content)
                self.assertEqual(result.returncode, 2)
                self.assertIn("input.jsonl:1:", result.stderr)
                self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
