"""Build deterministic T0.4 setup artifacts without executing a benchmark."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.t0_4.core import (
    build_manifest,
    config_hash_manifest,
    validate_config_set,
    verify_base_ancestor,
    verify_protected_paths_unchanged,
    write_canonical_json,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/t0_4/benchmark_manifest.json"),
        help="Repository-relative deterministic manifest destination.",
    )
    parser.add_argument(
        "--config-hashes",
        type=Path,
        default=Path("artifacts/t0_4/config_hashes.json"),
        help="Repository-relative deterministic config-hash destination.",
    )
    args = parser.parse_args()
    repo_root = REPO_ROOT
    verify_base_ancestor(repo_root)
    verify_protected_paths_unchanged(repo_root)
    validate_config_set(repo_root)
    manifest = build_manifest(repo_root)
    write_canonical_json(repo_root / args.output, manifest)
    write_canonical_json(repo_root / args.config_hashes, config_hash_manifest(repo_root))
    counts = manifest["derived_counts"]
    print(
        "T0.4 setup artifacts written; "
        f"Track-A units={counts['track_a_units']}, "
        f"Track-B records={counts['track_b_units']}, "
        f"unavailable inputs={counts['input_unavailable_documents']}."
    )
    print("No PDFs opened, no pages rendered, no engines probed, and no benchmark executed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
