# spout_player.py -- Controls the playing of a program for water spouts
# dlb, Aug 24

# Note: The code is mostly on it's way out in favor of the scripting language
# implemented in wsp_proc.py.  It is kept for the need of "one_shot".

import corehw
import time 
import copy
import random
import pad_leds

current_program = "" 
current_args = {} 
last_update_time = 0
last_time_check = 0
inital_cycle = False
temp_args = {}
random.seed(1234123)

def program_random():
    """ Hardcoded program to do random.  Obsolete now.  Use scripts instead."""
    global current_args, last_update_time, inital_cycle
    if inital_cycle:
        inital_cycle = False
        if "duration" not in current_args: current_args["duration"] = 50
        if "period" not in current_args: current_args["period"] = 1000
        corehw.all_off()
        last_update_time = time.monotonic_ns()
        pad_leds.set_flow_activity(True)
        pad_leds.set_sequence_activity(250, 50)
        return 
    t = time.monotonic_ns() 
    elp = (t - last_update_time) / 1_000_000.0 
    if elp > current_args["duration"]:
        corehw.all_off()
    if elp > current_args["period"]:
        corehw.all_off()
        num = random.randrange(0, 13)
        corehw.turn_pattern_on(num)
        last_update_time = t

def program_one_shot():
    """ Controls the one-shot program.  Used for manual control over each spout."""
    global current_program, current_args, last_update_time, inital_cycle, temp_args
    if inital_cycle:
        inital_cycle = False 
        if "spout" not in current_args:
            current_program = ""
            return
        if "duration" not in current_args: current_args["duration"] = 25
        last_update_time = time.monotonic_ns()
        temp_args["pattern"] = corehw.translate_spout_name(current_args["spout"])
        corehw.turn_pattern_on(temp_args["pattern"])
        pad_leds.set_flow_activity(True)
        pad_leds.set_sequence_activity(1000, 0)
        return
    t = time.monotonic_ns() 
    elp = (t - last_update_time) / 1_000_000.0
    if elp > current_args["duration"]:
        corehw.turn_pattern_off(temp_args["pattern"])
        pad_leds.set_flow_activity(False)
        pad_leds.set_sequence_activity(1000, 0)
        current_program = ""
        return

def set_program(prog, args):
    """ Sets the program to play.  Only one program can play at a time."""
    global current_program, last_update_time, current_args, inital_cycle 
    current_program = prog
    current_args = copy.deepcopy(args)
    corehw.all_off() 
    last_update_time = time.monotonic_ns()
    inital_cycle = True

def update_arguments(args):
    """ Updates the arguments of a running program. """
    for key in args:
        if key in current_args: current_args[key] = args[key]

def abort_program():
    """ Shuts down the current program. """
    global current_program 
    current_program = ""
    pad_leds.set_flow_activity(False)
    pad_leds.set_sequence_activity(1000, 0)
    corehw.all_off() 

def heartbeat():
    """ Plays the spout program. Call at least every 5 milliseconds."""
    global last_time_check, current_program
    t = time.monotonic_ns()
    elp = (t - last_time_check) / 1_000_000
    if elp < 2: return       # Check at most once every 2 milliseconds
    last_time_check = t
    # Send control to whichever program is playing.
    if current_program == "one_shot": program_one_shot() 
    if current_program == "random": program_random()

    

    