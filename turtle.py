# Libreria Turtle per Micro Python
# Maurizio Conti - Fablab Romagna 2022


import sys
import math
import time
import machine
import calibration

#import digitalio
#from analogio import AnalogIn

# Servo per Circuit Python
#import pulseio
#import adafruit_motor.servo
#import pwmio
#pwm = pulseio.PWMOut(board.GP20, frequency=50)
#pwm = pwmio.PWMOut(board.GP20, duty_cycle=2 ** 15, frequency=50)
#servo = adafruit_motor.servo.Servo( pwm,  min_pulse=calibration.min_pulse, max_pulse=calibration.max_pulse )

# Servo per Micro python ESP32 S2
#pinServo = machine.Pin(5, machine.Pin.OUT)
#servo = machine.PWM(pinServo, freq=42)

# Servo per Micro python ESP32 C3
pinServo = machine.Pin(1, machine.Pin.OUT)
servo = machine.PWM(pinServo, freq=42)

DEBUG = True

# [blu-rosa-giallo-arancio]
# Versione Raspberry Pi Pico
#Lstep0 = machine.Pin(2, machine.Pin.OUT) #Q4
#Lstep1 = machine.Pin(4, machine.Pin.OUT) #Q3
#Lstep2 = machine.Pin(6, machine.Pin.OUT) #Q2
#Lstep3 = machine.Pin(8, machine.Pin.OUT) #Q1

#Rstep0 = machine.Pin(3, machine.Pin.OUT) #Q8
#Rstep1 = machine.Pin(5, machine.Pin.OUT) #Q7
#Rstep2 = machine.Pin(7, machine.Pin.OUT) #Q6
#Rstep3 = machine.Pin(9, machine.Pin.OUT) #Q5


# [blu-rosa-giallo-arancio]
# Versione ESP8266 su Wemos D1 R2
#Lstep0 = machine.Pin(16, machine.Pin.OUT)
#Lstep1 = machine.Pin(5, machine.Pin.OUT)
#Lstep2 = machine.Pin(4, machine.Pin.OUT)
#Lstep3 = machine.Pin(0, machine.Pin.OUT)

#Rstep0 = machine.Pin(2, machine.Pin.OUT)
#Rstep1 = machine.Pin(14, machine.Pin.OUT)
#Rstep2 = machine.Pin(12, machine.Pin.OUT)
#Rstep3 = machine.Pin(13, machine.Pin.OUT)

# [blu-rosa-giallo-arancio]
# Versione ESP32 S2 su Wemos S2 mini
#Lstep0 = machine.Pin(18, machine.Pin.OUT) #Q4
#Lstep1 = machine.Pin(33, machine.Pin.OUT) #Q3
#Lstep2 = machine.Pin(35, machine.Pin.OUT) #Q2
#Lstep3 = machine.Pin(16, machine.Pin.OUT) #Q1

#Rstep0 = machine.Pin(12, machine.Pin.OUT) #Q8
#Rstep1 = machine.Pin(7, machine.Pin.OUT) #Q7
#Rstep2 = machine.Pin(9, machine.Pin.OUT) #Q6
#Rstep3 = machine.Pin(11, machine.Pin.OUT) #Q5

# [blu-rosa-giallo-arancio]
# Versione Wemos C3 mini
Lstep0 = machine.Pin(7, machine.Pin.OUT)  #Q4
Lstep1 = machine.Pin(8, machine.Pin.OUT)  #Q3
Lstep2 = machine.Pin(10, machine.Pin.OUT) #Q2
Lstep3 = machine.Pin(6, machine.Pin.OUT)  #Q1

Rstep0 = machine.Pin(5, machine.Pin.OUT)  #Q8
Rstep1 = machine.Pin(2, machine.Pin.OUT)  #Q7
Rstep2 = machine.Pin(3, machine.Pin.OUT)  #Q6
Rstep3 = machine.Pin(4, machine.Pin.OUT)  #Q5

# put connections in array to make life easier
R_stepper = [Rstep0, Rstep1, Rstep2, Rstep3]
L_stepper = [Lstep0, Lstep1, Lstep2, Lstep3]

#for wire in L_stepper:
#    wire.direction = digitalio.Direction.OUTPUT

#for wire in R_stepper:
#    wire.direction = digitalio.Direction.OUTPUT

# stepper patterns
patterns = [[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 1], [1, 0, 0, 1]]

_x = 0
_y = 0
_heading = 0
frac_error = 0
spacer = ''


def setDebug(val):
    global DEBUG
    DEBUG = val

def step(distance):
    steps = distance * calibration.steps_rev/(calibration.wheel_dia * math.pi)
    frac = steps-int(steps)
    if frac > 0.5:
        return int(steps + 1), 1 - frac
    else:
        return int(steps), -frac

def forward(distance):
    global _x, _y, _heading
    steps, frac = step(distance)
    
    if DEBUG:
        print("dist %s, steps %s, frac %s" % (distance, steps, frac))

    for x in range(steps):
        for pattern in range(len(patterns)):
            for bit in range(len(patterns[pattern])):  # fwd_mask[num]:
                if not calibration.invert_direction:
                    L_stepper[bit].value(patterns[pattern][bit])
                    R_stepper[bit].value(patterns[::-1][pattern][bit])
                else:
                    R_stepper[bit].value(patterns[pattern][bit])
                    L_stepper[bit].value(patterns[::-1][pattern][bit])
            time.sleep(calibration.delay_time/1000)

    # new point
    deltax = distance * math.cos(math.radians(_heading))
    deltay = distance * math.sin(math.radians(_heading))
    _x = _x + deltax
    _y = _y + deltay


def backward(distance):
    global _x, _y, _heading
    steps, frac = step(distance)

    if DEBUG:
        print("dist %s, steps %s, frac %s" % (distance, steps, frac))

    for x in range(steps):
        for pattern in range(len(patterns)):
            for bit in range(len(patterns[pattern])):  # fwd_mask[num]:
                if not calibration.invert_direction:
                    R_stepper[bit].value = patterns[pattern][bit]
                    L_stepper[bit].value = patterns[::-1][pattern][bit]
                else:
                    L_stepper[bit].value = patterns[pattern][bit]
                    R_stepper[bit].value = patterns[::-1][pattern][bit]
            time.sleep(calibration.delay_time/1000)

    # new point
    deltax = distance * math.cos(math.radians(_heading - 180))
    deltay = distance * math.sin(math.radians(_heading - 180))
    _x = _x + deltax
    _y = _y + deltay


def left(degrees):
    global _x, _y, _heading, frac_error
    
    if (degrees < 0):
        right(-degrees)
        
    else:
    
        rotation = degrees / 360.0
        distance = calibration.wheel_base * math.pi * rotation
        steps, frac = step(distance)
        frac_error += frac

        if DEBUG:
            print("dist %s, steps %s, frac %s" % (distance, steps, frac))

        for x in range(steps):
            for pattern in range(len(patterns)):
                for bit in range(len(patterns[pattern])):  # fwd_mask[num]:
                    if not calibration.invert_direction:
                        R_stepper[bit].value(patterns[pattern][bit])
                        L_stepper[bit].value(patterns[pattern][bit])
                    else:
                        R_stepper[bit].value(patterns[::-1][pattern][bit])
                        L_stepper[bit].value(patterns[::-1][pattern][bit])
                time.sleep(calibration.delay_time/1000)
        
        _heading = _heading + degrees
        
        while _heading > 360:
            _heading = _heading - 360
        
        if DEBUG:
            print("dist %s, steps %s, frac %s, frac err %s" % (distance, steps, frac, frac_error))


def right(degrees):
    global _x, _y, _heading
    if (degrees < 0):
        left(-degrees)
    else:
        if DEBUG:
            print("right %s(%s)" % (spacer, degrees))
        rotation = degrees / 360.0
        distance = calibration.wheel_base * math.pi * rotation
        steps, frac = step(distance)
        for x in range(steps):
            for pattern in range(len(patterns)):
                for bit in range(len(patterns[pattern])):  # fwd_mask[num]:
                    if not calibration.invert_direction:
                        R_stepper[bit].value(patterns[::-1][pattern][bit])
                        L_stepper[bit].value(patterns[::-1][pattern][bit])
                    else:
                        R_stepper[bit].value(patterns[pattern][bit])
                        L_stepper[bit].value(patterns[pattern][bit])
                time.sleep(calibration.delay_time/1000)
        _heading = _heading - degrees
        while _heading < 0:
            _heading = _heading + 360


def penup():
    #Circuit Python
    #servo.angle = calibration.PEN_UP
    servo.duty(calibration.PEN_UP)
    if DEBUG:
        print("penup ", calibration.PEN_UP)
    time.sleep_ms(200)


def pendown():
    max_pen_down = 85
    if calibration.PEN_DOWN < max_pen_down:
        #Circuit Python
        #servo.angle = calibration.PEN_DOWN
        servo.duty(calibration.PEN_DOWN)
        if DEBUG:
            print("pendown ", calibration.PEN_DOWN)
    else:
        #Circuit Python
        #servo.angle = max_pen_down
        servo.duty(max_pen_down)
        if DEBUG:
            print("pendown ", max_pen_down)
    time.sleep_ms(100)

def done():
    for value in range(4):
        L_stepper[value].value(False)
        R_stepper[value].value(False)
        
    penup()
    time.sleep(1)
    if DEBUG:
        print("done()")

def goto(x, y):
    global spacer
    spacer = '    '  # offsets debug statements after "goto(x, y)"
    center_x, center_y = position()
    bearing = getBearing(x, y, center_x, center_y)
    trnRight = heading() - bearing
    if DEBUG:
        print("goto(%s, %s)" % (x, y))
    if abs(trnRight) > 180:
        if trnRight >= 0:
            left(360 - trnRight)
            # if DEBUG: print('left(%s)' % (360 - trnRight))
        else:
            right(360 + trnRight)
            # if DEBUG: print('right(%s)' % (360 + trnRight))
    else:
        if trnRight >= 0:
            right(trnRight)
            # if DEBUG: print('right(%s)' % trnRight)
        else:
            left(-trnRight)
            # if DEBUG: print('left(%s)' % -trnRight)
    dist = distance(tuple(position()), (x, y))
    forward(dist)
    spacer = ''


def setheading(to_angle):
    '''
    Set the orientation of the turtle to to_angle.

    Aliases:  setheading | seth

    Argument:
    to_angle -- a number (integer or float)

    Set the orientation of the turtle to to_angle.
    Here are some common directions in degrees:

     standard - mode:          logo-mode:
    -------------------|--------------------
       0 - east                0 - north
      90 - north              90 - east
     180 - west              180 - south
     270 - south             270 - west

    Example:
    >>> setheading(90)
    >>> heading()
    90
    '''

    cur_heading = heading()
    if (to_angle - cur_heading) < 0:
        if (to_angle - cur_heading) > -180:
            left(to_angle - cur_heading)
            if DEBUG: print("Case 1 left(%s)" % (to_angle - cur_heading))
        else:
            left(to_angle - cur_heading + 360)
            if DEBUG: print("Case 2 left(%s)" % (to_angle - cur_heading + 360))
    else:
        if (to_angle - cur_heading) > 180:
            left(360 - to_angle - cur_heading - 180)
            if DEBUG: print("Case 3 left(%s)" % (360 - to_angle - cur_heading))
        else:
            left(to_angle - cur_heading)
            if DEBUG: print("Case 4 left(%s)" % (to_angle - cur_heading))


def pensize(size):
    print('pensize() is not implemented in Turtle Robot')
    pass


def pencolor(color):
    print('pencolor() is not implemented in Turtle Robot')
    pass


def speed(x):
    print('speed() is not implemented in Turtle Robot')
    pass

def shape(x):
    print('shape() is not implemented in Turtle Robot')
    pass


def position():
    return _x, _y


def heading():
    return _heading


def distance(pointA, pointB):
    return abs((pointB[0] - pointA[0])**2 + (pointB[1] - pointA[1])**2)**0.5


def getBearing(x, y, center_x, center_y):
    # https://stackoverflow.com/questions/5058617/bearing-between-two-points
    angle = math.degrees(math.atan2(y - center_y, x - center_x))
    bearing = (angle + 360) % 360
    return bearing


def circle(radius, extent=None, steps=None):
    """ Draw a circle with given radius.

    Arguments:
    radius -- a number
    extent (optional) -- a number
    steps (optional) -- an integer

    Draw a circle with given radius. The center is radius units left
    of the turtle; extent - an angle - determines which part of the
    circle is drawn. If extent is not given, draw the entire circle.
    If extent is not a full circle, one endpoint of the arc is the
    current pen position. Draw the arc in counterclockwise direction
    if radius is positive, otherwise in clockwise direction. Finally
    the direction of the turtle is changed by the amount of extent.

    As the circle is approximated by an inscribed regular polygon,
    steps determines the number of steps to use. If not given,
    it will be calculated automatically. Maybe used to draw regular
    polygons.

    call: circle(radius)                  # full circle
    --or: circle(radius, extent)          # arc
    --or: circle(radius, extent, steps)
    --or: circle(radius, steps=6)         # 6-sided polygon

    Example (for a Turtle instance named turtle):
    >>> turtle.circle(50)
    >>> turtle.circle(120, 180)  # semicircle
    """

    if extent is None:
        extent = 360
    if steps is None:
        frac = abs(extent)/360
        # print("frac = %s" % frac)
        steps = 1+int(min(11+abs(radius)/6.0, 59.0)*frac)
    w = 1.0 * extent / steps
    w2 = 0.5 * w
    length = 2.0 * radius * math.sin(w2*math.pi/180.0)
    if radius < 0:
        length, w, w2 = -length, -w, -w2
    if DEBUG:
        print("circle(%s, extent=%s, steps=%s)" % (radius, extent, steps))
    if False:
        print("length (step length) = %s" % length)
        print("w (turn angle)= %s" % w)		
        print("w2 (inital rotation) = %s" % w2)

        print("steps = %s" % steps)	
        print("extent = %s" % extent)
        # print("self._degreesPerAU = %s" % self._degreesPerAU)
    left(w2)
    for i in range(steps):
        forward(length)
        left(w)
    left(-w2)


def isButtonPushed():
    return not button.value #pulled up (True) when not pushed

########################
# Arrivati in fondo alla lib, ci assicuriamo che la penna sia su!
penup()
print( "FLR robot on", sys.platform )