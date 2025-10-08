import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplfinance as mpf
import pandas as pd
from dateutil import parser
from datetime import datetime

old_sembol = ""

# --- Canlı mum grafiği sınıfı ---
class CandleChart:
    def __init__(self, parent, symbol="PEHOL"):
        self.parent = parent
        self.symbol = symbol
        self.closed = False  # kapatma durumu

        # DataFrame: index -> datetime, columns -> Open/High/Low/Close
        self.ohlc = pd.DataFrame(columns=["Open","High","Low","Close"])

        # Matplotlib Figure
        self.fig, self.ax = plt.subplots(figsize=(8,4), dpi=100)
        self.fig.patch.set_facecolor('#1e1e1e')
        self.ax.set_facecolor('#111111')

        # Canvas TK içine gömme
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # Başlık
        self.ax.set_title(f"{self.symbol} - Canlı Grafik", color="#00eeff")
        self.current_minute = None

    # ✅ SEMBOL DEĞİŞTİRME FONKSİYONU
    def set_symbol(self):
        """Grafikteki sembolü değiştirir, verileri sıfırlar."""
        #if new_symbol != self.symbol:
        #    self.symbol = new_symbol
        self.ohlc = pd.DataFrame(columns=["Open","High","Low","Close"])
        self.current_minute = None
        self.ax.set_title(f"{self.symbol} - Canlı Grafik", color="#00eeff")
        self.redraw()
        print(f"Sembol değiştirildi: {self.symbol}")

    def update_from_tick(self, tick):
        global old_sembol
        """Tick format: {'Type':'T','Content':{'Symbol':..., 'Price':..., 'Date': '2025-09-18T13:59:21'}}"""
        if self.closed:
            return  # kapatılmış grafik için update yapma

        try:
            c = tick["Content"]
            sem = c["Symbol"]
            price = float(c["Price"])
            dt = parser.isoparse(c["Date"])   # ✅ değişiklik burada
        except Exception as e:
            print("Tick parse hatası:", e)
            return

        if sem != old_sembol:
            old_sembol = sem
            self.symbol = old_sembol
            self.set_symbol()
            return

        minute = dt.replace(second=0, microsecond=0)

        if self.current_minute is None:
            self.current_minute = minute
            self.ohlc = pd.DataFrame([{"Open":price,"High":price,"Low":price,"Close":price}], index=[minute])
        elif minute == self.current_minute:
            idx = self.ohlc.index[-1]
            h = max(self.ohlc.at[idx, "High"], price)
            l = min(self.ohlc.at[idx, "Low"], price)
            self.ohlc.at[idx, "High"] = h
            self.ohlc.at[idx, "Low"] = l
            self.ohlc.at[idx, "Close"] = price
        else:
            self.current_minute = minute
            new = pd.DataFrame([{"Open":price,"High":price,"Low":price,"Close":price}], index=[minute])
            self.ohlc = pd.concat([self.ohlc, new])
            
            max_candles = 150
            if len(self.ohlc) > max_candles:
                self.ohlc = self.ohlc.iloc[-max_candles:]

        self.redraw()

    def redraw(self):
        if self.closed or self.ohlc.empty:
            return
        try:
            self.ax.clear()
            s = mpf.make_mpf_style(base_mpf_style='nightclouds',
                                   marketcolors=mpf.make_marketcolors(up='lime', down='red', wick='white'))
            if not self.ohlc.empty:
                mpf.plot(self.ohlc, type='candle', ax=self.ax, style=s,
                         datetime_format='%H:%M', show_nontrading=True)
            self.ax.set_facecolor('#111111')
            self.ax.tick_params(axis='x', colors='white')
            self.ax.tick_params(axis='y', colors='white')
            self.ax.title.set_color("white")
            self.canvas.draw_idle()
        except Exception as e:
            print("Grafik yeniden çizme hatası:", e)

    def close(self):
        """Grafiği güvenli kapatma"""
        if self.closed:
            return
        self.closed = True
        try:
            print(f"{self.symbol} grafiği kapatılıyor...")
            self.canvas.get_tk_widget().pack_forget()
            self.canvas.get_tk_widget().destroy()
            plt.close(self.fig)
        except Exception as e:
            print("CandleChart close hatası:", e)