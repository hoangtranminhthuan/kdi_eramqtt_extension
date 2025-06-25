# era_iot.py
# Thư viện Era IoT cho MicroPython
from umqtt_robust import MQTTClient
import ujson
import network
import time

class EraIoT:
    def __init__(self, ssid, password, token):
        self._ssid = ssid
        self._password = password
        self._token = token
        self._client = None
        self._callbacks = {}

    def _connect_wifi(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(self._ssid, self._password)
        while not wlan.isconnected():
            time.sleep(0.5)
        print("WiFi connected")

    def connect(self):
        self._connect_wifi()
        self._client = MQTTClient(self._token, 'mqtt1.eoh.io')
        self._client.set_callback(self._on_message)
        self._client.set_last_will(self._get_topic("/is_online"), '{"ol":0}', retain=True)
        self._client.connect()
        self._client.subscribe(self._get_topic("/down"))
        self._client.subscribe(self._get_topic("/virtual_pin/#"))
        self._client.publish(self._get_topic("/is_online"), ujson.dumps({"ol":1, "wifi_ssid":self._ssid, "ask_configuration":1}), retain=True)

    def _get_topic(self, suffix):
        return "eoh/chip/%s%s" % (self._token, suffix)

    def _on_message(self, topic, payload):
        topic = topic.decode() if isinstance(topic, bytes) else topic
        payload = payload.decode() if isinstance(payload, bytes) else payload
        
        try:
            if topic in self._callbacks:
                self._callbacks[topic](payload)
            elif topic.startswith(self._get_topic("/virtual_pin/")):
                pin = topic.split("/")[-1]
                if pin in self._callbacks:
                    msg = ujson.loads(payload)
                    value = msg.get("value", 0)
                    # Pass both topic and value to match Blockly expectation
                    self._callbacks[pin](topic, value)
        except Exception as e:
            print(f"Error processing message: {e}")

    def publish(self, topic, message):
        if self._client:
            self._client.publish(topic, message)

    def on_receive_message(self, topic, callback):
        self._callbacks[topic] = callback

    def check_message(self):
        if self._client:
            self._client.check_msg()

    def wifi_connected(self):
        return network.WLAN(network.STA_IF).isconnected()

# Singleton để tương thích Blockly
era = None

def connect_wifi(ssid, password, token):
    global era
    try:
        era = EraIoT(ssid, password, token)
        era.connect()
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

def connect_broker(server="mqtt1.eoh.io", port=1883, username=None, password=None):
    pass  # không cần vì đã xử lý trong connect_wifi()

def publish(topic, message):
    if era:
        era.publish(topic, message)

def on_receive_message(topic, callback):
    if era:
        era.on_receive_message(topic, callback)

def check_message():
    if era:
        era.check_message()

def wifi_connected():
    return era and era.wifi_connected()

def is_connected():
    return wifi_connected()

def virtual_write(pin, value):
    """Write value to virtual pin"""
    if era and era._client:
        topic = f"eoh/chip/{era._token}/virtual_pin/{pin}"
        payload = ujson.dumps({"value": value})
        era._client.publish(topic, payload)

def publish_virtual_pin(pin, value):
    """Alias for virtual_write for backward compatibility"""
    virtual_write(pin, value)
    
def get_connection_status():
    if era:
        return {
            'wifi': era.wifi_connected(),
            'mqtt': era._client is not None,
            'token': era._token
        }
    return {'wifi': False, 'mqtt': False, 'token': None}

def on_virtual_pin_change(pin, callback):
    """Register callback for virtual pin changes"""
    if era:
        era.on_receive_message(str(pin), callback)

def get_virtual_pin_value(pin):
    """Get current value of virtual pin"""
    # Implementation needed based on ERA IoT API
    pass