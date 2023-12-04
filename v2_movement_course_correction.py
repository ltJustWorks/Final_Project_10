# iteration: 3
from vehicle_movement import drive, wait_until_motors_done 
from utils.brick import EV3ColorSensor, wait_ready_sensors, TouchSensor, reset_brick, busy_sleep
import brickpi3
from time import sleep
import threading
from color_classifier import classify_color
import Wheel


COLOR_SENSOR_FERRIS = EV3ColorSensor(2) #Right side color sensor initialization
COLOR_SENSOR_OTHER = EV3ColorSensor(4) #Left side color sensor initialization
BP = brickpi3.BrickPi3() #Brickpi instantiation
AUX_MOTOR_1 = BP.PORT_A #Right Motor
AUX_MOTOR_2 = BP.PORT_D # Left Motor
POWER_LIMIT = 80
SPEED_LIMIT = 1440
DEFAULT_SPEED = 950
DEFAULT_ROTATION = -840
drive_amount = 11  # Amount of rotation for forward drive
correction_amount = 30 
adjust_amount = 12 # hardcoded amount of rotation for turns
correct_amount = 8 # Course correction amount
backwards_adjust_amount = 9 # Backwards adjustment amount




class building: #Building objects used to determine paths and movements
    def __init__(self, name, distance):
        self.name = name # Name in the ## format.
        self.distance = distance # Distance from a certain building to be determined later.
        self.previous = None
        self.neighbors = None
        self.fire = None
        self.x = int(name[0])
        self.y = int(name[1])
        self.status = "safe"
        
def initiate(): #Initiate all 16 buildings
    building_list = []
    global p00
    p00 = building("00",999)
    building_list.append(p00)
    global p01
    p01 = building("01",999)
    building_list.append(p01)
    global p02
    p02 = building("02",999)
    building_list.append(p02)
    global p03
    p03 = building("03",999)
    building_list.append(p03)
    global p10
    p10 = building("10",999)
    building_list.append(p10)
    global p11
    p11 = building("11",999)
    building_list.append(p11)
    global p12
    p12 = building("12",999)
    building_list.append(p12)
    global p13
    p13 = building("13",999)
    building_list.append(p13)
    global p20
    p20 = building("20",999)
    building_list.append(p20)
    global p21
    p21 = building("21",999)
    building_list.append(p21)
    global p22
    p22 = building("22",999)
    building_list.append(p22)
    global p23
    p23 = building("23",999)
    building_list.append(p23)
    global p30
    p30 = building("30",999)
    building_list.append(p30)
    global p31
    p31 = building("31",999)
    building_list.append(p31)
    global p32
    p32 = building("32",999)
    building_list.append(p32)
    global p33
    p33 = building("33",999)
    building_list.append(p33)

    #Set neighbors
    p00.neighbors = [p01, p10]
    p01.neighbors = [p00, p02, p11]
    p02.neighbors = [p01, p03, p12]
    p03.neighbors = [p02, p13]

    p10.neighbors = [p11, p00, p20]
    p11.neighbors = [p10, p12, p01, p21]
    p12.neighbors = [p11, p13, p02, p22]
    p13.neighbors = [p03, p23, p12]

    p20.neighbors = [p10, p30, p21]
    p21.neighbors = [p11, p31, p20, p22]
    p22.neighbors = [p21, p23, p12, p32]
    p23.neighbors = [p13, p33, p22]

    p30.neighbors = [p20, p31]
    p31.neighbors = [p30, p32, p21]
    p32.neighbors = [p31, p33, p22]
    p33.neighbors = [p23, p32]
    
    return building_list

def movements(S, orientation): #Create sequence of movements for the robot from the list of buildings to go to
    M =[]
    for i in range(len(S)):
        B = S[i] #current building
        if(B.status=="nextFire"):
            if(B.name=="00"):
                if (orientation == "-x"):
                    M.append("right")
                    M.append("right")
                elif (orientation == "-y"):
                    M.append("left")
                    
                M.append("stop")
            else:
                M.append("drop")
                M.append("back up")
        else:
            nextB = S[i+1] #next building
            x0 = B.x
            y0 = B.y
            x1 = nextB.x
            y1 = nextB.y

            deltaX = x1-x0
            deltaY = y1-y0
            if deltaX!=0:
                if(deltaX<0):
                    if(orientation=="-x"):
                        M.append("move")
                    elif(orientation=="+x"):
                        if(y0==3):
                            M.append("right")
                            M.append("right")
                        else:
                            M.append("left")
                            M.append("left")
                        M.append("move")
                    elif(orientation=="+y"):
                        M.append("left")
                        M.append("move")
                    elif(orientation=="-y"):
                        M.append("right")
                        M.append("move")
                    orientation = "-x"

                elif(deltaX>0):
                    if(orientation=="-x"):
                        if(y0==3):
                            M.append("left")
                            M.append("left")
                        else:
                            M.append("right")
                            M.append("right")
                        M.append("move")
                    elif(orientation=="+x"):
                        M.append("move")
                    elif(orientation=="+y"):
                        M.append("right")
                        M.append("move")
                    elif(orientation=="-y"):
                        M.append("left")
                        M.append("move")
                    orientation = "+x"
            elif deltaY!=0:
                if(deltaY<0):
                    if(orientation=="-x"):
                        M.append("left")
                        M.append("move")
                    elif(orientation=="+x"):
                        M.append("right")
                        M.append("move")
                    elif(orientation=="+y"):
                        if(x0==0):
                            M.append("right")
                            M.append("right")
                        else:
                            M.append("left")
                            M.append("left")
                        M.append("move")
                    elif(orientation=="-y"):
                        M.append("move")
                    orientation = "-y"
                if(deltaY>0):
                    if(orientation=="-x"):
                        M.append("right")
                        M.append("move")
                    elif(orientation=="+x"):
                        M.append("left")
                        M.append("move")
                    elif(orientation=="+y"):
                        M.append("move")
                    elif(orientation=="-y"):
                        if(x0==0):
                            M.append("left")
                            M.append("left")
                        else:
                            M.append("right")
                            M.append("right")
                        M.append("move")
                    orientation = "+y"
    return M, orientation
        

def dijkstra(start, finish): # Find path with start building and end building
    Q = [p00, p01, p02, p03, p10, p11, p12, p13, p20, p21, p22, p23, p30, p31, p32, p33]
    for b3 in Q:
        b3.distance = 999
        b3.previous = None
    start.distance = 0 #Start building
    target = finish.name #Building we want to reach
    R =[]
    for b2 in Q:
        if b2.status == "Fire":
            Q.remove(b2)
    while len(Q)>0:
        #find vertex with min dist
        minIndex = 0
        index = -1
        for b in Q: #Check every building in the list
            index+=1
            if(b.distance<Q[minIndex].distance):
               minIndex = index #Save index of building with minimum distance

        #print(minIndex)
        u = Q.pop(minIndex)
        R.append(u)
        #Target reached
        if(u.name == target):
            #global S
            S = []
            while(u!=None):
                S.insert(0,u)
                u = u.previous
        #Not target
        if(u== None):
            return S
            break
        currentNeighbors = u.neighbors
        for v in currentNeighbors:
            if v in Q:
                if v.status!="Fire":
                    if not(v in R):
                        alt = u.distance+1
                        if(alt<v.distance):
                            v.distance = alt
                            v.previous = u

# Color class for the color sensors
class Color:
    def __init__(self, ferris, other):
        self.ferris_norm_rgb = ferris
        self.other_norm_rgb = other
    
    #Get left color
    def get_other_color(self):
        return classify_color(self.other_norm_rgb)
    
    #Get right color
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

def poll_norm_rgb(sensor):
    # polls sensor data and converts to normalized rgb values
    if sensor.get_value() == None or sum(sensor.get_value()) == 0:
        return [-1000, -1000, -1000]
    rgb = sensor.get_value()[:-1] 
    rgb = [round(x / sum(rgb), 2) for x in rgb]
    return rgb

#Threading setup
move_event = threading.Event()
backwards_adjust_event = threading.Event()
reverse_event = threading.Event()
adjust_event = threading.Event()
adjust_left_event = threading.Event()
adjust_right_event = threading.Event()

correct_left_event = threading.Event()
correct_right_event = threading.Event()

#Move function
def move():
    while True:
        if move_event.is_set(): # Move forward
            drive(drive_amount, drive_amount)
        elif reverse_event.is_set(): # Reverse
            drive(-drive_amount, -drive_amount*1.075)

        elif adjust_event.is_set(): # Any type of forward adjust
            print("in adjust mode")
            if adjust_left_event.is_set(): # Adjust left
                #print("adjusting left")
                adjust_left(adjust_amount)
            elif adjust_right_event.is_set(): # Adjust right
                #print("adjusting right")
                adjust_right(adjust_amount)
            elif correct_left_event.is_set(): # Correct left
                adjust_left(correct_amount)
            elif correct_right_event.is_set(): # Correct right
                adjust_right(correct_amount)
        
        elif backwards_adjust_event.is_set(): # Backwards adjust
            if adjust_left_event.is_set():
                backwards_adjust_left()
            elif adjust_right_event.is_set():
                backwards_adjust_right()
        
        elif turn_event.is_set(): # Turn event
            if turn_left_event.is_set():
                turn("left")
            elif turn_right_event.is_set():
                turn("right")
        
        sleep(0.02)

#More threading events setup
turn_event = threading.Event()
turn_left_event = threading.Event()
turn_right_event = threading.Event()

#Turn function
def turn(direction):
    if direction == "left":
        drive(drive_amount*5, 0) # only left motor moves
    elif direction == "right":
        drive(0, drive_amount) # only right motor moves

#Adjust functions
def adjust_left(adjust_amount):
    drive(adjust_amount*1.18, -adjust_amount*1.18) # left motor moves backwards, right motor moves forwards

def adjust_right(adjust_amount):
    drive(-adjust_amount, adjust_amount) # left motor moves forwards, right motor moves backwards

def backwards_adjust_left():
    drive(0, backwards_adjust_amount) # only left motor moves

def backwards_adjust_right():
    drive(backwards_adjust_amount, 0) # only right motor moves

def sensor_poll_to_color():
    # polls data and converts to Color class
    sleep(0.1)
    color = Color(poll_norm_rgb(COLOR_SENSOR_FERRIS), poll_norm_rgb(COLOR_SENSOR_OTHER))
    #print((poll_norm_rgb(COLOR_SENSOR_FERRIS), poll_norm_rgb(COLOR_SENSOR_OTHER)), end=' ')
    #print(color.get_ferris_color(), color.get_other_color())
    return color

current_line_color = "blue" # hardcoded starting position

# opposite colors when switching
def opposite_color(color):
    if color == "blue":
        return "red"
    elif color == "red":
        return "blue"

# move a block forward or backwards
def move_a_block(direction="forwards", move_to_top=True):
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
                print("adjusting backwards left")
                reverse_event.clear()

                backwards_adjust_event.set()
                adjust_right_event.set()
                sleep(0.8)
                adjust_right_event.clear()
                backwards_adjust_event.clear()
                
                backwards_adjust_event.set()
                adjust_left_event.set()
                sleep(1.3)
                adjust_left_event.clear()
                backwards_adjust_event.clear()
                reverse_event.set()
                

            else:
                print("Line detected, left sensor")
                # Stop moving
                move_event.clear()

                # Adjust by moving left motor back and right motor forward
                adjust_event.set()
                correct_left_event.set()
                while True:
                    polled_color = sensor_poll_to_color()
                    if not (polled_color.get_other_color() == current_line_color):
                        #print("adjust end")
                        sleep(0.005) # hardcoded
                        correct_left_event.clear()
                        break
                # Start moving again
                adjust_event.clear()
                move_event.set()

        # If right sensor detects red or blue
        if (polled_color.get_ferris_color() == current_line_color):
            if direction == "backwards":
                print("adjusting backwards right")
                reverse_event.clear()

                # move left motor
                # TEMP CHANGE USED TO BE 0.6
                backwards_adjust_event.set()
                adjust_left_event.set()
                sleep(0.8)
                adjust_left_event.clear()
                backwards_adjust_event.clear()

                backwards_adjust_event.set()
                adjust_right_event.set()
                sleep(1.3)
                adjust_right_event.clear()
                backwards_adjust_event.clear()
                
                reverse_event.set()
                print("adjusting done")
            
            else:
                print("Line detected, right sensor")
                # Stop moving
                move_event.clear()

                # Adjust by moving left motor back and right motor forward
                adjust_event.set()
                correct_right_event.set()
                while True:
                    polled_color = sensor_poll_to_color()

                    if not (polled_color.get_ferris_color() == current_line_color):
                        sleep(0.005)
                        correct_right_event.clear()
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
            if direction == "backwards":
                reverse_event.clear()
            else:
                move_event.clear()

            break
        
    # move to the outside part of the green square
    if direction == "forwards" and move_to_top:
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

# check if any sensor sees green
def any_sensor_sees_green(polled_color):
    return polled_color.get_ferris_color() == "green" or polled_color.get_other_color() == "green"

# check if no sensor sees green
def no_sensor_sees_green(polled_color):
    return polled_color.get_ferris_color() != "green" or polled_color.get_other_color() != "green"

# turn to the line
def turn_to_line(direction):
    global current_line_color

    print("current line color is:", current_line_color)

    move_event.set()
    sleep(.3)
    move_event.clear()
    #TEMP CHANGE first sleep used to be 1.28 second sleep used to be 1.1
    if direction == "left":
        print("turning left")
        adjust_event.set()
        adjust_right_event.clear()
        adjust_left_event.set()
        sleep(1)
        adjust_event.clear()
        adjust_left_event.clear()

    elif direction == "right":
        print("turning right")
        adjust_event.set()
        adjust_left_event.clear()
        adjust_right_event.set()
        sleep(1)
        adjust_event.clear()
        adjust_right_event.clear()
    
    # back up until reaches green

    reverse_event.set()
    sleep(0.3)
    reverse_event.clear()

    if current_line_color == "blue":
        current_line_color = "red"
    else:
        current_line_color = "blue"

    print("new line color is:", current_line_color)
    sleep(1)
    #print("turning done")

# wait for movement to be done function.
def wait_for_movement_done():
    while True:
        if not move_event.is_set():
            break
    
# main loop
print("before initialization")
wait_ready_sensors(True) # Input True to see what the robot is trying to initialize! False to be silent.
print("after initialization")
sleep(0.5) # wait for a bit

try:
    print("BrickPi Motos Position Demo:")
    try:
        # Initialize brickpi
        BP = brickpi3.BrickPi3 ()
        BP.offset_motor_encoder(AUX_MOTOR_1, BP.get_motor_encoder (AUX_MOTOR_1))
        BP.set_motor_limits (AUX_MOTOR_1, POWER_LIMIT*0.25, 90)
        BP.set_motor_limits (AUX_MOTOR_1 ,0)
        BP.offset_motor_encoder(AUX_MOTOR_2, BP.get_motor_encoder (AUX_MOTOR_2))
        BP.set_motor_limits (AUX_MOTOR_2, POWER_LIMIT*0.25, 90)
        BP.set_motor_limits (AUX_MOTOR_2 ,0)
        # Initialize carousel
        Wheel.init_carousel()
    except IOError as error:
        print(error)
    
    try:
        # Start movement task
        move_task = threading.Thread(target=move, name='turn_task')
        move_task.start()

        while True:
            
            fireindex = 0
            building_list = initiate() # Initialize all buildings
            # Input
            input_data = input("Enter input prompt in this format: x1,y1,e1,x2,y2,e2,x3,y3,e3 (together no space) \n Example: 1,1,A,2,2,B,3,3,C \n Input: ")
            input_lst = input_data.split(",") # Split input
            fires1 = [] # list of types of fire
            fire1 = input_lst[2] # Type of first building on fire
            fire2 = input_lst[5] # Type of second building on fire
            fire3 = input_lst[8] # Type of third building on fire
            # Check if extinguishers are valid
            if not (fire1 in "ABCDEF"):
                print("No corresponding extinguisher")
                continue
            if not (fire2 in "ABCDEF"):
                print("No corresponding extinguisher")
                continue
            if not (fire3 in "ABCDEF"):
                print("No corresponding extinguisher")
                continue
            l1 = input_lst[0]+input_lst[1] # Location of first building on fire
            l2 = input_lst[3]+input_lst[4] # Location of second building on fire
            l3 = input_lst[6]+input_lst[7] # Location of third building on fire
            #Set status of buildings on fire
            orientation="+x" # initial orientation
            allMoves = [] #list of all movements
            currentLocation = p00 #current location
            fires = [] # list of buildings on fire
            # Set status of buildings on fire
            for i in building_list:
                if (i.name == l2):
                    i.status = "Fire"
                    i.fire = fire2
                    fires.append(i)
                    fires1.append(fire2)
                if (i.name == l3):
                    i.status = "Fire"
                    i.fire = fire3
                    fires.append(i)
                    fires1.append(fire3)
                if (i.name == l1):
                    i.status = "Fire"
                    i.fire = fire1
                    fires.append(i)
                    fires1.append(fire1)
                    #next_building = i
            # Iterate through the list of buildings and find the path to each of them from the previous location
            for f in fires:
                for b in building_list:
                    if b.name == f.name:
                        b.status = "nextFire"
                        S = dijkstra(currentLocation, b)
                        currentLocation = S[len(S)-2]
                        M, orientation= movements(S, orientation) #Takes list of building objects we need to go through determined by the dijkstra function and returns a list of strings indicating the sequence of movements needed to extinguish the next fire
                        b.status = "Fire"
                        for l in S:
                            print(l.name)
                        for m in M:
                            #print(m)
                            allMoves.append(m)
            # Return to the starting point
            p00.status = "nextFire"
            S=dijkstra(currentLocation, p00)
            M, orientation= movements(S, orientation) #Takes list of building objects we need to go through determined by the dijkstra function and returns a list of strings indicating the sequence of movements needed to extinguish the next fire

            for l in S:
                print(l.name)
            s =""
            for m in M:
                #print(m)
                allMoves.append(m)

            p00.status = None
        
            for m in allMoves:
               #print(m)
               s+=m
               s+=", "
            print(s)

            #the allMoves variable is a list of all movements needed

            # Execute movements
            for i in range(len(allMoves)):
                m = allMoves[i]
                print(m)
                if (m == "move"): # Move forward
                    if i < len(allMoves) - 1 and allMoves[i+1] == "drop":
                        move_a_block(move_to_top=False) # Move to edge of green square
                        wait_for_movement_done()
                    else:
                        move_a_block()
                        wait_for_movement_done()
                    while True:
                        if not move_event.is_set():
                            break
                if (m == "right"): # Turn right
                    turn_to_line("right")
                    while True:
                        if not turn_event.is_set():
                            break    
                if (m == "left"): # Turn left
                    turn_to_line("left")
                    while True:
                        if not turn_event.is_set():
                            break
                if (m == "back up"): # Reverse
                    move_a_block("backwards")
                    while True:
                        if not move_event.is_set():
                            break
                if (m == "drop"): # Drop cube
                    # COMMENTED OUT TEMP, trying to check if the run can be done fully
                    #BP.set_motor_position_relative (AUX_MOTOR_1, -180) #hardcoded to deal with right drift
                    #BP.set_motor_position_relative (AUX_MOTOR_2, -180)
                    sleep(1)
                    Wheel.drop_cube(fires1[fireindex])
                    fireindex = fireindex+1
                    wait_for_movement_done()
                if (m == "stop"): # Stop and reset the robot
                    sleep(1)
                    Wheel.init_carousel()
                    Wheel.reset()
                    
        move_task.join() # End movement task

    except IOError as error:
        print(error) # Print error
except KeyboardInterrupt:
    BP.reset_all() # Reset all

BP.reset_all()
