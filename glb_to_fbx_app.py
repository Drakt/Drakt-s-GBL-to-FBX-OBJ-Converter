import shutil
import subprocess
import sys
import threading
import zipfile
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
from accurig_obj_export import export_accurig_obj


def runtime_file(name):
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / name


def native_converter():
    bundled = runtime_file("native_fbx_converter.exe")
    return bundled if bundled.exists() else None


class ConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.tk.call("tk", "scaling", 1.0)
        self.title("Drakt GLB to FBX/OBJ Converter")
        self.ui_scale = min(1.0, (self.winfo_screenwidth() - 40) / 1400, (self.winfo_screenheight() - 80) / 800)
        self.ui_width = int(1400 * self.ui_scale)
        self.ui_height = int(800 * self.ui_scale)
        self.geometry(f"{self.ui_width}x{self.ui_height}")
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.target_height = tk.StringVar(value="150")
        self.format_choice = tk.StringVar(value="FBX")
        self.make_zip = tk.BooleanVar(value=True)
        self.status = tk.StringVar(value="Ready")
        self.setup_theme()
        self.build_ui()

    def sp(self, value):
        return max(1, int(round(value * self.ui_scale)))

    def setup_theme(self):
        self.colors = {"bg": "#10181a", "panel": "#182326", "panel2": "#213033", "text": "#edf3e8", "muted": "#9fb0a6", "accent": "#9bc53d", "accent_dark": "#6f9226", "gold": "#d7a84c", "border": "#334548"}
        self.configure(bg=self.colors["bg"])
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Drakts.TFrame", background=self.colors["bg"])
        style.configure("Panel.TFrame", background=self.colors["panel"])
        style.configure("Panel.TLabelframe", background=self.colors["panel"], foreground=self.colors["text"], bordercolor=self.colors["border"])
        style.configure("Panel.TLabelframe.Label", background=self.colors["panel"], foreground=self.colors["gold"], font=("Segoe UI", 10, "bold"))
        style.configure("Drakts.TLabel", background=self.colors["panel"], foreground=self.colors["text"])
        style.configure("Muted.TLabel", background=self.colors["bg"], foreground=self.colors["muted"])
        style.configure("Accent.TButton", background=self.colors["accent"], foreground="#101510", borderwidth=0, padding=(16, 8), font=("Segoe UI", 10, "bold"))
        style.map("Accent.TButton", background=[("active", self.colors["gold"]), ("disabled", self.colors["accent_dark"])])
        style.configure("Drakts.TEntry", fieldbackground="#0e1517", foreground=self.colors["text"], bordercolor=self.colors["border"], lightcolor=self.colors["border"], darkcolor=self.colors["border"], padding=7)
        style.configure("Drakts.TCheckbutton", background=self.colors["panel"], foreground=self.colors["text"])

    def build_ui(self):
        self.overrideredirect(True)
        self.geometry(f"{self.ui_width}x{self.ui_height}")
        skin_path = runtime_file("drakt_mmo_skin.png")
        skin = Image.open(skin_path).convert("RGB").resize((self.ui_width, self.ui_height), Image.Resampling.LANCZOS)
        self.skin_image = ImageTk.PhotoImage(skin)
        self.background = tk.Canvas(self, width=self.ui_width, height=self.ui_height, highlightthickness=0, bd=0)
        self.background.place(x=0, y=0, relwidth=1, relheight=1)
        self.background.create_image(0, 0, image=self.skin_image, anchor="nw")
        self._field_regions = []
        self.background.bind("<Button-1>", self._focus_field)

        titlebar = tk.Frame(self, bg="#080b0b")
        titlebar.place(x=0, y=0, relwidth=1, height=self.sp(54))
        titlebar.bind("<Button-1>", self.start_drag)
        titlebar.bind("<B1-Motion>", self.drag_window)
        tk.Label(titlebar, text="D", bg="#080b0b", fg=self.colors["gold"], font=("Georgia", self.sp(19), "bold")).pack(side="left", padx=(self.sp(25), self.sp(12)))
        tk.Label(titlebar, text="Drakt GLB to FBX/OBJ Converter", bg="#080b0b", fg="#e7dfc6", font=("Segoe UI", self.sp(12))).pack(side="left")
        tk.Button(titlebar, text="×", command=self.destroy, bg="#080b0b", fg="#d8c995", activebackground="#7b2f27", activeforeground="white", bd=0, font=("Segoe UI", self.sp(20)), width=3).pack(side="right")
        tk.Button(titlebar, text="—", command=self.iconify, bg="#080b0b", fg="#d8c995", activebackground="#263d30", activeforeground="white", bd=0, font=("Segoe UI", self.sp(16)), width=3).pack(side="right")

        logo_path = runtime_file("drakt_logo.png")
        if logo_path.exists():
            logo = Image.open(logo_path).convert("RGBA").resize((self.sp(145), self.sp(145)), Image.Resampling.LANCZOS)
            self.logo_image = ImageTk.PhotoImage(logo)
            self.background.create_image(self.sp(34), self.sp(76), image=self.logo_image, anchor="nw")
        self.draw_text("DRAKT", 225, 125, "#d9a94c", ("Georgia", self.sp(70), "bold"))
        self.draw_text("GLB TO FBX/OBJ CONVERTER", 228, 186, "#ded8c5", ("Georgia", self.sp(22), "bold"))
        self.draw_text("TEXTURES\nPRESERVED", 1228, 136, "#a6d45d", ("Georgia", self.sp(17), "bold"), "center")

        self.input_entry = self.overlay_entry(246, 244, 879, 43, self.input_path)
        self.output_entry = self.overlay_entry(246, 314, 879, 43, self.output_path)
        self.height_entry = self.overlay_entry(246, 384, 265, 43, self.target_height, font_size=29, suffix="cm")
        self.overlay_label("GLB file", 126, 260)
        self.overlay_label("Output folder", 126, 330)
        self.overlay_label("Target height", 126, 400)
        self.overlay_button("BROWSE...", self.choose_input, 1144, 244, 125, 43)
        self.overlay_button("BROWSE...", self.choose_output, 1144, 314, 125, 43)
        self.overlay_label("Format", 560, 400)
        self.format_box = tk.OptionMenu(self, self.format_choice, "FBX", "OBJ", "Both")
        self.format_box.configure(bg="#171d1d", fg="#f0d38a", activebackground="#273a30", activeforeground="#fff3c7", highlightthickness=0, bd=0, width=12, font=("Georgia", self.sp(13), "bold"))
        self.format_box["menu"].configure(bg="#171d1d", fg="#f0d38a", activebackground="#273a30", activeforeground="#fff3c7", font=("Georgia", self.sp(13), "bold"))
        self.format_box.place(x=self.sp(645), y=self.sp(384), width=self.sp(210), height=self.sp(42))
        self.canvas_checkbox("Create a ZIP containing the FBX and textures", 875, 405, self.make_zip)

        self.convert_tag = self.transparent_button("CONVERT", self.start_conversion, 410, 455, 580, 62, ("Georgia", self.sp(28), "bold"), "#e8bd62")
        self.status_text_color = "#a6d45d"
        self.status_text_id = self.background.create_text(self.sp(60), self.sp(585), text=self.status.get(), fill=self.status_text_color, anchor="w", font=("Segoe UI", self.sp(39), "bold"))
        self.status.trace_add("write", self.refresh_status_text)
        self.log_lines = []
        self.log_text_id = self.background.create_text(self.sp(60), self.sp(668), text="", fill="#ded8c5", anchor="nw", width=self.sp(850), font=("Segoe UI", self.sp(12)))

    def draw_text(self, text, x, y, fill, font, anchor="w"):
        self.background.create_text(self.sp(x), self.sp(y), text=text, fill=fill, font=font, anchor=anchor)

    def refresh_status_text(self, *_):
        self.background.itemconfigure(self.status_text_id, text=self.status.get(), fill=self.status_text_color)

    def set_status_color(self, color):
        self.status_text_color = color
        self.background.itemconfigure(self.status_text_id, fill=color)

    def canvas_checkbox(self, text, x, y, variable):
        tag = "zip_checkbox"
        box_x, box_y = self.sp(x), self.sp(y - 13)
        self.background.create_rectangle(box_x, box_y, self.sp(x + 18), self.sp(y + 5), outline="#d9c58b", width=max(1, self.sp(2)), tags=(tag,))
        check_id = self.background.create_text(self.sp(x + 9), self.sp(y - 4), text="✓" if variable.get() else "", fill="#a6d45d", anchor="center", font=("Segoe UI", self.sp(13), "bold"), tags=(tag,))
        self.background.create_text(self.sp(x + 28), self.sp(y - 4), text=text, fill="#ded8c5", anchor="w", font=("Segoe UI", self.sp(12)), tags=(tag,))

        def refresh(*_):
            self.background.itemconfigure(check_id, text="✓" if variable.get() else "")

        variable.trace_add("write", refresh)
        self.background.tag_bind(tag, "<Button-1>", lambda _event: variable.set(not variable.get()))

    def overlay_label(self, text, x, y):
        self.draw_text(text, x, y, "#ded8c5", ("Segoe UI", self.sp(14), "bold"))

    def overlay_entry(self, x, y, width, height, variable, font_size=13, suffix=None):
        text_id = self.background.create_text(self.sp(x + 8), self.sp(y + height / 2), text=variable.get(), fill="#e2d9c0", anchor="w", font=("Segoe UI", self.sp(font_size)))
        suffix_id = None
        if suffix:
            suffix_id = self.background.create_text(self.sp(x + width - 14), self.sp(y + height / 2), text=suffix, fill="#d2bd80", anchor="e", font=("Segoe UI", self.sp(15), "bold"))
        entry = tk.Entry(self, textvariable=variable, bg="#171d1d", fg="#e2d9c0", insertbackground="#e2d9c0", relief="flat", bd=0, highlightthickness=0, font=("Segoe UI", self.sp(font_size)))
        entry.place_forget()

        def refresh(*_):
            self.background.itemconfigure(text_id, text=variable.get())

        def show_editor():
            self.background.itemconfigure(text_id, state="hidden")
            editor_width = width - 48 if suffix else width - 8
            entry.place(x=self.sp(x + 4), y=self.sp(y + 2), width=self.sp(editor_width), height=self.sp(height - 4))
            entry.focus_set()
            entry.icursor("end")

        def hide_editor(_event=None):
            entry.place_forget()
            self.background.itemconfigure(text_id, state="normal")

        variable.trace_add("write", refresh)
        entry.bind("<FocusOut>", hide_editor)
        entry.bind("<Return>", hide_editor)
        self._field_regions.append((x, y, width, height, show_editor))
        return entry

    def _focus_field(self, event):
        x = event.x / max(self.ui_scale, 0.001)
        y = event.y / max(self.ui_scale, 0.001)
        for field_x, field_y, field_w, field_h, show_editor in self._field_regions:
            if field_x <= x <= field_x + field_w and field_y <= y <= field_y + field_h:
                show_editor()
                return

    def overlay_button(self, text, command, x, y, width, height):
        return self.transparent_button(text, command, x, y, width, height, ("Georgia", self.sp(12), "bold"), "#d9a94c")

    def transparent_button(self, text, command, x, y, width, height, font, fill):
        tag = f"button_{len(getattr(self, '_transparent_buttons', []))}"
        self._transparent_buttons = getattr(self, "_transparent_buttons", []) + [tag]
        self.background.create_rectangle(self.sp(x), self.sp(y), self.sp(x + width), self.sp(y + height), fill="", outline="", tags=(tag,))
        self.background.create_text(self.sp(x + width / 2), self.sp(y + height / 2), text=text, fill=fill, font=font, anchor="center", tags=(tag,))
        self.background.tag_bind(tag, "<Button-1>", lambda event: command())
        self.background.tag_bind(tag, "<Enter>", lambda event: self.background.config(cursor="hand2"))
        self.background.tag_bind(tag, "<Leave>", lambda event: self.background.config(cursor=""))
        return tag

    def set_convert_enabled(self, enabled):
        if enabled:
            self.background.tag_bind(self.convert_tag, "<Button-1>", lambda event: self.start_conversion())
            self.background.itemconfigure(self.convert_tag, state="normal")
        else:
            self.background.tag_unbind(self.convert_tag, "<Button-1>")
            self.background.itemconfigure(self.convert_tag, state="disabled")

    def start_drag(self, event):
        self._drag_x, self._drag_y = event.x_root - self.winfo_x(), event.y_root - self.winfo_y()

    def drag_window(self, event):
        self.geometry(f"+{event.x_root - self._drag_x}+{event.y_root - self._drag_y}")

    def file_row(self, parent, label, variable, command):
        row = tk.Frame(parent, bg=self.colors["panel"])
        row.pack(fill="x", pady=5)
        tk.Label(row, text=label, width=17, anchor="w", bg=self.colors["panel"], fg=self.colors["text"], font=("Segoe UI", 10)).pack(side="left")
        tk.Entry(row, textvariable=variable, bg="#0e1517", fg=self.colors["text"], insertbackground=self.colors["text"], relief="groove", bd=2, highlightthickness=1, highlightbackground=self.colors["border"], highlightcolor=self.colors["gold"], font=("Segoe UI", 10)).pack(side="left", fill="x", expand=True, padx=(0, 8), ipady=7)
        if command:
            tk.Button(row, text="BROWSE...", command=command, bg="#26332d", fg=self.colors["gold"], activebackground="#385d34", activeforeground="#f1d68c", relief="groove", bd=2, padx=13, pady=7, font=("Segoe UI", 9, "bold")).pack(side="right")

    def choose_input(self):
        path = filedialog.askopenfilename(filetypes=[("GLB files", "*.glb"), ("All files", "*.*")])
        if path:
            self.input_path.set(path)
            if not self.output_path.get():
                self.output_path.set(str(Path(path).parent))

    def choose_output(self):
        path = filedialog.askdirectory()
        if path:
            self.output_path.set(path)

    def log_message(self, message):
        self.log_lines.append(message)
        self.background.itemconfigure(self.log_text_id, text="\n".join(self.log_lines[-8:]))

    def start_conversion(self):
        source = Path(self.input_path.get().strip())
        output = Path(self.output_path.get().strip())
        if not source.is_file() or source.suffix.lower() != ".glb":
            messagebox.showerror("GLB to FBX Converter", "Please select a valid GLB file.")
            return
        if not output.is_dir():
            messagebox.showerror("GLB to FBX Converter", "Please select an existing output folder.")
            return
        try:
            height = float(self.target_height.get().strip())
            if height <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("GLB to FBX Converter", "Target height must be a positive number in centimeters.")
            return
        selected_format = self.format_choice.get()
        if selected_format not in {"FBX", "OBJ", "Both"}:
            messagebox.showerror("GLB to FBX Converter", "Please choose FBX, OBJ, or Both.")
            return
        if selected_format in {"FBX", "Both"} and not native_converter():
            messagebox.showerror("GLB to FBX Converter", "The professional FBX conversion engine is missing. Please use the packaged application.")
            return
        self.set_convert_enabled(False)
        self.status.set("Converting...")
        self.set_status_color(self.colors["gold"])
        threading.Thread(target=self.convert, args=(source, output, self.make_zip.get(), height, selected_format), daemon=True).start()

    def convert(self, source, output, make_zip, height, selected_format):
        package = output / f"{source.stem} {selected_format}"
        try:
            obj_dir = package if selected_format in {"OBJ", "Both"} else package / "_conversion_source"
            accurig_obj, accurig_files = export_accurig_obj(source, obj_dir, height)
            textures = [path for path in accurig_files if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}]
            fbx = None
            if selected_format in {"FBX", "Both"}:
                fbx = package / f"{source.stem}_AccuRIG.fbx"
                helper = native_converter()
                result = subprocess.run([str(helper), str(accurig_obj), str(fbx)], cwd=str(helper.parent), capture_output=True, text=True, encoding="utf-8", errors="replace")
                if result.returncode != 0:
                    raise RuntimeError(result.stderr[-3000:] or result.stdout[-3000:] or "The professional FBX converter failed.")
                fbm_dir = package / f"{fbx.stem}.fbm"
                fbm_dir.mkdir(exist_ok=True)
                for texture in textures:
                    shutil.copy2(texture, fbm_dir / texture.name)
            zip_path = None
            if make_zip:
                zip_path = output / f"{source.stem} {selected_format}.zip"
                with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
                    for path in package.rglob("*"):
                        if path.is_file() and "_conversion_source" not in path.parts:
                            archive.write(path, arcname=f"{package.name}/{path.relative_to(package)}")
            self.after(0, self.success, fbx, accurig_obj if selected_format in {"OBJ", "Both"} else None, textures, selected_format, zip_path)
        except Exception as error:
            self.after(0, self.failure, str(error))

    def success(self, fbx, obj, textures, selected_format, zip_path):
        self.set_convert_enabled(True)
        self.status.set("Conversion complete")
        self.set_status_color(self.colors["accent"])
        if fbx:
            self.log_message(f"FBX: {fbx}")
        if obj:
            self.log_message(f"OBJ: {obj}")
        self.log_message(f"Textures: {len(textures)} exported with the {selected_format} output")
        if fbx:
            self.log_message(f"FBX texture folder: {fbx.parent / (fbx.stem + '.fbm')}")
        if zip_path:
            self.log_message(f"ZIP: {zip_path}")
        messagebox.showinfo("GLB to FBX Converter", "Conversion complete. Keep the FBX and textures together.")

    def failure(self, error):
        self.set_convert_enabled(True)
        self.status.set("Conversion failed")
        self.set_status_color("#e07a5f")
        self.log_message(error)
        messagebox.showerror("GLB to FBX Converter", error)


if __name__ == "__main__":
    ConverterApp().mainloop()
