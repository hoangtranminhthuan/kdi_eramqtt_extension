# era_iot.py

import ujson
from umqtt_robust import MQTTClient

# --- Cấu hình chung ---
ERA_BASE_TOPIC                   = 'eoh/chip/%s'
ERA_PREFIX_LWT_TOPIC             = '/is_online'
ERA_ONLINE_MESSAGE               = '{"ol":1, "wifi_ssid":"%s", "ask_configuration":1}'
ERA_OFFLINE_MESSAGE              = '{"ol":0}'
ERA_PUBLISH_MESSAGE              = '{"v": %d}'

# Subscribe prefixes
ERA_SUB_PREFIX_DOWN_TOPIC        = '/down'
ERA_SUB_PREFIX_VIRTUAL_TOPIC_BASE= '/virtual_pin/'

# Publish format
ERA_PUB_PREFIX_CONFIG_DATA_TOPIC = '/config/%d/value'

# Broker
ERA_MQTT_SERVER                  = 'mqtt1.eoh.io'
ERA_MQTT_PORT                    = 1883


class EraIoT:
    def __init__(self, ssid, pwd, token, client_id=None):
        self._ssid      = ssid
        self._pwd       = pwd
        self._token     = token
        self._client_id = client_id or token

        # mapping pin → config_id, và pin → callback
        self._config_ids = {}
        self._callbacks  = {}

        # Khởi tạo client (tự reconnect/retry)
        self._client = MQTTClient(
            client_id    = self._client_id,
            server       = ERA_MQTT_SERVER,
            port         = ERA_MQTT_PORT,
            user         = self._token,
            password     = self._token
        )

        # Last Will: nếu mất kết nối sẽ publish offline message
        will_topic = self._get_topic(ERA_PREFIX_LWT_TOPIC)
        self._client.set_last_will(
            topic   = will_topic,
            msg     = ERA_OFFLINE_MESSAGE,
            retain  = True,
            qos     = 1
        )

        # callback chung cho tất cả incoming message
        self._client.set_callback(self._message_callback)


    def _get_topic(self, suffix):
        """Trả về e.g. 'eoh/chip/<token>' + suffix"""
        return (ERA_BASE_TOPIC % self._token) + suffix


    def connect(self):
        """Kết nối, publish online, subscribe và loop chờ message"""
        # 1) connect và tự động retry bên trong umqtt_robust
        self._client.connect()

        # 2) gửi online message
        online_topic = self._get_topic(ERA_PREFIX_LWT_TOPIC)
        online_msg   = ERA_ONLINE_MESSAGE % self._ssid
        self._client.publish(
            topic  = online_topic,
            msg    = online_msg,
            retain = True,
            qos    = 1
        )

        # 3) subscribe đến 2 prefix: /down và /virtual_pin/+
        down_topic   = self._get_topic(ERA_SUB_PREFIX_DOWN_TOPIC)
        virt_topic   = self._get_topic(ERA_SUB_PREFIX_VIRTUAL_TOPIC_BASE + '+')
        self._client.subscribe(topic = down_topic, qos = 1)
        self._client.subscribe(topic = virt_topic, qos = 1)

        # 4) vòng lặp chờ message
        while True:
            self._client.wait_msg()


    def _message_callback(self, topic, msg):
        """Phân luồng xuống _on_config_down hoặc _on_virtual_pin"""
        topic = topic.decode()
        if topic == self._get_topic(ERA_SUB_PREFIX_DOWN_TOPIC):
            self._on_config_down(msg)
        elif topic.startswith(self._get_topic(ERA_SUB_PREFIX_VIRTUAL_TOPIC_BASE)):
            self._on_virtual_pin(topic, msg)


    def _on_config_down(self, payload):
        """Xử lý cấu hình /down"""
        data    = ujson.loads(payload)
        devices = data.get('configuration', {}) \
                      .get('arduino_pin', {}) \
                      .get('devices', [])
        for d in devices:
            for v in d.get('virtual_pins', []):
                pin = int(v['pin_number'])
                self._config_ids[pin] = v['config_id']


    def _on_virtual_pin(self, topic, payload):
        """Xử lý lệnh từ /virtual_pin/<pin>"""
        data  = ujson.loads(payload)
        value = int(data.get('value', 0))
        prefix = self._get_topic(ERA_SUB_PREFIX_VIRTUAL_TOPIC_BASE)
        pin_str = topic[len(prefix):]
        try:
            pin = int(pin_str)
        except ValueError:
            return
        cb = self._callbacks.get(pin)
        if cb:
            cb(topic, value)


    def virtual_write(self, pin, value, qos=1):
        """Publish giá trị lên /config/<config_id>/value"""
        cfg_id = self._config_ids.get(pin)
        if cfg_id is None:
            return
        topic = self._get_topic(ERA_PUB_PREFIX_CONFIG_DATA_TOPIC % cfg_id)
        msg   = ERA_PUBLISH_MESSAGE % value
        self._client.publish(topic = topic, msg = msg, retain = True, qos = qos)


    def on_virtual_read(self, pin, callback):
        """Đăng ký callback cho pin ảo"""
        self._callbacks[pin] = callback
