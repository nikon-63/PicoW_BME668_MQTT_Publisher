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
led.off()

def connect_wifi(SSID, PASSWORD):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to network...')
        wlan.connect(SSID, PASSWORD)
        wlan.ifconfig(('192.168.100.40', '255.255.255.0', '192.168.100.1', '8.8.8.8'))
        retries = 0
        while not wlan.isconnected():
            retries += 1
            if retries > 3:
                print("Failed to connect to Wi-Fi. Restarting system.")
                machine.reset()
                time.sleep(1)
            else:
                time.sleep(5)
    print('Network configuration:', wlan.ifconfig())
    return wlan 

def connect_mqtt():
    client = MQTTClient('PicoW-LivingRoom', MQTT_SERVER, user=MQTT_USER, password=MQTT_PASSWORD, keepalive=60)
    try:
        client.connect()
        print("MQTT reconnected")
        return client
    except Exception as e:
        print("Error reconnecting MQTT:", e)
        machine.reset()

def publishMQTT(client, Location, Type, Value):
    topic = Location + Type
    try:
        client.publish(topic, msg=str(Value))
    except Exception as e:
        print("Error publishing MQTT:", e)
        connect_mqtt()

def readBME():
    sensor = bme68x.BME68X()
    data = sensor.save_data('data.json')
    return round(data['T'], 1), round(data['H'], 1)

wlan = connect_wifi(WIFI_SSID, WIFI_PASSWORD)
led.on() if wlan.isconnected() else led.off()

client = connect_mqtt()

Temperature_Reference = 0
Humidity_Reference = 0

while True:
    if not wlan.isconnected():
        led.off()
        wlan = connect_wifi(WIFI_SSID, WIFI_PASSWORD)
        client = connect_mqtt()
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
