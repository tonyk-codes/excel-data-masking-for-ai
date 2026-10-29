from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .config import load_settings
from .processor import process_pair


def launch_ui() -> None:
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        raise RuntimeError("The desktop UI needs an active graphical desktop display.") from exc
    root.title("SheetVeil - Privacy-Safe Excel Pair Tokenizer")
    root.geometry("760x480")
    root.minsize(680, 430)

    before = tk.StringVar()
    after = tk.StringVar()
    output = tk.StringVar(value=str(Path.cwd() / "sheetveil_output"))
    config = tk.StringVar()
    key_file = tk.StringVar()
    save_key = tk.BooleanVar(value=False)
    status = tk.StringVar(value="Ready. All processing is local.")

    frame = ttk.Frame(root, padding=18)
    frame.pack(fill="both", expand=True)
    ttk.Label(frame, text="SheetVeil", font=("TkDefaultFont", 20, "bold")).grid(row=0, column=0, columnspan=3, sticky="w")
    ttk.Label(frame, text="Create deterministic, privacy-safe before-and-after Excel pairs for AI workflow inference.", wraplength=700).grid(row=1, column=0, columnspan=3, sticky="w", pady=(2, 18))

    def file_row(row, label, variable, types):
        ttk.Label(frame, text=label).grid(row=row, column=0, sticky="w", pady=6)
        ttk.Entry(frame, textvariable=variable).grid(row=row, column=1, sticky="ew", padx=8)
        ttk.Button(frame, text="Browse...", command=lambda: variable.set(filedialog.askopenfilename(filetypes=types) or variable.get())).grid(row=row, column=2)

    excel_types = [("Excel workbooks", "*.xlsx *.xlsm *.xltx *.xltm"), ("All files", "*")]
    file_row(2, "Before workbook", before, excel_types)
    file_row(3, "After workbook", after, excel_types)
    ttk.Label(frame, text="Output folder").grid(row=4, column=0, sticky="w", pady=6)
    ttk.Entry(frame, textvariable=output).grid(row=4, column=1, sticky="ew", padx=8)
    ttk.Button(frame, text="Browse...", command=lambda: output.set(filedialog.askdirectory() or output.get())).grid(row=4, column=2)
    file_row(5, "Config JSON (optional)", config, [("JSON", "*.json"), ("All files", "*")])
    file_row(6, "Existing key (optional)", key_file, [("Key files", "*.key *.txt"), ("All files", "*")])
    ttk.Checkbutton(frame, text="Save generated key beside the output folder (needed only to extend this project later)", variable=save_key).grid(row=7, column=0, columnspan=3, sticky="w", pady=(12, 4))
    ttk.Label(frame, text="Warning: equality and repetition patterns remain visible. Review complex workbooks containing macros, queries, pivot caches, images, or embedded objects before sharing.", foreground="#8a4b00", wraplength=700).grid(row=8, column=0, columnspan=3, sticky="w", pady=10)

    progress = ttk.Progressbar(frame, mode="indeterminate")
    progress.grid(row=9, column=0, columnspan=3, sticky="ew", pady=7)
    ttk.Label(frame, textvariable=status).grid(row=10, column=0, columnspan=3, sticky="w")

    def worker():
        try:
            settings = load_settings(config.get() or None)
            key_out = str(Path(output.get()).parent / "sheetveil_project.key") if save_key.get() and not key_file.get() else None
            report = process_pair(before.get(), after.get(), output.get(), settings, key_file.get() or None, key_out)
            root.after(0, lambda: messagebox.showinfo("Completed", f"Masked pair created.\nShared tokens: {report['movement_summary']['shared_token_count']}\nOutput: {output.get()}"))
            root.after(0, lambda: status.set("Completed successfully."))
        except Exception as exc:  # noqa: BLE001 - worker boundary must report all processing failures.
            error = str(exc)
            root.after(0, lambda: messagebox.showerror("SheetVeil error", error))
            root.after(0, lambda: status.set("Failed. Review the error message."))
        finally:
            root.after(0, progress.stop)
            root.after(0, lambda: run_button.config(state="normal"))

    def run():
        if not before.get() or not after.get() or not output.get():
            messagebox.showwarning("Missing information", "Select both workbooks and an output folder.")
            return
        run_button.config(state="disabled")
        status.set("Processing locally...")
        progress.start(10)
        threading.Thread(target=worker, daemon=True).start()

    run_button = ttk.Button(frame, text="Create masked pair", command=run)
    run_button.grid(row=11, column=0, columnspan=3, sticky="ew", pady=(18, 0))
    frame.columnconfigure(1, weight=1)
    root.mainloop()
