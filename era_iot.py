# # era_iot.py
# # Thư viện Era IoT cho MicroPython
# from umqtt_robust import MQTTClient
# import ujson
# import network
# import time

# class EraIoT:
#     def __init__(self, ssid, password, token):
#         self._ssid = ssid
#         self._password = password
#         self._token = token
#         self._client = None
#         self._callbacks = {}

#     def _connect_wifi(self):
#         wlan = network.WLAN(network.STA_IF)
#         wlan.active(True)
#         wlan.connect(self._ssid, self._password)
#         while not wlan.isconnected():
#             time.sleep(0.5)
#         print("WiFi connected")

#     def connect(self):
#         self._connect_wifi()
#         self._client = MQTTClient(self._token, 'mqtt1.eoh.io')
#         self._client.set_callback(self._on_message)
#         self._client.set_last_will(self._get_topic("/is_online"), '{"ol":0}', retain=True)
#         self._client.connect()
#         self._client.subscribe(self._get_topic("/down"))
#         self._client.subscribe(self._get_topic("/virtual_pin/#"))
#         self._client.publish(self._get_topic("/is_online"), ujson.dumps({"ol":1, "wifi_ssid":self._ssid, "ask_configuration":1}), retain=True)

#     def _get_topic(self, suffix):
#         return "eoh/chip/%s%s" % (self._token, suffix)

#     def _on_message(self, topic, payload):
#         topic = topic.decode() if isinstance(topic, bytes) else topic
#         payload = payload.decode() if isinstance(payload, bytes) else payload
        
#         try:
#             if topic in self._callbacks:
#                 self._callbacks[topic](payload)
#             elif topic.startswith(self._get_topic("/virtual_pin/")):
#                 pin = topic.split("/")[-1]
#                 if pin in self._callbacks:
#                     msg = ujson.loads(payload)
#                     value = msg.get("value", 0)
#                     # Pass both topic and value to match Blockly expectation
#                     self._callbacks[pin](topic, value)
#         except Exception as e:
#             print(f"Error processing message: {e}")

#     def publish(self, topic, message):
#         if self._client:
#             self._client.publish(topic, message)

#     def on_receive_message(self, topic, callback):
#         self._callbacks[topic] = callback

#     def check_message(self):
#         if self._client:
#             self._client.check_msg()

#     def wifi_connected(self):
#         return network.WLAN(network.STA_IF).isconnected()

# # Singleton để tương thích Blockly
# era = None

# def connect_wifi(ssid, password, token):
#     global era
#     try:
#         era = EraIoT(ssid, password, token)
#         era.connect()
#         return True
#     except Exception as e:
#         print(f"Connection failed: {e}")
#         return False

# def connect_broker(server="mqtt1.eoh.io", port=1883, username=None, password=None):
#     pass  # không cần vì đã xử lý trong connect_wifi()

# def publish(topic, message):
#     if era:
#         era.publish(topic, message)

# def on_receive_message(topic, callback):
#     if era:
#         era.on_receive_message(topic, callback)

# def check_message():
#     if era:
#         era.check_message()

# def wifi_connected():
#     return era and era.wifi_connected()

# def is_connected():
#     return wifi_connected()

# def virtual_write(pin, value):
#     """Write value to virtual pin"""
#     if era and era._client:
#         topic = f"eoh/chip/{era._token}/virtual_pin/{pin}"
#         payload = ujson.dumps({"value": value})
#         era._client.publish(topic, payload)

# def publish_virtual_pin(pin, value):
#     """Alias for virtual_write for backward compatibility"""
#     virtual_write(pin, value)
    
# def get_connection_status():
#     if era:
#         return {
#             'wifi': era.wifi_connected(),
#             'mqtt': era._client is not None,
#             'token': era._token
#         }
#     return {'wifi': False, 'mqtt': False, 'token': None}

# def on_virtual_pin_change(pin, callback):
#     """Register callback for virtual pin changes"""
#     if era:
#         era.on_receive_message(str(pin), callback)

# def get_virtual_pin_value(pin):
#     """Get current value of virtual pin"""
#     # Implementation needed based on ERA IoT API
#     pass

# # era_iot.py - Corrected version
# # Thư viện Era IoT cho MicroPython
# from umqtt_robust import MQTTClient
# import ujson
# import network
# import time

# class EraIoT:
#     def __init__(self, wifi_ssid, wifi_password, era_token):
#         self._wifi_ssid = wifi_ssid
#         self._wifi_password = wifi_password
#         self._era_token = era_token  # Token dùng cho cả username và password MQTT
#         self._client = None
#         self._callbacks = {}
#         print(f"[DEBUG] EraIoT initialized with:")
#         print(f"  WiFi SSID: {wifi_ssid}")
#         print(f"  WiFi Password: {'*' * len(wifi_password) if wifi_password else 'None'}")
#         print(f"  Era Token: {era_token[:8]}...{era_token[-4:] if len(era_token) > 12 else era_token}")

#     def _connect_wifi(self):
#         print(f"[DEBUG] Connecting to WiFi: {self._wifi_ssid}")
#         wlan = network.WLAN(network.STA_IF)
#         wlan.active(True)
        
#         # Kiểm tra xem đã kết nối chưa
#         if wlan.isconnected():
#             print(f"[DEBUG] Already connected to WiFi")
#             return True
            
#         wlan.connect(self._wifi_ssid, self._wifi_password)
#         timeout = 30  # 30 seconds timeout
#         start_time = time.time()
        
#         while not wlan.isconnected():
#             if time.time() - start_time > timeout:
#                 print(f"[ERROR] WiFi connection timeout after {timeout}s")
#                 return False
#             time.sleep(0.5)
#             print(".", end="")
            
#         print(f"\n[SUCCESS] WiFi connected to {self._wifi_ssid}")
#         print(f"[INFO] IP address: {wlan.ifconfig()[0]}")
#         return True

#     def connect(self):
#         # Kết nối WiFi trước
#         if not self._connect_wifi():
#             raise Exception("Failed to connect to WiFi")
            
#         # Kết nối MQTT với Era IoT
#         print(f"[DEBUG] Connecting to MQTT broker: mqtt1.eoh.io")
#         print(f"[DEBUG] MQTT Client ID: {self._era_token}")
#         print(f"[DEBUG] MQTT Username: {self._era_token}")
#         print(f"[DEBUG] MQTT Password: {self._era_token}")
        
#         try:
#             # Era IoT sử dụng token làm:
#             # - client_id
#             # - username 
#             # - password
#             self._client = MQTTClient(
#                 client_id="01",
#                 server='mqtt1.eoh.io',
#                 port=1883,
#                 user=self._era_token,      # Username = token
#                 password=self._era_token   # Password = token
#             )
            
#             self._client.set_callback(self._on_message)
#             self._client.set_last_will(self._get_topic("/is_online"), '{"ol":0}', retain=True)
#             self._client.connect()
            
#             # Subscribe to topics
#             down_topic = self._get_topic("/down")
#             vpin_topic = self._get_topic("/virtual_pin/#")
            
#             print(f"[DEBUG] Subscribing to: {down_topic}")
#             print(f"[DEBUG] Subscribing to: {vpin_topic}")
            
#             self._client.subscribe(down_topic)
#             self._client.subscribe(vpin_topic)
            
#             # Publish online status
#             online_payload = ujson.dumps({
#                 "ol": 1, 
#                 "wifi_ssid": self._wifi_ssid, 
#                 "ask_configuration": 1
#             })
#             online_topic = self._get_topic("/is_online")
#             print(f"[DEBUG] Publishing online status to: {online_topic}")
#             self._client.publish(online_topic, online_payload, retain=True)
            
#             print(f"[SUCCESS] MQTT connected to Era IoT with token: {self._era_token[:8]}...")
            
#         except Exception as e:
#             print(f"[ERROR] MQTT connection failed: {e}")
#             raise

#     def _get_topic(self, suffix):
#         topic = "eoh/chip/%s%s" % (self._era_token, suffix)
#         return topic

#     def _on_message(self, topic, payload):
#         topic = topic.decode() if isinstance(topic, bytes) else topic
#         payload = payload.decode() if isinstance(payload, bytes) else payload
        
#         print(f"[DEBUG] Received message - Topic: {topic}, Payload: {payload}")
        
#         try:
#             if topic in self._callbacks:
#                 self._callbacks[topic](payload)
#             elif topic.startswith(self._get_topic("/virtual_pin/")):
#                 pin = topic.split("/")[-1]
#                 print(f"[DEBUG] Virtual pin message - Pin: {pin}")
#                 if pin in self._callbacks:
#                     try:
#                         msg = ujson.loads(payload)
#                         value = msg.get("value", payload)  # Fallback to raw payload
#                         print(f"[DEBUG] Calling callback for pin {pin} with value: {value}")
#                         self._callbacks[pin](topic, value)
#                     except:
#                         # If JSON parsing fails, use raw payload
#                         print(f"[DEBUG] JSON parse failed, using raw payload: {payload}")
#                         self._callbacks[pin](topic, payload)
#                 else:
#                     print(f"[DEBUG] No callback registered for pin {pin}")
#         except Exception as e:
#             print(f"[ERROR] Error processing message: {e}")

#     def publish(self, topic, message):
#         if self._client:
#             print(f"[DEBUG] Publishing - Topic: {topic}, Message: {message}")
#             self._client.publish(topic, message)
#         else:
#             print("[ERROR] MQTT client not connected")

#     def on_receive_message(self, topic, callback):
#         print(f"[DEBUG] Registering callback for topic/pin: {topic}")
#         self._callbacks[topic] = callback

#     def check_message(self):
#         if self._client:
#             try:
#                 self._client.check_msg()
#             except Exception as e:
#                 print(f"[ERROR] Check message failed: {e}")
#                 # Try to reconnect
#                 try:
#                     self.connect()
#                 except:
#                     pass

#     def wifi_connected(self):
#         return network.WLAN(network.STA_IF).isconnected()

# # Singleton để tương thích Blockly
# era = None

# def connect_wifi(wifi_ssid, wifi_password, era_token):
#     """
#     Kết nối WiFi và Era IoT
#     Args:
#         wifi_ssid: Tên WiFi
#         wifi_password: Mật khẩu WiFi  
#         era_token: Token Era IoT (dùng cho cả username và password MQTT)
#     """
#     global era
#     print(f"[DEBUG] connect_wifi called with:")
#     print(f"  WiFi SSID: {wifi_ssid}")
#     print(f"  WiFi Password: {'*' * len(wifi_password) if wifi_password else 'None'}")
#     print(f"  Era Token: {era_token}")
    
#     # Validate inputs
#     if not wifi_ssid or not wifi_password or not era_token:
#         print("[ERROR] Missing required parameters (wifi_ssid, wifi_password, or era_token)")
#         return False
        
#     if len(era_token) < 10:  # Basic token validation
#         print("[ERROR] Era token seems too short")
#         return False
    
#     try:
#         era = EraIoT(wifi_ssid, wifi_password, era_token)
#         era.connect()
#         print("[SUCCESS] Era IoT connection established")
#         return True
#     except Exception as e:
#         print(f"[ERROR] Connection failed: {e}")
#         era = None
#         return False

# def connect_broker(server="mqtt1.eoh.io", port=1883, username=None, password=None):
#     """Compatibility function - not needed as handled in connect_wifi"""
#     pass

# def publish(topic, message):
#     if era:
#         era.publish(topic, message)
#     else:
#         print("[ERROR] Era IoT not connected. Call connect_wifi() first.")

# def on_receive_message(topic, callback):
#     if era:
#         era.on_receive_message(topic, callback)
#     else:
#         print("[ERROR] Era IoT not connected. Call connect_wifi() first.")

# def check_message():
#     if era:
#         era.check_message()

# def wifi_connected():
#     return era and era.wifi_connected()

# def is_connected():
#     return wifi_connected() and era and era._client

# def virtual_write(pin, value):
#     """Write value to virtual pin"""
#     if era and era._client:
#         topic = f"eoh/chip/{era._era_token}/virtual_pin/{pin}"
#         payload = ujson.dumps({"value": value})
#         print(f"[DEBUG] Virtual write - Pin: {pin}, Value: {value}, Topic: {topic}")
#         era._client.publish(topic, payload)
#     else:
#         print("[ERROR] Era IoT not connected")

# def publish_virtual_pin(pin, value):
#     """Alias for virtual_write for backward compatibility"""
#     virtual_write(pin, value)
    
# def get_connection_status():
#     """Get current connection status"""
#     if era:
#         return {
#             'wifi': era.wifi_connected(),
#             'mqtt': era._client is not None,
#             'wifi_ssid': era._wifi_ssid,
#             'era_token': era._era_token
#         }
#     return {'wifi': False, 'mqtt': False, 'wifi_ssid': None, 'era_token': None}

# def on_virtual_pin_change(pin, callback):
#     """Register callback for virtual pin changes"""
#     if era:
#         era.on_receive_message(str(pin), callback)
#     else:
#         print("[ERROR] Era IoT not connected. Call connect_wifi() first.")

# def get_virtual_pin_value(pin):
#     """Get current value of virtual pin - would need server API"""
#     # This would require querying the Era IoT server
#     # Implementation depends on Era IoT API
#     pass

# # Helper function for debugging
# def debug_status():
#     """Print current connection status"""
#     status = get_connection_status()
#     print("=== Era IoT Status ===")
#     print(f"WiFi: {'Connected' if status['wifi'] else 'Disconnected'}")
#     print(f"MQTT: {'Connected' if status['mqtt'] else 'Disconnected'}")
#     print(f"WiFi SSID: {status['wifi_ssid']}")
#     print(f"Era Token: {status['era_token'][:8] + '...' if status['era_token'] else 'None'}")
#     print("====================")

# # Test function
# def test_connection():
#     """Test function để kiểm tra kết nối"""
#     print("=== Testing Era IoT Connection ===")
    
#     # Thay bằng thông tin thực tế của bạn
#     wifi_ssid = "R&D"
#     wifi_password = "kdi@2017" 
#     era_token = "dff9a7dd-726e-44f8-b6d1-84d3873148bd"
    
#     print("1. Testing connection...")
#     if connect_wifi(wifi_ssid, wifi_password, era_token):
#         print("2. Connection successful!")
#         debug_status()
        
#         print("3. Testing virtual pin write...")
#         publish_virtual_pin(1, "Hello Era IoT")
        
#         print("4. Testing message check...")
#         for i in range(5):
#             check_message()
#             time.sleep(1)
#     else:
#         print("2. Connection failed!")
        
# test_connection()

"""
Era IoT helper for MicroPython – fixed version (compat 🛠️)
-----------------------------------------------------------
*  Short or fixed `client_id` (≤23 chars)
*  Clean debug logging
*  Works with *all* MicroPython `umqtt_robust` versions
"""

from umqtt_robust import MQTTClient
import network, ujson, time, ubinascii, machine

__all__ = [
    "EraIoT", "connect_wifi", "publish", "publish_virtual_pin",
    "on_receive_message", "on_virtual_pin_change", "check_message",
    "wifi_connected", "is_connected", "debug_status",
]


class EraIoT:
    """High-level helper for Era IoT MQTT cloud."""

    def __init__(
        self,
        wifi_ssid: str,
        wifi_password: str,
        era_token: str,
        *,
        client_id: str | None = None,
        keepalive: int = 60,
        debug: bool = True,
    ) -> None:
        self._ssid = wifi_ssid
        self._pw = wifi_password
        self._token = era_token  # also used for MQTT user/pass
        self._fixed_cid = client_id  # may be None –> auto
        self._keepalive = keepalive
        self._debug = debug

        self._client: MQTTClient | None = None
        self._cbs: dict[str, callable] = {}

        self._log("EraIoT init – SSID=%s | CID=%s" % (wifi_ssid, (client_id or "<auto>")[:23]))

    # ------------------------------------------------------------------
    def _log(self, msg: str) -> None:
        if self._debug:
            print("[ERA]", msg)

    # Wi‑Fi -------------------------------------------------------------
    def _ensure_wifi(self, timeout: int = 30) -> None:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        if wlan.isconnected():
            self._log("Wi‑Fi already connected")
            return
        self._log(f"Connecting Wi‑Fi → {self._ssid}")
        wlan.connect(self._ssid, self._pw)
        tic = time.time()
        while not wlan.isconnected():
            if time.time() - tic > timeout:
                raise OSError("Wi‑Fi timeout")
            time.sleep(0.5)
            print(".", end="")
        print()
        self._log("Wi‑Fi OK – IP %s" % wlan.ifconfig()[0])

    # MQTT --------------------------------------------------------------
    def _auto_client_id(self) -> bytes:
        if self._fixed_cid:
            return self._fixed_cid.encode()
        suffix = ubinascii.hexlify(machine.unique_id()).decode()[:4]
        base = self._token.replace("-", "")[:19]
        return f"{base}{suffix}".encode()

    def _topic(self, suffix: str) -> str:
        return f"eoh/chip/{self._token}{suffix}"

    def connect(self, host: str = "mqtt1.eoh.io", port: int = 1883, ssl: bool = False):
        self._ensure_wifi()
        cid = self._auto_client_id()
        self._log(f"MQTT connect → {host}:{port} CID={cid.decode()}")

        # some umqtt builds don't accept clean_session kwarg → omit for compat
        self._client = MQTTClient(
            client_id=cid,
            server=host,
            port=port,
            user=self._token.encode(),
            password=self._token.encode(),
            keepalive=self._keepalive,
            ssl=ssl,
        )

        # last‑will & callback
        self._client.set_last_will(self._topic("/is_online"), b"{\"ol\":0}", retain=True)
        self._client.set_callback(self._on_message)
        self._client.connect()

        self._client.subscribe(self._topic("/down"))
        self._client.subscribe(self._topic("/virtual_pin/#"))

        self.publish(self._topic("/is_online"), ujson.dumps({"ol": 1}), retain=True)
        self._log("MQTT connected & online flag sent")

    # ------------------------------------------------------------------
    def publish(self, topic: str, msg, *, retain: bool = False):
        if not self._client:
            raise RuntimeError("MQTT not connected")
        self._log(f"PUB {topic} ← {msg}")
        self._client.publish(topic, msg if isinstance(msg, bytes) else str(msg), retain=retain)

    def virtual_write(self, pin, value):
        self.publish(self._topic(f"/virtual_pin/{pin}"), ujson.dumps({"value": value}))

    publish_virtual_pin = virtual_write

    # ------------------------------------------------------------------
    def on_receive_message(self, topic_or_pin: str, cb):
        self._cbs[topic_or_pin] = cb
        self._log(f"callback registered → {topic_or_pin}")

    def _on_message(self, t_b: bytes, p_b: bytes):
        topic, payload = t_b.decode(), p_b.decode()
        self._log(f"RX {topic} → {payload}")
        if topic in self._cbs:
            self._cbs[topic](payload)
            return
        vbase = self._topic("/virtual_pin/")
        if topic.startswith(vbase):
            pin = topic[len(vbase):]
            cb = self._cbs.get(pin)
            if cb:
                try:
                    val = ujson.loads(payload).get("value", payload)
                except ValueError:
                    val = payload
                cb(pin, val)

    # ------------------------------------------------------------------
    def loop(self):
        if self._client:
            try:
                self._client.check_msg()
            except Exception as e:
                self._log(f"MQTT lost – {e}. Reconnecting…")
                time.sleep(2)
                try:
                    self.connect()
                except Exception as e2:
                    self._log(f"reconnect failed: {e2}")

    # helpers -----------------------------------------------------------
    def wifi_connected(self):
        return network.WLAN(network.STA_IF).isconnected()

    # ------------------------------------------------------------------
    @staticmethod
    def _demo():
        era = EraIoT("R&D", "kdi@2017", "dff9a7dd-726e-44f8-b6d1-84d3873148bd", client_id="01")
        era.connect()
        era.virtual_write(1, "Xin chào Era IoT!")
        while True:
            era.loop()
            time.sleep(1)
            
# backward‑compat helpers ----------------------------------------------
era: EraIoT | None = None


def connect_wifi(ssid, pw, token, *, client_id="01"):
    global era
    era = EraIoT(ssid, pw, token, client_id=client_id)
    era.connect()
    return True


def publish(topic, message):
    if not era:
        raise RuntimeError("call connect_wifi() first")
    era.publish(topic, message)


def publish_virtual_pin(pin, value):
    if not era:
        raise RuntimeError("call connect_wifi() first")
    era.virtual_write(pin, value)


def on_receive_message(tp, cb):
    if not era:
        raise RuntimeError("call connect_wifi() first")
    era.on_receive_message(tp, cb)


def check_message():
    if era:
        era.loop()


def wifi_connected():
    return era and era.wifi_connected()


def is_connected():
    return wifi_connected() and era and era._client


def debug_status():
    if era:
        print("=== EraIoT status ===")
        print("Wi‑Fi:", "OK" if era.wifi_connected() else "OFF")
        print("MQTT:", "OK" if era._client else "OFF")
        print("CID:", (era._fixed_cid or era._auto_client_id()).decode())
        print("=====================")
    else:
        print("EraIoT not initialised")


if __name__ == "__main__":
    EraIoT._demo()
