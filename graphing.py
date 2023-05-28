import pandas as pd
import matplotlib.pyplot as plt

# Set the time window for the graphed data
#start_time = pd.Timestamp('2023-05-24 14:51:22')
start_time = pd.Timestamp('2023-05-24')
end_time = pd.Timestamp('2023-12-31')

# Read the CSV file using pandas
data = pd.read_csv('data.csv')
data = data.interpolate()  # Interpolate NaN values using linear interpolation

# Extract the relevant columns from the data
timestamp = pd.to_datetime(data['Timestamp'])
light = data['Light']
moisture = data['Moisture']
temperature = data['Temperature']
humidity = data['Humidity']

# Filter the data based on the time window
time_filtered_data = data[(timestamp >= start_time) & (timestamp <= end_time)]
time_filtered_timestamp = timestamp[(timestamp >= start_time) & (timestamp <= end_time)]

# Create subplots for each sensor
fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, sharex=True)

# Plot for Light
ax1.plot(time_filtered_timestamp, time_filtered_data['Light'], label='Light')
ax1.set_ylabel('Light')
ax1.legend()

# Plot for Moisture
ax2.plot(time_filtered_timestamp, time_filtered_data['Moisture'], label='Moisture')
ax2.set_ylabel('Moisture')
ax2.legend()

# Plot for Temperature
ax3.plot(time_filtered_timestamp, time_filtered_data['Temperature'], label='Temperature')
ax3.set_ylabel('Temperature')
ax3.legend()

# Plot for Humidity
ax4.plot(time_filtered_timestamp, time_filtered_data['Humidity'], label='Humidity')
ax4.set_xlabel('Timestamp')
ax4.set_ylabel('Humidity')
ax4.legend()

# Adjust layout and display the plots
plt.tight_layout()
plt.show()
