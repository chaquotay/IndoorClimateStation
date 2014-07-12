#!/usr/bin/env python

"""Displays temperature and relative humidity on an LCD using Tinkerforge bricklets."""

HOST = "localhost"
PORT = 4223
UPDATE_PERIOD = 1000

from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_temperature import Temperature
from tinkerforge.bricklet_humidity import Humidity
from tinkerforge.bricklet_lcd_20x4 import LCD20x4


class ClimateSensors:

    def __init__(self, host, port):
        self.hum = None
        self.hum_value = 0.0
        self.temp = None
        self.temp_value = 0.0
        self.lcd = None

        self.port = port
        self.host = host
        self.conn = IPConnection()

        self.conn.register_callback(IPConnection.CALLBACK_ENUMERATE, self.cb_enumerate)
        self.conn.register_callback(IPConnection.CALLBACK_CONNECTED, self.cb_connected)

    def update_display(self):
        if self.lcd is not None:
            self.lcd.write_line(1, 2, 'Temp:   {:3.2f} C'.format(self.temp_value))
            self.lcd.write_line(2, 2, 'RelHum: {:3.2f} %'.format(self.hum_value))

    def connect(self):
        if self.conn.get_connection_state() == self.conn.CONNECTION_STATE_DISCONNECTED:
            self.conn.connect(self.host, self.port)
            self.conn.enumerate()

    def disconnect(self):
        if self.conn.get_connection_state() != self.conn.CONNECTION_STATE_DISCONNECTED:
            if self.lcd is not None:
                self.lcd.backlight_off()
                self.lcd.clear_display()
            self.conn.disconnect()

    def cb_connected(self, connected_reason):
        self.conn.enumerate()

    def cb_enumerate(self, uid, connected_uid, position, hardware_version, firmware_version, device_identifier, enumeration_type):
        if enumeration_type == IPConnection.ENUMERATION_TYPE_DISCONNECTED:
            # print("DISCONNECTED")
            return

        if device_identifier == Temperature.DEVICE_IDENTIFIER:
            self.temp = Temperature(uid, self.conn)
            self.temp.register_callback(self.temp.CALLBACK_TEMPERATURE, self.cb_temperature)
            self.update_temperature(self.temp.get_temperature())
            self.temp.set_temperature_callback_period(UPDATE_PERIOD)

        if device_identifier == Humidity.DEVICE_IDENTIFIER:
            self.hum = Humidity(uid, self.conn)
            self.hum.register_callback(self.hum.CALLBACK_HUMIDITY, self.cb_humidity)
            self.update_humidity(self.hum.get_humidity())
            self.hum.set_humidity_callback_period(UPDATE_PERIOD)

        if device_identifier == LCD20x4.DEVICE_IDENTIFIER:
            self.lcd = LCD20x4(uid, self.conn)
            self.lcd.backlight_on()

    def cb_temperature(self, temperature):
        self.update_temperature(temperature)
        self.update_display()

    def update_temperature(self, raw_temperature):
        self.temp_value = raw_temperature / 100.0

    def cb_humidity(self, humidity):
        self.update_humidity(humidity)
        self.update_display()

    def update_humidity(self, raw_humidity):
        self.hum_value = raw_humidity / 10.0

if __name__ == "__main__":
    sensors = ClimateSensors(HOST, PORT)
    sensors.connect()
    input('Press key to exit\n')
    sensors.disconnect()