from umqtt.robust2 import MQTTClient
import network
import time
import bme68x
from machine import Pin, reset
import os


WIFI_SSID = ""
WIFI_PASSWORD = ""
MQTT_SERVER = ''
MQTT_USER = ''
MQTT_PASSWORD = ''

led = Pin("LED", Pin.OUT)

led.value(1)

wlan_retry_count = 0
mqtt_retry_count = 0

def led_blink():
    led.value(1)
    time.sleep(0.5)
    led.value(0)

def logCrash(log):
    with open('CrashLogs.txt', 'a') as f:
        f.write(log)
        f.write('\n')

def readBME():
    data = sensor.save_data('data.json')
    return round(data['T'], 1), round(data['H'], 1)

def mqtt_connect():
    client = MQTTClient(client_id="PicoW-LivingRoom", server=MQTT_SERVER, port=1883, user=MQTT_USER, password=MQTT_PASSWORD, keepalive=3600)
    client.connect()
    print('Connected to MQTT Broker')
    return client



wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASSWORD)
wlan.ifconfig(('192.168.100.40', '255.255.255.0', '192.168.100.1', '8.8.8.8'))
while wlan.isconnected() == False:
    if wlan_retry_count > 6:
        print("Failed first connection to WiFi")
        logCrash("Failed first connection to WiFi")
        time.sleep(5)
        reset()
    print('Waiting for connection...')
    wlan_retry_count += 1
    led_blink()
    time.sleep(5)
print("Connected to WiFi")


try:
    client = mqtt_connect()
except OSError as e:
    print("Failed first connection to MQTT, resetting device...")
    logCrash("Failed first connection to MQTT")
    led_blink()
    time.sleep(5)
    reset()

sensor = bme68x.BME68X()

Temperature_Reference = 0
Humidity_Reference = 0

while True:
    if not wlan.isconnected():
        logCrash("Lost connection to WiFi")
        led_blink()
        time.sleep(5)
        reset()
    if client.is_conn_issue():
        if mqtt_retry_count > 6:
            logCrash("Lost connection to MQTT")
            time.sleep(5)
            reset()
        mqtt_retry_count += 1
        client.reconnect()
        led_blink()
        time.sleep(5)

    Temperature, Humidity = readBME()
    if Temperature != Temperature_Reference:
        Temperature_Reference = Temperature
        client.publish(("LivingRoom/Temperature"), str(Temperature))
        print("Temperature changed to ", Temperature)
    if Humidity != Humidity_Reference:
        Humidity_Reference = Humidity
        client.publish(("LivingRoom/Humidity"), str(Humidity))
        print("Humidity changed to ", Humidity)
    time.sleep(30)
    
    

