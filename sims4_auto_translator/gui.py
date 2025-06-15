from __future__ import annotations

import os
import tkinter as tk
import tkinter.ttk as ttk
from pathlib import Path
from tkinter import filedialog, messagebox

from .deepl_api import DeepLTranslator
from .parsers import (
    mask_placeholders,
    parse_strings_file,
    unmask_placeholders,
    write_strings_file,
)
from .packer import pack_strings_to_package



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
    tk.Entry(root, textvariable=apikey_var, width=40).grid(row=2, column=1, columnspan=2, sticky='ew')

    tk.Label(root, text='Game Folder:').grid(row=3, column=0, sticky='e')
    game_var = tk.StringVar()
    tk.Entry(root, textvariable=game_var, width=40).grid(row=3, column=1, sticky='ew')
    tk.Button(root, text='Browse', command=lambda: game_var.set(filedialog.askdirectory())).grid(row=3, column=2)

    tk.Label(root, text='Output Folder:').grid(row=4, column=0, sticky='e')
    output_var = tk.StringVar()
    tk.Entry(root, textvariable=output_var, width=40).grid(row=4, column=1, sticky='ew')
    tk.Button(root, text='Browse', command=lambda: output_var.set(filedialog.askdirectory())).grid(row=4, column=2)
    use_game_var = tk.BooleanVar(value=False)
    tk.Checkbutton(root, text='Use Game Folder', variable=use_game_var).grid(row=4, column=3, sticky='w')

    pack_var = tk.BooleanVar(value=False)
    tk.Checkbutton(root, text='Create .package', variable=pack_var).grid(row=5, column=0, columnspan=2, sticky='w')

    progress = tk.IntVar(value=0)
    progress_bar = tk.ttk.Progressbar(root, variable=progress, maximum=100)
    progress_bar.grid(row=6, column=0, columnspan=4, sticky='ew', pady=5)

    def start_translation() -> None:
        folder = game_var.get()
        if not folder:
            messagebox.showerror('Error', 'Game folder not selected')
            return
        output_root = Path(output_var.get()) if output_var.get() else None
        if use_game_var.get() or output_root is None:
            output_root = Path(folder)
        source = source_var.get().upper()
        target = target_var.get().upper()
        file_list = list(Path(folder).rglob('*.strings'))
        package_list = list(Path(folder).rglob('Strings_*.package'))
        if not file_list and not package_list:
            messagebox.showerror('Error', 'No .strings or Strings_*.package files found')
            return
        key = apikey_var.get() or os.environ.get('DEEPL_AUTH_KEY', '')
        if not key:
            messagebox.showerror('Error', 'API key required')
            return
        translator = DeepLTranslator(key)
        progress_bar.configure(maximum=len(file_list) + len(package_list))
        progress.set(0)
        progress_index = 0
        for fp in file_list:
            entries = parse_strings_file(fp)
            texts = [e[1] for e in entries]
            masked = []
            maps = []
            for t in texts:
                m, mp = mask_placeholders(t)
                masked.append(m)
                maps.append(mp)
            translated = translator.translate(masked, source, target)
            restored = [unmask_placeholders(t, mp) for t, mp in zip(translated, maps)]
            out_path = output_root / fp.relative_to(folder)
            write_strings_file(zip([e[0] for e in entries], restored), out_path)
            if pack_var.get():
                pack_strings_to_package(zip([e[0] for e in entries], restored), out_path.with_suffix('.package'))
            progress_index += 1
            progress.set(progress_index)
            root.update_idletasks()

        from .dbpf import iter_stbl_from_package, parse_stbl
        for pkg in package_list:
            for inst, data in iter_stbl_from_package(pkg):
                entries = parse_stbl(data)
                texts = [e[1] for e in entries]
                masked = []
                maps = []
                for t in texts:
                    m, mp = mask_placeholders(t)
                    masked.append(m)
                    maps.append(mp)
                translated = translator.translate(masked, source, target)
                restored = [unmask_placeholders(t, mp) for t, mp in zip(translated, maps)]
                out_rel = pkg.relative_to(folder).with_suffix(f'_{inst:08X}.strings')
                out_path = output_root / out_rel
                write_strings_file(zip([e[0] for e in entries], restored), out_path)
                progress_index += 1
                progress.set(progress_index)
                root.update_idletasks()
        messagebox.showinfo('Done', f'Translated files saved to {output_root}')

    tk.Button(root, text='Translate', command=start_translation).grid(row=7, column=0, columnspan=4, pady=5)

    root.mainloop()


if __name__ == '__main__':
    run_gui()
