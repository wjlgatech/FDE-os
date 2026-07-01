"""Tests for doc-understanding: OOXML fixtures are written as real zips, not mocks."""
import importlib.util
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "doc_understand.py"
spec = importlib.util.spec_from_file_location("doc_understand", _SCRIPT)
du = importlib.util.module_from_spec(spec)
spec.loader.exec_module(du)

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
S = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"

DOCX_BODY = f"""<?xml version="1.0"?>
<w:document xmlns:w="{W}"><w:body>
  <w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>Protocol Overview</w:t></w:r></w:p>
  <w:p><w:r><w:t>This trial follows </w:t></w:r><w:r><w:t>the USDM standard.</w:t></w:r></w:p>
  <w:tbl>
    <w:tr><w:tc><w:tcPr><w:gridSpan w:val="2"/></w:tcPr><w:p><w:r><w:t>Visit schedule</w:t></w:r></w:p></w:tc></w:tr>
    <w:tr><w:tc><w:p><w:r><w:t>Week 1</w:t></w:r></w:p></w:tc>
          <w:tc><w:p><w:r><w:t>Screening</w:t></w:r></w:p></w:tc></w:tr>
    <w:tr><w:tc><w:tcPr><w:vMerge w:val="restart"/></w:tcPr><w:p><w:r><w:t>Week 2</w:t></w:r></w:p></w:tc>
          <w:tc><w:p><w:r><w:t>Dosing</w:t></w:r></w:p></w:tc></w:tr>
    <w:tr><w:tc><w:tcPr><w:vMerge/></w:tcPr><w:p/></w:tc>
          <w:tc><w:p><w:r><w:t>Labs</w:t></w:r></w:p></w:tc></w:tr>
  </w:tbl>
</w:body></w:document>"""

DOCX_TRACKED = f"""<?xml version="1.0"?>
<w:document xmlns:w="{W}"><w:body>
  <w:p><w:r><w:t>Baseline text.</w:t></w:r>
       <w:ins w:id="1" w:author="a"><w:r><w:t> Added clause.</w:t></w:r></w:ins>
       <w:del w:id="2" w:author="a"><w:r><w:delText>Removed clause.</w:delText></w:r></w:del></w:p>
</w:body></w:document>"""

XLSX_SHARED = f"""<?xml version="1.0"?>
<sst xmlns="{S}"><si><t>Site</t></si><si><r><t>Enroll</t></r><r><t>ed</t></r></si></sst>"""
XLSX_WB = f"""<?xml version="1.0"?>
<workbook xmlns="{S}"><sheets><sheet name="Sites" sheetId="1"/></sheets></workbook>"""
XLSX_SHEET = f"""<?xml version="1.0"?>
<worksheet xmlns="{S}"><sheetData>
  <row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>1</v></c></row>
  <row r="2"><c r="A2" t="inlineStr"><is><t>Boston</t></is></c><c r="C2"><v>42</v></c></row>
</sheetData><mergeCells count="1"><mergeCell ref="A1:A2"/></mergeCells></worksheet>"""


def _write_docx(path: Path, body_xml: str) -> None:
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("word/document.xml", body_xml)


def _write_xlsx(path: Path) -> None:
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("xl/workbook.xml", XLSX_WB)
        zf.writestr("xl/sharedStrings.xml", XLSX_SHARED)
        zf.writestr("xl/worksheets/sheet1.xml", XLSX_SHEET)


class TestDocx(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.doc = Path(self.tmp.name) / "protocol.docx"
        _write_docx(self.doc, DOCX_BODY)

    def tearDown(self):
        self.tmp.cleanup()

    def test_headings_and_paragraphs(self):
        rep = du.parse(self.doc)
        self.assertEqual(rep["format"], "docx")
        self.assertEqual(rep["blocks"][0], {"type": "heading", "level": 1, "text": "Protocol Overview"})
        self.assertEqual(rep["blocks"][1]["text"], "This trial follows the USDM standard.")

    def test_table_merges_resolved(self):
        rep = du.parse(self.doc)
        table = rep["blocks"][2]
        self.assertEqual(table["rows"][0], ["Visit schedule", None])       # gridSpan=2
        self.assertEqual(table["rows"][3][0], None)                         # vMerge continue
        self.assertEqual(table["rows"][3][1], "Labs")
        self.assertEqual(table["merged_cells"], 2)

    def test_clean_doc_passes_gate(self):
        rep = du.parse(self.doc)
        ok, reasons = du.gate(rep, threshold=0.7)
        self.assertTrue(ok, reasons)
        self.assertTrue(rep["revisions"]["clean"])

    def test_track_changes_block_the_gate(self):
        tracked = Path(self.tmp.name) / "tracked.docx"
        _write_docx(tracked, DOCX_TRACKED)
        rep = du.parse(tracked)
        self.assertEqual(rep["revisions"], {"insertions": 1, "deletions": 1, "clean": False})
        self.assertNotIn("Removed clause", rep["blocks"][0]["text"])        # delText excluded
        self.assertIn("Added clause", rep["blocks"][0]["text"])
        ok, reasons = du.gate(rep)
        self.assertFalse(ok)
        self.assertTrue(any("track-changes" in r for r in reasons))


class TestXlsx(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.xl = Path(self.tmp.name) / "sites.xlsx"
        _write_xlsx(self.xl)

    def tearDown(self):
        self.tmp.cleanup()

    def test_shared_and_inline_strings(self):
        rep = du.parse(self.xl)
        table = rep["blocks"][0]
        self.assertEqual(table["sheet"], "Sites")
        self.assertEqual(table["rows"][0], ["Site", "Enrolled"])            # rich text concatenated
        self.assertEqual(table["rows"][1], ["Boston", None, "42"])          # sparse C2 -> dense grid

    def test_merged_ranges_counted(self):
        rep = du.parse(self.xl)
        self.assertEqual(rep["merged_ranges"], 1)


class TestGateHonesty(unittest.TestCase):
    def test_empty_doc_is_no_go(self):
        with tempfile.TemporaryDirectory() as tmp:
            empty = Path(tmp) / "empty.docx"
            _write_docx(empty, f'<?xml version="1.0"?><w:document xmlns:w="{W}"><w:body/></w:document>')
            rep = du.parse(empty)
            ok, reasons = du.gate(rep)
            self.assertFalse(ok)
            self.assertTrue(any("zero blocks" in r for r in reasons))
            self.assertEqual(rep["quality"]["overall"], 0.3)                # structure/coverage are 0

    def test_unknown_format_refuses(self):
        with self.assertRaises(ValueError):
            du.parse("scan.pdf")


class TestTextFormats(unittest.TestCase):
    def test_markdown_and_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            md = Path(tmp) / "note.md"
            md.write_text("# Title\n\nBody text.", encoding="utf-8")
            rep = du.parse(md)
            self.assertEqual(rep["blocks"][0]["type"], "heading")
            cv = Path(tmp) / "data.csv"
            cv.write_text("a,b\n1,2\n", encoding="utf-8")
            rep2 = du.parse(cv)
            self.assertEqual(rep2["blocks"][0]["rows"], [["a", "b"], ["1", "2"]])

    def test_cli_gate_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            md = Path(tmp) / "note.md"
            md.write_text("# Title\n\nBody.", encoding="utf-8")
            self.assertEqual(du.main(["gate", str(md)]), 0)
            tracked = Path(tmp) / "t.docx"
            _write_docx(tracked, DOCX_TRACKED)
            self.assertEqual(du.main(["gate", str(tracked)]), 1)


if __name__ == "__main__":
    sys.exit(unittest.main())
