# knowledge/

Generated knowledge artifacts. The canonical **FDE knowledge spine** (`fde-spine.graph.json` +
`fde-spine.html`) is produced by the `knowledgefy` skill (U2) from `FDE-research-synthesis.md`
(U3). The JSON is what drafting steps consume; the HTML is the human-browsable map.

A second, complementary base — the **FDE competency spine** (`jd-competency-spine.graph.json` +
`.html`) — is compiled from real job descriptions. `jd-compiler` turns the JDs in
`course/target-jds/` into the prose vault `vault/jd-competencies/`, and `knowledgefy` builds the
spine from it. Where the domain spine answers *what the FDE role is*, the competency spine answers
*what the FDE market demands* (and grows as JDs are added). Regenerate:

```bash
python3 ../skills/jd-compiler/scripts/jd_compile.py matrix ../course/target-jds/*.md --note vault/jd-competencies
python3 ../skills/knowledgefy/scripts/knowledgefy.py build vault/jd-competencies/ \
  --out jd-competency-spine.graph.json --html jd-competency-spine.html
```

Artifacts here are generated — regenerate with `knowledgefy` / `jd-compiler` rather than hand-editing.
