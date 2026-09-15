#!/usr/bin/env python3

import argparse
import base64
import json
import os
import sys
import urllib.parse


def get_value(data, *names):
    for name in names:
        value = data.get(name)
        if value is not None:
            return value
    return None


def single_line(value):
    return str(value or "").replace("\r", " ").replace("\n", " ")


def get_validation(data):
    raw = get_value(data, "validation", "Validation")
    if not isinstance(raw, list):
        return []

    findings = []
    for item in raw:
        if not isinstance(item, dict):
            continue

        message = single_line(get_value(item, "message", "Message"))
        if not message:
            continue

        findings.append(
            {
                "severity": single_line(get_value(item, "severity", "Severity") or "warning").lower(),
                "code": single_line(get_value(item, "code", "Code") or "validation"),
                "message": message,
            }
        )

    return findings


def parse_response():
    try:
        data = json.loads(os.environ.get("UPLOAD_JSON", ""))
    except (TypeError, json.JSONDecodeError):
        return 1

    ext_id = single_line(get_value(data, "ID", "id"))
    if not ext_id:
        return 1

    name = single_line(get_value(data, "Name", "name") or ext_id)
    version = single_line(get_value(data, "Version", "version"))
    manage_url = single_line(get_value(data, "ManageUrl", "manageUrl"))
    token_in_url = bool(get_value(data, "ManageTokenIncludedInUrl", "manageTokenIncludedInUrl"))
    validation = get_validation(data)

    gallery = (os.environ.get("GALLERY_URL") or "https://www.vsixgallery.com").rstrip("/")
    details_url = f"{gallery}/extension/{ext_id}"
    badge_path = f"/badge/{urllib.parse.quote(ext_id)}.svg"
    if version:
        badge_path += f"?v={urllib.parse.quote(version)}"
    badge_url = f"{gallery}{badge_path}"
    validation_json = json.dumps(validation, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    validation_base64 = base64.b64encode(validation_json).decode("ascii")

    for value in (
        ext_id,
        name,
        version,
        details_url,
        badge_url,
        manage_url,
        "1" if token_in_url else "0",
        validation_base64,
    ):
        print(value)

    return 0


def decode_validation():
    encoded = os.environ.get("VALIDATION_BASE64", "")
    if not encoded:
        return []

    try:
        value = base64.b64decode(encoded).decode("utf-8")
        decoded = json.loads(value)
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
        return []

    return decoded if isinstance(decoded, list) else []


def command_escape(value):
    return value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def emit_annotations():
    for finding in decode_validation():
        severity = finding.get("severity", "warning")
        command = "notice" if severity == "info" else "warning"
        code = command_escape(single_line(finding.get("code", "validation")))
        message = command_escape(single_line(finding.get("message", "")))
        if message:
            print(f"::{command} title=VSIX validation ({code})::{message}")


def markdown_escape(value):
    return single_line(value).replace("|", r"\|")


def render_summary():
    findings = decode_validation()
    if not findings:
        return

    print("### Validation warnings")
    print("")
    print("The extension was published, but the gallery found the following quality issues:")
    print("")
    print("| Check | Message |")
    print("|---|---|")
    for finding in findings:
        code = markdown_escape(finding.get("code", "validation"))
        message = markdown_escape(finding.get("message", ""))
        print(f"| `{code}` | {message} |")
    print("")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("parse", "annotations", "summary"))
    args = parser.parse_args()

    if args.command == "parse":
        return parse_response()
    if args.command == "annotations":
        emit_annotations()
    else:
        render_summary()
    return 0


if __name__ == "__main__":
    sys.exit(main())
