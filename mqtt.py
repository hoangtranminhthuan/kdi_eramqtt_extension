
import time
from umqtt_robust import MQTTClient
import ubinascii
import machine
import network
from utility import *

# --- ERA MQTT Topic Configuration ---
# Base topic, phải format với chip_id (vd: mqtt.username hoặc ID thiết bị)
ERA_BASE_TOPIC = 'eoh/chip/%s'

# Last-Will and Testament (LWT)
ERA_PREFIX_LWT_TOPIC    = '/is_online'
ERA_ONLINE_MESSAGE      = '{"ol":1, "wifi_ssid":"%s", "ask_configuration":1}'
ERA_OFFLINE_MESSAGE     = '{"ol":0}'

# General publish message template
ERA_PUBLISH_MESSAGE     = '{"v": %d}'

# Các topic để subscribe
ERA_SUB_PREFIX_DOWN_TOPIC      = '/down'
ERA_SUB_PREFIX_VIRTUAL_TOPIC   = '/virtual_pin/+'

# Các topic để publish
ERA_PUB_PREFIX_INFO_TOPIC           = '/info'
ERA_PUB_PREFIX_MODBUS_DATA_TOPIC    = '/data'
ERA_PUB_PREFIX_CONFIG_DATA_TOPIC    = '/config/%d/value'
ERA_PUB_PREFIX_MULTI_CONFIG_DATA_TOPIC = '/config_value'
# --------------------------------------

class MQTT:

    def __init__(self):
        self.client = None
        self.server = ''
        self.username = ''
        self.password = ''
        self.topic_prefix = ''
        self.message = ''
        self.topic = ''
        self.wifi_ssid = ''
        self.wifi_password = ''
        self.callbacks = {}
        self.last_sent = 0

    def __on_receive_message(self, topic, msg):
        #print((str(topic), str(msg)))
        msg = msg.decode('ascii')
        topic = topic.decode('ascii')
        if callable(self.callbacks.get(topic)):
            self.callbacks.get(topic)(msg)
            

    def connect_wifi(self, ssid, password, wait_for_connected=True):
        self.wifi_ssid = ssid
        self.wifi_password = password
        say('Connecting to WiFi...')
        self.station = network.WLAN(network.STA_IF)
        if self.station.active():
            self.station.active(False)
            time.sleep_ms(500)

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
                  raise Exception('Failed to connect to WiFi')

        if wait_for_connected:
            count = 0
            while self.station.isconnected() == False:
                count = count + 1
                if count > 150:
                    say('Failed to connect to WiFi')
                    raise Exception('Failed to connect to WiFi')
                time.sleep_ms(100)

            say('Wifi connected. IP:' + self.station.ifconfig()[0])

    def wifi_connected(self):
        return self.station.isconnected()

    def connect_broker(self, server='mqtt1.eoh.io', port=1883, username='', password=''):
        client_id = str(ubinascii.hexlify(machine.unique_id())) + str(time.ticks_ms())
        self.client = MQTTClient(client_id, server, port, username, password)
        try:
            self.client.disconnect()
        except:
            pass
        self.client.connect()
        self.client.set_callback(self.__on_receive_message)
        self.server = server
        self.username = username
        self.password = password
        if server.lower() == 'mqtt.ohstem.vn' or server.lower() == 'mqtt1.eoh.io':
            self.token = username
            self.topic_prefix = 'eoh/chip/{}/'.format(self.token)
        else:
            self.topic_prefix = ''
        say('Connected to MQTT broker')

    def check_message(self):
        if self.client == None:
            return
        if not self.wifi_connected():
            say('WiFi disconnected. Reconnecting...')
            self.connect_wifi(self.wifi_ssid, self.wifi_password)
            self.client.connect()
            #self.connect_broker()
            self.resubscribe()         

        self.client.check_msg()
    
    def on_receive_message(self, topic, callback):
        if self.client == None:
            return
        topic = self.topic_prefix + 'config/{}/value'.format(topic)

        self.callbacks[topic] = callback
        self.client.subscribe(topic)
    
    def resubscribe(self):
        for key in self.callbacks.keys():
            self.client.subscribe(key)
            #print(key)
    
    def publish(self, topic, message):
        if self.client == None:
            return
        now = time.ticks_ms()
        if now - self.last_sent < 1000:
            time.sleep_ms(1000-(now-self.last_sent))
        topic = self.topic_prefix + 'config/{}/value'.format(topic)
        self.client.publish(topic, str(message))
        self.last_sent = time.ticks_ms()

mqtt = MQTT()

def unit_test():    
    import time
    mqtt.connect_wifi('wifi', 'password')
    mqtt.connect_broker(server='mqtt.ohstem.vn', port=1883, username='test', password='')
    mqtt.publish('V1', 'Hello')

    def process(msg):
      print(msg)

    mqtt.on_receive_message('V2', process)
    i = 0
    while True:
      mqtt.check_message()
      mqtt.publish('V2', i)
      i += 1
      time.sleep(1)

if __name__ == '__main__':
    unit_test()


