import customtkinter as ctk

class ScrollableGrid:
    def __init__(self, parent, capt, columns, col_widths=None, height=350, width=450, left=30, top=40, on_select=None):
        self.parent = parent
        self.on_select = on_select   # satır seçilince çağrılacak callback
        self.selected_row = None
        self.selected_data = None

        # Ana frame
        self.frame = ctk.CTkFrame(parent, corner_radius=15, fg_color="#1e1e1e", width=width, height=height)
        self.frame.pack_propagate(True)
        self.frame.place(x=left, y=top)

        # Başlık (caption)
        self.caption = ctk.CTkLabel(
            self.frame,
            text=capt,
            text_color="#00eeff",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        self.caption.pack(anchor="w", padx=8, pady=(6, 2))

        # Canvas + Scrollbar
        self.canvas = ctk.CTkCanvas(
            self.frame,
            height=height - 40,
            width=width,
            bg="#1e1e1e",
            highlightthickness=0
        )
        self.scrollbar = ctk.CTkScrollbar(self.frame, orientation="vertical", command=self.canvas.yview)

        # İçerik frame
        self.scrollable_frame = ctk.CTkFrame(self.canvas, fg_color="#1e1e1e")
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=(5,0), pady=(0,5))
        self.scrollbar.pack(side="right", fill="y", pady=(0,5))

        # Başlık satırı
        self.columns = columns
        self.headers = []
        for i, col in enumerate(columns):
            lbl = ctk.CTkLabel(
                self.scrollable_frame,
                text=col,
                text_color="white",
                fg_color="#333333",
                corner_radius=8,
                font=ctk.CTkFont(size=12, weight="bold")
            )
            lbl.grid(row=0, column=i, sticky="nsew", padx=2, pady=2)
            self.scrollable_frame.grid_columnconfigure(
                i, weight=1, minsize=(col_widths[i] if col_widths else 100)
            )
            self.headers.append(lbl)

        self.rows = []
        self.row_map = {}

    def add_row(self, key, values):
        row_index = len(self.rows) + 1
        row_widgets = []
        for i, val in enumerate(values):
            if "%" in str(val):
                text_color = "#FF0000" if "-" in str(val) else "#00FF00"
            else:
                text_color = "white"

            lbl = ctk.CTkLabel(
                self.scrollable_frame,
                text=str(val),
                text_color=text_color,
                fg_color="#1e1e1e",
                font=ctk.CTkFont(size=12)
            )
            lbl.grid(row=row_index, column=i, sticky="nsew", padx=2, pady=2)

            # Satıra tıklama olayı
            lbl.bind("<Button-1>", lambda e, idx=row_index: self.on_row_click(idx))

            row_widgets.append(lbl)

        self.rows.append(row_widgets)
        self.row_map[key] = row_index

    def update_row(self, key, values):
        if key in self.row_map:
            row_index = self.row_map[key]
            row_widgets = self.rows[row_index - 1]
            for i, val in enumerate(values):
                row_widgets[i].configure(text=str(val))
        else:
            self.add_row(key, values)

    def on_row_click(self, row_index):
        # eski seçili satırı temizle
        if self.selected_row:
            for widget in self.selected_row:
                widget.configure(fg_color="#1e1e1e")

        # yeni seçilen satır
        self.selected_row = self.rows[row_index - 1]
        for widget in self.selected_row:
            widget.configure(fg_color="#444444")

        # verileri al
        self.selected_data = [w.cget("text") for w in self.selected_row]
        print("Seçilen satır:", self.selected_data)

        # callback çağır
        if self.on_select:
            self.on_select(self.selected_data)

    def clear(self):
        for row in self.rows:
            for widget in row:
                widget.destroy()
        self.rows.clear()
        self.row_map.clear()
        self.selected_row = None
        self.selected_data = None
