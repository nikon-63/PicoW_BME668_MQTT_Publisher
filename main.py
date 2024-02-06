import network
import time
from umqtt.simple import MQTTClient
import bme68x
from machine import Pin

# Configuration Constants
WIFI_SSID = ""
WIFI_PASSWORD = ""
MQTT_SERVER = ''
MQTT_USER = ''
MQTT_PASSWORD = ''

led = Pin('LED', Pin.OUT)
led.on()
time.sleep(1)
led.off()

# Connect WiFi Function
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to network...')
        wlan.connect(ssid, password)
        wlan.ifconfig(('192.168.100.40', '255.255.255.0', '192.168.100.1', '8.8.8.8'))
        while not wlan.isconnected():
            pass
    print('Network configuration:', wlan.ifconfig())
    return wlan

# Reconnect MQTT
def reconnect_mqtt(client):
    try:
        client.connect()
        print("MQTT reconnected")
    except Exception as e:
        print("Error reconnecting MQTT:", e)
        time.sleep(5)

# Publish MQTT
def publishMQTT(client, Location, Type, Value):
    topic = Location + Type
    try:
        client.publish(topic, msg=str(Value))
    except Exception as e:
        print("Error publishing MQTT:", e)
        reconnect_mqtt(client)

# Read BME Sensor
def readBME():
    sensor = bme68x.BME68X()
    data = sensor.save_data('data.json')
    return round(data['T'], 1), round(data['H'], 1)

wlan = connect_wifi(WIFI_SSID, WIFI_PASSWORD)
led.on() if wlan.isconnected() else led.off()

# MQTT Settings and connection
client = MQTTClient('PicoW', MQTT_SERVER, user=MQTT_USER, password=MQTT_PASSWORD, keepalive=60)
reconnect_mqtt(client)

# Reference Values
Temperature_Reference = 0
Humidity_Reference = 0

while True:
    if not wlan.isconnected():
        wlan = connect_wifi(WIFI_SSID, WIFI_PASSWORD)
        reconnect_mqtt(client)
    Temperature, Humidity = readBME()
    if Temperature != Temperature_Reference:
        Temperature_Reference = Temperature
        publishMQTT(client, "LivingRoom/", "Temperature", Temperature)
        print("Temperature changed to ", Temperature)
    if Humidity != Humidity_Reference:
        Humidity_Reference = Humidity
        publishMQTT(client, "LivingRoom/", "Humidity", Humidity)
        print("Humidity changed to ", Humidity)
    time.sleep(30)

