import time
import network
import ubinascii
import machine
import ujson
from umqtt_robust import MQTTClient
from utility import say

class MQTT:
    def __init__(self):
        self.client = None
        self.server = ''
        self.port = 1883
        self.username = ''
        self.password = ''
        self.topic_prefix = ''
        self.wifi_ssid = ''
        self.wifi_password = ''
        self.callbacks = {}
        self.last_sent = 0
        self.virtual_pins = {}
        say("MQTT initialized")

    def __on_receive_message(self, topic: bytes, msg: bytes) -> None:
        topic_str = topic.decode('ascii')
        payload = msg.decode('ascii')
        say(f"Received message topic={topic_str}, payload={payload}")
        try:
            data = ujson.loads(payload)
            say(f"JSON parsed: {data}")
        except Exception as e:
            say(f"JSON decode error: {e}")
            return

        handler = self.callbacks.get(topic_str)
        if callable(handler):
            say(f"Dispatching to handler {handler.__name__}")
            handler(payload)
        else:
            say("No handler for topic")

    def connect_wifi(self, ssid: str, password: str, wait_for_connected: bool = True) -> None:
        say(f"Connecting to WiFi ssid={ssid}")
        self.wifi_ssid = ssid
        self.wifi_password = password

        self.station = network.WLAN(network.STA_IF)
        if self.station.active():
            self.station.active(False)
            time.sleep_ms(200)
        self.station.active(True)

        for i in range(5):
            try:
                self.station.connect(ssid, password)
                say("station.connect called")
                break
            except OSError as e:
                say(f"WiFi connect attempt {i+1} error: {e}")
                time.sleep_ms(500)
        else:
            say('Failed to connect to WiFi')
            raise RuntimeError("WiFi connect failed")

        if wait_for_connected:
            start = time.ticks_ms()
            while not self.station.isconnected():
                if time.ticks_diff(time.ticks_ms(), start) > 15000:
                    say('WiFi connection timeout')
                    raise RuntimeError("WiFi timeout")
                time.sleep_ms(200)
            ip = self.station.ifconfig()[0]
            say(f"WiFi connected with IP: {ip}")

    def wifi_connected(self) -> bool:
        status = self.station.isconnected()
        say(f"WiFi connected? {status}")
        return status

    def connect_broker(self,
                       server: str = 'mqtt1.eoh.io',
                       port: int = 1883,
                       username: str = '',
                       password: str = '') -> None:
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        client_id = ubinascii.hexlify(machine.unique_id()).decode() + str(time.ticks_ms())
        say(f"Connecting to broker server={server}, port={port}, user={username}")

        try:
            if self.client:
                self.client.disconnect()
                say("Previous client disconnected")
        except Exception as e:
            say(f"Error during disconnect: {e}")

        self.client = MQTTClient(client_id, server, port, username, password)
        self.client.set_callback(self.__on_receive_message)
        self.client.connect()
        say('Broker connected')

        online_topic = f"eoh/chip/{username}/is_online"
        say(f"Publishing online to topic {online_topic}")
        self.client.publish(online_topic, '{"ol":1}', retain=True, qos=1)

        self.topic_prefix = f"eoh/chip/{username}/"
        say(f"Topic prefix set to {self.topic_prefix}")

    def subscribe_config_down(self, token: str, callback=None) -> None:
        topic = f"eoh/chip/{token}/down"
        say(f"Subscribing to config down topic {topic}")
        self.on_receive_message(topic, callback or self._handle_config_down)

    def _handle_config_down(self, msg: str) -> None:
        say(f"Handling config down: {msg}")
        try:
            data = ujson.loads(msg)
        except Exception as e:
            say(f"JSON decode error in config_down: {e}")
            return

        devices = data.get('configuration', {}).get('arduino_pin', {}).get('devices', [])
        self.virtual_pins.clear()
        for d in devices:
            for v in d.get('virtual_pins', []):
                pin = int(v['pin_number'])
                cid = int(v['config_id'])
                self.virtual_pins[pin] = cid
                say(f"Virtual pin V{pin} -> config_id {cid}")

    def on_receive_message(self, topic: str, callback) -> None:
        full_topic = self.topic_prefix + topic
        self.callbacks[full_topic] = callback
        self.client.subscribe(full_topic)
        say(f"Subscribed to {full_topic}")

    def resubscribe(self) -> None:
        say("Resubscribing all topics")
        for t in self.callbacks:
            self.client.subscribe(t)
            say(f"Resubscribed {t}")

    def check_message(self) -> None:
        say("Checking incoming messages")
        if not self.client:
            say("No MQTT client available")
            return

        if not self.wifi_connected():
            say('WiFi disconnected, reconnecting')
            self.connect_wifi(self.wifi_ssid, self.wifi_password)
            self.client.connect()
            self.resubscribe()

        try:
            self.client.check_msg()
        except Exception as e:
            say(f"Error in check_msg: {e}")

    def publish(self, topic: str, message: str, qos: int = 1, retain: bool = False) -> None:
        if not self.client:
            say("Publish called but no client")
            return

        now = time.ticks_ms()
        if now - self.last_sent < 1000:
            wait = 1000 - (now - self.last_sent)
            say(f"Throttling publish for {wait}ms")
            time.sleep_ms(wait)

        full_topic = self.topic_prefix + topic
        say(f"Publishing to topic {full_topic}, message {message}")
        self.client.publish(full_topic, message, retain=retain, qos=qos)
        self.last_sent = time.ticks_ms()

    def virtual_write(self, pin: int, value: Union[int, float, str]) -> None:
        say(f"virtual_write pin={pin}, value={value}")
        if pin not in self.virtual_pins:
            say(f"Pin {pin} not registered")
            return

        cfg_id = self.virtual_pins[pin]
        prefix = self.topic_prefix
        if not prefix.endswith('/'):
            prefix += '/'

        topic = f"{prefix}config/{cfg_id}/value"
        payload = str(value)
        say(f"Publishing virtual value to {topic}, payload {payload}")
        self.client.publish(topic, payload)



mqtt = MQTT()



