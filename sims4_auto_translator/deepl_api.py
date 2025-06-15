from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Dict, Iterable, List

import requests
from rich.console import Console

from .utils import load_json, save_json

console = Console()
CACHE_PATH = Path('translated_cache.json')
DEEPL_FREE_ENDPOINT = 'https://api-free.deepl.com/v2/translate'
DEEPL_PRO_ENDPOINT = 'https://api.deepl.com/v2/translate'


class DeepLTranslator:
    def __init__(self, auth_key: str) -> None:
        if auth_key.startswith('free:'):
            self.endpoint = DEEPL_FREE_ENDPOINT
            auth_key = auth_key[len('free:'):]
        else:
            self.endpoint = DEEPL_PRO_ENDPOINT
        self.auth_key = auth_key
        self.cache: Dict[str, Dict[str, str]] = load_json(CACHE_PATH)

    def _cache_key(self, text: str, source: str, target: str) -> str:
        pair = f"{source.lower()}-{target.lower()}"
        return f"{pair}||{text}"

    def translate(self, texts: Iterable[str], source: str, target: str) -> List[str]:
        results: List[str] = []
        uncached: List[str] = []
        for text in texts:
            key = self._cache_key(text, source, target)
            if key in self.cache:
                results.append(self.cache[key])
            else:
                results.append('')
                uncached.append(text)
        if not uncached:
            return results

        batches: List[List[str]] = []
        batch: List[str] = []
        total_chars = 0
        for text in uncached:
            if len(batch) >= 50 or total_chars + len(text) > 20000:
                batches.append(batch)
                batch = []
                total_chars = 0
            batch.append(text)
            total_chars += len(text)
        if batch:
            batches.append(batch)

        translated: Dict[str, str] = {}
        for batch in batches:
            for attempt in range(5):
                try:
                    resp = requests.post(
                        self.endpoint,
                        data={
                            'auth_key': self.auth_key,
                            'source_lang': source.upper(),
                            'target_lang': target.upper(),
                            **{f'text[{i}]': t for i, t in enumerate(batch)},
                        },
                        timeout=10,
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        for orig, trans in zip(batch, [t['text'] for t in data['translations']]):
                            translated[orig] = trans
                        break
                    if resp.status_code in (429, 500, 503):
                        wait = 2 ** attempt
                        console.print(f"DeepL rate limited, retrying in {wait}s...")
                        time.sleep(wait)
                        continue
                    resp.raise_for_status()
                except Exception as e:  # network error or HTTPError
                    wait = 2 ** attempt
                    console.print(f"Error contacting DeepL: {e}. Retrying in {wait}s")
                    time.sleep(wait)
            else:
                console.print("Failed to translate batch after retries")
                for orig in batch:
                    translated[orig] = orig

        for text, result in translated.items():
            key = self._cache_key(text, source, target)
            self.cache[key] = result
        save_json(self.cache, CACHE_PATH)

        idx = 0
        for i, text in enumerate(texts):
            key = self._cache_key(text, source, target)
            if results[i]:
                continue
            results[i] = self.cache.get(key, translated.get(uncached[idx], text))
            idx += 1
        return results
