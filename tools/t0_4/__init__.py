"""T0.4 preregistration and setup-only benchmark support.

This package deliberately exposes no command that executes an OCR engine.
Benchmark execution belongs in a later, separately authorized worktree.
"""

from .core import BASE_COMMIT, NOT_AVAILABLE, NOT_YET_ANNOTATED, NOT_YET_RENDERED

__all__ = ["BASE_COMMIT", "NOT_AVAILABLE", "NOT_YET_ANNOTATED", "NOT_YET_RENDERED"]
