"""classmark -- CAPCO-style banner builder. PLACEHOLDERS ONLY.

We do not ship real classification markings. Operators on cleared systems fill
in the values at runtime. This library validates *shape*, not content.

Reference: ODNI CAPCO Implementation Manual (unclassified, public).
"""
from __future__ import annotations

from dataclasses import dataclass, field

VALID_LEVELS = ["UNCLASSIFIED", "CONFIDENTIAL", "SECRET", "TOP SECRET"]
VALID_FGI = ["FGI"]  # Foreign Government Information marker placeholder


@dataclass
class ClassificationBanner:
    """Builds a CAPCO-shape banner. Validation of *form*, not content."""

    level: str = "UNCLASSIFIED"  # operator-supplied
    # operator-supplied SCI compartments
    sci: list[str] = field(default_factory=list)
    # SAP program IDs (operator-supplied)
    sap: list[str] = field(default_factory=list)
    # NOFORN/REL TO/ORCON etc. (operator-supplied)
    dissem: list[str] = field(default_factory=list)
    # Non-IC dissem (FOUO/CUI etc.)
    nonic: list[str] = field(default_factory=list)

    def __post_init__(self):
        # Coerce None list fields to empty lists so render/validate are safe
        if self.sci is None:
            self.sci = []
        if self.sap is None:
            self.sap = []
        if self.dissem is None:
            self.dissem = []
        if self.nonic is None:
            self.nonic = []
        if not isinstance(self.level, str):
            raise TypeError(
                "ClassificationBanner.level must be a str, "
                f"got {type(self.level).__name__}"
            )

    def validate(self) -> tuple[bool, list[str]]:
        errs: list[str] = []
        if self.level not in VALID_LEVELS:
            errs.append(
                f"Invalid base level: {self.level}."
                f" Expected one of {VALID_LEVELS}."
            )
        # Higher levels with no markings is a smell, but not invalid shape
        if self.level == "UNCLASSIFIED" and (self.sci or self.sap):
            errs.append("UNCLASSIFIED cannot carry SCI/SAP compartments")
        return (len(errs) == 0, errs)

    def render(self) -> str:
        """Render the banner-line string. Operator content is passed through."""
        # Filter out any None entries that callers may have inserted post-init
        sci = [s for s in self.sci if s is not None]
        sap = [s for s in self.sap if s is not None]
        dissem = [s for s in self.dissem if s is not None]
        nonic = [s for s in self.nonic if s is not None]

        parts = [self.level]
        if sci:
            parts.append("/".join(sci))
        if sap:
            parts.append("SAR-" + "/".join(sap))
        suffix = []
        if dissem:
            suffix.extend(dissem)
        if nonic:
            suffix.extend(nonic)
        line = "//".join(parts)
        if suffix:
            line += "//" + "/".join(suffix)
        return line

    @classmethod
    def placeholder(cls) -> "ClassificationBanner":
        """Returns a safe, public-release placeholder."""
        return cls(level="UNCLASSIFIED", dissem=["FOR PUBLIC RELEASE"])
