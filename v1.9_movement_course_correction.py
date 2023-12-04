# iteration: 3
from vehicle_movement import drive, wait_until_motors_done 
from utils.brick import EV3ColorSensor, wait_ready_sensors, TouchSensor, reset_brick, busy_sleep
import brickpi3
from time import sleep
import threading
from color_classifier import classify_color
from Wheel import init_carousel, drop_cube 

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
backwards_adjust_event = threading.Event()
reverse_event = threading.Event()
adjust_event = threading.Event()
adjust_left_event = threading.Event()
adjust_right_event = threading.Event()

drop_event = threading.Event()
drop_A_event = threading.Event()
drop_B_event = threading.Event()
drop_C_event = threading.Event()
drop_D_event = threading.Event()
drop_E_event = threading.Event()
drop_F_event = threading.Event()


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
        
        elif backwards_adjust_event.is_set():
            if adjust_left_event.is_set():
                backwards_adjust_left()
            elif adjust_right_event.is_set():
                backwards_adjust_right()

        elif turn_event.is_set():
            if turn_left_event.is_set():
                turn("left")
            elif turn_right_event.is_set():
                turn("right")
        
        elif drop_event.is_set():
            if drop_A_event.is_set():
                drop_cube("A")
            elif drop_B_event.is_set():
                drop_cube("B")
            elif drop_C_event.is_set():
                drop_cube("C")
            elif drop_D_event.is_set():
                drop_cube("D")
            elif drop_E_event.is_set():
                drop_cube("E")
            elif drop_F_event.is_set():
                drop_cube("F")

        sleep(0.02)

turn_event = threading.Event()
turn_left_event = threading.Event()
turn_right_event = threading.Event()

def turn(direction):
    if direction == "left":
        drive(drive_amount, 0)
    elif direction == "right":
        drive(0, drive_amount)

adjust_amount = 6 # hardcoded
def adjust_left():
    drive(adjust_amount, -adjust_amount)

def adjust_right():
    drive(-adjust_amount, adjust_amount)
    #TEMP CHANGES
def backwards_adjust_left():
    drive(0, adjust_amount)

def backwards_adjust_right():
    drive(adjust_amount, 0)

def sensor_poll_to_color():
    # polls data and converts to Color class
    sleep(0.1)
    color = Color(poll_norm_rgb(COLOR_SENSOR_FERRIS), poll_norm_rgb(COLOR_SENSOR_OTHER))
    #print((poll_norm_rgb(COLOR_SENSOR_FERRIS), poll_norm_rgb(COLOR_SENSOR_OTHER)), end=' ')
    #print(color.get_ferris_color(), color.get_other_color())
    return color

current_line_color = "blue" # hardcoded, TODO ask ta about starting position

def opposite_color(color):
    if color == "blue":
        return "red"
    elif color == "red":
        return "blue"

def move_a_block(direction="forwards"):
    global current_line_color
    # color sensors are at green 
    print("at green")
    if direction == "backwards":
        reverse_event.set()
    else:
        move_event.set()

    # detect when the color changes to brown
    while True:
        polled_color = sensor_poll_to_color()
        if (not polled_color.get_ferris_color() == "green") and (not polled_color.get_other_color() == "green"):
            print("break from green detected")
            break

    # detect when the color changes back to green, then stop
    while True:
        polled_color = sensor_poll_to_color()

        # If left sensor detects red or blue
        if (polled_color.get_other_color() == current_line_color):
            if direction == "backwards":
                reverse_event.clear()

                backwards_adjust_event.set()
                adjust_left_event.set()
                while True:
                    polled_color = sensor_poll_to_color()
                    if not (polled_color.get_other_color() == current_line_color):
                        sleep(0.02)
                        adjust_left_event.clear()
                        break
                
                backwards_adjust_event.clear()
                reverse_event.set()

            else:
                #print("Line detected, left sensor")
                # Stop moving
                move_event.clear()

                # Adjust by moving left motor back and right motor forward
                adjust_event.set()
                adjust_left_event.set()
                while True:
                    polled_color = sensor_poll_to_color()
                    if not (polled_color.get_other_color() == current_line_color):
                        #print("adjust end")
                        sleep(0.02) # hardcoded
                        adjust_left_event.clear()
                        break
                # Start moving again
                adjust_event.clear()
                move_event.set()

        # If right sensor detects red or blue
        if (polled_color.get_ferris_color() == current_line_color):
            if direction == "backwards":
                reverse_event.clear()

                backwards_adjust_event.set()
                adjust_left_event.set()
                while True:
                    polled_color = sensor_poll_to_color()
                    if not (polled_color.get_other_color() == current_line_color):
                        sleep(0.01)
                        adjust_left_event.clear()
                        break
                
                backwards_adjust_event.clear()
                reverse_event.set()
            
            else:
            #print("Line detected, right sensor")
            # Stop moving
                move_event.clear()

                # Adjust by moving left motor back and right motor forward
                adjust_event.set()
                adjust_right_event.set()
                while True:
                    polled_color = sensor_poll_to_color()

                    if not (polled_color.get_ferris_color() == current_line_color):
                        sleep(0.01)
                        adjust_left_event.clear()
                        break
                # Start moving again
                adjust_event.clear()
                move_event.set()

        if polled_color == "brown":
            pass
            #print("brown detected")
        polled_color = sensor_poll_to_color()
        if any_sensor_sees_green(polled_color):
            print("green detected, should stop")
            move_event.clear()
            reverse_event.clear()
            break
        
    # move to the outside part of the green square
    if direction == "forwards":
        move_event.set()
    while True:
        polled_color = sensor_poll_to_color()
        if not any_sensor_sees_green(polled_color):
            move_event.clear()
            break
    reverse_event.set()
    while True:
        if any_sensor_sees_green(sensor_poll_to_color()):
            sleep(0.02)
            reverse_event.clear()
            break
    sleep(1)

def any_sensor_sees_green(polled_color):
    return polled_color.get_ferris_color() == "green" or polled_color.get_other_color() == "green"

def no_sensor_sees_green(polled_color):
    return polled_color.get_ferris_color() != "green" or polled_color.get_other_color() != "green"

def turn_to_line(direction):
    global current_line_color

    #print("turn function started")
    print("current line color is:", current_line_color)

    move_event.set()
    sleep(.3)
    move_event.clear()

    if direction == "left":
        adjust_event.set()
        adjust_left_event.set()
        sleep(1.28)
        adjust_event.clear()
        adjust_left_event.clear()

    elif direction == "right":
        adjust_event.set()
        adjust_right_event.set()
        sleep(1.1)
        adjust_event.clear()
        adjust_right_event.clear()
    
    # back up until reaches green

    reverse_event.set()
    sleep(0.3)
    reverse_event.clear()
        
        
    """
    turn_event.set()
    if direction == "left":
        turn_left_event.set()
        while True:
            polled_color = sensor_poll_to_color().get_ferris_color()
            if polled_color == opposite_color(current_line_color):
                turn_event.clear()
                turn_left_event.clear()
                turn_right_event.clear()
                # adjust a bit (hardcoded)
                adjust_event.set()
                adjust_right_event.set()
                sleep(.3)
                adjust_event.clear()
                adjust_right_event.clear()
                break
    elif direction == "right":
        turn_right_event.set()
        while True:
            polled_color = sensor_poll_to_color().get_other_color()
            if polled_color == opposite_color(current_line_color):
                turn_event.clear()
                turn_left_event.clear()
                turn_right_event.clear()
                # adjust a bit (hardcoded)
                adjust_event.set()
                adjust_left_event.set()
                sleep(.3)
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
    """

    if current_line_color == "blue":
        current_line_color = "red"
    else:
        current_line_color = "blue"

    print("new line color is:", current_line_color)
    sleep(1)
    #print("turning done")

def wait_for_movement_done():
    while True:
        if not move_event.is_set():
            break
    
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
        init_carousel()
    except IOError as error:
        print(error)
    
    try:
        move_task = threading.Thread(target=move, name='turn_task')
        move_task.start()

        while True:
            user_input = input("Enter your action (left, right, left_three, right_three, forwards, backwards): ").lower()

            if user_input == 'left':
                turn_to_line('left')
                wait_for_movement_done()
            elif user_input == 'right':
                turn_to_line('right')
                wait_for_movement_done()
            elif user_input == 'left_three':
                for _ in range(3):
                    turn_to_line('left')
                    wait_for_movement_done()
            elif user_input == 'right_three':
                for _ in range(3):
                    turn_to_line('right')
                    wait_for_movement_done()
            elif user_input == 'forwards':
                move_a_block()
                wait_for_movement_done()
            elif user_input == 'backwards':
                move_a_block('backwards')
                wait_for_movement_done()

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
        #drop_cube("A")
        #wait_for_movement_done()
        #move_a_block("backwards")
        #wait_for_movement_done()
        """       

        move_task.join()

    except IOError as error:
        print(error)
except KeyboardInterrupt:
    BP.reset_all()

BP.reset_all()
