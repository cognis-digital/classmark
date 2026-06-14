"""classmark -- CAPCO-shape banner + portion-marking library.

We ship the SHAPE of CAPCO markings (banner-line builder, portion-mark
validator, control-marking placeholder table). We do NOT ship real
classification content. Operators on cleared systems supply real values.

Reference: ODNI CAPCO Implementation Manual (public reference doc).
Reference: 32 CFR Part 2002 (CUI Program).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from cognis_mil import Finding, ScanResult, Severity

# CUI categories from National Archives CUI Registry (public)
CUI_CATEGORIES = {
    "CTI": "Critical Infrastructure Information",
    "PRVCY": "Privacy / PII",
    "PROCURE": "Procurement and Acquisition",
    "TAX": "Tax Information",
    "EXPT": "Export Control",
    "LEGAL": "Legal",
    "OPSEC": "Operations Security",
    # ... operator extends from full CUI registry
}

DISSEM_MARKERS = {
    "NOFORN": "Not Releasable to Foreign Nationals",
    "ORCON": "Originator Controlled",
    "REL TO": "Releasable To [list of countries]",
    "FGI": "Foreign Government Information",
    "PROPIN": "Proprietary Information Involved",
    "RELIDO": "Releasable by Information Disclosure Officials",
    "DISPLAY ONLY": "Display Only [list of countries]",
    # placeholders -- operators add per their ATO
}

_BANNER_PREFIXES = (
    "UNCLASSIFIED",
    "CONFIDENTIAL",
    "SECRET",
    "TOP SECRET",
    "CUI",
    "UNCLASSIFIED//",
)

_PORTION_RE = re.compile(r"\(([A-Z]{1,4})(?://[A-Z0-9 ,/]+)?\)")

_SCANNED_SUFFIXES = frozenset((".txt", ".md", ".html", ".docx", ".json"))


def validate_portion_mark(mark: str) -> tuple[bool, str]:
    """Validate a portion mark of the form (X) or (X//Y).

    Accepted top-level: U, C, S, TS (CAPCO short forms).
    """
    if not isinstance(mark, str):
        return False, f"Expected a string, got {type(mark).__name__}"
    m = mark.strip()
    if not m:
        return False, "Portion mark must not be empty"
    if not (m.startswith("(") and m.endswith(")")):
        return False, "Portion marks must be in parentheses: (U), (S//NF), etc."
    inner = m[1:-1].strip()
    if not inner:
        return False, "Portion mark must not be empty inside parentheses"
    parts = inner.split("//")
    top = parts[0].strip()
    VALID_TOP = {"U", "C", "S", "TS", "UN", "CUI"}
    if top not in VALID_TOP:
        return False, f"Top-level mark must be one of {VALID_TOP}, got '{top}'"
    return True, "Valid shape"


def detect_banners(text: str) -> list[tuple[int, str]]:
    """Find lines that look like CAPCO banners. Returns [(line_no, line)].

    Returns an empty list for None or non-string input.
    """
    if not isinstance(text, str) or not text:
        return []
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if s.startswith(_BANNER_PREFIXES):
            out.append((i, s))
    return out


def detect_portion_marks(text: str) -> list[tuple[int, str]]:
    """Find portion marks (heuristic). Public test data only.

    Returns an empty list for None or non-string input.
    """
    if not isinstance(text, str) or not text:
        return []
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        for m in _PORTION_RE.finditer(line):
            out.append((i, m.group(0)))
    return out


def scan(target=".", **opts):
    """Scan a directory/file for banner-line consistency.

    Raises SystemExit(2) with a message on stderr if *target* does not exist.
    """
    r = ScanResult(tool_name="classmark", tool_version="0.1.0")

    if target is None:
        print("classmark: error: target must not be None", file=sys.stderr)
        sys.exit(2)

    p = Path(str(target))

    if not p.exists():
        print(
            f"classmark: error: target does not exist: {target}",
            file=sys.stderr,
        )
        sys.exit(2)

    files: list[Path] = []
    if p.is_dir():
        files = [
            f
            for f in p.rglob("*")
            if f.is_file() and f.suffix in _SCANNED_SUFFIXES
        ]
    elif p.is_file():
        files = [p]
    else:
        # Special filesystem node (socket, device, etc.) -- treat as empty scan
        print(
            f"classmark: warning: target is neither a file nor a directory: {target}",
            file=sys.stderr,
        )

    r.items_scanned = len(files)
    banner_set: set[str] = set()

    for f in files:
        try:
            text = f.read_text(errors="ignore")
        except OSError as exc:
            print(
                f"classmark: warning: could not read {f}: {exc}",
                file=sys.stderr,
            )
            continue

        banners = detect_banners(text)
        portions = detect_portion_marks(text)

        # 1. Document with portion marks should have a banner
        if portions and not banners:
            r.add(
                Finding(
                    "CM-NOBANNER",
                    Severity.HIGH,
                    f"{f.name}: has portion marks but no banner line",
                    location=str(f),
                    remediation="Add a banner line at top + bottom of the doc",
                )
            )

        # 2. Validate portion-mark shape (cap at 50 to avoid runaway output)
        for ln, pm in portions[:50]:
            ok, msg = validate_portion_mark(pm)
            if not ok:
                r.add(
                    Finding(
                        "CM-BADPM",
                        Severity.MODERATE,
                        f"{f.name}:{ln}: invalid portion-mark shape: {pm}",
                        location=f"{f}:{ln}",
                        remediation=msg,
                    )
                )

        # 3. Inconsistent banners within one doc
        doc_banners = {b for _, b in banners}
        if len(doc_banners) > 1:
            r.add(
                Finding(
                    "CM-INCONSISTENT",
                    Severity.HIGH,
                    f"{f.name}: multiple distinct banner lines",
                    description=f"Found {len(doc_banners)} different banners",
                    location=str(f),
                    remediation=(
                        "A single document should have one consistent banner"
                    ),
                )
            )
        banner_set.update(doc_banners)

    r.meta = {"unique_banners_found": sorted(banner_set)}
    r.finalize()
    return r
