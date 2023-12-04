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
    global p00
    p00 = building("00",999)
    global p01
    p01 = building("01",999)
    global p02
    p02 = building("02",999)
    global p03
    p03 = building("03",999)
    global p10
    p10 = building("10",999)
    global p11
    p11 = building("11",999)
    global p12
    p12 = building("12",999)
    global p13
    p13 = building("13",999)
    global p20
    p20 = building("20",999)
    global p21
    p21 = building("21",999)
    global p22
    p22 = building("22",999)
    global p23
    p23 = building("23",999)
    global p30
    p30 = building("30",999)
    global p31
    p31 = building("31",999)
    global p32
    p32 = building("32",999)
    global p33
    p33 = building("33",999)

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
               
    
initiate() #initiate all 16 buildings

#Set status of buildings on fire

orientation="+y"
fires = [p32, p03, p20] #all fire locations

AllB = [p00, p01, p02, p03, p10, p11, p12, p13, p20, p21, p22, p23, p30, p31, p32, p33]
allMoves = [] #list of all movements
currentLocation = p00
for f in fires:
    for b in AllB:
        if b.name == f.name:
            f.status = "Fire"
for f in fires:
    for b in AllB:
        if b.name == f.name:
            b.status = "nextFire"
            S = dijkstra(currentLocation, b)
            currentLocation = S[len(S)-2]
            M, orientation= movements(S, orientation) #Takes list of building objects we need to go through determined by the dijkstra function and returns a list of strings indicating the sequence of movements needed to extinguish the next fire
            b.status = "Fire"
#            for l in S:
#                print(l.name)
            for m in M:
                #print(m)
                allMoves.append(m)
p00.status = "nextFire"
S=dijkstra(currentLocation, p00)
M, orientation= movements(S, orientation) #Takes list of building objects we need to go through determined by the dijkstra function and returns a list of strings indicating the sequence of movements needed to extinguish the next fire

#for l in S:
#    print(l.name)
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
