#!/usr/bin/env python3

"""
This test is used to collect data from the color sensor.
It must be run on the robot.
"""

# Add your imports here, if any
from utils.brick import EV3ColorSensor, wait_ready_sensors, TouchSensor, reset_brick, busy_sleep
from time import sleep


DELAY_SEC = 0.01  # seconds of delay between measurements
COLOR_SENSOR_DATA_FILE = "../data_analysis/color_sensor.csv"

# complete this based on your hardware setup
COLOR_SENSOR = EV3ColorSensor(4)
COLOR_SENSOR_FERRIS = EV3ColorSensor(2)

wait_ready_sensors(True) # Input True to see what the robot is trying to initialize! False to be silent.


def collect_color_sensor_data():
    "Collect color sensor data."
    try:
        while True:
            sleep(1)
            other_rgb = COLOR_SENSOR.get_value()[:-1]
            other_rgb = [round(x / sum(other_rgb), 2) for x in other_rgb]
            ferris_rgb = COLOR_SENSOR_FERRIS.get_value()[:-1]
            ferris_rgb = [round(x / sum(ferris_rgb), 2) for x in ferris_rgb]

            print("other sensor: ", other_rgb, "ferris sensor: ", ferris_rgb)

            
    except KeyboardInterrupt as e:  # capture all exceptions including KeyboardInterrupt (Ctrl-C)
        print("Interrupt,", error)
        pass
    finally:
        print("Done collecting color samples")
        reset_brick() # Turn off everything on the brick's hardware, and reset it
        exit()


if __name__ == "__main__":
    collect_color_sensor_data()
