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


"""
ERA IoT MQTT helper – built specifically for mqtt1.eoh.io
---------------------------------------------------------
- Fixed server: mqtt1.eoh.io
- Port: 1883 (no TLS)
- Uses token for username, password, and topic prefix
- Publishes /is_online status
- Handles /virtual_pin/{pin} subscription and callback
"""

from umqtt_robust import MQTTClient
import network, time, ujson, ubinascii, machine

era = None  # global instance

class EraMQTT:
    def __init__(self, token, ssid, password, *, client_id=None, debug=True):
        self.token = token
        self.ssid = ssid
        self.wifi_pw = password
        self.client_id = client_id or self._gen_client_id()
        self.client = None
        self._callbacks = {}
        self.debug = debug

    def _log(self, msg):
        if self.debug:
            print('[ERA]', msg)

    def _gen_client_id(self):
        suffix = ubinascii.hexlify(machine.unique_id()).decode()[-4:]
        base = self.token.replace('-', '')[:19]
        return base + suffix

    def _topic(self, suffix):
        return f"eoh/chip/{self.token}{suffix}"

    def connect_wifi(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        if wlan.isconnected():
            self._log('Wi-Fi already connected')
            return
        self._log(f'Connecting to Wi-Fi {self.ssid}...')
        wlan.connect(self.ssid, self.wifi_pw)
        timeout = 15
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1
        if not wlan.isconnected():
            raise Exception('Wi-Fi connection failed')
        self._log(f'Wi-Fi connected: {wlan.ifconfig()[0]}')

    def connect_mqtt(self):
        self._log('Connecting to MQTT broker mqtt1.eoh.io:1883...')
        self.client = MQTTClient(
            client_id=self.client_id.encode(),
            server='mqtt1.eoh.io',
            port=1883,
            user=self.token.encode(),
            password=self.token.encode(),
            keepalive=60
        )
        self.client.set_callback(self._on_message)
        self.client.set_last_will(self._topic('/is_online'), b'{"ol":0}', retain=True)
        self.client.connect()
        self.client.subscribe(self._topic('/down'))
        self.client.subscribe(self._topic('/virtual_pin/#'))
        self._log('MQTT connected')
        self.publish('/is_online', {"ol": 1})

    def publish(self, suffix, value):
        topic = self._topic(suffix)
        msg = ujson.dumps(value) if isinstance(value, dict) else str(value)
        self.client.publish(topic, msg)
        self._log(f'Published to {topic}: {msg}')

    def virtual_write(self, pin, value):
        self.publish(f"/virtual_pin/{pin}", {"value": value})

    def _on_message(self, topic_b, payload_b):
        topic = topic_b.decode()
        payload = payload_b.decode()
        self._log(f'Received → {topic}: {payload}')
        if topic.startswith(self._topic('/virtual_pin/')):
            pin = topic.rsplit('/', 1)[-1]
            if pin in self._callbacks:
                try:
                    data = ujson.loads(payload)
                    value = data.get("value", payload)
                except:
                    value = payload
                self._callbacks[pin](pin, value)

    def on_virtual_pin(self, pin, callback):
        self._callbacks[str(pin)] = callback
        self._log(f'Registered callback for pin {pin}')

    def loop(self):
        if self.client:
            try:
                self.client.check_msg()
            except Exception as e:
                self._log(f'Loop error: {e}')


def connect_wifi(ssid, wifi_pw, token, client_id=None):
    global era
    era = EraMQTT(token, ssid, wifi_pw, client_id=client_id)
    era.connect_wifi()
    era.connect_mqtt()
    return True

def publish_virtual_pin(pin, value):
    if era:
        era.virtual_write(pin, value)

def on_virtual_pin_change(pin, callback):
    if era:
        era.on_virtual_pin(pin, callback)

def check_message():
    if era:
        era.loop()

def wifi_connected():
    return network.WLAN(network.STA_IF).isconnected()

def is_connected():
    return era is not None and era.client is not None and wifi_connected()

def debug_status():
    if era:
        print("Wi-Fi:", "ON" if wifi_connected() else "OFF")
        print("MQTT:", "ON" if era.client else "OFF")
    else:
        print("EraMQTT not initialized")