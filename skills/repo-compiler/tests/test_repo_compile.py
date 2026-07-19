"""repo-compiler tests — pure functions, offline fixtures, no network ever."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from repo_compile import (  # noqa: E402
    build_graph, build_skill, classify, needs_refresh, slugify, validate_graph,
)

FIXTURE = {
    "repo": "example/awesome-agents",
    "sha": "a" * 40,
    "default_branch": "main",
    "stars": 12345,
    "description": "A curated collection of agent tools.",
    "topics": ["mcp", "ai-agents"],
    "license": "MIT",
    "pushed_at": "2026-07-01T00:00:00Z",
    "html_url": "https://github.com/example/awesome-agents",
    "readme": (
        "# Awesome Agents\n\nIntro text with a [link](https://example.com/a).\n\n"
        "## Servers\n\nMore [evidence](https://example.com/b).\n\n"
        "### Filesystem\n\ndetail\n\n"
        "## Clients\n\n```md\n# not-a-heading (fenced)\n[not-a-link](https://x.y)\n```\n"
    ),
}


# --- graph extraction ------------------------------------------------------

def test_graph_has_repo_topics_concepts_evidence():
    g = build_graph(FIXTURE, "why")
    types = {n["type"] for n in g["nodes"]}
    assert types == {"repo", "topic", "concept", "evidence"}
    labels = [n["label"] for n in g["nodes"] if n["type"] == "concept"]
    assert labels == ["Awesome Agents", "Servers", "Filesystem", "Clients"]


def test_code_fences_do_not_pollute_graph():
    g = build_graph(FIXTURE)
    assert all("not-a-heading" not in n["label"] for n in g["nodes"])
    assert all(n.get("source_url") != "https://x.y" for n in g["nodes"])


def test_heading_nesting_produces_part_of_chain():
    g = build_graph(FIXTURE)
    edges = {(e["from"], e["to"]) for e in g["edges"] if e["rel"] == "part_of"}
    assert ("c-filesystem", "c-servers") in edges          # h3 under h2
    assert ("c-servers", "c-awesome-agents") in edges      # h2 under h1


def test_provenance_is_sha_pinned():
    g = build_graph(FIXTURE)
    concept = next(n for n in g["nodes"] if n["type"] == "concept")
    assert f"/blob/{'a' * 40}/README.md" in concept["source_url"]
    assert g["source"]["sha"] == "a" * 40


def test_validate_passes_on_good_graph():
    assert validate_graph(build_graph(FIXTURE)) == []


def test_validate_catches_dangling_edge_and_missing_provenance():
    g = build_graph(FIXTURE)
    g["edges"].append({"from": "ghost", "to": "nowhere", "rel": "cites"})
    g["nodes"][0] = dict(g["nodes"][0], source_url="")
    errs = validate_graph(g)
    assert any("dangling" in e for e in errs)
    assert any("provenance" in e for e in errs)


# --- classification + skill contract ---------------------------------------

@pytest.mark.parametrize("desc,expected", [
    ("A curated collection of agent tools.", "curated-index"),
    ("A community driven registry service", "registry"),
    ("Open source AI engineering platform: evals, observability", "platform"),
    ("The fast, Pythonic way to build MCP servers", "framework"),
    ("The definitive roadmap to becoming an FDE", "learning-resource"),
    ("Does something unusual", "tool"),
])
def test_classify(desc, expected):
    assert classify({"description": desc, "topics": []}) == expected


def test_skill_has_honest_edges_and_pinned_source():
    s = build_skill(FIXTURE, "why we cite it")
    assert s["notGoodAt"], "every skill must carry a non-empty notGoodAt"
    assert s["kind"] == "curated-index"
    assert s["integration"]["as"] == "discovery-source"
    assert s["source"]["sha"] == "a" * 40
    assert "why we cite it" in s["useWhen"]


def test_missing_license_adds_honest_edge():
    s = build_skill(dict(FIXTURE, license=None))
    assert any("license unclear" in n for n in s["notGoodAt"])


# --- freshness --------------------------------------------------------------

def test_needs_refresh_only_on_sha_change():
    assert needs_refresh("abc", "def") is True
    assert needs_refresh("abc", "abc") is False
    assert needs_refresh(None, "abc") is True


def test_slugify_stable():
    assert slugify("PrefectHQ/fastmcp") == "prefecthq-fastmcp"
