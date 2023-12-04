import brickpi3
import time
from time import sleep
from vehicle_movement import wait_until_motors_done


INIT_TIME = 1

BP = brickpi3.BrickPi3()
AUX_MOTOR_1 = BP.PORT_C
AUX_MOTOR_2 = BP.PORT_B
POWER_LIMIT = 20
SPEED_LIMIT = 75

extinguisherList = "LABCDEF"
last_code = "A"


def find_degrees(pos_a,pos_b):
    total_degrees= 363
    num_positions = 6
    angular_distance = -total_degrees/num_positions
    index_a = extinguisherList.index(pos_a)
    index_b = extinguisherList.index(pos_b)
    position_difference  = (index_b - index_a) % num_positions
    degrees_to_move = position_difference * angular_distance
    return degrees_to_move

try:
    print("BrickPi Motors ferris Ferris Wheel Demo:")
    try:
        BP = brickpi3.BrickPi3 ()
        #BP.offset_motor_encoder(AUX_MOTOR_1, BP.get_motor_encoder (AUX_MOTOR_1)) #Set motor initial position to 0 for a certain angle
        BP.set_motor_limits (AUX_MOTOR_1, POWER_LIMIT, SPEED_LIMIT)
        ##BP.set_motor_limits (AUX_MOTOR_1 ,0)
        ##BP.offset_motor_encoder(AUX_MOTOR_2, BP.get_motor_encoder (AUX_MOTOR_2))
        BP.set_motor_limits (AUX_MOTOR_2, POWER_LIMIT, SPEED_LIMIT)
        ##BP.set_motor_limits (AUX_MOTOR_2 ,0)
        BP.set_motor_position(AUX_MOTOR_1, 0)
        BP.set_motor_position_relative(AUX_MOTOR_1, -362)
        #BP.set_motor_position_relative(AUX_MOTOR_1, 130) ## -25 is the right value for the initial position according to the preset initial angle position of the motor
        #BP.set_motor_position_relative(AUX_MOTOR_1, -20)
    except IOError as error:
        print(error)
    
    while True:
        code = input("enter cube code:")
        ##BP.set_motor_limits (AUX_MOTOR_1, POWER_LIMIT, SPEED_LIMIT)
        ##BP.set_motor_limits (AUX_MOTOR_2, POWER_LIMIT, SPEED_LIMIT)
        ##BP.set_motor_position_relative (AUX_MOTOR_1, 0)
        ##BP.set_motor_position_relative (AUX_MOTOR_2, 0)
        try:
            if not(code in "LABCDEF"):
                print("No corresponding extinguisher")
                continue
            if (code == "L"):
                BP.set_motor_position(AUX_MOTOR_1, 0)
                BP.set_motor_limits (AUX_MOTOR_1 ,0)
                BP.set_motor_limits (AUX_MOTOR_2 ,0)
                break
            else:
                BP.set_motor_position_relative(AUX_MOTOR_1, find_degrees(last_code, code))
                sleep(3)
                last_code = code
            sleep(1)
            BP.set_motor_position_relative(AUX_MOTOR_2, -50)
            sleep(1)
            BP.set_motor_position_relative(AUX_MOTOR_2, 50)
            sleep(1)
        except IOError as error:
            print(error)
except KeyboardInterrupt:
    BP.reset_all()
                    

