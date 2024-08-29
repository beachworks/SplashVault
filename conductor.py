# conductor.py -- Conducts the operation of the splash pad in the background
# dlb, Aug 2024
#
# Possible commands:
#
#   off          -- Shuts down all spouts. Stops the playing of a program
#   play         -- Plays a program. params: program name 
#   flow         -- Sets the flow to a percentage 0-100
#   spout        -- Turns a spout on for a period of time. params: spount number, duration.
#   blink        -- Blinks the status light. params: color, rate, duty
#   pattern      -- Turns a pattern of spouts on for a period of time. params:
#                   pattern name, duration.
#
# Note: the background task is a daemon which means it will die when the program
# exits.  Therefore, the caller is responsible for turning off the waterspounts 
# before exiting.
#
# The backgound task runs in a loop.  Each iteration of the loop occurs every millisecond.
# The 
#


import corehw
import threading
import time
import copy 
import pad_leds
import ball_valve
import wsp_proc as proc
import spout_player as player
cmd_lock = threading.Lock()
status_lock = threading.Lock()
conductor_inited = False

pending_cmd = ""
pending_cmd_waiting = False
pending_cmd_args = None
loop_count = 0
pad_status = { }

flow_increment = 2.5  # Percentage of flow change

def _execute_cmd(cmd, args={}):
    global flow_increment
    if cmd == "stop":
        proc.abort_program()
        player.abort_program() 
        corehw.all_off()
        pad_leds.set_flow_activity(False)
        pad_leds.set_sequence_activity(1000, 0)
        return
    if cmd == "play":               # Plays the given program.
        proc.abort_program()
        player.abort_program()
        corehw.all_off()
        pad_leds.set_flow_activity(False)
        pad_leds.set_sequence_activity(1000, 0)
        if "program" not in args: return 
        pad_leds.set_flow_activity(True)
        pad_leds.set_sequence_activity(500, 50)
        proc.start_program(args["program"])
        return
    if cmd == "one_shot":           # Fires one spout
        proc.abort_program()
        prog_args = copy.deepcopy(args)
        if "spout" not in prog_args: return 
        if "duration" not in args: prog_args["duration"] = corehw.duration
        player.set_program("one_shot", prog_args)
        return
    if cmd == "reset":          # resets the flow
        ball_valve.reset_to_zero()
        return
    if cmd == "set_flow":       # Sets the flow to a given percentage
        if "position" not in args: return 
        if args["position"] >= 100: ball_valve.reset_to_fullon()
        else: ball_valve.set_position(args["position"])
        return
    if cmd == "higher":         # Sets the flow up
        new_targ = ball_valve.get_current_target() + flow_increment
        if new_targ < 0: new_targ = 0
        if new_targ > 100: new_targ = 100
        ball_valve.set_position(new_targ)
        return
    if cmd == "lower":          # Sets the flow down
        new_targ = ball_valve.get_current_target() - flow_increment
        if new_targ < 0: new_targ = 0
        if new_targ > 100: new_targ = 100
        ball_valve.set_position(new_targ)
        return
    if cmd == "flow_increment": # Sets the flow increment for higher/lower
        if "flow_increment" not in args: return
        flow_increment = args["flow_increment"]
        return

def _update_status():
    global status_dict
    psi = corehw.get_psi()
    if psi is None: psi = (-1, -1)
    bs = corehw.check_ball_valve()
    full_open, full_close = False, False
    if bs > 0: full_open = True 
    if bs < 0: full_close = True
    flow_percent = ball_valve.get_current_position()
    status_lock.acquire()
    pad_status["psi_input"] = psi[0]
    pad_status["psi_output"] = psi[1]
    pad_status["flow_percent"] = flow_percent 
    pad_status["flow_fully_opened"] = full_open
    pad_status["flow_fully_closed"] = full_close
    pad_status["duration"] = corehw.duration 
    pad_status["period"] = corehw.period
    status_lock.release()

def _conduct():
    """ Do actual work.  Should be called once per millisecond.  """
    global pending_cmd, pending_cmd_waiting, pending_cmd_args
    global loop_count 
    loop_count += 1 
    # Do we have a new command?  Check once every 10 ms
    if loop_count % 10 == 0:
        newcmd = "" 
        newcmd_args = None
        cmd_lock.acquire()
        if pending_cmd_waiting:
            newcmd = pending_cmd
            newcmd_args = pending_cmd_args
            pending_cmd = ""
            pending_cmd_args = None
            pending_cmd_waiting = False
        cmd_lock.release()
        if newcmd != "": _execute_cmd(newcmd, newcmd_args)
        _update_status()
    pad_leds.heartbeat()
    ball_valve.heartbeat() 
    player.heartbeat()
    proc.heartbeat()

def _run_conductor():
    """ The main entry point for the background task. """
    global conductor_inited
    loop_start_time = time.monotonic_ns() 
    pad_leds.set_run_period(1000, 25)
    ball_valve.reset_to_zero()
    proc.read_programs()
    conductor_inited = True
    while True:
        # Try to keep the loop on a 1 microsecond cadance.
        current_time = time.monotonic_ns() 
        elp = (current_time - loop_start_time) / 1_000_000.0  # elp in milliseconds
        if elp < 1.0:
            # Need to sleep (and yield) for remainder. 
            time_to_sleep = (1.0 - elp) / 1000.0  
            time.sleep(time_to_sleep)
        loop_start_time = time.monotonic_ns()
        _conduct()

## -------------------------------------------------------------------------------
## Public Interface Functions 

def init():
    """ Initialize the background task.  Must be called once at startup."""
    t = threading.Thread(name="splash_pad_conductor", daemon=True, target=_run_conductor)
    t.start()
    while True:
        if conductor_inited == True: return 
        time.sleep(0.100)

def command(cmd, args={}):
    """ Issues a command to the splash pad. cmd is the name of the command and
    args is a dict of arguments for the cmd."""
    global pending_cmd, pending_cmd_waiting, pending_cmd_args
    cmd_lock.acquire()
    pending_cmd = cmd  
    pending_cmd_args = copy.deepcopy(args)
    pending_cmd_waiting = True 
    cmd_lock.release()

def update_arguments(args):
    """ Updates the arguments to a currently running command. """
    player.update_arguments(args)

def get_status():
    """ Returns a dictionary of parameters that describes the state of the pad. 
    See _update_status for a list of parameters."""
    status_lock.acquire()
    s = copy.deepcopy(pad_status)
    status_lock.release()
    return s 







