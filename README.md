# sims4-auto-translator

A simple utility to translate Sims 4 localisation files using DeepL.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DEEPL_AUTH_KEY=your-key-here
```

On Windows use:

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
set DEEPL_AUTH_KEY=your-key-here
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

In the GUI you can now select the Sims 4 game folder. Every `.strings` file
found inside that folder will be translated and written either back to the game
folder or to a directory you choose.

You can also tick **Create .package** to generate a mod package alongside the
translated `.strings` files.

![CLI](cli.png)
![GUI](gui.png)

## Building an executable

You can bundle the translator into a single Windows executable using
[PyInstaller](https://pyinstaller.org/):

```bash
pip install pyinstaller
pyinstaller --onefile -n sims4-auto-translator sims4_auto_translator/main.py
```

After running the command the `dist` directory will contain
`sims4-auto-translator.exe` which can be used in place of the Python command.

Machine translation quality may vary. This project is not affiliated with EA. Check DeepL pricing for large volumes.
