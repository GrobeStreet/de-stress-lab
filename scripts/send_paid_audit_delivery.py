#!/usr/bin/env python3
"""Send a bounded audit package to the private delivery endpoint."""

from __future__ import annotations

import base64
import json
import mimetypes
import os
import urllib.error
import urllib.request
from pathlib import Path

ALLOWED_FILES = (
    "audit.json",
    "audit.md",
    "delivery-manifest.json",
    "execution.md",
    "scope.md",
)
MAX_DELIVERY_BYTES = 5_000_000


def build_payload(
    delivery: Path,
    repository: str,
    order_reference: str,
) -> dict[str, object]:
    """Build a bounded package without reading arbitrary delivery paths."""
    files: list[dict[str, str]] = []
    total_bytes = 0
    for name in ALLOWED_FILES:
        path = delivery / name
        if not path.is_file():
            continue
        content = path.read_bytes()
        total_bytes += len(content)
        if total_bytes > MAX_DELIVERY_BYTES:
            raise ValueError("Delivery package exceeds the 5 MB safety limit")
        files.append(
            {
                "name": name,
                "content_type": mimetypes.guess_type(name)[0]
                or "application/octet-stream",
                "content_base64": base64.b64encode(content).decode("ascii"),
            }
        )
    required = {"delivery-manifest.json", "execution.md", "scope.md"}
    if not required.issubset({file["name"] for file in files}):
        raise ValueError("Delivery package is missing required records")
    return {
        "order_reference": order_reference,
        "repository_url": repository,
        "files": files,
    }


def send(payload: dict[str, object]) -> None:
    """Send the package using the private shared callback token."""
    url = os.environ["AUDIT_DELIVERY_URL"]
    token = os.environ["AUDIT_DELIVERY_TOKEN"]
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "de-stress-audit-workflow",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            if response.status != 200:
                raise RuntimeError(f"Delivery endpoint returned {response.status}")
    except urllib.error.HTTPError as error:
        raise RuntimeError(
            f"Delivery endpoint returned {error.code}"
        ) from error


def main() -> None:
    delivery = Path(os.environ.get("DELIVERY_DIRECTORY", "delivery"))
    payload = build_payload(
        delivery,
        os.environ["REPOSITORY_URL"],
        os.environ["ORDER_REFERENCE"],
    )
    send(payload)
    print("Customer delivery accepted.")


if __name__ == "__main__":
    main()
