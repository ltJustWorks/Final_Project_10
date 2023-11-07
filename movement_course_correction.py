# iteration: 3
from vehicle_movement import drive, wait_until_motors_done 
from utils.brick import EV3ColorSensor, wait_ready_sensors, TouchSensor, reset_brick, busy_sleep
import brickpi3
from time import sleep
import threading
from color_classifier import classify_color

COLOR_SENSOR_FERRIS = EV3ColorSensor(2)
COLOR_SENSOR_OTHER = EV3ColorSensor(4)
BP = brickpi3.BrickPi3()
AUX_MOTOR_1 = BP.PORT_A
AUX_MOTOR_2 = BP.PORT_D
POWER_LIMIT = 80
SPEED_LIMIT = 1440
DEFAULT_SPEED = 950
DEFAULT_ROTATION = -840

class Color:
    def __init__(self, ferris, other):
        self.ferris_norm_rgb = ferris
        self.other_norm_rgb = other
    
    def get_other_color(self):
        return classify_color(self.other_norm_rgb)
    
    def get_ferris_color(self):
        return classify_color(self.ferris_norm_rgb)

    def get_color(self):
        # check if colors read are same, within some amount of variation
        # only need to check if one of the sensors reads green cause movement is not quite exact
        # just check other_norm_rgb for now, if needed take avg of other and ferris rgb arrays
        return self.get_other_color()
    

# deprecated, use classify_color instead
#green = Color([0.21, 0.52, 0.27], [0.16, 0.61, 0.22])
#green = Color([0.16, 0.61, 0.22], [0.21, 0.53, 0.27])
#brown = Color([0.55, 0.26, 0.18], [0.25, 0.36, 0.39])
#red = Color([0.83, 0.08, 0.09], [0.71, 0.16, 0.12])
#blue = Color([0.26, 0.26, 0.48], [0.25, 0.36, 0.39])

#green_other = [0.16, 0.61, 0.22] # obtained from test readings
#green_ferris = [0.21, 0.52, 0.27]
#variation = 0.09 # an arbitrary constant
drive_amount = 11
correction_amount = 30

def poll_norm_rgb(sensor):
    # polls sensor data and converts to normalized rgb values
    if sensor.get_value() == None or sum(sensor.get_value()) == 0:
        return [-1000, -1000, -1000]
    rgb = sensor.get_value()[:-1] 
    rgb = [round(x / sum(rgb), 2) for x in rgb]
    return rgb

move_event = threading.Event()
reverse_event = threading.Event()
adjust_event = threading.Event()
adjust_left_event = threading.Event()
adjust_right_event = threading.Event()

def move():
    while True:
        if move_event.is_set():
            drive(drive_amount, drive_amount)
        elif reverse_event.is_set():
            drive(-drive_amount, -drive_amount)

        elif adjust_event.is_set():
            #print("in adjust mode")
            if adjust_left_event.is_set():
                #print("adjusting left")
                adjust_left()
            elif adjust_right_event.is_set():
                #print("adjusting right")
                adjust_right()

        elif turn_event.is_set():
            if turn_left_event.is_set():
                turn("left")
            elif turn_right_event.is_set():
                turn("right")

        sleep(0.02)

turn_event = threading.Event()
turn_left_event = threading.Event()
turn_right_event = threading.Event()

def turn(direction):
    if direction == "left":
        drive(drive_amount, 0)
    elif direction == "right":
        drive(0, drive_amount)

adjust_amount = 12 # hardcoded
def adjust_left():
    drive(adjust_amount, -adjust_amount)

def adjust_right():
    drive(-adjust_amount, adjust_amount)

def sensor_poll_to_color():
    # polls data and converts to Color class
    sleep(0.1)
    print((poll_norm_rgb(COLOR_SENSOR_FERRIS), poll_norm_rgb(COLOR_SENSOR_OTHER)), end=' ')
    print(Color(poll_norm_rgb(COLOR_SENSOR_FERRIS), poll_norm_rgb(COLOR_SENSOR_OTHER)).get_color())
    return Color(poll_norm_rgb(COLOR_SENSOR_FERRIS), poll_norm_rgb(COLOR_SENSOR_OTHER))

def move_a_block():
    # color sensors are at green 
    #print("at green")
    move_event.set()
    # detect when the color changes to brown
    while True:
        polled_color = sensor_poll_to_color().get_color()
        if not polled_color == "green":
            #print("break from green detected")
            break

    # detect when the color changes back to green, then stop
    while True:
        polled_color = sensor_poll_to_color()

        # If left sensor detects red or blue
        if polled_color.get_other_color() == "red" or polled_color.get_other_color() == "blue":
            #print("Line detected, left sensor")
            # Stop moving
            move_event.clear()
            # Adjust by moving left motor back and right motor forward
            adjust_event.set()
            adjust_left_event.set()
            while True:
                polled_color = sensor_poll_to_color()
                if not (polled_color.get_other_color() == "red" or polled_color.get_other_color() =="blue"):
                    #print("adjust end")
                    sleep(0.02) # hardcoded
                    adjust_left_event.clear()
                    break
            # Start moving again
            adjust_event.clear()
            move_event.set()

        # If right sensor detects red or blue
        if polled_color.get_ferris_color() == "red" or polled_color.get_ferris_color() == "blue":
            #print("Line detected, right sensor")
            # Stop moving
            move_event.clear()
            # Adjust by moving left motor back and right motor forward
            adjust_event.set()
            adjust_right_event.set()
            while True:
                polled_color = sensor_poll_to_color()

                if not (polled_color.get_ferris_color() == "blue" or polled_color.get_ferris_color() == "red"):
                    sleep(0.02)
                    adjust_left_event.clear()
                    break
            # Start moving again
            adjust_event.clear()
            move_event.set()

        if polled_color == "brown":
            pass
            #print("brown detected")
        polled_color = sensor_poll_to_color()
        if polled_color.get_ferris_color() == "green" or polled_color.get_ferris_color() == "green":
            print("green detected, should stop")
            move_event.clear()
            break

    sleep(1)

def turn_to_line(direction):

    #print("turn function started")
    turn_event.set()
    if direction == "left":
        turn_left_event.set()
        while True:
            polled_color = sensor_poll_to_color().get_ferris_color()
            if polled_color == "red" or polled_color == "blue":
                turn_event.clear()
                turn_left_event.clear()
                turn_right_event.clear()
                # adjust a bit (hardcoded)
                adjust_event.set()
                adjust_right_event.set()
                sleep(.6)
                adjust_event.clear()
                adjust_right_event.clear()
                break
    elif direction == "right":
        turn_right_event.set()
        while True:
            polled_color = sensor_poll_to_color().get_other_color()
            if polled_color == "red" or polled_color == "blue":
                turn_event.clear()
                turn_left_event.clear()
                turn_right_event.clear()
                # adjust a bit (hardcoded)
                adjust_event.set()
                adjust_left_event.set()
                sleep(.6)
                adjust_event.clear()
                adjust_left_event.clear()
                break
    
    # back up until green reached
    reverse_event.set()
    while True:
        polled_color = sensor_poll_to_color()
        if polled_color.get_other_color() == "green" or polled_color.get_ferris_color() == "green":
            reverse_event.clear()
            break
    sleep(1)
    #print("turning done")
    
# main loop
print("before initialization")
wait_ready_sensors(True) # Input True to see what the robot is trying to initialize! False to be silent.
print("after initialization")
sleep(0.5)

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
        move_task = threading.Thread(target=move, name='turn_task')
        move_task.start()

        for i in range(4):
            print(f"turn number {i}")
            for j in range(3):
                print(f"move number: {j}")
                move_a_block()
                while True:
                    if not move_event.is_set():
                        break
            
            turn_to_line("left")
            while True:
                if not move_event.is_set():
                    break

        """
        for i in range(2):
            move_a_block()
            sleep(0.1)
            while True:
                if not move_event.is_set():
                    break
            turn_to_line("left")
            while True:
                print("turning")
                if not move_event.is_set():
                    print("turning done")
                    break
            move_a_block()
            while True:
                if not move_event.is_set():
                    break
            turn_to_line("right")
            while True:
                if not move_event.is_set():
                    break
        """

        move_task.join()

    except IOError as error:
        print(error)
except KeyboardInterrupt:
    BP.reset_all()

BP.reset_all()
