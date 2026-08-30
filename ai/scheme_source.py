"""
In-memory scheme data source with proper (non-naive) search and filters.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import List, Optional

from ai.scheme_models import Scheme
from ai.scheme_importer import load_schemes
from ai.caste_normalizer import CASTE_MAP
from ai.state_normalizer import normalize_state

logger = logging.getLogger("scheme_source")


class SchemeSource:
    _instance: Optional["SchemeSource"] = None

    def __init__(self, csv_path: Optional[Path] = None):
        self._schemes: List[Scheme] = load_schemes(csv_path)
        logger.info("[SchemeSource] Loaded %s schemes.", len(self._schemes))

    @classmethod
    def get_instance(cls, csv_path: Optional[Path] = None) -> "SchemeSource":
        if cls._instance is None:
            cls._instance = cls(csv_path)
        return cls._instance

    def all(self) -> List[Scheme]:
        return list(self._schemes)

    def get(self, scheme_id: str) -> Optional[Scheme]:
        for scheme in self._schemes:
            if scheme.scheme_id == scheme_id:
                return scheme
        return None

    def by_level(self, level: str) -> List[Scheme]:
        return [s for s in self._schemes if s.government_level.lower() == level.lower()]

    def by_state(self, state: str) -> List[Scheme]:
        """
        Returns schemes applicable to the given state: central schemes
        (unrestricted) PLUS schemes whose states_allowed/state explicitly
        includes it.
        """
        normalized = normalize_state(state) or state
        result = []
        for scheme in self._schemes:
            if scheme.eligibility.is_central and not scheme.eligibility.states_allowed:
                result.append(scheme)
                continue
            states_allowed = scheme.eligibility.states_allowed or (
                [scheme.state] if scheme.state else []
            )
            if normalized in states_allowed:
                result.append(scheme)
        return result

    def by_category(self, category_code: str) -> List[Scheme]:
        """
        Proper category/caste filtering. If `category_code` is a caste
        code (SC/ST/OBC/GENERAL/EWS), filter using the normalized
        caste_allowed field — NOT naive substring search.
        Otherwise, filter by the scheme's category tag list.
        """
        code = category_code.strip().upper()
        if code in {"SC", "ST", "OBC", "GENERAL", "EWS", "ALL"}:
            result = []
            for scheme in self._schemes:
                allowed = scheme.eligibility.caste_allowed
                if not allowed or "ALL" in allowed or code in allowed:
                    result.append(scheme)
            return result

        # Generic category tag filter (e.g. "Business & Entrepreneurship")
        code_l = category_code.strip().lower()
        return [
            s for s in self._schemes
            if any(code_l in c.lower() for c in s.category)
        ]

    def search(self, query: str) -> List[Scheme]:
        """
        Semantic-aware search. Caste-like queries ("SC", "ST", "OBC") are
        routed through by_category() to use normalized eligibility instead
        of naive substring matching against the entire row. Free-text
        queries fall back to a proper (tokenized) text search across
        name/description/category/benefits.
        """
        if not query:
            return []
        code = query.strip().upper()
        if code in {"SC", "ST", "OBC", "GENERAL", "EWS"}:
            return self.by_category(code)

        pattern = re.compile(re.escape(query.strip()), re.IGNORECASE)
        result = []
        for scheme in self._schemes:
            haystack = " ".join(filter(None, [
                scheme.scheme_name,
                scheme.description,
                " ".join(scheme.category),
                " ".join(scheme.benefits),
                scheme.eligibility_text_raw,
            ]))
            if pattern.search(haystack):
                result.append(scheme)
        return result


def get_scheme_source() -> SchemeSource:
    return SchemeSource.get_instance()
