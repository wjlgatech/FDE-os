"""hub_query tests — offline fixture registry, no filesystem coupling to generated artifacts."""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from hub_query import diagnose, find, load_registry, main, render_skill  # noqa: E402


def skill(name, kind, one, use=(), stars=100):
    return {
        "id": f"skill-{name.replace('/', '-')}", "name": name, "kind": kind, "oneLine": one,
        "stars": stars, "license": "MIT", "notGoodAt": ["something honest"],
        "useWhen": list(use),
        "integration": {"as": "workflow-organ", "how": "wire behind a seam"},
        "source": {"repo": name, "sha": "b" * 40, "url": f"https://github.com/{name}"},
    }


SKILLS = [
    skill("acme/langfuse-like", "platform", "LLM observability and evals platform",
          use=["eval-obs organ"], stars=500),
    skill("acme/fastmcp-like", "framework", "build MCP servers fast", stars=900),
    skill("acme/awesome-like", "curated-index", "curated collection of MCP servers", stars=100),
]


def test_find_ranks_relevant_first():
    res = find("observability evals", SKILLS)
    assert res and res[0][1]["name"] == "acme/langfuse-like"
    assert res[0][0] == 1.0


def test_find_ties_break_by_stars_then_name():
    res = find("mcp servers", SKILLS)
    names = [s["name"] for _, s in res]
    assert names.index("acme/fastmcp-like") < names.index("acme/awesome-like")


def test_find_no_match_returns_empty_and_diagnose_names_vocab():
    assert find("quantum knitting", SKILLS) == []
    d = diagnose(SKILLS)
    assert "curated-index" in d and "repos.yml" in d


def test_render_includes_honest_edge_and_pinned_source():
    out = render_skill(SKILLS[0], 0.5)
    assert "not good at: something honest" in out
    assert "@ bbbbbbbb" in out


def _registry(tmp_path):
    p = tmp_path / "hub-skills.json"
    p.write_text(json.dumps({"contractVersion": "1.0", "skills": SKILLS}))
    return str(p)


def test_cli_find_and_recipe_and_list(tmp_path, capsys):
    reg = _registry(tmp_path)
    assert main(["--registry", reg, "find", "observability"]) == 0
    assert "langfuse-like" in capsys.readouterr().out
    assert main(["--registry", reg, "recipe", "fastmcp"]) == 0
    assert "build MCP servers fast" in capsys.readouterr().out
    assert main(["--registry", reg, "list"]) == 0
    assert capsys.readouterr().out.count("→") == 3


def test_cli_zero_match_exits_2_with_diagnostic(tmp_path, capsys):
    reg = _registry(tmp_path)
    assert main(["--registry", reg, "find", "quantum", "knitting"]) == 2
    assert "no match" in capsys.readouterr().out


def test_cli_missing_registry_exits_1(tmp_path, capsys):
    assert main(["--registry", str(tmp_path / "nope.json"), "list"]) == 1
    assert "repo_compile.py all" in capsys.readouterr().err


def test_load_registry_reads_real_shape(tmp_path):
    assert load_registry(_registry(tmp_path))[0]["kind"] == "platform"
