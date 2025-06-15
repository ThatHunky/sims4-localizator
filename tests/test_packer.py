import sys, pathlib, zipfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from sims4_auto_translator.packer import pack_strings_to_package


def test_pack(tmp_path):
    out = tmp_path / "test.package"
    data = [("key", "Value")]
    pack_strings_to_package(data, out)
    assert out.exists()
    with zipfile.ZipFile(out) as zf:
        assert "language.strings" in zf.namelist()
        content = zf.read("language.strings").decode("utf-8").strip()
    assert content == "key = Value"
