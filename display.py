import machine
from machine import Timer
import ssd1306
import secrets
from umqtt.robust import MQTTClient
import json
# import time


def do_connect():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network')
        sta_if.active(True)
        sta_if.connect(secrets.WIFI_SSID, secrets.WIFI_PASS)
        while not sta_if.isconnected():
            pass
    print('network config: ', sta_if.ifconfig())


def cb_callback(topic, message):
    print((topic, message))


class HomeDisplay():
    def __init__(self):
        i2c = machine.I2C(-1, machine.Pin(5), machine.Pin(4))
        self._screen = ssd1306.SSD1306_I2C(128, 64, i2c)
        self._client = MQTTClient(secrets.DEVICE_LOCATION, secrets.MQTT_HOST,
                                  secrets.MQTT_PORT,
                                  user=secrets.MQTT_USER,
                                  password=secrets.MQTT_PASS)
        # self._client.set_callback(self.subscription_callback)
        self._client.set_callback(cb_callback)
        self._client.connect()
        self._client.subscribe("sensors/#")
        self._screen.fill(0)
        self._screen.show()
        self._message_text = ""
        self._client.wait_msg()
        print("successfully initialized display system")
        # we should probably have a dict for the latest values
        # and then when we want to display a thing we can iterate over it

    def subscription_callback(topic, message):
        print((topic, message))
        # topic is 'sensors/location/type'
        tags = topic.split("/", 2)[1].split("/")
        # dict of key location->sensor->value
        # except message has too much info so we need to strip it
        # our message might just be a string anyway but str shoudln't  hurt)
        j = json.loads(str(message.payload))
        print("{0} -> {1} -> {2}".format(tags[0], tags[1], j.value))

    def display_readings(self):
        print("fake display code")
        # top row: location
        # 16px down: temperature ºC
        # next row down: humidity %


if __name__ == '__main__':
    print("connecting to wifi")
    do_connect()
    print("connected to wifi, starting work")
    hd = HomeDisplay()
    hd.display_readings()
    # micropython.mem_info()
    hd._client.check_msg()
    timer = Timer(-1)
    timer.init(period=30000, mode=Timer.PERIODIC,
               callback=lambda t: hd.display_readings())
