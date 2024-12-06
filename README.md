# IoT-system-for-automatic-window-control

# Raspberry Pi Pico Weather Monitoring and Motor Control

This project uses a Raspberry Pi Pico to monitor temperature and pressure using a BMP280 sensor. The data is sent to both **ThingSpeak** (via MQTT) and **Google Sheets** (via HTTP requests). Additionally, based on the temperature readings, a motor connected via an L298N motor driver is controlled.

## Features
- Read temperature and pressure data from the BMP280 sensor.
- Publish temperature and pressure data to **ThingSpeak** via MQTT.
- Send data to **Google Sheets** using HTTP requests for real-time data logging.
- Control an L298N motor driver to move the motor based on temperature readings (move forward if temperature exceeds 30°C and move backward if it falls below 30°C).
- Display sensor data and status on an OLED display (SSD1306).
- Automatically scan and connect to available Wi-Fi networks.

## Components Required
- Raspberry Pi Pico
- BMP280 sensor (for temperature and pressure measurement)
- L298N motor driver
- DC Motor
- OLED display (SSD1306)
- Wi-Fi network (for internet connectivity)
- MQTT broker (ThingSpeak)
- Google Sheets integration (via a Google Apps Script)

## Setup
1. Connect the BMP280 sensor to the Raspberry Pi Pico via I2C.
2. Connect the L298N motor driver and a DC motor.
3. Connect the OLED display (SSD1306) to the Raspberry Pi Pico via I2C.
4. Configure the ThingSpeak MQTT channel and Google Sheets API endpoint in the code.
5. Upload the code to the Raspberry Pi Pico and run the program.

## How It Works
- The code scans available Wi-Fi networks and connects to a chosen network.
- It then reads temperature and pressure data from the BMP280 sensor and sends this data to **ThingSpeak** and **Google Sheets**.
- The motor is controlled based on the temperature: if the temperature is above 30°C, the motor moves forward; if the temperature is below 30°C, the motor moves backward.
- The system displays real-time temperature, pressure, and operational status on an OLED screen.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
