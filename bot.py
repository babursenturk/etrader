import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import requests
import hashlib
import json
import inspect
import time
import base64
import socket
import threading
import queue
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from api_class import API
from scrollable_panel import ScrollablePanel
from api_ws_class import AlgoLabSocket
from scrollable_grid import ScrollableGrid
from datetime import datetime
from tabbed_panel import TabbedPanel
from can_chart import CandleChart

running = True  # global flag
loop_id = 0
state_lap = 0
state_2_lap = 0
laptout = 0
session_tout = 0
msg_queue = queue.Queue()
stop_event = threading.Event()
global m_datetime
live_sembol = {"Type": "T", "Symbols": ["TKFEN", "TATEN"]}
focused_sembol = "ETILR"
focused_price = 0
focused_low = 0
focused_high = 0
focused_lot = 0
balance = 0
order_request = False
live_tout = 0
recon_req = False
threads = []

test_data = ['TATEN', '64.85', '3.05%', '64.9', '64.85', '64.55', '65.07', 'SAT']   #test for emir giris

# --- Konfigürasyon ---
apikey = "----------------------------------------------"
username = "11111111111"
password = "123456"
subAccount = ""
sembol = "TATEN"
direction = ""
pricetype = ""
price = ""
lot = ""
sms = False
email = False
sembol_datetime = ""

caption_sem = "Canlı Piyasa"
caption_proc = "İşlem Paneli"
caption_port = "Portföy"
caption_cash = "Nakit Akışı"


api = API(apikey, username, password, token=None, hash_val=None)

# --- GUI ---
root = ctk.CTk()
root.title("Premikra - Deniz Yatırım")
root.configure(fg_color="black")
root.geometry("1500x950")

style = ttk.Style()
style.theme_use("default")

# Entry stil
style.configure(
    "Custom.TEntry",
    padding=2,
    foreground="white",
    fieldbackground="#222831",   # entry iç rengi
    background="#222831",
    bordercolor="#00ADB5",
    insertcolor="white",
    font=("Arial", 10),
)

# Button stil
style.configure(
    "Custom.TButton",
    padding=2,
    foreground="white",
    background="#00ADB5",
    font=("Arial", 10, "bold"),
    borderwidth=0
)
style.map(
    "Custom.TButton",
    background=[("active", "#007B7F")],
    foreground=[("active", "white")]
)

def row_portfoy_selected(data):
    print("Portföyden secim:", data)


def row_sembol_selected(data):
    global price, sembol

    print("Sembollerden secim:", data)
    sembol = data[0]    #iletilecek emir globale atar.
    fiyat = round(float(data[1]), 2) if data[1] else 0.0    #iletilecek emir globaline atar.
    price = str(fiyat)
    degisim = data[2]
    yuksek = round(float(data[3]), 2) if data[3] else 0.0
    dusuk = round(float(data[4]), 2) if data[4] else 0.0
    alis = round(float(data[5]), 2) if data[5] else 0.0
    satis = round(float(data[6]), 2) if data[6] else 0.0
    #datem = data bunu yap. tarihi canli objeden cek.
    # Emir paneline gönderelim (örnek değerlerle harmanlanmış)
    emir_panel.update_data(
        sembol=sembol,
        limit=alis,       # buraya alış fiyatını koydum
        fiyat=fiyat,
        taban=dusuk,
        tavan=yuksek,
        lot_buy=0,        # burası sembolden gelmiyor, kullanıcı girecek ya da portfoyden bulup tüm lot'u alabiliriz SELL önerisi olarak.
        lot_sell=0
    )
    #chart.update_symbol(sembol, price, datem)

def handle_buy(sembol_son, lot_son, sms_son, email_son):
    global sembol
    global lot, direction, pricetype, order_request, sms, email, price, subAccount
    sembol = sembol_son
    lot = lot_son

    sms = False if (sms_son==0) else True
    email = False if (email_son==0) else True
    print("Parent BUY çağrıldı:", sembol, lot)

    if lot == 0: return
    direction = "BUY"
    pricetype = "piyasa"
    subAccount = ""

    print(sembol,"-",direction,"-",pricetype,"-",price,"-",lot_son,"-",sms,"-",email,"-",subAccount)
    order_request = True    #siparisi gec

def handle_sell(sembol_son, lot_son, sms_son, email_son):
    #global price
    #print("Parent SELL çağrıldı:", sembol, lot)
    #price = 64
    #row_sembol_selected(test_data)
    global sembol
    global lot, direction, pricetype, order_request, sms, email, price, subAccount
    sembol = sembol_son
    lot = lot_son

    sms = False if (sms_son==0) else True
    email = False if (email_son==0) else True
    print("Parent SELL çağrıldı:", sembol, lot)

    if lot == 0: return
    direction = "SELL"
    pricetype = "piyasa"
    subAccount = ""

    print(sembol,"-",direction,"-",pricetype,"-",price,"-",lot_son,"-",sms,"-",email,"-",subAccount)
    order_request = True    #satisi gec

def handle_lim_buy(sembol_son, fiyat, lot_son, sms_son, email_son):
    print("buy")

def handle_lim_sell(sembol_son, fiyat, lot_son, sms_son, email_son):
    print("sell")

def handle_login():
    u = username_entry.get()
    p = password_entry.get()
    api.username = u
    api.password = p
    resp = api.LoginUser()
    if resp and "content" in resp and "token" in resp["content"]:
        api.token = resp["content"]["token"]
        show_toast(root, "Lütfen telefonunuza gelen kodu giriniz.")
        #messagebox.showinfo("Bilgi", "Lütfen telefonunuza gelen SMS'i giriniz.")
    else:
        messagebox.showerror("Hata", "Login başarısız!")

def handle_sms():
    sms = sms_entry.get().strip()
    resp = api.LoginUserControl(sms)
    if resp and "content" in resp and "hash" in resp["content"]:
        api.hash = resp["content"]["hash"]
        #messagebox.showinfo("Bilgi", "SMS doğrulandı. Veri çekilebilir.")
        threading.Thread(target=rest_worker, daemon=True).start()


    else:
        messagebox.showerror("Hata", "SMS doğrulama başarısız!")

# LOGIN ve SMS Kısmı --------------------------------------------------
frame_top = ctk.CTkFrame(root, fg_color="black")
frame_top.pack(anchor="ne", pady=10, padx=10)

username_entry = ctk.CTkEntry(frame_top, width=150, fg_color="#222831", text_color="white")
username_entry.insert(0, username)
username_entry.grid(row=0, column=0, padx=5)

password_entry = ctk.CTkEntry(frame_top, width=150, show="*", fg_color="#222831", text_color="white")
password_entry.insert(0, password)
password_entry.grid(row=0, column=1, padx=5)

login_button = ctk.CTkButton(frame_top, text="Login", fg_color="#00ADB5", hover_color="#007B7F", command=handle_login)
login_button.grid(row=0, column=2, padx=5)

sms_entry = ctk.CTkEntry(frame_top, width=100, fg_color="#222831", text_color="white")
sms_entry.grid(row=0, column=3, padx=5)

sms_button = ctk.CTkButton(frame_top, text="SMS Onay", fg_color="#00ADB5", hover_color="#007B7F", command=handle_sms)
sms_button.grid(row=0, column=4, padx=5)

# [sembol, fiyat, f"{degisim}%", yuksek,dusuk, alis, satis, yon]
columns = ["Sembol", "Fiyat", "Değişim %", "Yüksek","Düşük","Alış", "Satış", "Yön"]
sembol_panel = ScrollableGrid(root, caption_sem, columns, col_widths=[100, 80,80, 80, 80, 80, 100, 80], left=20, top=50, width=600, on_select=row_sembol_selected)

# ---------- PANELLER -------------------------------------------
columns_port = ["Sembol", "Lot", "Maliyet", "Fiyat", "Kar/Zarar"]
portfoy_panel = ScrollableGrid(root, caption_port, columns_port, col_widths=[100, 80, 80, 80, 100], left=660, top=50, on_select=row_portfoy_selected)

emir_panel = TabbedPanel(root, caption_proc, ["Limit", "Piyasa"], on_buy=handle_buy, on_sell=handle_sell, on_lim_buy=handle_lim_buy, on_lim_sell=handle_lim_sell, left = 20, top = 450, height = 300, width=550)
#emir_panel.update_data("TATEN", limit=186.19, fiyat=59.2, taban=53.45, tavan=65.25, lot_buy=300, lot_sell=50)

columns_cash = ["t0", "t1", "t2"]
cash_panel = ScrollableGrid(root, caption_cash, columns_cash, col_widths=[100, 100, 100], width = 300, height = 100, left=1150, top=50)

frame_graph = ctk.CTkFrame(root, corner_radius=15, fg_color="#1e1e1e", height = 700, width = 700)
frame_graph.place(x=660, y=450)
chart = CandleChart(frame_graph, symbol="PEHOL")

# --- Yeni Sembol Ekleme Alanı ----------------------------------
# Çerçeve
frame_symbol = ctk.CTkFrame(root, bg_color="black", height = 35, width = 150)
frame_symbol.place(x=480, y=50)

entry_symbol = ctk.CTkEntry(frame_symbol, width=60)
entry_symbol.place(x=5, y=3)

def add_symbol():
    global soket
    global focused_sembol
    new_sym = entry_symbol.get().strip().upper()
    focused_sembol = new_sym
    if new_sym and new_sym not in live_sembol["Symbols"]:
        live_sembol["Symbols"].append(new_sym)
        print("Eklendi:", new_sym)
        print("Güncel liste:", live_sembol["Symbols"])
                    
        if soket.connected:
            soket.send(live_sembol)
    entry_symbol.delete(0, ctk.END)

btn_symbol_add = ctk.CTkButton(frame_symbol, text="Ekle", fg_color="#00ADB5", hover_color="#007B7F", width = 40, command=add_symbol)
btn_symbol_add.place(x=100, y=3)    

m_datetime = ctk.CTkLabel(root, text="-", font=ctk.CTkFont(size=18), text_color="white")
m_datetime.place(x=10, y=10)
m_liveindicator = ctk.CTkLabel(root, text="●", font=ctk.CTkFont(size=18), text_color="#00FF00")
m_liveindicator.place(x=200, y=10)

def show_toast(root, message, color="gray", duration=3000):
    toast = ctk.CTkToplevel(root)
    toast.overrideredirect(True)
    toast.configure(fg_color="black")

    x = root.winfo_x() + 400
    y = root.winfo_y() + 100
    toast.geometry(f"+{x}+{y}")

    label = ctk.CTkLabel(toast, text=message, text_color="white", fg_color=color, font=ctk.CTkFont(size=11))
    label.pack(padx=10, pady=5)

    toast.after(duration, toast.destroy)

def reconnect_socket():
    global soket
    try:
        soket.close()
    except:
        pass
    soket = AlgoLabSocket(apikey, api.hash)
    soket.connect()
    if soket.connected:
        soket.send(live_sembol)
        print("Soket yeniden bağlandı.")

def socket_listener():
    global soket, state_lap, live_tout, recon_req
    while not stop_event.is_set():
        if soket and soket.connected:
            try:
                data_sok = soket.recv()
                if data_sok:
                    #print("[THREAD] Veri alındı:", data_sok)  # gelen ham veri
                    msg_queue.put(("LIVE_RESP", data_sok))  # GUI thread'ine aktarıyoruz
                else:
                    print("[THREAD] Boş veri döndü. Reconnecting...")
                    reconnect_socket()
                    
            except socket.timeout:
                continue
            except Exception as e:
                print("Soket hatası:", e)
                reconnect_socket()
                break
        else:
            print("[THREAD] Soket bağlı değil")
            break
        time.sleep(0.1)  # CPU'yu yakmamak için küçük uyku

# --- Cashflow Alanı --------------------
def update_cashpanel(data):
    #print(data)
    if not data or "content" not in data:
        return

    pos = data["content"]
    t0 = pos.get("t0", "") + " TL"
    t1 = pos.get("t1", "") + " TL"
    t2 = pos.get("t2", "") + " TL"

    #print(t0, "-", t1, "-", t2)
    cash_panel.update_row(
        t0,
        [t0, t1, t2]
    )    
# ------------ Emir paneli ---------------
#def update_emirpanel():
#    tab1 = emir_panel.get_tab("Limit")
#    lbl1 = ctk.CTkLabel(tab1, text="Ali", text_color="white")
#    lbl1.pack(pady=10)

#    tab2 = emir_panel.get_tab("Piyasa")
#    lbl2 = ctk.CTkLabel(tab2, text="Patron", text_color="orange")
#    lbl2.pack(pady=10)

# --- Portföy Paneli (scrollable) ---
def update_portfolio(data):
    portfoy_panel.clear()
    if data and data.get("success"):
        for pos in data["content"]:
            code = pos.get("code", "")
            if code in ["-", "TRY"]:
                continue

            stock = f"{float(pos['totalstock']):.2f}" if pos.get("totalstock") else ""
            maliyet = pos.get("maliyet", "")
            price = pos.get("unitprice", "")
            try:
                profit = float(pos["profit"])
                profit_str = f"{profit:.2f} TL"
                #profit_color = "green" if profit > 0 else "red" if profit < 0 else "white"
            except:
                profit_str = str(pos.get("profit", "")) + " TL"
                #profit_color = "white"

            portfoy_panel.update_row(code, [code, stock, maliyet, price, f"{profit_str}"])
        return

def read_sembolinfo(sembol, data):
    if not data or "Content" not in data:
        return

    if "Content" in data and "Type" in data:
        mesaj_tip = data["Type"]

    if (mesaj_tip == "T"):
        try:
            pos = data["Content"]
            if sembol == pos.get("Symbol", ""):
                return True
            else:
                return False
        except Exception as e:
            print("sembol compare hatasi", e)

# --- Sembol veri ---------------------
def update_sembol(data):
    if not data or "Content" not in data:
        return

    if "Content" in data and "Type" in data:
        mesaj_tip = data["Type"]

    if (mesaj_tip == "T"):
        try:
            pos = data["Content"]
            sembol = pos.get("Symbol", "")
            fiyat = pos.get("Price", "")
            alis  = pos.get("Ask", "")
            satis = pos.get("Bid", "")
            yuksek = pos.get("High", "")
            dusuk = pos.get("Low", "")
            degisim = pos.get("ChangePercentage", "")
            #tarih = pos.get("Date","")
            if pos.get("Direction","") == "B":
                yon = "AL"
            elif pos.get("Direction","") == "S":
                yon = "SAT"
        except Exception as e:
            print("live parse hatasi", e)
        # grid_panel global ya da dışarıdan parametre olabilir
        sembol_panel.update_row(
            sembol,
            [sembol, fiyat, f"{degisim}%", yuksek,dusuk, alis, satis, yon]
        )
    elif (mesaj_tip == "O"):
        print(data["Content"])

def rest_worker():
    global order_request, state_2_lap, running

    while not stop_event.is_set():
        try:
            if order_request:
                try:
                    resp = api.SendOrder(sembol,direction,pricetype,price,lot,sms,email,subAccount)
                    msg_queue.put(("ORDER_RESP", resp))
                except Exception as e:
                    msg_queue.put(("ORDER_ERROR", str(e)))
                finally:
                    order_request = False
                continue  # order varsa diğer işlere bakmadan devam et
            else:
                if state_2_lap == 0:
                    state_2_lap = 1
                    if session := api.SessionRefresh():
                        try:
                            print(session)
                        except Exception as e:
                            print(f"Hata oluştu: {e}")
                elif state_2_lap == 1:
                    state_2_lap = 2
                    resp_pos = api.GetInstantPosition(subAccount)  
                    if resp_pos:
                        msg_queue.put(("PORTFOLIO_RESP", resp_pos))
                elif state_2_lap == 2:
                    state_2_lap = 0
                    resp_cash = api.CashFlow(subAccount)
                    if resp_cash:
                        msg_queue.put(("CASHFLOW_RESP", resp_cash))
        except Exception as e:
            print("rest worker error", e)
        
        time.sleep(5)

def ws_heartbeat_worker():
    global soket
    while not stop_event.is_set():
        if soket and soket.connected:
            try:
                hb = {"Type": "H", "Token": api.token}
                soket.send(hb)
                print("soket heartbeat", hb)
            except Exception as e:
                print("ws_heartbeat error:", e)
        time.sleep(60)   # 30 sn’de bir ws heartbeat

def stop_threads():
    stop_event.set()
    for t in threads:
        if t.is_alive():
            t.join(timeout=2)
    threads.clear()

def on_close():
    global running, threads, loop_id
    print("Uygulama kapatılıyor...")

    for aid in root.tk.call('after', 'info'):
        try:
            root.after_cancel(aid)
        except:
            pass

    # 1) sinyali ver (thread'ler bu flag'i kontrol etmeli)
    running = False
    stop_event.set()

    try:
        if chart:
            chart.close()  # ✅ CandleChart güvenli kapatma
    except Exception as e:
        print("Chart close hatası:", e)

    # 2) soketi güvenli kapat
    try:
        if 'soket' in globals() and soket and getattr(soket, "connected", False):
            try:
                soket.close()
                print("Soket bağlantısı kapatıldı.")
            except Exception as e:
                print("Soket kapatma hatası:", e)
    except Exception as e:
        print("Soket kontrol hatası:", e)

    # 3) after() ile planlı loop'u iptal et (loop_id geçerli ise)
    try:
        if isinstance(loop_id, int) and loop_id != 0:
            root.after_cancel(loop_id)
            print("after loop iptal edildi.")
    except Exception as e:
        print("after_cancel hatası:", e)

    # 4) thread'leri join et (kısa timeout)
    for t in threads:
        try:
            if t.is_alive():
                print(f"Thread join denemesi: {t.name}")
                t.join(timeout=2)
        except Exception as e:
            print("Thread join hatası:", e)

    # 5) biraz bekle, sonra GUI'yi kapat
    try:
        time.sleep(0.1)
    except:
        pass

    try:
        root.destroy()
    except Exception as e:
        print("root.destroy hatası:", e)

root.protocol("WM_DELETE_WINDOW", on_close)
# --- loop() ---
def loop():
    global state_lap, soket, now_str, recon_req, loop_id
    global threads, running

    if not running:
        return
    #update_sembol(dummy_msg)
    #update_sembol(dummy_msg2)
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    m_datetime.configure(text=f"{now_str}")
            
    if api.hash:  # sadece login + sms doğrulama yapılmışsa

        if state_lap == 0:
            print("soket connecting")
            soket = AlgoLabSocket(apikey, api.hash) 
            soket.connect() 

            if soket.connected:
                print("soket connected")
                state_lap = 1
                soket.send(live_sembol)
                stop_event.clear()
                threads = []
                t1 = threading.Thread(target=socket_listener, daemon=True)
                t2 = threading.Thread(target=ws_heartbeat_worker, daemon=True)
                t1.start()
                t2.start()
                threads.extend([t1,t2])

        elif state_lap == 1:
            if soket.connected:
                if msg_queue.empty():
                    #print("[MAIN] Queue boş, henüz veri yok")
                    m_liveindicator.configure(text_color="#ff0000")
                while not msg_queue.empty():
                    try:
                        typ, raw = msg_queue.get_nowait()
                        m_liveindicator.configure(text_color="#00FF00")
                        #print("[MAIN] Queue'dan veri çekildi:", raw)
                        if typ == "ORDER_RESP":
                            print(raw)
                            
                            if "content" in raw:
                                order_mesaj = raw["content"]
                                show_toast(root, order_mesaj, color="#2992e7")
    
                        elif typ == "LIVE_RESP":
                            msg = json.loads(raw)
                            update_sembol(msg)

                            if (read_sembolinfo(sembol, msg)):  # Eger odaklandigimiz sembolun datası gelmisse grafigi guncelleyelim.
                                chart.update_from_tick(msg)
                        elif typ == "PORTFOLIO_RESP":
                            update_portfolio(raw)
                        elif typ == "CASHFLOW_RESP":
                            update_cashpanel(raw)
                    except Exception as e:
                        print("Json parse hatası:", e)


    if not stop_event.is_set():
        if not root.winfo_exists():
            return
        loop_id = root.after(100, loop)  # 500ms aralık (GUI akıcı)
    else:
        print("[MAIN] stop_event set, çıkış için root.destroy() bekleniyor")


# --- setup() ---
def setup():
    #update_emirpanel()
    loop()  # döngüyü başlat
    root.mainloop()

if __name__ == "__main__":
    setup()
