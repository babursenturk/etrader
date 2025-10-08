import customtkinter as ctk

class TabbedPanel:
    def __init__(self, parent, capt, tabs,
                 on_buy=None, on_sell=None, on_lim_buy=None, on_lim_sell=None, # callback'ler buradan alınır
                 height=350, width=450, left=30, top=40):
        self.parent = parent
        self.on_buy = on_buy
        self.on_sell = on_sell
        self.on_lim_buy = on_lim_buy
        self.on_lim_sell = on_lim_sell

        # Ana frame
        self.frame = ctk.CTkFrame(parent, corner_radius=15, fg_color="#1e1e1e",
                                  width=width, height=height)
        self.frame.pack_propagate(False)
        self.frame.place(x=left, y=top)

        # Başlık
        self.caption = ctk.CTkLabel(
            self.frame,
            text=capt,
            text_color="#00eeff",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        self.caption.pack(anchor="w", padx=8, pady=(6, 2))

        # Tabview
        self.tabview = ctk.CTkTabview(
            self.frame,
            width=width - 20,
            height=height - 50,
            fg_color="#1e1e1e",
            segmented_button_fg_color="#222222",
            segmented_button_selected_color="#444444",
            segmented_button_selected_hover_color="#666666",
            segmented_button_unselected_color="#1e1e1e",
            segmented_button_unselected_hover_color="#333333",
            text_color="white"
        )
        self.tabview.pack(fill="y", expand=True, padx=8, pady=5)

        # Sekmeler
        self.tabs = {}
        for tab_name in tabs:
            tab = self.tabview.add(tab_name)
            tab.configure(fg_color="#1e1e1e")
            self.tabs[tab_name] = tab

        try:
            self.tabview._segmented_button.grid(sticky="w")
            self.tabview._segmented_button.configure(
                font=ctk.CTkFont(size=12, weight="bold")
            )
        except Exception as e:
            print("Tab styling error:", e)

        if "Piyasa" in self.tabs:
            self._build_piyasa_tab(self.tabs["Piyasa"])
        if "Limit" in self.tabs:
            self._build_limit_tab(self.tabs["Limit"])

    def get_tab(self, name):
        return self.tabs.get(name)

    def _build_piyasa_tab(self, tab):
        # Üst sembol
        top_frame = ctk.CTkFrame(tab, fg_color="#2a2a2a", corner_radius=10)
        top_frame.pack(fill="x", padx=10, pady=5)

        self.entry_symbol = ctk.CTkEntry(top_frame, placeholder_text="Sembol", width=100)
        self.entry_symbol.pack(side="left", padx=5, pady=5)

        self.lbl_info = ctk.CTkLabel(
            top_frame,
            text="İşlem Limiti 0   Fiyat 0   Taban 0   Tavan 0",
            text_color="white",
            anchor="w"
        )
        self.lbl_info.pack(side="left", padx=10)

        # Orta bölüm
        middle_frame = ctk.CTkFrame(tab, fg_color="#1e1e1e")
        middle_frame.pack(fill="x", padx=10, pady=5)

        # Sol taraf (Alış)
        left = ctk.CTkFrame(middle_frame, fg_color="#1e1e1e")
        left.pack(side="left", expand=True, fill="both", padx=5)

        #ctk.CTkLabel(left, text="Lot", text_color="white").pack(anchor="w")
        self.entry_lot_buy = ctk.CTkEntry(left, width=120, justify="center")
        self.entry_lot_buy.insert(0, "0")
        self.entry_lot_buy.pack(pady=5)

        self.btn_buy = ctk.CTkButton(
            left, text="Alış", fg_color="#258D71",
            hover_color="#5E9284", width=100,
            command=self._on_buy
        )
        self.btn_buy.pack(pady=10)

        # Sağ taraf (Satış)
        right = ctk.CTkFrame(middle_frame, fg_color="#1e1e1e")
        right.pack(side="left", expand=True, fill="both", padx=5)

        #ctk.CTkLabel(right, text="Lot", text_color="white").pack(anchor="w")
        self.entry_lot_sell = ctk.CTkEntry(right, width=120, justify="center", placeholder_text="Mevcut 0")
        self.entry_lot_sell.pack(pady=5)

        self.btn_sell = ctk.CTkButton(
            right, text="Satış", fg_color="#C94B64",
            hover_color="#C2808D", width=100,
            command=self._on_sell
        )
        self.btn_sell.pack(pady=10)

        # Alt bölüm (Switchler)
        bottom_frame = ctk.CTkFrame(tab, fg_color="#1e1e1e")
        bottom_frame.pack(pady=5)

        self.switch_sms = ctk.CTkSwitch(bottom_frame, text="Sms")
        self.switch_sms.pack(side="left", padx=10)

        self.switch_email = ctk.CTkSwitch(bottom_frame, text="Email")
        self.switch_email.pack(side="left", padx=10)

    def _build_limit_tab(self, tab):
        # Üst sembol
        top_frame = ctk.CTkFrame(tab, fg_color="#2a2a2a", corner_radius=10)
        top_frame.pack(fill="x", padx=10, pady=5)

        self.entry_symbol_limit = ctk.CTkEntry(top_frame, placeholder_text="Sembol", width=100)
        self.entry_symbol_limit.pack(side="left", padx=5, pady=5)

        self.lbl_info_limit = ctk.CTkLabel(
            top_frame,
            text="İşlem Limiti 0   Fiyat 0   Taban 0   Tavan 0",
            text_color="white",
            anchor="w"
        )
        self.lbl_info_limit.pack(side="left", padx=10)

        # Orta bölüm
        middle_frame = ctk.CTkFrame(tab, fg_color="#1e1e1e")
        middle_frame.pack(fill="x", padx=10, pady=5)

        # Sol taraf (Alış)
        left = ctk.CTkFrame(middle_frame, fg_color="#1e1e1e")
        left.pack(side="left", expand=True, fill="both", padx=5)

        # fiyat + lot yan yana
        buy_row = ctk.CTkFrame(left, fg_color="#1e1e1e")
        buy_row.pack(pady=5)

        self.entry_price_buy = ctk.CTkEntry(buy_row, width=80, justify="center", placeholder_text="Fiyat")
        self.entry_price_buy.pack(side="left", padx=3)

        self.entry_lot_buy_limit = ctk.CTkEntry(buy_row, width=80, justify="center", placeholder_text="Lot")
        self.entry_lot_buy_limit.insert(0, "0")
        self.entry_lot_buy_limit.pack(side="left", padx=3)

        self.btn_buy_limit = ctk.CTkButton(
            left, text="Alış", fg_color="#258D71",
            hover_color="#5E9284", width=100,
            command=self._on_lim_buy
        )
        self.btn_buy_limit.pack(pady=10)

        # Sağ taraf (Satış)
        right = ctk.CTkFrame(middle_frame, fg_color="#1e1e1e")
        right.pack(side="left", expand=True, fill="both", padx=5)

        # fiyat + lot yan yana
        sell_row = ctk.CTkFrame(right, fg_color="#1e1e1e")
        sell_row.pack(pady=5)

        self.entry_price_sell = ctk.CTkEntry(sell_row, width=80, justify="center", placeholder_text="Fiyat")
        self.entry_price_sell.pack(side="left", padx=3)

        self.entry_lot_sell_limit = ctk.CTkEntry(sell_row, width=80, justify="center", placeholder_text="Lot")
        self.entry_lot_sell_limit.pack(side="left", padx=3)

        self.btn_sell_limit = ctk.CTkButton(
            right, text="Satış", fg_color="#C94B64",
            hover_color="#C2808D", width=100,
            command=self._on_lim_sell
        )
        self.btn_sell_limit.pack(pady=10)

        # Alt bölüm (Switchler)
        bottom_frame = ctk.CTkFrame(tab, fg_color="#1e1e1e")
        bottom_frame.pack(pady=5)

        self.switch_sms_limit = ctk.CTkSwitch(bottom_frame, text="Sms")
        self.switch_sms_limit.pack(side="left", padx=10)

        self.switch_email_limit = ctk.CTkSwitch(bottom_frame, text="Email")
        self.switch_email_limit.pack(side="left", padx=10)


    # --- Handlers ---
    def _on_buy(self):
        lot = self.entry_lot_buy.get()
        symbol = self.entry_symbol.get()
        sms = self.switch_sms.get()
        email = self.switch_email.get()
        if self.on_buy:
            self.on_buy(symbol, lot, sms, email)  # dışarıyı çağır
        else:
            print(f"Alış işlemi -> {symbol}, Lot: {lot}")

    def _on_sell(self):
        lot = self.entry_lot_sell.get()
        symbol = self.entry_symbol.get()
        sms = self.switch_sms.get()
        email = self.switch_email.get()
        if self.on_sell:
            self.on_sell(symbol, lot, sms, email)  # dışarıyı çağır
        else:
            print(f"Satış işlemi -> {symbol}, Lot: {lot}")

    def _on_lim_buy(self):
        lot = self.entry_lot_buy.get()
        symbol = self.entry_symbol.get()
        fiyat = self.entry_price_buy.get()
        sms = self.switch_sms.get()
        email = self.switch_email.get()
        if self.on_lim_buy:
            self.on_lim_buy(symbol, fiyat, lot, sms, email)  # dışarıyı çağır
        else:
            print(f"Alış işlemi -> {symbol}, Lot: {lot}")

    def _on_lim_sell(self):
        lot = self.entry_lot_sell.get()
        symbol = self.entry_symbol.get()
        fiyat = self.entry_price_sell.get()
        sms = self.switch_sms.get()
        email = self.switch_email.get()
        if self.on_lim_sell:
            self.on_lim_sell(symbol, fiyat, lot, sms, email)  # dışarıyı çağır
        else:
            print(f"Satış işlemi -> {symbol}, Lot: {lot}")

    def update_data(self, sembol, limit, fiyat, taban, tavan, lot_buy=None, lot_sell=None):
        self.entry_symbol.delete(0, "end")
        self.entry_symbol.insert(0, sembol)

        self.entry_symbol_limit.delete(0, "end")
        self.entry_symbol_limit.insert(0, sembol)

        self.lbl_info.configure(
            text=f"İşlem Limiti: {limit} | Fiyat: {fiyat} | Taban: {taban} | Tavan: {tavan}"
        )
        self.lbl_info_limit.configure(
            text=f"İşlem Limiti: {limit} | Fiyat: {fiyat} | Taban: {taban} | Tavan: {tavan}"
        )

        if lot_buy is not None:
            self.entry_lot_buy.delete(0, "end")
            self.entry_lot_buy.insert(0, str(lot_buy))

        if lot_sell is not None:
            self.entry_lot_sell.delete(0, "end")
            self.entry_lot_sell.insert(0, str(lot_sell))

        if lot_buy is not None:
            self.entry_lot_buy_limit.delete(0, "end")
            self.entry_lot_buy_limit.insert(0, str(lot_buy))

        if lot_sell is not None:
            self.entry_lot_sell_limit.delete(0, "end")
            self.entry_lot_sell_limit.insert(0, str(lot_sell))