import base64
import importlib.util
import io
import json
import os
from contextlib import redirect_stdout
from pathlib import Path
from unittest import TestCase, main
from unittest.mock import patch


SCRIPT = Path(__file__).parents[1] / "scripts" / "process-upload-response.py"
SPEC = importlib.util.spec_from_file_location("process_upload_response", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ProcessUploadResponseTests(TestCase):
    def test_parse_response_keeps_existing_fields_and_encodes_validation(self):
        response = {
            "id": "Example.Extension",
            "name": "Example Extension",
            "version": "1.2.3",
            "manageUrl": "https://example.test/manage",
            "manageTokenIncludedInUrl": True,
            "validation": [
                {
                    "severity": "warning",
                    "code": "icon.too-small",
                    "message": "Use a larger icon.",
                }
            ],
        }

        output = io.StringIO()
        with patch.dict(
            os.environ,
            {
                "UPLOAD_JSON": json.dumps(response),
                "GALLERY_URL": "https://gallery.test",
            },
            clear=True,
        ), redirect_stdout(output):
            self.assertEqual(0, MODULE.parse_response())

        fields = output.getvalue().splitlines()
        self.assertEqual("Example.Extension", fields[0])
        self.assertEqual("https://gallery.test/extension/Example.Extension", fields[3])
        self.assertEqual("1", fields[6])
        validation = json.loads(base64.b64decode(fields[7]).decode("utf-8"))
        self.assertEqual("icon.too-small", validation[0]["code"])

    def test_parse_response_supports_legacy_response_without_validation(self):
        with patch.dict(
            os.environ,
            {"UPLOAD_JSON": '{"ID":"Legacy.Extension","Name":"Legacy"}'},
            clear=True,
        ):
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(0, MODULE.parse_response())

        fields = output.getvalue().splitlines()
        self.assertEqual([], json.loads(base64.b64decode(fields[7]).decode("utf-8")))

    def test_annotations_and_summary_include_warning(self):
        findings = [
            {
                "severity": "warning",
                "code": "description.too-short",
                "message": "Use a | clearer description.",
            }
        ]
        encoded = base64.b64encode(json.dumps(findings).encode("utf-8")).decode("ascii")

        with patch.dict(os.environ, {"VALIDATION_BASE64": encoded}, clear=True):
            annotations = io.StringIO()
            with redirect_stdout(annotations):
                MODULE.emit_annotations()
            summary = io.StringIO()
            with redirect_stdout(summary):
                MODULE.render_summary()

        self.assertIn("::warning title=VSIX validation (description.too-short)", annotations.getvalue())
        self.assertIn("### Validation warnings", summary.getvalue())
        self.assertIn(r"Use a \| clearer description.", summary.getvalue())


if __name__ == "__main__":
    main()
