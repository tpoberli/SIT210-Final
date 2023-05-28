import pandas as pd
import matplotlib.pyplot as plt
import subprocess
import time
import csv
import datetime
import paho.mqtt.client as mqtt
import threading

# MQTT client callback functions
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("SIT210/wave")

def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))
    message = str(msg.payload.decode("utf-8"))
    data = message.split(",")
    
    light = (data[0][11:])
    moisture = (data[1][13:])
    temperature = (data[2][9:13].replace("}", ""))
    humidity = ((data[3][9:13]).replace("}", ""))
    
    with open('data.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        current_time = datetime.datetime.now()
        writer.writerow([current_time, light, moisture, temperature, humidity])

# MQTT client setup
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("broker.emqx.io", 1883, 60)

# Run the MQTT client in a separate thread
mqtt_thread = threading.Thread(target=client.loop_forever)
mqtt_thread.start()

# Define the directory where the command should be executed
directory = "rpi-rgb-led-matrix/bindings/python/samples"
base_command = "sudo python3 runtext.py -r=16 --led-gpio-mapping=regular --led-chain 1 --led-parallel 1 --led-brightness 100"

while True:
    # Read the CSV file using pandas
    data = pd.read_csv('data.csv')
    data = data.interpolate()  # Interpolate NaN values using linear interpolation

    # Extract the relevant columns from the data
    timestamp = pd.to_datetime(data['Timestamp'])
    light = data['Light']
    moisture = data['Moisture']
    temperature = data['Temperature']
    humidity = data['Humidity']

    # Calculate the mean of the last 10 values for each variable
    light_mean = light.tail(10).mean()
    moisture_mean = moisture.tail(10).mean()
    temperature_mean = temperature.tail(10).mean()
    humidity_mean = humidity.tail(10).mean()

    # Generate the text argument for the command
    text_arg = f"--text='Light: {light_mean:.2f}Lux Moisture: {moisture_mean:.2f} Temperature: {temperature_mean:.2f}°C Humidity: {humidity_mean:.2f}%'"

    # Construct the modified command
    command = f"{base_command} {text_arg}"

    # Run the command from the specified directory
    subprocess.run(command, shell=True, cwd=directory)

    # Wait for 10 minutes before the next iteration
    time.sleep(600)  # 600 seconds = 10 minutes
