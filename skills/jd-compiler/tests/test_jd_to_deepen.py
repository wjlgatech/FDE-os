"""jd_to_deepen produces a valid 'deepen' artifact (deepen-types contract)."""
import importlib.util, os, re, unittest
_H=os.path.dirname(__file__); _S=os.path.join(_H,"..","scripts","jd_to_deepen.py")
spec=importlib.util.spec_from_file_location("j2d",_S); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
JD=os.path.abspath(os.path.join(_H,"..","..","..","course","target-jds","anthropic-fde-applied-ai.md"))

class T(unittest.TestCase):
    def setUp(self):
        self.a=m.build_artifact(m.compile_jd(JD),"Anthropic — FDE","https://job-boards.greenhouse.io/anthropic/jobs/4985877008","job-description","anthropic-fde",True)
    def test_grounded_source(self):
        self.assertTrue(re.match(r"^https?://",self.a["source"]["url"])); self.assertTrue(self.a["source"]["title"])
    def test_graph_nonempty_and_no_dangling_edges(self):
        g=self.a["graph"]; ids={n["id"] for n in g["nodes"]}
        self.assertTrue(g["nodes"])
        for e in g["edges"]: self.assertIn(e["source"],ids); self.assertIn(e["target"],ids)
    def test_every_skill_has_honest_limits(self):
        self.assertTrue(self.a["skills"])
        for s in self.a["skills"]: self.assertTrue(s["notGoodAt"], f"{s['id']} missing notGoodAt")
    def test_id_is_a_slug(self):
        self.assertRegex(self.a["id"], r"^[a-z0-9-]+$")
    def test_bad_url_rejected_by_cli(self):
        self.assertEqual(m.main([JD,"--title","x","--url","not-http"]), 2)

if __name__=="__main__": unittest.main()
