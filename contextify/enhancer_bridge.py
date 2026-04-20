"""Shared prompt enhancement bridge for external integrations (e.g., VS Code extension)."""

from __future__ import annotations

import sys


def enhance_prompt(input_text: str) -> str:
    """Enhance a user prompt in a deterministic way.

    This function is intentionally lightweight and dependency-free so it can be
    called reliably from external tools.
    """
    normalized_input = " ".join(input_text.strip().split())

    if not normalized_input:
        return ""

    return "\n".join(
        [
            "You are an expert AI programming assistant. Implement the request below with production-ready code.",
            "",
            "Request:",
            normalized_input,
            "",
            "Constraints:",
            "- Preserve existing architecture and naming where possible.",
            "- Keep changes minimal, focused, and testable.",
            "- Include edge-case handling and clear error messages.",
            "- Return concise implementation notes and next steps.",
        ]
    )


def main() -> int:
    raw_input = " ".join(sys.argv[1:]).strip()

    if not raw_input:
        return 1

    print(enhance_prompt(raw_input))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
