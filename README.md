# sims4-auto-translator

A simple utility to translate Sims 4 localisation files using DeepL.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DEEPL_AUTH_KEY=your-key-here
```

Translate a file from English to Ukrainian:

```bash
python -m sims4_auto_translator.main translate path/to/english.strings --target-lang UK
```

Run the GUI:

```bash
python -m sims4_auto_translator.main gui
```

_Output directory will contain subfolders named `source-target`._

![CLI](cli.png)
![GUI](gui.png)

Machine translation quality may vary. This project is not affiliated with EA. Check DeepL pricing for large volumes.
