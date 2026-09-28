"""
JSON Exporter for Phase 9 Reporting & Export Center.
Generates structured JSON exports for programmatic access and data pipelines.
"""
import json
import os
from typing import Any, Dict


def generate_json_report(data: Dict[str, Any], output_path: str) -> int:
    """
    Generate structured JSON report file and write to output_path.
    Returns file size in bytes.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return os.path.getsize(output_path)
