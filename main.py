import network
import time
from umqtt.simple import MQTTClient
import bme68x
from machine import Pin

led = Pin('LED', Pin.OUT)
led.on()
time.sleep(1)
led.off()

def publishMQTT(Location, Type, Value):
    topic = Location + Type
    client.publish(topic, msg=str(Value))
    
def readBME():
    sensor = bme68x.BME68X()
    data = sensor.save_data('data.json')
    return round(data['T'], 1), round(data['H'], 1)
    

#Connect WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("<WiFi SSID>","<WiFi Password>")
wlan.ifconfig(('192.168.100.40', '255.255.255.0', '192.168.100.1', '8.8.8.8'))
time.sleep(5)


if wlan.isconnected() == True:
    led.on()

#MQTT Settings and connection
mqtt_server = '<Server IP>'
client_id = 'PicoW'
user_t = '<Username>'
password_t = '<Password>'
client = MQTTClient(client_id, mqtt_server, user=user_t, password=password_t, keepalive=60)
client.connect()

#For the BME
data = {
    'temperature_c': 0,
    'pressure_hPa': 0,
    'altitude_m': 0,
    'humidity_percent': 0,
    'G': 0,
    }

#Reference Values
Temperature_Reference = 0
Humidity_Reference = 0

while True:
    Temperature, Humidity = readBME()
    if Temperature != Temperature_Reference:
        Temperature_Reference = Temperature
        publishMQTT("LivingRoom/", "Temperature", Temperature)
        print("Temperature changed to ", Temperature)
    if Humidity != Humidity_Reference:
        Humidity_Reference = Humidity
        publishMQTT("LivingRoom/", "Humidity", Humidity)
        print("Humidity changed to ", Humidity)
    time.sleep(30)



