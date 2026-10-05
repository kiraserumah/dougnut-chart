"""Desktop interface for preparing workbooks and exporting doughnut charts."""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import matplotlib

matplotlib.use("Agg")

from doughnut import chart, prepare


def run_action(root, action, success):
    root.configure(cursor="watch")
    root.update_idletasks()
    try:
        action()
    except Exception as error:
        messagebox.showerror("Gagal", str(error), parent=root)
    else:
        messagebox.showinfo("Selesai", success, parent=root)
    finally:
        root.configure(cursor="")


def prepare_excel(root):
    source = filedialog.askopenfilename(
        parent=root, title="Pilih Excel sumber", filetypes=[("Excel", "*.xlsx")]
    )
    if not source:
        return
    destination = filedialog.asksaveasfilename(
        parent=root,
        title="Simpan Excel untuk diedit",
        defaultextension=".xlsx",
        initialfile="manipulated.xlsx",
        filetypes=[("Excel", "*.xlsx")],
    )
    if not destination:
        return
    if Path(source).resolve() == Path(destination).resolve():
        messagebox.showerror("Gagal", "File hasil harus berbeda dari file sumber.", parent=root)
        return
    run_action(root, lambda: prepare(source, destination), f"Excel siap diedit:\n{destination}")


def create_charts(root):
    source = filedialog.askopenfilename(
        parent=root, title="Pilih Excel yang sudah diedit", filetypes=[("Excel", "*.xlsx")]
    )
    if not source:
        return
    destination = filedialog.askdirectory(parent=root, title="Pilih folder untuk gambar chart")
    if not destination:
        return
    run_action(root, lambda: chart(source, destination), f"Chart tersimpan di:\n{destination}")


def main():
    root = tk.Tk()
    root.title("Doughnut Charts")
    root.geometry("440x210")
    root.resizable(False, False)

    frame = ttk.Frame(root, padding=24)
    frame.pack(fill="both", expand=True)
    ttk.Label(frame, text="Doughnut Charts", font=("Segoe UI", 17, "bold")).pack(anchor="w")
    ttk.Label(frame, text="Siapkan Excel, edit nilainya, lalu buat chart.").pack(anchor="w", pady=(4, 16))
    ttk.Button(frame, text="1. Siapkan Excel untuk diedit", command=lambda: prepare_excel(root)).pack(fill="x", pady=4)
    ttk.Button(frame, text="2. Buat chart dari Excel editan", command=lambda: create_charts(root)).pack(fill="x", pady=4)
    root.mainloop()


if __name__ == "__main__":
    main()