import customtkinter as ctk
from tkhtmlview import HTMLLabel
import plotly.graph_objects as go

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.geometry("800x600")
root.title("Scrollable Plotly Panel with Update")

class ScrollablePanel:
    def __init__(self, parent, title="Panel", height=400, width=700):
        self.container = ctk.CTkFrame(parent, corner_radius=20, fg_color="#1f1f1f")
        self.container.pack(padx=20, pady=20)

        lbl_title = ctk.CTkLabel(self.container, text=title, font=("Arial", 14, "bold"))
        lbl_title.pack(anchor="w", padx=5, pady=5)

        # Canvas + scrollbar
        self.canvas = ctk.CTkCanvas(self.container, bg="#1f1f1f", highlightthickness=0,
                                    width=width, height=height)
        self.scrollbar = ctk.CTkScrollbar(self.container, orientation="vertical",
                                          command=self.canvas.yview)
        self.scroll_frame = ctk.CTkFrame(self.canvas, fg_color="#2b2b2b")

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0,0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # HTML label referansları
        self.html_labels = []

    def add_html(self, html_content, height=400):
        label = HTMLLabel(self.scroll_frame, html=html_content, width=650, height=height)
        label.pack(padx=5, pady=5)
        self.html_labels.append(label)

    def update_html(self, index, new_html):
        if 0 <= index < len(self.html_labels):
            label = self.html_labels[index]
            label.set_html(new_html)  # HTMLLabel'da içerik güncelleme
        else:
            print("Index out of range")

# Panel oluştur
panel = ScrollablePanel(root, title="Plotly Grafikleri")

# Örnek Plotly grafikleri ekle
for i in range(3):
    fig = go.Figure(data=go.Bar(y=[i+1, (i+1)*2, (i+1)*3]))
    html_str = fig.to_html(include_plotlyjs='cdn', full_html=False)
    panel.add_html(html_str, height=300)

# Örnek güncelleme: 2. grafiği değiştir
def update_graph():
    fig = go.Figure(data=go.Bar(y=[10, 5, 8]))
    new_html = fig.to_html(include_plotlyjs='cdn', full_html=False)
    panel.update_html(1, new_html)

# 3 saniye sonra güncelle
root.after(3000, update_graph)

root.mainloop()
