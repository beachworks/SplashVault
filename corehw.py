# Core Hardware Drivers for Splash Machine at Brandon's Beach House
# dlb, Aug 2024
#
#
# Please see the "Splash Pad Documentation" Power Point for more
# information

import gpiozero
import serial
import time

spout_names = ("a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n",
            "gate", "center", "corners", "inside_corners", "major_row_1", "major_row_2", "major_row_3",
            "minor_row_1", "minor_row_2", "major_column_1", "major_column_2", "major_column_3",
            "minor_column_1", "minor_column2", "diagonal_1", "diagonal_2", "outside_box", "inside_box")

duration =  150   # Global value for duration
period   = 1000   # Global value for period

waterspout_gpios = [2, 3, 4, 17, 27, 22, 10, 18, 23, 24, 25, 8, 7, 1]
waterspouts = []
ball_valve_gpios = [9, 12]
ball_valve_sensor_gpios = [0, 5]
status_led_gpios = [13, 19, 26]
waterspouts = []
input_psi_conversion_factor = 100.0 / 65536.0
output_psi_conversion_factor = 100.0 / 65536.0 
run_led = gpiozero.LED(status_led_gpios[0], active_high=True, initial_value=False)
activity_led_red = gpiozero.LED(status_led_gpios[1], active_high=True, initial_value=False)
activity_led_green = gpiozero.LED(status_led_gpios[2], active_high=True, initial_value=False)
psi_port = serial.Serial("/dev/ttyAMA0", baudrate=921600, timeout=0.0005)
ball_closed_switch = gpiozero.DigitalInputDevice(ball_valve_sensor_gpios[0], pull_up=True)
ball_open_switch = gpiozero.DigitalInputDevice(ball_valve_sensor_gpios[1], pull_up=True)
ball_valve_relay1 = gpiozero.DigitalOutputDevice(ball_valve_gpios[0], active_high=False, initial_value=False)
ball_valve_relay2 = gpiozero.DigitalOutputDevice(ball_valve_gpios[1], active_high=False, initial_value=False)
for iopin in waterspout_gpios:
    s = gpiozero.DigitalOutputDevice(iopin, active_high=False, initial_value=False)
    waterspouts.append(s)

# Define Patterns
# The layout of the water spouts is as follows:
#
#  A(0)      B(1)       C(2)
#       D(3)       E(4)
#  F(5)      G(6)       H(7)
#       I(8)       J(9)
#  K(10)     L(11)      M(12)
#
# And N(13) are the 5 spouts at the gate.

ws_gate = [13]
ws_center = [6]
ws_corners = [0, 2, 10, 12]
ws_inside_corners = [3, 4, 8, 9]
ws_major_row_1 = [0, 1, 2]
ws_major_row_2 = [5, 6, 7]
ws_major_row_3 = [10, 11, 12]
ws_minor_row_1 = [3, 4]
ws_minor_row_2 = [8, 9]
ws_major_column_1 = [0, 5, 10]
ws_major_column_2 = [1, 6, 11]
ws_major_column_3 = [2, 7, 12]
ws_minor_column_1 = [3, 8]
ws_minor_column_2 = [4, 9]
ws_diagonal_1 = [0, 3, 6, 9, 12]
ws_diagonal_2 = [2, 4, 6, 8, 10]
ws_outside_box = [0, 1, 2, 5, 7, 10, 11, 12]
ws_inside_box = [3, 4, 8, 9]

ws_major_rows = [ws_major_row_1, ws_major_row_2, ws_major_row_3]
ws_minor_rows = [ws_minor_row_1, ws_minor_row_2]
ws_all_rows   = [ws_major_row_1, ws_minor_row_1, ws_major_row_2, ws_minor_row_2, ws_major_row_3]
ws_major_columns = [ws_major_column_1, ws_major_column_2, ws_major_column_3]
ws_minor_columns = [ws_minor_column_1, ws_minor_column_2]
ws_all_columns = [ws_major_column_1, ws_minor_column_1, ws_major_column_2, ws_minor_column_2, ws_major_column_3]
ws_all_diagonals = [ws_diagonal_1, ws_diagonal_2]

def translate_spout_name(name):
    if type(name) is int:
        if name >= 0 and name <= 13: return [name]
        return [] 
    if type(name) is not str: return []
    name = name.lower() 
    if name == "a": return [0]
    if name == "b": return [1]
    if name == "c": return [2]
    if name == "d": return [3]
    if name == "e": return [4]
    if name == "f": return [5]
    if name == "g": return [6]
    if name == "h": return [7]
    if name == "i": return [8]
    if name == "j": return [9]
    if name == "k": return [10]
    if name == "l": return [11]
    if name == "m": return [12]
    if name == "n": return [13]
    if name == "gate": return ws_gate
    if name == "center": return ws_center
    if name == "corners": return ws_corners
    if name == "inside_corners": return ws_inside_corners
    if name == "major_row_1": return ws_major_row_1
    if name == "major_row_2": return ws_major_row_2
    if name == "major_row_3": return ws_major_row_3
    if name == "minor_row_1": return ws_minor_row_1
    if name == "minor_row_2": return ws_minor_row_2
    if name == "major_column_1": return ws_major_column_1
    if name == "major_column_2": return ws_major_column_2
    if name == "major_column_3": return ws_major_column_3
    if name == "minor_column_1": return ws_minor_column_1
    if name == "minor_column_2": return ws_minor_column_2
    if name == "diagonal_1": return ws_diagonal_1
    if name == "diagonal_2": return ws_diagonal_2
    if name == "outside_box": return ws_outside_box
    if name == "inside_box": return ws_inside_box
    return []

def all_off():
    """ Turn all waterspouts off."""
    for w in waterspouts:
        w.off()

def turn_pattern_on(arg):
    """ Turns the waterspouts in the given pattern on."""
    pattern = ""
    if type(arg) is int:
        if arg >=0 and arg < len(spout_names): 
            pattern = spout_names[arg]
        else: return
    if type(arg) is str:
        pattern = arg
    if type(arg) is list: 
        for i in arg:
            if type(i) is int:
                if i >= 0 and i <= 13: waterspouts[i].on()
        return 
    spouts = translate_spout_name(pattern)
    for spout in spouts:
        if spout < 0 or spout > 13: continue
        waterspouts[spout].on()

def turn_pattern_off(arg):
    """ Turns the waterspouts in the given pattern off."""
    pattern = ""
    if type(arg) is int:
        if arg >=0 and arg < len(spout_names): 
            pattern = spout_names[arg]
        else: return
    if type(arg) is str:
        pattern = arg
    if type(arg) is list: 
        for i in arg:
            if type(i) is int:
                if i >= 0 and i <= 13: waterspouts[i].off()
        return 
    spouts = translate_spout_name(pattern)
    for spout in spouts:
        if spout < 0 or spout > 13: continue
        waterspouts[spout].off()

def fire_pattern(pattern, period=0.025):
    """ Fires all the spounts in the pattern for the given period (in seconds)."""
    t0 = time.monotonic_ns()
    turn_pattern_on(pattern) 
    while True:
        t1 = time.monotonic_ns() 
        elp = (t1 - t0) / 1_000_000_000.00
        if elp > period: break 
    turn_pattern_off(pattern)

def ball_valve_move(direction):
    """Moves (or stops) the ball valve. Direction > 0 moves toward open, < 0 toward close, 0 = stops moving.""" 
    if direction == 0:
        ball_valve_relay1.off()
        ball_valve_relay2.off()
        return
    if direction > 0:
        ball_valve_relay1.on()
        ball_valve_relay2.off() 
    else:
        ball_valve_relay1.off()
        ball_valve_relay2.on() 

def check_ball_valve():
    """ Returns -1 if fully closed, +1 if fully opened, or zero if between opened and closed."""
    s1 = ball_open_switch.value
    s2 = ball_closed_switch.value
    if s1 == True: return 1
    if s2 == True: return -1
    return 0

def time_ball_movement():
    """ Use this for developement.  Results: about 5.25 seconds to open, and 5.33 to close."""
    ball_valve_move(-1)
    while True:
        if check_ball_valve() == -1: break
    ball_valve_move(0)
    t0 = time.monotonic_ns()
    ball_valve_move(1)
    while True:
        if check_ball_valve() == 1: break
    t1 = time.monotonic_ns()
    elp = (t1 - t0) / 1_000_000.00
    print("Time to Open Valve: %9.3f ms" % elp) 
    t0 = time.monotonic_ns() 
    ball_valve_move(-1)
    while True:
        if check_ball_valve() == -1: break 
    t1 = time.monotonic_ns()
    elp = (t1 - t0) / 1_000_000.00
    print("Time to Close Valve: %9.3f ms" % elp)
    ball_valve_move(0)


# Get the two PSI readings, before the ball valve and after. Returned in PSI.
# This routine blocks for about 0.5 milliseconds
def get_psi():
    for i in range(3):
        t0 = time.monotonic_ns()
        psi_port.write(b"?")                     # This takes about 0.1 ms
        #tw = time.monotonic_ns()
        #elp = (tw - t0) / 1_000_000.00
        #print("Time to request: %7.3f ms" % elp)
        #tr0 = time.monotonic_ns()
        rcv_buf = ""
        t_read_start = time.monotonic_ns()
        while True:
            new_part = psi_port.read_all().decode()
            rcv_buf = rcv_buf + new_part 
            if len(rcv_buf) >= 12 and rcv_buf[-1] == '\n': break
            t = time.monotonic_ns()
            elp = (t - t_read_start) / 1_000_000.00
            if elp > 0.5:
                print("Failed getting psi -- timeout after read_all")
                return None
        #print("Recevied Buf before processing: " + rcv_buf)
        n = len(rcv_buf)
        rcv_buf = rcv_buf[-13:-1]
        #print("Recevied Buf after Processing: " + rcv_buf)
        #tr1 = time.monotonic_ns()
        #elp = (tr1 - tr0) / 1_000_000.00
        #print("Time to respond: %7.3f ms" % elp)
        rcv = rcv_buf.strip()
        #print("Received: " + rcv)
        #t1 = time.monotonic_ns()
        #elptime = (t1 - t0) / 1_000_000.00
        #print("Elapsed Time = %7.3f ms" % elptime)
        w = rcv.split(",")
        if len(w) != 2: continue 
        if len(w[0]) != 5 or len(w[1]) != 5: continue
        try:
            psi1 = int(w[0])
            psi2 = int(w[1])
            #print("raw readings = %d, %d" % (psi1, psi2))
            t1 = time.monotonic_ns()
            elptime = (t1 - t0) / 1_000_000.00
            # print("Trys = %d, Elapsed Time = %7.3f ms" % (i, elptime))
            return (psi1 * input_psi_conversion_factor, psi2 * output_psi_conversion_factor)
        except:
            psi_port.readll()  # Clear out the port.
            continue 
    print("Failed to get psi.")
    return None
        

def ring(t1=0.05, t2=0.20):
    for s in waterspouts:
        s.on()
        time.sleep(t1)
        s.off()
        time.sleep(t2)




