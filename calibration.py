# robot specific parameters
wheel_dia = 67.3     # mm (increase = decrease distance)
wheel_base = 78.5  # mm (increase = spiral clockwise)

# stepper parameters
steps_rev = 512    # 512 for 64x gearbox, 128 for 16x gearbox
delay_time = 3     # time between steps in ms (too quick will freeze motors)
invert_direction = False  # change if turtle running backward

# servo parameters
PEN_DOWN = 130    # angle of servo when pen is down
PEN_UP = 50       # angle of servo when pen is up
min_pulse = 500
max_pulse = 2200