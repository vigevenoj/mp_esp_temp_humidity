import dht
from machine import Pin, Timer
from umqtt.robust import MQTTClient
import json


def do_connect():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect('ROFL', 'BUTTSBUTTSBUTTS!!!')
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())


class Pooper():
    def __init__(self):
        self._sensor = dht.DHT22(Pin(12))
        self._location = "downstairs"
        self._red = Pin(0, Pin.OUT)
        self._red.on()  # this is inverted, so off
        self._blue = Pin(0, Pin.OUT)
        self._blue.on()
        MQTT_HOST = "sharkbaitextraordinaire.com"
        MQTT_PORT = 8885
        self._client = MQTTClient(self._location, MQTT_HOST, MQTT_PORT)
        self._client.connect()

    def take_readings(self):
        self._red.off()  # toggle red LED on while taking a reading
        self._sensor.measure()
        temperature = self._sensor.temperature()
        humidity = self._sensor.humidity()
        self._red.on()  # red LED off
        self._blue.off()  # blue LED on for network
        self._client.publish(
            'sensors/harold/{}/temperature'.format(self._location),
            bytes(str(json.dumps({"temperature": temperature, "units": "C"})),
                  'utf-8'))
        self._client.publish(
            'sensors/harold/{}/humidity'.format(self._location),
            bytes(str(json.dumps({"humidity": humidity, "units": "%"})),
                  'utf-8'))
        self._blue.on()  # blue LED off again
        print("Temperature: {0}".format(temperature))
        print("Humidity: {0}".format(humidity))


if __name__ == '__main__':
    do_connect()
    pooper = Pooper()
    pooper.take_readings()
    timer = Timer(-1)
    timer.init(period=30000, mode=Timer.PERIODIC,
               callback=lambda t:pooper.take_readings())
