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
        self.username = ''
        self.password = ''
        self.topic_prefix = ''
        self.wifi_ssid = ''
        self.wifi_password = ''
        self.callbacks = {}
        self.last_sent = 0
        # mapping pin_number → config_id
        self.virtual_pins = {}

    def __on_receive_message(self, topic: bytes, msg: bytes) -> None:
        topic_str = topic.decode('ascii')
        payload   = msg.decode('ascii')
        if callable(self.callbacks.get(topic_str)):
            self.callbacks[topic_str](payload)

    def connect_wifi(self, ssid: str, password: str, wait_for_connected: bool = True) -> None:
        self.wifi_ssid = ssid
        self.wifi_password = password
        say('Connecting to WiFi...')
        self.station = network.WLAN(network.STA_IF)
        if self.station.active():
            self.station.active(False)
            time.sleep_ms(500)

        # Try up to 5 times
        for i in range(5):
            try:
                self.station.active(True)
                self.station.connect(ssid, password)
                break
            except OSError:
                self.station.active(False)
                time.sleep_ms(500)
                if i == 4:
                    say('Failed to connect to WiFi')
                    raise

        if wait_for_connected:
            count = 0
            while not self.station.isconnected():
                count += 1
                if count > 150:  # ~15 seconds
                    say('Failed to connect to WiFi')
                    raise
                time.sleep_ms(100)

            ip = self.station.ifconfig()[0]
            say(f'WiFi connected. IP: {ip}')

    def wifi_connected(self) -> bool:
        return self.station.isconnected()

    def connect_broker(self, server: str = 'mqtt1.eoh.io', port: int = 1883,
                       username: str = '', password: str = '') -> None:
        client_id = ubinascii.hexlify(machine.unique_id()).decode() + str(time.ticks_ms())

        # Xác định topic is_online
        online_topic = f"eoh/chip/{username}/is_online"

        # Cấu hình will: khi client mất kết nối bất ngờ, broker sẽ publish {"ol":0}
        will_payload = '{"ol":0}'
        will_qos     = 1
        will_retain  = True

        # Tạo client với LWT
        self.client = MQTTClient(
            client_id,
            server,
            port,
            username,
            password,
            keepalive=60,
            will=(online_topic, will_payload, will_retain, will_qos)
        )

        # Kết nối
        try:
            self.client.disconnect()
        except:
            pass
        self.client.connect()
        self.client.set_callback(self.__on_receive_message)

        # Ngay sau khi connect xong, publish thông báo online
        online_payload = '{"ol":1}'
        self.client.publish(online_topic, online_payload, retain=True, qos=1)

        say('Connected to MQTT broker — online announced')

    def subscribe_config_down(self, token: str, callback=None) -> None:
        """
        Subscribe topic eoh/chip/{token}/config/down.
        If no callback provided, use internal handler to populate virtual_pins.
        """
        topic = f"eoh/chip/{token}/config/down"
        cb = callback or self._handle_config_down
        self.on_receive_message(topic, cb)

    def _handle_config_down(self, msg: str) -> None:
        """
        Default handler for config/down messages.
        Parses JSON and fills self.virtual_pins.
        """
        data = ujson.loads(msg)
        devices = data.get('configuration', {}) \
                      .get('arduino_pin', {}) \
                      .get('devices', [])
        for d in devices:
            for v in d.get('virtual_pins', []):
                pin    = int(v['pin_number'])
                cfg_id = int(v['config_id'])
                self.virtual_pins[pin] = cfg_id
        print("Config received, pin→config_id:", self.virtual_pins)

    def on_receive_message(self, topic: str, callback) -> None:
        """
        Subscribe an arbitrary topic and register a callback.
        """
        full_topic = self.topic_prefix + topic
        self.callbacks[full_topic] = callback
        self.client.subscribe(full_topic)
        say(f"Subscribed to {full_topic}")

    def resubscribe(self) -> None:
        """
        Re-subscribe to all topics after reconnect.
        """
        for t in self.callbacks.keys():
            self.client.subscribe(t)

    def check_message(self) -> None:
        """
        Should be called periodically.
        Checks for incoming messages and handles reconnection logic.
        """
        if not self.client:
            return
        if not self.wifi_connected():
            say('WiFi disconnected. Reconnecting...')
            self.connect_wifi(self.wifi_ssid, self.wifi_password)
            self.client.connect()
            self.resubscribe()
        self.client.check_msg()

    def publish(self, topic: str, message: str) -> None:
        """
        Publish a string message to a topic, throttled to 1s between sends.
        """
        if not self.client:
            return
        now = time.ticks_ms()
        if now - self.last_sent < 1000:
            time.sleep_ms(1000 - (now - self.last_sent))
        full_topic = self.topic_prefix + topic
        self.client.publish(full_topic, message)
        self.last_sent = time.ticks_ms()

mqtt = MQTT()
# --------------------
# Example usage
# --------------------
# def main():
#     TOKEN      = 'dff9a7dd-726e-44f8-b6d1-84d3873148bd'
#     WIFI_SSID  = 'R&D'
#     WIFI_PASS  = 'kdi@2017'

#     mqtt = MQTT()

#     # 1. Kết nối WiFi
#     mqtt.connect_wifi(WIFI_SSID, WIFI_PASS)

#     # 2. Kết nối MQTT Broker
#     mqtt.connect_broker(server='mqtt1.eoh.io', port=1883)

#     # 3. Subscribe cấu hình xuống
#     mqtt.subscribe_config_down(TOKEN)

#     # 4. Vòng lặp chính
#     while True:
#         mqtt.check_message()

#         # Ví dụ: nếu pin 1 đã có config_id, gửi giá trị 123
#         if 1 in mqtt.virtual_pins:
#             cfg = mqtt.virtual_pins[1]
#             topic = f"eoh/chip/{TOKEN}/config/{cfg}/value"
#             payload = ujson.dumps({"v": 123})
#             mqtt.publish(topic, payload)

#         time.sleep(5)


# if __name__ == '__main__':
#     main()
