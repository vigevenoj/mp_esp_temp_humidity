import dht
import machine


class Pooper():
    def __init__(self):
        self._sensor = dht.DHT22(machine.Pin(12))

    def poop_readings(self):
        self._sensor.measure()
        print("Temperature: {0}".format(self._sensor.temperature()))
        print("Humidity: {0}".format(self._sensor.humidity()))


if __name__ == '__main__':
    pooper = Pooper()
    pooper.poop_readings()
