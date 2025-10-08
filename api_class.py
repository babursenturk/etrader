import requests
import hashlib
import json
import inspect
import time
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

hostname = "www.algolab.com.tr"
api_hostname = f"https://{hostname}"
api_url = api_hostname + "/api"   # rest-api
api_sock_url = api_hostname + "/api/ws"   # rest-api


class API():
    def __init__(self, api_key, username, password, token=None, hash_val=None):
        try:
            self.api_code = api_key.split("-")[1]
        except Exception:
            self.api_code = api_key
        self.api_key = "API-" + self.api_code
        self.username = username
        self.password = password
        self.api_hostname = api_hostname
        self.api_url = api_url
        self.headers = {"APIKEY": self.api_key}
        self.token = token
        self.hash = hash_val
        self.last_request = 0.0
        self.LOCK = False

    # ----------------- LoginUser (SMS isteği atılır) -----------------
    def LoginUser(self):
        """
        Username/password ile ilk login isteğini gönderir.
        Dönen response'tan token beklenir (token SMS doğrulaması için gerekli).
        """
        try:
            f = inspect.stack()[0][3]
            u = self.encrypt(self.username)
            p = self.encrypt(self.password)
            payload = {"username": u, "password": p}
            endpoint = "/api/LoginUser"
            resp = self.post(endpoint=endpoint, payload=payload, login=True)
            return self.error_check(resp, f)
        except Exception as e:
            print(f"{f}() fonksiyonunda hata oluştu: {e}")
            return False

    # (class API içindeki ilgili metot)
    def LoginUserControl(self, sms_code):
        """
        Token ile birlikte SMS kodunu doğrular.
        Dönen yapıda hash ve/veya token varsa self.hash / self.token içine atar.
        """
        try:
            f = inspect.stack()[0][3]
            if not self.token:
                print("Token yok. Önce LoginUser() çağrılmalı ve token alınmalı.")
                return False

            t = self.encrypt(self.token)
            s = self.encrypt(sms_code)
            payload = {'token': t, 'password': s}
            endpoint = "/api/LoginUserControl"
            resp = self.post(endpoint=endpoint, payload=payload, login=True)
            data = self.error_check(resp, f)

            # **Önemli düzeltme**: hash ve token genelde `content` altındalar
            if data and isinstance(data, dict):
                content = data.get("content", {}) or {}
                if isinstance(content, dict):
                    if "hash" in content:
                        self.hash = content.get("hash")
                    if "token" in content:
                        self.token = content.get("token")

            return data
        except Exception as e:
            print(f"{f}() fonksiyonunda hata oluştu: {e}")
            return False

    # ---------------------- Session refresh ------------------------
    def SessionRefresh(self):
        """
        Oturum süresi uzatmak için atılan bir istektir.
        Cevap olarak Success: True veya eğer hash'iniz geçerliliğini yitirmişse 401 auth hatası olarak döner.
        """
        try:
            f = inspect.stack()[0][3]
            endpoint = "/api/SessionRefresh"
            payload = {}
            resp = self.post(endpoint, payload=payload)
            return self.error_check(resp, f)
        except Exception as e:
                print(f"{f}() fonsiyonunda hata oluştu: {e}")

    # ---------------------- Hisse Portföy ----------------------
    def GetInstantPosition(self, sub_account=""):
        """
        Yatırım Hesabınıza bağlı alt hesapları (101, 102 v.b.) ve limitlerini görüntüleyebilirsiniz.
        """
        try:
            f = inspect.stack()[0][3]
            end_point = "/api/InstantPosition"
            payload = {'Subaccount': sub_account}
            resp = self.post(end_point, payload)
            return self.error_check(resp, f)
        except Exception as e:
            print(f"{f}() fonsiyonunda hata oluştu: {e}")
    # ---------------------- CashFlow sorgusu ------------------------
    def CashFlow(self, sub_account=""):
        """
        /api/CashFlow endpoint'ine istek atar. Dönen JSON içindeki 'content'
        altında gelen t1, t2, ... alanlarını kullanıcıya gösterir.
        """
        try:
            f = inspect.stack()[0][3]
            end_point = "/api/CashFlow"
            payload = {'Subaccount': sub_account}
            resp = self.post(end_point, payload)
            return self.error_check(resp, f)
        except Exception as e:
            print(f"{f}() fonsiyonunda hata oluştu: {e}")
            return False

    # ---------------------- Sembol bilgisi ------------------------------
    def GetEquityInfo(self, symbol):
        """
        Sembolle ilgili tavan taban yüksek düşük anlık fiyat gibi bilgileri çekebilirsiniz.
        :String symbol: Sembol Kodu Örn: ASELS
        """
        try:
            f = inspect.stack()[0][3]
            endpoint = "/api/GetEquityInfo"
            payload = {'symbol': symbol}
            resp = self.post(endpoint, payload=payload)
            return self.error_check(resp, f)
        except Exception as e:
            print(f"{f}() fonsiyonunda hata oluştu: {e}")
            return False

    # ----------------------- Emir Gönderimi ---------------------------------
    def SendOrder(self, symbol, direction, pricetype, price, lot, sms, email, subAccount):
        try:
            end_point = "/api/SendOrder"
            payload = {
                "symbol": symbol,
                "direction": direction,
                "pricetype": pricetype,
                "price": price,
                "lot": lot,
                "sms": sms,
                "email": email,
                "subAccount": subAccount
            }
            resp = self.post(end_point, payload)
            try:
                data = resp.json()
                return data
            except:
                f = inspect.stack()[0][3]
                print(f"{f}() fonksiyonunda veri tipi hatasi. Veri, json formatindan farkli geldi:")
                
                print(resp.text)
                
        except Exception as e:
            f = inspect.stack()[0][3]
            print(f"{f}() fonsiyonunda hata oluştu: {e}")
    # ---------------------- POST helper ----------------------------
    def post(self, endpoint, payload, login=False):
        url = self.api_url
        if not login:
            checker = self.make_checker(endpoint, payload)
            headers = {"APIKEY": self.api_key,
                       "Checker": checker,
                       "Authorization": self.hash
                       }
        else:
            headers = {"APIKEY": self.api_key}
        return self._request("POST", url, endpoint, payload=payload, headers=headers)

    # ---------------------- Error / JSON kontrol -------------------
    def error_check(self, resp, f, silent=False):
        try:
            if resp is False or resp is None:
                if not silent: print(f"{f}() - response None veya False döndü")
                return False
            if resp.status_code == 200:
                return resp.json()
            if not silent:
                print(f"Error kodu: {resp.status_code}")
                print(resp.text)
            return False
        except Exception:
            if not silent:
                print(f"{f}() fonksiyonunda veri tipi hatasi. Veri, json formatindan farkli geldi:")
                try:
                    print(resp.text)
                except Exception:
                    print("<response okunamadı>")
            return False

    # ---------------------- Checker oluştur ------------------------
    def make_checker(self, endpoint, payload):
        body = json.dumps(payload).replace(' ', '') if len(payload) > 0 else ""
        data = self.api_key + self.api_hostname + endpoint + body
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    # ---------------------- HTTP request (throttle) ----------------
    def _request(self, method, url, endpoint, payload, headers):
        # basit lock / throttle (orijinal örneğe sadık)
        while self.LOCK:
            time.sleep(0.1)
        self.LOCK = True
        try:
            response = False
            if method == "POST":
                t = time.time()
                diff = t - self.last_request
                wait_for = self.last_request > 0.0 and diff < 5.0
                if wait_for:
                    time.sleep(5 - diff + 0.1)
                # requests.post(url + endpoint, ... )  --> orijinal örneklerde böyleydi
                response = requests.post(url + endpoint, json=payload, headers=headers, timeout=30)
                self.last_request = time.time()
        except requests.RequestException as e:
            print(f"HTTP hata: {e}")
            response = False
        finally:
            self.LOCK = False
        return response

    # ---------------------- AES encrypt (orijinal metoda sadık) -------
    def encrypt(self, text):
        iv = b'\0' * 16
        key = base64.b64decode(self.api_code.encode('utf-8'))
        cipher = AES.new(key, AES.MODE_CBC, iv)
        bytes_val = text.encode()
        padded_bytes = pad(bytes_val, 16)
        r = cipher.encrypt(padded_bytes)
        return base64.b64encode(r).decode("utf-8")