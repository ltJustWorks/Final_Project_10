# iteration: 3
from vehicle_movement import drive, wait_until_motors_done 
from utils.brick import EV3ColorSensor, wait_ready_sensors, TouchSensor, reset_brick, busy_sleep
import brickpi3
from time import sleep
import threading
from color_classifier import classify_color
from Wheel import init_carousel, drop_cube

class building: #Building objects used to determine paths and movements
    def __init__(self, name, distance):
        self.name = name
        self.distance = distance
        self.previous = None
        self.neighbors = None
        self.x = int(name[0])
        self.y = int(name[1])
        self.status = "safe"
        

    

def initiate(): #initiate all 16 buildings
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
    firstu = start
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
move_backwards_event = threading.Event()
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
            if move_backwards_event.is_set():
                drive(-drive_amount, -drive_amount)
            else:
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

adjust_amount = 12 # hardcoded
def adjust_left():
    drive(adjust_amount, -adjust_amount)

def adjust_right():
    drive(-adjust_amount, adjust_amount)

def sensor_poll_to_color():
    # polls data and converts to Color class
    sleep(0.1)
    color = Color(poll_norm_rgb(COLOR_SENSOR_FERRIS), poll_norm_rgb(COLOR_SENSOR_OTHER))
    #print((poll_norm_rgb(COLOR_SENSOR_FERRIS), poll_norm_rgb(COLOR_SENSOR_OTHER)), end=' ')
    #print(color.get_ferris_color(), color.get_other_color())
    return color

current_line_color = "blue" # hardcoded, TODO ask ta about starting position

def move_a_block(direction="forwards"):
    global current_line_color
    # color sensors are at green 
    print("at green")
    move_event.set()
    if direction=="backwards":
        move_backwards_event.set()

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
                    sleep(0.08) # hardcoded
                    adjust_left_event.clear()
                    break
            # Start moving again
            adjust_event.clear()
            move_event.set()

        # If right sensor detects red or blue
        if (polled_color.get_ferris_color() == current_line_color):
            #print("Line detected, right sensor")
            # Stop moving
            move_event.clear()
            # Adjust by moving left motor back and right motor forward
            adjust_event.set()
            adjust_right_event.set()
            while True:
                polled_color = sensor_poll_to_color()

                if not (polled_color.get_ferris_color() == current_line_color):
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
        if polled_color.get_ferris_color() == "green" or polled_color.get_other_color() == "green":
            print("green detected, should stop")
            move_event.clear()
            break

    if direction=="backwards":
        move_backwards_event.clear()
    sleep(1)

def turn_to_line(direction):
    global current_line_color

    #print("turn function started")
    print("current line color is:", current_line_color)
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
                sleep(.2)
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
                sleep(.2)
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
        #init_carousel()
        #sleep(4)
    except IOError as error:
        print(error)
    
    try:
        move_task = threading.Thread(target=move, name='turn_task')
        move_task.start()
        building_list = initiate()
        l1 = input("Enter first fire location (together no space): ")
        t1 = input("Enter first fire type: ")
        l2 = input("Enter second fire location (together no space): ")
        t2 = input("Enter second fire type: ")
        l3 = input("Enter third fire location (together no space): ")
        t3 = input("Enter third fire type: ")
        #Set status of buildings on fire
        orientation="+x"
        allMoves = [] #list of all movements
        currentLocation = p00
        fires = []
        for i in building_list:
            if (i.name == l2):
                i.status = "Fire"
                fires.append(i)
            if (i.name == l3):
                i.status = "Fire"
                fires.append(i)
            if (i.name == l1):
                i.status = "Fire"
                fires.append(i)
                #next_building = i
        for f in fires:
            for b in building_list:
                if b.status == f.status:
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
        p00.status = "nextFire"
        S=dijkstra(currentLocation, p00)
        M, orientation= movements(S, orientation) #Takes list of building objects we need to go through determined by the dijkstra function and returns a list of strings indicating the sequence of movements needed to extinguish the next fire

        #for l in S:
        #print(l.name)
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

        """
        for m in M:
            print(m)
            if (m == "move"):
                move_a_block()
                while True:
                    if not move_event.is_set():
                        break
            if (m == "right"):
                turn_to_line("right")
                while True:
                    if not move_event.is_set():
                        break    
            if (m == "left"):
                turn_to_line("left")
                while True:
                    if not move_event.is_set():
                        break
            if (m == "back up"):
                move_a_block("backwards")
                while True:
                    if not move_event.is_set():
                        break
            if (m == "drop"):
                drop_cube("A")
                wait_for_movement_done()
            """
        print(orientation)
        print(nextStartB.name)
        
        
        
        move_task.join()

    except IOError as error:
        print(error)
except KeyboardInterrupt:
    BP.reset_all()

BP.reset_all()
