import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from sims4_auto_translator import deepl_api
from sims4_auto_translator.deepl_api import DeepLTranslator


def test_cache(tmp_path, monkeypatch):
    call_count = 0

    def fake_post(url, data, timeout):
        nonlocal call_count
        call_count += 1
        class Resp:
            status_code = 200
            def json(self):
                return {'translations': [{'text': data['text[0]'] + '_uk'}]}
        return Resp()

    monkeypatch.setattr('sims4_auto_translator.deepl_api.requests.post', fake_post)
    monkeypatch.setattr(deepl_api, 'CACHE_PATH', tmp_path / 'cache.json')
    translator = DeepLTranslator('testkey')
    result1 = translator.translate(['hello'], 'EN', 'UK')
    result2 = translator.translate(['hello'], 'EN', 'UK')
    assert result1 == ['hello_uk']
    assert result2 == ['hello_uk']
    assert call_count == 1
