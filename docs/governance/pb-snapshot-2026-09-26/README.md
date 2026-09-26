# P-B historical governance snapshot

This directory preserves the eight authorized P-B governance documents as an
immutable historical observation point. The files were extracted directly from
the committed Git tree, not copied from the mutable P-B working tree.

- **Source repository:** `D:/sem_iitk/sem9/thesis`
- **Source branch:** `pb-governance-20260926`
- **Source commit:** `15c9debefe1c43c1d5e63842eb87fa5aacf73df4`
- **Source paths:** repository-root `P-B_*.md` files listed below
- **Destination:** `docs/governance/pb-snapshot-2026-09-26/`
- **Extraction method:** `git archive` from the committed tree

| source path | destination path | source SHA-256 | destination SHA-256 | comparison |
|---|---|---|---|---|
| `P-B_AUTHOR_DECISION_PACK.md` | `docs/governance/pb-snapshot-2026-09-26/P-B_AUTHOR_DECISION_PACK.md` | `298f09449e75099fb0b220e067450475d160189281a346c004cc80122ba41783` | `298f09449e75099fb0b220e067450475d160189281a346c004cc80122ba41783` | MATCH |
| `P-B_CURRENT_AUTHOR_DECISIONS.md` | `docs/governance/pb-snapshot-2026-09-26/P-B_CURRENT_AUTHOR_DECISIONS.md` | `9a47ff25cf3e3ed65f546fbe2d62b7f14eeb148fe0240b6faba6a55a1cedb5d7` | `9a47ff25cf3e3ed65f546fbe2d62b7f14eeb148fe0240b6faba6a55a1cedb5d7` | MATCH |
| `P-B_DECISION_ID_CROSSWALK.md` | `docs/governance/pb-snapshot-2026-09-26/P-B_DECISION_ID_CROSSWALK.md` | `28e3cc505e844a727940dcc381d24015a3ad7bd4880353cfc361c699c5754641` | `28e3cc505e844a727940dcc381d24015a3ad7bd4880353cfc361c699c5754641` | MATCH |
| `P-B_DEPENDENCY_MAP.md` | `docs/governance/pb-snapshot-2026-09-26/P-B_DEPENDENCY_MAP.md` | `3b3e90c4370dc79992215942d7a661833cab3da5e7bb8a4faf79ac43b33f9c1b` | `3b3e90c4370dc79992215942d7a661833cab3da5e7bb8a4faf79ac43b33f9c1b` | MATCH |
| `P-B_FINAL_REPORT.md` | `docs/governance/pb-snapshot-2026-09-26/P-B_FINAL_REPORT.md` | `76322addb05fa9b01b394d4d6ca7c78af720919cdfcc3032e42540a4b6916374` | `76322addb05fa9b01b394d4d6ca7c78af720919cdfcc3032e42540a4b6916374` | MATCH |
| `P-B_RATIFICATION_GAP_REGISTER.md` | `docs/governance/pb-snapshot-2026-09-26/P-B_RATIFICATION_GAP_REGISTER.md` | `7f0d06d769634749a61d452fe730862f9feb4ca17c92655f271640d153279a0d` | `7f0d06d769634749a61d452fe730862f9feb4ca17c92655f271640d153279a0d` | MATCH |
| `P-B_SOURCE_COVERAGE_REGISTER.md` | `docs/governance/pb-snapshot-2026-09-26/P-B_SOURCE_COVERAGE_REGISTER.md` | `262698b3a3518e58935a95750ef4818081754ab50691e90612d1ec3755cbb714` | `262698b3a3518e58935a95750ef4818081754ab50691e90612d1ec3755cbb714` | MATCH |
| `P-B_SOURCE_MANIFEST.md` | `docs/governance/pb-snapshot-2026-09-26/P-B_SOURCE_MANIFEST.md` | `b2546c0ad108e6d5e666e50e15022add811327fd1729a9609a6a5377d5fd07bb` | `b2546c0ad108e6d5e666e50e15022add811327fd1729a9609a6a5377d5fd07bb` | MATCH |

The contemporaneous P-B worktree bytes differed from the committed-tree bytes
for the first seven files above; only `P-B_SOURCE_MANIFEST.md` matched. The
committed-tree bytes are preserved here, as required. No P-B snapshot file is a
current author decision: current governance is in
`docs/governance/CURRENT_DECISIONS.md` and its dated ratification addendum.
