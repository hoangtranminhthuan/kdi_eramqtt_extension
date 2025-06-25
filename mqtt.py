# import time
# import network
# import ubinascii
# import machine
# import ujson
# from umqtt_robust import MQTTClient
# from utility import say

# class MQTT:
#     def __init__(self):
#         self.client = None
#         self.server = ''
#         self.username = ''
#         self.password = ''
#         self.topic_prefix = ''
#         self.wifi_ssid = ''
#         self.wifi_password = ''
#         self.callbacks = {}
#         self.last_sent = 0
#         # mapping pin_number → config_id
#         self.virtual_pins = {}

#     def __on_receive_message(self, topic: bytes, msg: bytes) -> None:
#         topic_str = topic.decode('ascii')
#         payload   = msg.decode('ascii')
#         if callable(self.callbacks.get(topic_str)):
#             self.callbacks[topic_str](payload)

#     def connect_wifi(self, ssid: str, password: str, wait_for_connected: bool = True) -> None:
#         self.wifi_ssid = ssid
#         self.wifi_password = password
#         say('Connecting to WiFi...')
#         self.station = network.WLAN(network.STA_IF)
#         if self.station.active():
#             self.station.active(False)
#             time.sleep_ms(500)

#         # Try up to 5 times
#         for i in range(5):
#             try:
#                 self.station.active(True)
#                 self.station.connect(ssid, password)
#                 break
#             except OSError:
#                 self.station.active(False)
#                 time.sleep_ms(500)
#                 if i == 4:
#                     say('Failed to connect to WiFi')
#                     raise

#         if wait_for_connected:
#             count = 0
#             while not self.station.isconnected():
#                 count += 1
#                 if count > 150:  # ~15 seconds
#                     say('Failed to connect to WiFi')
#                     raise
#                 time.sleep_ms(100)

#             ip = self.station.ifconfig()[0]
#             say(f'WiFi connected. IP: {ip}')

#     def wifi_connected(self) -> bool:
#         return self.station.isconnected()

#     def connect_broker(self, server: str = 'mqtt1.eoh.io', port: int = 1883,
#                        username: str = '', password: str = '') -> None:
#         client_id = ubinascii.hexlify(machine.unique_id()).decode() + str(time.ticks_ms())
#         self.client = MQTTClient(client_id, server, port, username, password)
#         try:
#             self.client.disconnect()
#         except:
#             pass
#         self.client.connect()
#         self.client.set_callback(self.__on_receive_message)
#         self.server   = server
#         self.username = username
#         self.password = password
#         self.topic_prefix = ''  # if you need a base prefix, set it here
#         say('Connected to MQTT broker')

#     def subscribe_config_down(self, token: str, callback=None) -> None:
#         """
#         Subscribe topic eoh/chip/{token}/config/down.
#         If no callback provided, use internal handler to populate virtual_pins.
#         """
#         topic = f"eoh/chip/{token}/config/down"
#         cb = callback or self._handle_config_down
#         self.on_receive_message(topic, cb)

#     def _handle_config_down(self, msg: str) -> None:
#         """
#         Default handler for config/down messages.
#         Parses JSON and fills self.virtual_pins.
#         """
#         data = ujson.loads(msg)
#         devices = data.get('configuration', {}) \
#                       .get('arduino_pin', {}) \
#                       .get('devices', [])
#         for d in devices:
#             for v in d.get('virtual_pins', []):
#                 pin    = int(v['pin_number'])
#                 cfg_id = int(v['config_id'])
#                 self.virtual_pins[pin] = cfg_id
#         print("Config received, pin→config_id:", self.virtual_pins)

#     def on_receive_message(self, topic: str, callback) -> None:
#         """
#         Subscribe an arbitrary topic and register a callback.
#         """
#         full_topic = self.topic_prefix + topic
#         self.callbacks[full_topic] = callback
#         self.client.subscribe(full_topic)
#         say(f"Subscribed to {full_topic}")

#     def resubscribe(self) -> None:
#         """
#         Re-subscribe to all topics after reconnect.
#         """
#         for t in self.callbacks.keys():
#             self.client.subscribe(t)

#     def check_message(self) -> None:
#         """
#         Should be called periodically.
#         Checks for incoming messages and handles reconnection logic.
#         """
#         if not self.client:
#             return
#         if not self.wifi_connected():
#             say('WiFi disconnected. Reconnecting...')
#             self.connect_wifi(self.wifi_ssid, self.wifi_password)
#             self.client.connect()
#             self.resubscribe()
#         self.client.check_msg()

#     def publish(self, topic: str, message: str) -> None:
#         """
#         Publish a string message to a topic, throttled to 1s between sends.
#         """
#         if not self.client:
#             return
#         now = time.ticks_ms()
#         if now - self.last_sent < 1000:
#             time.sleep_ms(1000 - (now - self.last_sent))
#         full_topic = self.topic_prefix + topic
#         self.client.publish(full_topic, message)
#         self.last_sent = time.ticks_ms()

# mqtt = MQTT()
# # --------------------
# # Example usage
# # --------------------
# # def main():
# #     TOKEN      = 'dff9a7dd-726e-44f8-b6d1-84d3873148bd'
# #     WIFI_SSID  = 'R&D'
# #     WIFI_PASS  = 'kdi@2017'

# #     mqtt = MQTT()

# #     # 1. Kết nối WiFi
# #     mqtt.connect_wifi(WIFI_SSID, WIFI_PASS)

# #     # 2. Kết nối MQTT Broker
# #     mqtt.connect_broker(server='mqtt1.eoh.io', port=1883)

# #     # 3. Subscribe cấu hình xuống
# #     mqtt.subscribe_config_down(TOKEN)

# #     # 4. Vòng lặp chính
# #     while True:
# #         mqtt.check_message()

# #         # Ví dụ: nếu pin 1 đã có config_id, gửi giá trị 123
# #         if 1 in mqtt.virtual_pins:
# #             cfg = mqtt.virtual_pins[1]
# #             topic = f"eoh/chip/{TOKEN}/config/{cfg}/value"
# #             payload = ujson.dumps({"v": 123})
# #             mqtt.publish(topic, payload)

# #         time.sleep(5)


# # if __name__ == '__main__':
# #     main()


import time
import network
import ubinascii
import machine
import ujson
from umqtt_robust import MQTTClient
from utility import say, match_mqtt_topic

# ——— Các hằng số topic/payload ———
ERA_BASE_TOPIC               = 'eoh/chip/%s'
ERA_PREFIX_LWT_TOPIC         = '/is_online'
ERA_ONLINE_MESSAGE           = '{"ol":1,"wifi_ssid":"%s","ask_configuration":1}'
ERA_OFFLINE_MESSAGE          = '{"ol":0}'
ERA_PUBLISH_MESSAGE          = '{"v":%d}'

ERA_SUB_PREFIX_DOWN_TOPIC    = '/down'
ERA_SUB_PREFIX_VIRTUAL_TOPIC = '/virtual_pin/+'

ERA_PUB_PREFIX_CONFIG_DATA   = '/config/%d/value'

ERA_MQTT_SERVER              = 'mqtt1.eoh.io'
ERA_MQTT_PORT                = 1883


class EraIoTSync:
    def __init__(self, ssid: str, password: str, token: str):
        self._ssid = ssid
        self._password = password
        self._token = token
        # map pin_number → config_id
        self._virtual_pins = {}
        # map pin_number_cb → callback
        self._pin_cbs = {}

        # Cấu hình MQTTClient từ umqtt_robust
        client_id = ubinascii.hexlify(machine.unique_id()).decode() + str(time.ticks_ms())
        self._mqtt_conf = {
            'client_id': client_id,
            'server':    ERA_MQTT_SERVER,
            'port':      ERA_MQTT_PORT,
            'user':      token,
            'password':  token,
            'keepalive': 60,
            'reconnect': True,
        }
        MQTTClient.DEBUG = True
        self._client = MQTTClient(**self._mqtt_conf)
        self._client.set_callback(self._on_message)

    def _get_topic(self, suffix: str) -> str:
        return (ERA_BASE_TOPIC % self._token) + suffix

    def connect(self):
        # 1. Kết nối Wi-Fi
        say('Connecting to WiFi...')
        sta = network.WLAN(network.STA_IF)
        sta.active(True)
        sta.connect(self._ssid, self._password)
        start = time.time()
        while not sta.isconnected():
            if time.time() - start > 15:
                raise RuntimeError('WiFi connect timeout')
            time.sleep(0.1)
        say('WiFi connected: ' + sta.ifconfig()[0])

        # 2. Kết nối MQTT broker
        try:
            self._client.disconnect()
        except:
            pass
        self._client.connect()
        say('Connected to MQTT broker')

        # 3. Gửi online LWT
        self._client.publish(
            self._get_topic(ERA_PREFIX_LWT_TOPIC),
            ERA_ONLINE_MESSAGE % self._ssid,
            retain=True,
            qos=1
        )

        # 4. Subscribe 2 topic: config/down và virtual_pin/+
        down    = self._get_topic(ERA_SUB_PREFIX_DOWN_TOPIC)
        vpin    = self._get_topic(ERA_SUB_PREFIX_VIRTUAL_TOPIC)
        self._client.subscribe(down, qos=1)
        self._client.subscribe(vpin, qos=1)
        say(f'Subscribed to {down} and {vpin}')

    def _on_message(self, topic: bytes, msg: bytes):
        topic_str = topic.decode('ascii')
        # Config down
        if topic_str.endswith(ERA_SUB_PREFIX_DOWN_TOPIC):
            self._handle_config_down(msg)
            return
        # Virtual pin command
        if match_mqtt_topic(topic_str, self._get_topic(ERA_SUB_PREFIX_VIRTUAL_TOPIC)):
            self._handle_virtual_pin(topic_str, msg)

    def _handle_config_down(self, payload: bytes):
        data = ujson.loads(payload)
        devices = data.get('configuration', {}) \
                      .get('arduino_pin', {}) \
                      .get('devices', [])
        for d in devices:
            for v in d.get('virtual_pins', []):
                pin    = int(v['pin_number'])
                cfg_id = int(v['config_id'])
                self._virtual_pins[pin] = cfg_id
        say('Config received: ' + str(self._virtual_pins))

    def _handle_virtual_pin(self, topic_str: str, payload: bytes):
        data  = ujson.loads(payload)
        value = int(data.get('value', 0))
        parts = match_mqtt_topic(topic_str, self._get_topic(ERA_SUB_PREFIX_VIRTUAL_TOPIC))
        if parts and len(parts) == 1:
            pin = int(parts[0])
            cb  = self._pin_cbs.get(pin)
            if cb:
                cb(value)

    def on_virtual_read(self, pin: int, callback):
        """
        Đăng ký callback (hàm sync) khi server gửi lệnh cho virtual pin.
        """
        self._pin_cbs[pin] = callback

    def virtual_write(self, pin: int, value: int, qos: int = 1):
        """
        Gửi giá trị lên topic /config/{config_id}/value
        """
        cfg_id = self._virtual_pins.get(pin)
        if cfg_id is None:
            return
        topic = self._get_topic(ERA_PUB_PREFIX_CONFIG_DATA % cfg_id)
        self._client.publish(topic, ERA_PUBLISH_MESSAGE % value, retain=True, qos=qos)

    def check_msg(self):
        """
        Gọi định kỳ để nhận & xử lý incoming MQTT messages.
        """
        try:
            self._client.check_msg()
        except OSError:
            say('MQTT lost, reconnecting...')
            self.connect()

mqtt = EraIoTSync()
# # ——— Ví dụ sử dụng ———
# def main():
#     TOKEN = 'YOUR_DEVICE_TOKEN'
#     SSID  = 'your_ssid'
#     PWD   = 'your_password'

#     iot = EraIoTSync(SSID, PWD, TOKEN)
#     iot.connect()

#     # Đăng ký handler cho pin 1
#     def on_v1(val):
#         say('Received V1 -> ' + str(val))
#     iot.on_virtual_read(1, on_v1)

#     # Vòng lặp chính
#     while True:
#         iot.check_msg()
#         # Ví dụ gửi giá trị đo pin 1 nếu đã được config
#         if 1 in iot._virtual_pins:
#             iot.virtual_write(1, 123)
#         time.sleep(5)


# if __name__ == '__main__':
#     main()
