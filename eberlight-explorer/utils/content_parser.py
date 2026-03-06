"""마크다운, YAML, BibTeX 파일을 위한 콘텐츠 파싱 유틸리티."""

import os
import re
import yaml


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def load_yaml(filename: str) -> dict:
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    filepath = os.path.join(data_dir, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def read_local_file(relative_path: str) -> str | None:
    filepath = os.path.join(REPO_ROOT, relative_path)
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def extract_title(markdown_text: str) -> str:
    for line in markdown_text.split("\n"):
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return "Untitled"


def extract_metadata_table(markdown_text: str) -> dict:
    """첫 번째 마크다운 테이블(메타데이터 섹션)에서 키-값 쌍을 추출합니다."""
    metadata = {}
    in_table = False
    for line in markdown_text.split("\n"):
        line = line.strip()
        if line.startswith("|") and "---" not in line:
            parts = [p.strip() for p in line.split("|")]
            parts = [p for p in parts if p]
            if len(parts) >= 2:
                key = re.sub(r"\*\*", "", parts[0]).strip()
                val = re.sub(r"\*\*", "", parts[1]).strip()
                if key and val and key.lower() not in ("field", "item"):
                    metadata[key] = val
                    in_table = True
        elif in_table and not line.startswith("|"):
            break
    return metadata


def extract_section(markdown_text: str, section_name: str,
                     aliases: list[str] | None = None) -> str | None:
    """특정 ## 제목 아래의 콘텐츠를 추출합니다.

    Args:
        markdown_text: 전체 마크다운 콘텐츠.
        section_name: 검색할 기본 제목 (부분 문자열 매칭).
        aliases: 기본 제목을 찾지 못했을 때 시도할 대체 제목 부분 문자열.
    """
    names_to_try = [section_name] + (aliases or [])
    for name in names_to_try:
        lines = markdown_text.split("\n")
        capturing = False
        result = []
        for line in lines:
            if line.strip().startswith("## ") and name.lower() in line.lower():
                capturing = True
                continue
            elif line.strip().startswith("## ") and capturing:
                break
            elif capturing:
                result.append(line)
        if result:
            return "\n".join(result).strip()
    return None


def extract_tldr(markdown_text: str) -> str | None:
    return extract_section(markdown_text, "TL;DR")


def _clean_bibtex_value(val: str) -> str:
    """BibTeX 필드 값 정리 — LaTeX 중괄호 및 특수 문자 제거."""
    # Remove outer braces: {TomoGAN} -> TomoGAN
    val = re.sub(r'\{([^}]*)\}', r'\1', val)
    # Handle LaTeX accents: {\"u} -> ü, {\u{g}} -> g, etc.
    val = val.replace('\\"u', 'ü').replace('\\"o', 'ö').replace('\\"a', 'ä')
    val = val.replace("\\'e", 'é').replace("\\'a", 'á')
    # Clean remaining backslash commands
    val = re.sub(r'\\[a-zA-Z]+\{?', '', val)
    # Remove stray braces
    val = val.replace('{', '').replace('}', '')
    return val.strip()


def parse_bibtex(bibtex_text: str) -> list[dict]:
    """항목 목록을 반환하는 견고한 BibTeX 파서."""
    entries = []
    # Split by @ entries
    raw_entries = re.split(r'(?=@\w+\{)', bibtex_text)

    for raw in raw_entries:
        raw = raw.strip()
        if not raw.startswith('@'):
            continue

        # Extract type and key
        header_match = re.match(r'@(\w+)\{([^,]+),', raw)
        if not header_match:
            continue

        entry_type = header_match.group(1)
        entry_key = header_match.group(2).strip()

        # Extract fields using a more robust pattern
        # Match: field = {value that can span lines and contain nested braces}
        fields = {}
        # Find all field=value pairs
        field_pattern = re.compile(
            r'(\w+)\s*=\s*\{((?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*)\}',
            re.DOTALL
        )
        for fm in field_pattern.finditer(raw):
            field_name = fm.group(1).lower()
            field_value = _clean_bibtex_value(fm.group(2).strip())
            fields[field_name] = field_value

        entries.append({
            "type": entry_type,
            "key": entry_key,
            **fields,
        })

    return entries
