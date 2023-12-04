import brickpi3

from brick import busy_sleep

INIT_TIME = 1

BP = brickpi3.BrickPi3()
AUX_MOTOR_1 = BP.PORT_A
AUX_MOTOR_2 = BP.PORT_D
POWER_LIMIT = 80
SPEED_LIMIT = 1440
DEFAULT_SPEED = 950
DEFAULT_ROTATION = -840

def is_moving():
    return BP.get_motor_status(AUX_MOTOR_1)[3] != 0 or BP.get_motor_status(AUX_MOTOR_2)[3] != 0

def wait_until_motors_done():
    while not is_moving():
        busy_sleep(0.05)
    while is_moving():
        busy_sleep(0.1)

def drive(left_rotation, right_rotation):
    BP.set_motor_limits (AUX_MOTOR_1, POWER_LIMIT, DEFAULT_SPEED*2.25)
    BP.set_motor_position_relative (AUX_MOTOR_1, left_rotation*1.26) #hardcoded to deal with right drift
    BP.set_motor_limits (AUX_MOTOR_2, POWER_LIMIT, DEFAULT_SPEED)
    BP.set_motor_position_relative (AUX_MOTOR_2, right_rotation)

def turn(direction="left"):
    # just implementing left direction for now
    CONST_1 = 380
    CONST_2 = 250
    CONST_3 = 360

    # drive bot forward
    drive(-CONST_1, -CONST_1) # constants will be hardcoded later
    wait_until_motors_done()

    # turn left wheel back, right wheel forward
    drive(CONST_2, -CONST_2) # constants will be hardcoded later
    wait_until_motors_done()

    # drive bot backward
    drive(CONST_3, CONST_3)
    wait_until_motors_done()
    #busy_sleep(10) # MIGHT NOT BE A GOOD IMPLEMENTATION. PLEASE REVIEW

def do_a_thing():
    for i in range(4):
        move(3)
        turn("left")


def move(num_blocks):
    drive(DEFAULT_ROTATION*num_blocks, DEFAULT_ROTATION*num_blocks)
    wait_until_motors_done()

'''
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
        blocks_to_move = 4
        stuff = str(input("Press m to move a block, t to turn left, d to do a thing"))
        try:
            if stuff == "m":
                move(1)
            elif stuff == "t":
                turn()
            elif stuff == "d":
                do_a_thing()
        except IOError as error:
            print(error)
except KeyboardInterrupt:
    BP.reset_all()
'''
