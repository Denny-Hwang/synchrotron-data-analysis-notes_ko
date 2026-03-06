#!/usr/bin/env python3
"""싱크로트론 데이터 분석 노트 저장소를 스캔하고 YAML 인덱스를 검증/재구축합니다."""

import os
import sys
import yaml

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def validate_file_references():
    """YAML 카탈로그에서 참조된 모든 파일이 실제로 존재하는지 확인합니다."""
    errors = []

    yaml_files = [
        "content_index.yaml",
        "modality_metadata.yaml",
        "method_taxonomy.yaml",
        "publication_catalog.yaml",
        "tool_catalog.yaml",
        "cross_references.yaml",
    ]

    for yf in yaml_files:
        filepath = os.path.join(DATA_DIR, yf)
        if not os.path.exists(filepath):
            errors.append(f"누락된 YAML 파일: {yf}")
            continue

        with open(filepath, "r") as f:
            data = yaml.safe_load(f)

        paths = _extract_paths(data)
        for p in paths:
            full_path = os.path.join(REPO_ROOT, p)
            if not os.path.exists(full_path):
                errors.append(f"[{yf}] 누락된 파일: {p}")

    return errors


def _extract_paths(obj, paths=None):
    """YAML 구조에서 파일 경로 문자열을 재귀적으로 추출합니다."""
    if paths is None:
        paths = []
    if isinstance(obj, dict):
        for key, val in obj.items():
            if key in ("path", "file", "readme", "data_format", "ai_ml",
                       "architecture", "pros_cons", "reproduction",
                       "reverse_eng", "workflow", "catalog"):
                if isinstance(val, str) and "/" in val:
                    paths.append(val)
            else:
                _extract_paths(val, paths)
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, str) and "/" in item and item.endswith((".md", ".ipynb", ".bib")):
                paths.append(item)
            else:
                _extract_paths(item, paths)
    return paths


def count_repo_files():
    """저장소의 총 마크다운 및 노트북 파일 수를 계산합니다."""
    counts = {"md": 0, "ipynb": 0, "bib": 0}
    for root, dirs, files in os.walk(REPO_ROOT):
        if ".git" in root or "eberlight-explorer" in root:
            continue
        for f in files:
            ext = os.path.splitext(f)[1].lstrip(".")
            if ext in counts:
                counts[ext] += 1
    return counts


if __name__ == "__main__":
    print("=" * 60)
    print("eBERlight 탐색기 - 인덱스 검증기")
    print("=" * 60)

    counts = count_repo_files()
    print(f"\n저장소 파일 수: {counts}")

    errors = validate_file_references()
    if errors:
        print(f"\n❌ {len(errors)}개의 오류 발견:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("\n✅ 모든 파일 참조가 유효합니다!")
        sys.exit(0)
