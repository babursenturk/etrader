import customtkinter as ctk
from tkinter import ttk

class ScrollablePanel:
    def __init__(self, parent, title="Panel", height=200, width=350, leftmarg = 0, topmarg = 0):
        # Dış çerçeve (rounded)
        self.container = ctk.CTkFrame(parent, corner_radius=10, fg_color="#383838")
        self.container.pack(side="left", anchor="n", padx=10, pady=10)
        self.container.place(x=leftmarg, y=topmarg)

        # Başlık
        lbl_title = ctk.CTkLabel(self.container, text=title, text_color="white",
                                 font=("Arial", 13, "bold"))
        lbl_title.pack(anchor="w", padx=5, pady=3)

        # scroll bar style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Vertical.TScrollbar",
                        troughcolor="#333333",
                        background="#00bfff",
                        bordercolor="#1f1f1f",
                        arrowcolor="white",
                        gripcount=0,
                        width=15)

        # Canvas + scrollbar
        self.canvas = ctk.CTkCanvas(self.container, bg="#1f1f1f", highlightthickness=0,
                                    height=height, width=width)
        self.scrollbar = ttk.Scrollbar(self.container, orient="vertical",
                                       command=self.canvas.yview)
        self.scroll_frame = ctk.CTkFrame(self.canvas, fg_color="#1f1f1f")  # İç frame

        # Scroll ayarı
        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True) # burayi degistircez. koordinat girecegiz.
        self.scrollbar.pack(side="right", fill="y")

    def clear(self):
        for w in self.scroll_frame.winfo_children():
            w.destroy()

    def add_label(self, text, color="white", bold=False):
        font = ("Arial", 14, "bold") if bold else ("Arial", 12)
        lbl = ctk.CTkLabel(self.scroll_frame, text=text, text_color=color, font=font,
                            anchor="w")
        lbl.pack(fill="x", pady=2, padx=5, anchor="w")
