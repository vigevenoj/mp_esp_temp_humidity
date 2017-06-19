import dht
from machine import Pin, Timer
from umqtt.robust import MQTTClient
import json
import secrets
import utime
import math
""" secrets.py must containing the following entries
# WIFI_SSID
# WIFI_PASS
# MQTT_HOST
# MQTT_PORT
# MQTT_USER
# MQTT_PASS
# DEVICE_LOCATION
It is required for this program to operate """


def do_connect():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(secrets.WIFI_SSID, secrets.WIFI_PASS)
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())


class Pooper():
    def __init__(self):
        self._sensor = dht.DHT22(Pin(12))
        self._location = secrets.DEVICE_LOCATION
        self._red = Pin(0, Pin.OUT)
        self._red.on()  # this is inverted, so off
        self._blue = Pin(2, Pin.OUT)
        self._blue.on()
        self._client = MQTTClient(self._location, secrets.MQTT_HOST,
                                  secrets.MQTT_PORT,
                                  user=secrets.MQTT_USER,
                                  password=secrets.MQTT_PASS)
        self._client.set_last_will(
            "/lwt/sensors/harold/{0}".format(self._location),
            "sensor at harold {0} is offline".format(self._location)
        )
        self._client.connect()
        self._prev_temp = -32  # This is well outside PDX temperature range
        self._prev_humidity = -2  # Negative humidity is impossible

    def take_readings(self):
        self._red.off()  # toggle red LED on while taking a reading
        utime.sleep_ms(250)
        self._sensor.measure()
        temperature = self._sensor.temperature()
        humidity = self._sensor.humidity()
        self._red.on()  # red LED off
        utime.sleep_ms(100)
        self._blue.off()  # blue LED on for network
        utime.sleep_ms(250)
        if math.fabs(temperature - self._prev_temp) >= 0.1:
            self._client.publish(
                'sensors/harold/{}/temperature'.format(self._location),
                bytes(str(json.dumps({"type": "temperature",
                                      "value": temperature,
                                      "units": "C"})), 'utf-8'), retain=True)
        if math.fabs(humidity - self._prev_humidity) >= 0.1:
            self._client.publish(
                'sensors/harold/{}/humidity'.format(self._location),
                bytes(str(json.dumps({"type": "humidity",
                                      "value": humidity,
                                      "units": "%"})), 'utf-8'), retain=True)
        self._prev_humidity = humidity
        self._prev_temp = temperature
        self._blue.on()  # blue LED off again
        print("Temperature: {0}".format(temperature))
        print("Humidity: {0}".format(humidity))


if __name__ == '__main__':
    do_connect()
    pooper = Pooper()
    pooper.take_readings()
    timer = Timer(-1)
    timer.init(period=30000, mode=Timer.PERIODIC,
               callback=lambda t: pooper.take_readings())
