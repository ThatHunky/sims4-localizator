import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from sims4_auto_translator.parsers import mask_placeholders, unmask_placeholders


def test_mask_unmask():
    text = 'Hello {0.String} <b>World</b>'
    masked, mapping = mask_placeholders(text)
    assert masked != text
    restored = unmask_placeholders(masked, mapping)
    assert restored == text
