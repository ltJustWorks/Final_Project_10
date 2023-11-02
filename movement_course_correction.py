# iteration: 2
from vehicle_movement import drive, wait_until_motors_done 
from utils.brick import EV3ColorSensor, wait_ready_sensors, TouchSensor, reset_brick
import brickpi3
from time import sleep

COLOR_SENSOR_FERRIS = EV3ColorSensor(4)
COLOR_SENSOR_OTHER = EV3ColorSensor(3)
BP = brickpi3.BrickPi3()
AUX_MOTOR_1 = BP.PORT_A
AUX_MOTOR_2 = BP.PORT_D
POWER_LIMIT = 80
SPEED_LIMIT = 1440
DEFAULT_SPEED = 500
DEFAULT_ROTATION = -840


green_other = [0.16, 0.61, 0.22]
green_ferris = [0.21, 0.52, 0.27]
variation = 0.6
drive_amount = 360

def isColorGreen(color_other, color_ferris):
    # check if colors read are green, within some amount of variation
    check = True

    for i in range(3):
        if abs(color_other[i] - green_other[i]) > variation:
            check = False
    for i in range(3):
        if abs(color_ferris[i] - green_ferris[i]) > variation:
            check = False

    return check

def poll_norm_rgb(sensor):
    # polls sensor data and converts to normalized rgb values
    if sensor.get_value() == None or sum(sensor.get_value()) == 0:
        return [-1000, -1000, -1000]
    rgb = sensor.get_value()[:-1] 
    print(rgb)
    return [round(x / sum(rgb), 2) for x in rgb]

def get_color(norm_rgb):
    # gets color from normalized rgb value array
    # IMPLEMENT THIS LATER, USE AN ENUM OR SOMETHING LIKE THAT IDK IF ENUMS EXIST IN PYTHON
    pass

def move_test():
    # color sensors are at green 
    # detect when the color changes to brown
    while True:
        if not isColorGreen(poll_norm_rgb(COLOR_SENSOR_OTHER), poll_norm_rgb(COLOR_SENSOR_FERRIS)):
            break
        drive(drive_amount, drive_amount)
        wait_until_motors_done()

    # detect when the color changes back to green, then stop
    while True:
        if isColorGreen(poll_norm_rgb(COLOR_SENSOR_OTHER), poll_norm_rgb(COLOR_SENSOR_FERRIS)):
            break
        drive(drive_amount, drive_amount)
        wait_until_motors_done()

# main loop
wait_ready_sensors(True) # Input True to see what the robot is trying to initialize! False to be silent.

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
    
    while True:
        try:
            sleep(1)
            if isColorGreen(poll_norm_rgb(COLOR_SENSOR_OTHER), poll_norm_rgb(COLOR_SENSOR_FERRIS)):
                print("color is green")
            else:
                print("color is not green", poll_norm_rgb(COLOR_SENSOR_OTHER), poll_norm_rgb(COLOR_SENSOR_FERRIS))
        except IOError as error:
            print(error)
except KeyboardInterrupt:
    BP.reset_all()

BP.reset_all()
