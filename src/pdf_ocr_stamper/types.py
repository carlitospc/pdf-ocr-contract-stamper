# src/pdf_ocr_stamper/types.py
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class MatchSource(str, Enum):
    RULES_MATCH = "rules_match"              # hubo regla y anchors válidos
    RULES_FALLBACK = "rules_fallback"        # hubo regla pero se usó fallback (anchors no hallados)
    NO_RULES_MANIFEST = "no_rules_manifest"  # no hubo regla; se usó manifest.csv
    NO_RULES_DEFAULT = "no_rules_default"    # no hubo regla; se usó posición por defecto

@dataclass
class StampOutcome:
    match_source: MatchSource
    rule_name: Optional[str] = None
    reason: Optional[str] = None          # e.g., "anchors_not_found", "no_rule_matched", etc.
    pages_affected: Optional[int] = None
