"""retrieval tests — corpus chunking, hybrid search, compression, citations."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from retrieval import Retriever, compress, load_corpus, verify_citation  # noqa: E402

CORPUS = os.path.join(os.path.dirname(__file__), "..", "corpus")


class TestCorpus(unittest.TestCase):
    def test_chunks_carry_doc_lines_and_effective_date(self):
        chunks = load_corpus(CORPUS)
        self.assertGreater(len(chunks), 10)
        for c in chunks:
            self.assertTrue(c.doc.endswith(".md"))
            self.assertLessEqual(c.start_line, c.end_line)
        v4 = [c for c in chunks if c.doc == "procurement-policy-v4-amendment.md"]
        self.assertTrue(all(c.effective_date == "2026-04-01" for c in v4))


class TestSearch(unittest.TestCase):
    def setUp(self):
        self.r = Retriever(CORPUS)

    def test_delegation_query_finds_delegation_doc_first(self):
        hits = self.r.search("approval limits by role Managers Directors", top_k=3)
        self.assertEqual(hits[0][0].doc, "delegation-of-authority.md")

    def test_software_threshold_query_surfaces_both_policy_versions(self):
        hits = self.r.search("software purchases threshold CTO approval amendment "
                             "supersedes", top_k=3)
        docs = {c.doc for c, _ in hits}
        self.assertIn("procurement-policy-v4-amendment.md", docs)
        self.assertIn("procurement-policy-v3.md", docs)

    def test_scores_expose_the_hybrid_machinery(self):
        (chunk, scores), *_ = self.r.search("unknown vendors escalated onboarding")
        self.assertIn("bm25_rank", scores)
        self.assertIn("kw_rank", scores)
        self.assertIn("rrf", scores)


class TestCompressionAndCitations(unittest.TestCase):
    def setUp(self):
        self.chunks = load_corpus(CORPUS)

    def test_compress_keeps_verbatim_sentences_within_limit(self):
        chunk = next(c for c in self.chunks
                     if c.doc == "delegation-of-authority.md"
                     and "Managers" in c.text)
        out = compress(chunk, "approval limits Managers", max_sentences=2)
        self.assertTrue(out)
        self.assertLessEqual(out.count("."), 3)
        # every kept sentence must be quotable — verbatim modulo whitespace
        self.assertTrue(verify_citation(
            {"doc": chunk.doc, "quote": out.split(". ")[0]}, CORPUS))

    def test_verify_citation_rejects_fabricated_quotes(self):
        good = {"doc": "delegation-of-authority.md",
                "quote": "Managers: up to and including $10,000."}
        fake = {"doc": "delegation-of-authority.md",
                "quote": "Managers: up to and including $99,000."}
        missing = {"doc": "no-such-doc.md", "quote": "anything"}
        empty = {"doc": "delegation-of-authority.md", "quote": ""}
        self.assertTrue(verify_citation(good, CORPUS))
        self.assertFalse(verify_citation(fake, CORPUS))
        self.assertFalse(verify_citation(missing, CORPUS))
        self.assertFalse(verify_citation(empty, CORPUS))


if __name__ == "__main__":
    unittest.main()
