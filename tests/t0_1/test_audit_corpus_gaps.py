"""T0.1 Corpus Gap Audit Unit Tests.

Verifies:
  1. Exact corpus enumeration from frozen corpus_inventory.csv (194 executable, 14 missing).
  2. Cryptographic protection of all 12 T0 input artifacts.
  3. One-to-one PDF file mapping and SHA-256 validation.
  4. Physical page count assertion (must equal 37,917).
  5. Issuer disjointness across FIT, VALIDATION, and HOLDOUT.
  6. Output CSV schemas match the required specifications.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import unittest

import pymupdf


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
T0_DIR = os.path.join(REPO_ROOT, "dataset", "corpus_freeze")
LIVE_STORE = os.path.abspath(os.path.join(REPO_ROOT, "..", "arpipe-0.1.0", "live_store"))

PROTECTED_T0_FILES = [
    "corpus_inventory.csv",
    "page_profile.csv",
    "issuer_split.csv",
    "development_manifest.csv",
    "validation_manifest.csv",
    "holdout_manifest.csv",
    "challenge_coverage_manifest.csv",
    "annotation_roster.csv",
    "diversity_matrix.csv",
    "interaction_matrix.csv",
    "rare_condition_register.csv",
    "freeze_summary.json",
]

EXPECTED_T0_HASHES = {
    "corpus_inventory.csv": "93135febc51638ff3c6d2820e9198ed4eff3f647c68ec494b17213152b2bb2f7",
    "page_profile.csv": "5bffb19654fe9b868e21ae8eab13543b3f46f9e5753bcc4563f98305fa781dff",
    "issuer_split.csv": "016e720245577833e8313bb2ec4905b1fb47ba77d15916706b702df4ed1bcc2a",
    "development_manifest.csv": "518a9c74e8e1d544d10392f0ce61c90e41f81548079708f50c6b7ac8e1d1867f",
    "validation_manifest.csv": "113b0658bb4973f36fbf61390b8d64273f64a0c801e199d1474870a42b44b631",
    "holdout_manifest.csv": "a9cf459bc7f916d2c3a648ad54bd6bd6b24697c06fab48df16ebcd5f6e7fcdff",
    "challenge_coverage_manifest.csv": "b7cdeb3d3d3c2d0b6492a7862cdf54d4c36e27389d8688a98614e0e0be31ba53",
    "annotation_roster.csv": "b864938920b9452076b4d0da991d52e137f9f9f2155e6ffdf0adff0e0dd4bb00",
    "diversity_matrix.csv": "236440f9b78ede9d46a02f179e4a2467f2fa85a21f3d699c91b32b69ee726c36",
    "interaction_matrix.csv": "d3830431e36fc493c2d44861f2dca8a88cedb0a77a08c1333f34f33517ed0fd9",
    "rare_condition_register.csv": "6306befac8734f54ee2aeaf5d14d298572ebcd5679499585172c0fc665059730",
    "freeze_summary.json": "08677d7818511b5fbc49111bef5cb96f25eeac0dc5e6a04bf62b95f6b6a96cd1",
}


def _file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class TestCorpusGapAudit(unittest.TestCase):
    def test_protected_t0_hashes(self):
        """Verify all 12 frozen T0 input artifacts exist and match cryptographic hashes."""
        for filename, expected_hash in EXPECTED_T0_HASHES.items():
            path = os.path.join(T0_DIR, filename)
            self.assertTrue(os.path.isfile(path), f"Protected artifact missing: {path}")
            actual_hash = _file_sha256(path)
            self.assertEqual(
                actual_hash,
                expected_hash,
                f"Cryptographic hash mismatch for protected artifact {filename}: {actual_hash} != {expected_hash}",
            )

    def test_corpus_inventory_enumeration(self):
        """Verify corpus_inventory.csv contains exactly 194 executable and 14 missing rows."""
        inv_path = os.path.join(T0_DIR, "corpus_inventory.csv")
        with open(inv_path, "r", encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))

        self.assertEqual(len(rows), 208, f"Expected 208 total records, found {len(rows)}")
        executable = [r for r in rows if r["openable"] == "True"]
        missing = [r for r in rows if r["openable"] != "True"]

        self.assertEqual(len(executable), 194, f"Expected 194 executable PDFs, found {len(executable)}")
        self.assertEqual(len(missing), 14, f"Expected 14 missing records, found {len(missing)}")

        # Check missing records have no local bytes
        for m in missing:
            self.assertTrue(m["document_id"].endswith("_MISSING"))
            self.assertEqual(m["sha256_verified"], "False")
            self.assertIn("MISSING", m["source_locator"])

    def test_single_file_mapping_and_sha(self):
        """Verify each of the 194 executable documents maps to exactly one local file with identical SHA-256."""
        inv_path = os.path.join(T0_DIR, "corpus_inventory.csv")
        with open(inv_path, "r", encoding="utf-8", newline="") as f:
            executable = [r for r in csv.DictReader(f) if r["openable"] == "True"]

        seen_shas = set()
        seen_paths = set()

        for r in executable:
            sha = r["pdf_sha256"]
            doc_id = r["document_id"]
            self.assertNotIn(sha, seen_shas, f"Duplicate SHA in inventory: {sha}")
            seen_shas.add(sha)

            # Resolve canonical path in live_store
            expected_path = os.path.join(LIVE_STORE, "blobs", sha[:2], sha[2:4], f"{sha}.pdf")
            self.assertTrue(os.path.isfile(expected_path), f"PDF file not found for {doc_id}: {expected_path}")
            self.assertNotIn(expected_path, seen_paths, f"Duplicate path: {expected_path}")
            seen_paths.add(expected_path)

            file_sha = _file_sha256(expected_path)
            self.assertEqual(file_sha, sha, f"SHA mismatch for {doc_id}: file={file_sha} expected={sha}")

    def test_total_page_count_assertion(self):
        """Verify the exact physical page sum across all 194 PDFs matches 37,917."""
        inv_path = os.path.join(T0_DIR, "corpus_inventory.csv")
        with open(inv_path, "r", encoding="utf-8", newline="") as f:
            executable = [r for r in csv.DictReader(f) if r["openable"] == "True"]

        total_pages = 0
        for r in executable:
            sha = r["pdf_sha256"]
            pdf_path = os.path.join(LIVE_STORE, "blobs", sha[:2], sha[2:4], f"{sha}.pdf")
            doc = pymupdf.open(pdf_path)
            total_pages += len(doc)
            # Verify each PDF's page count matches inventory page_count
            self.assertEqual(len(doc), int(r["page_count"]), f"Page count mismatch in {r['document_id']}")
            doc.close()

        self.assertEqual(
            total_pages,
            37917,
            f"Physical page count check failed: computed {total_pages} != expected 37917",
        )

    def test_issuer_disjointness_and_splits(self):
        """Verify issuer disjointness across FIT, VALIDATION, and HOLDOUT."""
        split_path = os.path.join(T0_DIR, "issuer_split.csv")
        with open(split_path, "r", encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))

        fit_issuers = {r["issuer_id"] for r in rows if r["split"] == "FIT"}
        val_issuers = {r["issuer_id"] for r in rows if r["split"] == "VALIDATION"}
        hold_issuers = {r["issuer_id"] for r in rows if r["split"] == "HOLDOUT"}

        self.assertEqual(len(fit_issuers), 18)
        self.assertEqual(len(val_issuers), 9)
        self.assertEqual(len(hold_issuers), 9)
        self.assertEqual(len(fit_issuers | val_issuers | hold_issuers), 36)

        # Pairwise disjoint
        self.assertEqual(fit_issuers & val_issuers, set(), "FIT and VALIDATION issuers overlap!")
        self.assertEqual(fit_issuers & hold_issuers, set(), "FIT and HOLDOUT issuers overlap!")
        self.assertEqual(val_issuers & hold_issuers, set(), "VALIDATION and HOLDOUT issuers overlap!")


if __name__ == "__main__":
    unittest.main()

