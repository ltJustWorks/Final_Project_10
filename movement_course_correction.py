# iteration: 2
from vehicle_movement import drive, wait_until_motors_done 
from utils.brick import EV3ColorSensor, wait_ready_sensors, TouchSensor, reset_brick, busy_sleep
import brickpi3
from time import sleep
import threading

COLOR_SENSOR_FERRIS = EV3ColorSensor(3)
COLOR_SENSOR_OTHER = EV3ColorSensor(4)
BP = brickpi3.BrickPi3()
AUX_MOTOR_1 = BP.PORT_A
AUX_MOTOR_2 = BP.PORT_D
POWER_LIMIT = 80
SPEED_LIMIT = 1440
DEFAULT_SPEED = 500
DEFAULT_ROTATION = -840

class Color:
    ferris_norm_rgb = [0, 0, 0]
    other_norm_rgb = [0, 0, 0]

    def __init__(self, ferris, other):
        self.ferris_norm_rgb = ferris
        self.other_norm_rgb = other

    def equals(self, color_to_compare):
        # check if colors read are same, within some amount of variation
        # only need to check if one of the sensors reads green cause movement is not quite exact
        other_check = True
        ferris_check = True
        for i in range(3):
            if abs(color_to_compare.other_norm_rgb[i] - self.other_norm_rgb[i]) > variation:
                other_check = False
        for i in range(3):
            if abs(color_to_compare.ferris_norm_rgb[i] - self.ferris_norm_rgb[i]) > variation:
                ferris_check = False

        return other_check or ferris_check

    def ferris_equals(self, color_to_compare):
        ferris_check = True
        for i in range(3):
            if abs(color_to_compare.ferris_norm_rgb[i] - self.ferris_norm_rgb[i]) > variation:
                ferris_check = False
        return ferris_check

    def other_equals(self, color_to_compare):
        other_check = True
        for i in range(3):
            if abs(color_to_compare.other_norm_rgb[i] - self.other_norm_rgb[i]) > variation:
                other_check = False
        return other_check

#green = Color([0.21, 0.52, 0.27], [0.16, 0.61, 0.22])
green = Color([0.16, 0.61, 0.22], [0.21, 0.52, 0.27])
brown = Color([0.55, 0.26, 0.18], [0.25, 0.36, 0.39])
red = Color([0.83, 0.08, 0.09], [0.77, 0.14, 0.09])
blue = Color([0.26, 0.26, 0.48], [0.25, 0.36, 0.39])

#green_other = [0.16, 0.61, 0.22] # obtained from test readings
#green_ferris = [0.21, 0.52, 0.27]
variation = 0.06 # an arbitrary constant
drive_amount = 15
correction_amount = 20

def poll_norm_rgb(sensor):
    # polls sensor data and converts to normalized rgb values
    if sensor.get_value() == None or sum(sensor.get_value()) == 0:
        return [-1000, -1000, -1000]
    rgb = sensor.get_value()[:-1] 
    rgb = [round(x / sum(rgb), 2) for x in rgb]
    return rgb

stop_event = threading.Event()
def move():
    while not stop_event.is_set():
        drive(drive_amount, drive_amount)
        sleep(0.1)

def turn(direction="right"):
    while not stop_event.is_set():
        drive(0, drive_amount)
        sleep(0.1)

def sensor_poll_to_color():
    # polls data and converts to Color class
    print(poll_norm_rgb(COLOR_SENSOR_FERRIS), poll_norm_rgb(COLOR_SENSOR_OTHER))
    sleep(0.1)
    return Color(poll_norm_rgb(COLOR_SENSOR_FERRIS), poll_norm_rgb(COLOR_SENSOR_OTHER))
    

def move_a_block():
    move_task = threading.Thread(target=move, name='move_task')
    # color sensors are at green 
    print("at green")
    move_task.start()
    # detect when the color changes to brown
    while True:
        polled_color = sensor_poll_to_color()
        if not polled_color.equals(green):
            print("break from green detected")
            break

    # detect when the color changes back to green, then stop
    while True:
        polled_color = sensor_poll_to_color()
        if polled_color.equals(brown):
            print("brown detected")
        if polled_color.equals(green):
            print("green detected, should stop")
            stop_event.set()
            break

        """
        if (polled_color.ferris_equals(blue) or polled_color.ferris_equals(red)):
            print("line detected, ferris")
            wait_until_motors_done()
        elif (polled_color.other_equals(blue) or polled_color.other_equals(red)):
            print("line detected, other")
            wait_until_motors_done()
        """

    move_task.join()
    stop_event.clear()

def turn_to_line():
    # drive left motor until other sensor sees red
    turn_task = threading.Thread(target=turn, name='turn_task')
    turn_task.start()
    while True:
        polled_color = sensor_poll_to_color()
        if polled_color.other_equals(red) or polled_color.other_equals(blue):
            stop_event.set()
            break

    turn_task.join()
    stop_event.clear()

# main loop
wait_ready_sensors(True) # Input True to see what the robot is trying to initialize! False to be silent.
sleep(1)

try:
    print("BrickPi Motos Position Demo:")
    try:
        BP = brickpi3.BrickPi3 ()
        BP.offset_motor_encoder(AUX_MOTOR_1, BP.get_motor_encoder (AUX_MOTOR_1))
        BP.set_motor_limits (AUX_MOTOR_1, POWER_LIMIT, SPEED_LIMIT)
        BP.set_motor_limits (AUX_MOTOR_1 ,0)
        BP.offset_motor_encoder(AUX_MOTOR_2, BP.get_motor_encoder (AUX_MOTOR_2))
        BP.set_motor_limits (AUX_MOTOR_2, POWER_LIMIT, SPEED_LIMIT)
        BP.set_motor_limits (AUX_MOTOR_2 ,0)
    except IOError as error:
        print(error)
    
    try:
        move_a_block()
        turn_to_line()
    except IOError as error:
        print(error)
except KeyboardInterrupt:
    BP.reset_all()

BP.reset_all()
