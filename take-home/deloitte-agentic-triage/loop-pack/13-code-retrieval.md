# Source: take-home/deloitte-agentic-triage/scripts/retrieval.py

```python
#!/usr/bin/env python3
"""retrieval — hybrid retrieval with reranking, compression, and verifiable citations.

The graded pipeline the field converged on, in stdlib: BM25 lexical ranking
fused with an exact-bigram keyword ranking via reciprocal-rank fusion (the
"hybrid + rerank" baseline), contextual compression down to the sentences
that matter, and citations pinned to doc + line span whose quotes are
*verbatim-verifiable* against the corpus — an answer that can't produce a
checkable quote doesn't count as grounded.

Deliberately not here: embeddings and dense retrieval. On a six-document
policy corpus, lexical hybrid is the honest baseline; the Retriever class is
the seam where a dense index would plug in for a corpus that needs one.
"""
from __future__ import annotations

import math
import os
import re


class Chunk:
    def __init__(self, doc: str, heading: str, start_line: int, end_line: int,
                 text: str, effective_date: str | None):
        self.doc = doc
        self.heading = heading
        self.start_line = start_line
        self.end_line = end_line
        self.text = text
        self.effective_date = effective_date  # doc-level, parsed once per file

    @property
    def id(self) -> str:
        return f"{self.doc}#L{self.start_line}-L{self.end_line}"


_EFFECTIVE_RE = re.compile(r"Effective date:\s*(\d{4}-\d{2}-\d{2})")
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)")
_WORD_RE = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> list[str]:
    return _WORD_RE.findall(text.lower())


def load_corpus(corpus_dir: str) -> list[Chunk]:
    chunks: list[Chunk] = []
    for fname in sorted(os.listdir(corpus_dir)):
        if not fname.endswith(".md"):
            continue
        with open(os.path.join(corpus_dir, fname), encoding="utf-8") as f:
            lines = f.read().splitlines()
        m = _EFFECTIVE_RE.search("\n".join(lines))
        effective = m.group(1) if m else None
        heading, start, buf = "", 1, []
        for i, line in enumerate(lines, start=1):
            hm = _HEADING_RE.match(line)
            if hm:
                if buf and any(x.strip() for x in buf):
                    chunks.append(Chunk(fname, heading, start, i - 1,
                                        "\n".join(buf).strip(), effective))
                heading, start, buf = hm.group(2), i, [line]
            else:
                buf.append(line)
        if buf and any(x.strip() for x in buf):
            chunks.append(Chunk(fname, heading, start, len(lines),
                                "\n".join(buf).strip(), effective))
    return chunks


class _BM25:
    def __init__(self, chunks: list[Chunk], k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.docs = [_tokens(c.text) for c in chunks]
        self.avg_len = sum(len(d) for d in self.docs) / max(1, len(self.docs))
        self.df: dict[str, int] = {}
        for d in self.docs:
            for t in set(d):
                self.df[t] = self.df.get(t, 0) + 1
        self.n = len(self.docs)

    def score(self, query_tokens: list[str], idx: int) -> float:
        d = self.docs[idx]
        score = 0.0
        for t in query_tokens:
            tf = d.count(t)
            if not tf:
                continue
            idf = math.log(1 + (self.n - self.df[t] + 0.5) / (self.df[t] + 0.5))
            score += idf * tf * (self.k1 + 1) / (
                tf + self.k1 * (1 - self.b + self.b * len(d) / self.avg_len))
        return score


def _bigrams(tokens: list[str]) -> list[tuple]:
    return list(zip(tokens, tokens[1:]))


def _rrf(rankings: list[list[int]], k: int = 60) -> dict[int, float]:
    fused: dict[int, float] = {}
    for ranking in rankings:
        for rank, idx in enumerate(ranking, start=1):
            fused[idx] = fused.get(idx, 0.0) + 1.0 / (k + rank)
    return fused


class Retriever:
    def __init__(self, corpus_dir: str):
        self.chunks = load_corpus(corpus_dir)
        self._bm25 = _BM25(self.chunks)

    def search(self, query: str, top_k: int = 4) -> list[tuple[Chunk, dict]]:
        q = _tokens(query)
        idxs = list(range(len(self.chunks)))
        bm25_rank = sorted(idxs, key=lambda i: -self._bm25.score(q, i))
        qb = _bigrams(q)
        kw_rank = sorted(idxs, key=lambda i: -sum(
            1 for bg in qb if bg in _bigrams(_tokens(self.chunks[i].text))))
        fused = _rrf([bm25_rank, kw_rank])
        top = sorted(fused, key=lambda i: -fused[i])[:top_k]
        return [(self.chunks[i],
                 {"rrf": round(fused[i], 5),
                  "bm25_rank": bm25_rank.index(i) + 1,
                  "kw_rank": kw_rank.index(i) + 1}) for i in top]


_SENT_RE = re.compile(r"(?<=[.!?])\s+")


def compress(chunk: Chunk, query: str, max_sentences: int = 3) -> str:
    """Contextual compression: keep only the sentences that overlap the query,
    in original order, verbatim (so any of them can serve as a citation quote)."""
    body = re.sub(r"^#{1,6}\s+.*$", "", chunk.text, flags=re.MULTILINE).strip()
    sentences = [s.strip() for s in _SENT_RE.split(body.replace("\n", " ")) if s.strip()]
    q = set(_tokens(query))
    scored = [(len(q & set(_tokens(s))), i, s) for i, s in enumerate(sentences)]
    keep = sorted(sorted(scored, key=lambda t: (-t[0], t[1]))[:max_sentences],
                  key=lambda t: t[1])
    return " ".join(s for score, _, s in keep if score > 0) or (
        sentences[0] if sentences else "")


class Citation:
    def __init__(self, doc: str, lines: str, quote: str):
        self.doc, self.lines, self.quote = doc, lines, quote

    def as_dict(self) -> dict:
        return {"doc": self.doc, "lines": self.lines, "quote": self.quote}


def cite(chunk: Chunk, quote: str) -> Citation:
    return Citation(chunk.doc, f"L{chunk.start_line}-L{chunk.end_line}", quote)


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def verify_citation(citation: dict, corpus_dir: str) -> bool:
    """A citation is valid only if its quote appears verbatim (modulo
    whitespace) in the named document. No verifiable quote ⇒ not grounded."""
    path = os.path.join(corpus_dir, citation["doc"])
    if not os.path.exists(path) or not citation.get("quote"):
        return False
    with open(path, encoding="utf-8") as f:
        return _norm(citation["quote"]) in _norm(f.read())

```
