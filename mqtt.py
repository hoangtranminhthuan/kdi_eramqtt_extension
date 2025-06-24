import time
from umqtt_robust import MQTTClient
import ubinascii
import machine
import network
from utility import *

# ERA MQTT configuration
ERA_BASE_TOPIC = 'eoh/chip/%s'
ERA_PREFIX_LWT_TOPIC = '/is_online'
ERA_ONLINE_MESSAGE = '{"ol":1, "wifi_ssid":"%s", "ask_configuration":1}'
ERA_OFFLINE_MESSAGE = '{"ol":0}'
ERA_PUBLISH_MESSAGE = '{"v": %d}'

# Subscribe topics
ERA_SUB_PREFIX_DOWN_TOPIC = '/down'
ERA_SUB_PREFIX_VIRTUAL_TOPIC = '/virtual_pin/+'

# Publish topics
ERA_PUB_PREFIX_INFO_TOPIC = '/info'
ERA_PUB_PREFIX_MODBUS_DATA_TOPIC = '/data'
ERA_PUB_PREFIX_CONFIG_DATA_TOPIC = '/config/%d/value'
ERA_PUB_PREFIX_MULTI_CONFIG_DATA_TOPIC = '/config_value'

ERA_MQTT_SERVER = 'mqtt1.eoh.io'
ERA_MQTT_PORT = 1883

class MQTT:
    def __init__(self, wifi_ssid, wifi_password, chip_id, username='', password=''):
        self.wifi_ssid = wifi_ssid
        self.wifi_password = wifi_password
        self.chip_id = chip_id
        self.base_topic = ERA_BASE_TOPIC % chip_id
        self.server = ERA_MQTT_SERVER
        self.port = ERA_MQTT_PORT
        self.username = username
        self.password = password
        self.client = None
        self.callbacks = {}
        self.last_sent = 0

    def wifi_connected(self):
        return network.WLAN(network.STA_IF).isconnected()

    def connect_wifi(self):
        wlan = network.WLAN(network.STA_IF)
        if not wlan.isconnected():
            say('Connecting to WiFi...')
            wlan.active(True)
            wlan.connect(self.wifi_ssid, self.wifi_password)
            timeout = time.ticks_ms()
            while not wlan.isconnected() and time.ticks_diff(time.ticks_ms(), timeout) < 10000:
                time.sleep_ms(500)
        say('WiFi connected: %s' % wlan.ifconfig()[0])

    def connect_broker(self):
        # Setup MQTT client with LWT
        lwt_topic = self.base_topic + ERA_PREFIX_LWT_TOPIC
        lwt_msg = ERA_OFFLINE_MESSAGE
        client_id = ubinascii.hexlify(machine.unique_id()).decode()
        self.client = MQTTClient(client_id=client_id,
                                 server=self.server,
                                 port=self.port,
                                 user=self.username,
                                 password=self.password,
                                 keepalive=60,
                                 ssl=False,
                                 ssl_params={},
                                 last_will=(lwt_topic, lwt_msg, True, 1))
        self.client.set_callback(self.__on_receive_message)
        self.client.connect()
        # Publish online status
        online_msg = ERA_ONLINE_MESSAGE % self.wifi_ssid
        self.client.publish(lwt_topic, online_msg, retain=True)
        # Subscribe to downlink and virtual pin topics
        self.client.subscribe(self.base_topic + ERA_SUB_PREFIX_DOWN_TOPIC)
        self.client.subscribe(self.base_topic + ERA_SUB_PREFIX_VIRTUAL_TOPIC)
        say('Connected to MQTT broker %s:%d' % (self.server, self.port))

    def __on_receive_message(self, topic, msg):
        # Dispatch callback based on full topic
        if topic in self.callbacks:
            self.callbacks[topic](msg)

    def on_receive_message(self, suffix_topic, callback):
        full_topic = self.base_topic + suffix_topic
        self.callbacks[full_topic] = callback
        self.client.subscribe(full_topic)

    def check_message(self):
        if self.client is None:
            return
        if not self.wifi_connected():
            say('WiFi disconnected. Reconnecting...')
            self.connect_wifi()
            self.connect_broker()
        self.client.check_msg()

    def publish(self, value):
        # Publish a value on the info topic
        topic = self.base_topic + ERA_PUB_PREFIX_INFO_TOPIC
        msg = ERA_PUBLISH_MESSAGE % value
        now = time.ticks_ms()
        if now - self.last_sent < 1000:
            time.sleep_ms(1000 - (now - self.last_sent))
        self.client.publish(topic, msg)
        self.last_sent = now

# Example usage

def unit_test():
    mqtt = MQTT('YourSSID', 'YourPass', 'chip01')
    mqtt.connect_wifi()
    mqtt.connect_broker()

    def handle_down(data):
        print('Downlink:', data)

    mqtt.on_receive_message(ERA_SUB_PREFIX_DOWN_TOPIC, handle_down)
    count = 0
    while True:
        mqtt.check_message()
        mqtt.publish(count)
        count += 1
        time.sleep(1)

if __name__ == '__main__':
    unit_test()
