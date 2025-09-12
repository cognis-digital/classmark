from pathlib import Path
from classmark.core import validate_portion_mark, detect_banners, detect_portion_marks, scan
from cognis_mil import ClassificationBanner
D = Path(__file__).parent.parent / "demos"
def test_banner_builder():
    b = ClassificationBanner.placeholder()
    assert "UNCLASSIFIED" in b.render()
    assert b.validate()[0] is True
def test_pm_valid():
    assert validate_portion_mark("(U)")[0]
    assert validate_portion_mark("(S//NF)")[0]
def test_pm_invalid():
    ok, _ = validate_portion_mark("(X)")
    assert not ok
def test_detect():
    text = (D / "doc-ok.txt").read_text()
    assert len(detect_banners(text)) >= 1
    assert len(detect_portion_marks(text)) >= 1
def test_scan():
    r = scan(str(D))
    ids = {f.id for f in r.findings}
    assert "CM-NOBANNER" in ids
    assert "CM-BADPM" in ids
