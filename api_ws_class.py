import hashlib, json, subprocess, ssl, socket
import pandas as pd
from websocket import create_connection, WebSocketTimeoutException

hostname = "www.algolab.com.tr"
api_hostname = f"https://{hostname}"
api_url = api_hostname + "/api"
socket_url = f"wss://{hostname}/api/ws"


class ConnectionTimedOutException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class AlgoLabSocket():
    def __init__(self, api_key, hash):
        """
        :String api_key: API_KEY
        :String hash: LoginUser'dan dönen Hash kodu
        :String type: T: Tick Paketi (Fiyat), D: Depth Paketi (Derinlik), O: Emir Statüsü
        :Obj type: callback: Soketin veriyi göndereceği fonksiyon
        """
        self.connected = False
        self.df = pd.DataFrame(columns=["Date", "Hisse", "Yon", "Fiyat", "Lot", "Deger", "Usd", "Alici", "Satici"])
        self.ws = None
        self.api_key = api_key
        self.hash = hash
        self.data = self.api_key + api_hostname + "/ws"
        self.checker = hashlib.sha256(self.data.encode('utf-8')).hexdigest()
        self.headers = {
            "APIKEY": self.api_key,
            "Authorization": self.hash,
            "Checker": self.checker
        }

    def load_ciphers(self):
        output = subprocess.run(["openssl", "ciphers"], capture_output=True).stdout
        output_str = output.decode("utf-8")
        ciphers = output_str.strip().split("\n")
        return ciphers[0]

    def close(self):
        self.connected = False
        self.ws = None

    def connect(self):
        print("Socket bağlantisi kuruluyor...")
        context = ssl.create_default_context()
        context.set_ciphers("DEFAULT")
        try:
            sock = socket.create_connection((hostname, 443))
            ssock = context.wrap_socket(sock, server_hostname=hostname)
            self.ws = create_connection(socket_url, socket=ssock, header=self.headers, timeout=0.1)
            self.ws.settimeout(30)
            self.connected = True
        except Exception as e:
            self.close()
            print(f"Socket Hatasi: {e}")
            return False
        if self.connected:
            print("Socket bağlantisi başarili.")
        return self.connected

    def recv(self):
        try:
            data = self.ws.recv()
        except WebSocketTimeoutException:
            data = ""
        except Exception as e:
            print("Recv Error:", e)
            data = None
            self.close()
        return data
    def send(self, d):
        try:
            # Eğer mesajda Token varsa override etme
            data = d.copy()
            if "Token" not in data:
                data["token"] = self.hash
            resp = self.ws.send(json.dumps(data))
        except Exception as e:
            print("Send Error:", e)
            resp = None
            self.close()
        return resp