from __future__ import annotations

import tkinter as tk
import tkinter.ttk as ttk
from pathlib import Path
from tkinter import filedialog, messagebox

from .deepl_api import DeepLTranslator
from .parsers import parse_strings_file, write_strings_file, mask_placeholders, unmask_placeholders
from .utils import console


def run_gui() -> None:
    root = tk.Tk()
    root.title('Sims4 Auto Translator')

    tk.Label(root, text='Source Lang:').grid(row=0, column=0, sticky='e')
    source_var = tk.StringVar(value='EN')
    tk.Entry(root, textvariable=source_var).grid(row=0, column=1)

    tk.Label(root, text='Target Lang:').grid(row=1, column=0, sticky='e')
    target_var = tk.StringVar(value='UK')
    tk.Entry(root, textvariable=target_var).grid(row=1, column=1)

    apikey_var = tk.StringVar()
    tk.Label(root, text='DeepL API Key:').grid(row=2, column=0, sticky='e')
    tk.Entry(root, textvariable=apikey_var, width=40).grid(row=2, column=1)

    progress = tk.IntVar(value=0)
    progress_bar = tk.ttk.Progressbar(root, variable=progress, maximum=100)
    progress_bar.grid(row=4, column=0, columnspan=2, sticky='ew', pady=5)

    def start_translation() -> None:
        file_path = filedialog.askopenfilename(title='Select strings file')
        if not file_path:
            return
        source = source_var.get().upper()
        target = target_var.get().upper()
        key = apikey_var.get() or os.environ.get('DEEPL_AUTH_KEY', '')
        if not key:
            messagebox.showerror('Error', 'API key required')
            return
        translator = DeepLTranslator(key)
        entries = parse_strings_file(Path(file_path))
        texts = [e[1] for e in entries]
        masked = []
        maps = []
        for t in texts:
            m, mp = mask_placeholders(t)
            masked.append(m)
            maps.append(mp)
        translated = translator.translate(masked, source, target)
        restored = [unmask_placeholders(t, mp) for t, mp in zip(translated, maps)]
        out_dir = Path('output') / f"{source.lower()}-{target.lower()}"
        out_dir.mkdir(parents=True, exist_ok=True)
        write_strings_file(zip([e[0] for e in entries], restored), out_dir / Path(file_path).name)
        progress.set(100)
        messagebox.showinfo('Done', f'Translation saved to {out_dir}')

    tk.Button(root, text='Translate', command=start_translation).grid(row=3, column=0, columnspan=2, pady=5)

    root.mainloop()


if __name__ == '__main__':
    run_gui()
