# ball_valve.py -- Controls the position of the ball valve.
# dlb, Aug 24

# The ball valve takes about 5 seconds to fully open or close.
# This modudle is responsibe for setting the ball value to
# positions in-between open and close.  The postion is 
# measured in terms of percent open, where zero is fully 
# closed, and 100 is fully open.

import corehw 
import time

full_movement_time = 5300   # milliseconds to move full span
tollerance = 0.125          # Percentage of tollerance to set valve
target_position = 0         # In percent of fully opened
current_position = 0        # In percent of fully opened
forward_motion = False
reverse_motion = False
reset_mode = False          # If in Reset Mode.
fullon_mode = False         # if in Full On Mode.
last_time_check = 0
last_update_time = time.monotonic_ns()
loop_count = 0

def print_status():
    """ Prints the status of the ball valve, for debugging."""
    switches = corehw.check_ball_valve()
    print(f"t_pos={target_position:.2f}  c_pos={current_position:.2f}  fwd={forward_motion}  rev={reverse_motion} switches={switches}")

def set_position(target):
    """ Sets the target position, in percent, of the ball valve.  Non-blocking. Use get_current_positon()
    to determine when the operation is complete."""
    global target_position
    target_position = target

def get_current_position():
    """ Returns the current position, in percent."""
    global current_position
    return current_position

def get_current_target():
    """ Returns the target position, in percent. """
    global target_position
    return target_position

def in_motion():
    """ Returns True if ball valve is in motion."""
    global forward_motion, reverse_motion
    if forward_motion: return True 
    if reverse_motion: return True
    return False

def is_fullon():
    """ Returns True if ball valve is fully open."""
    switches = corehw.check_ball_valve()
    if switches > 0: return True
    return False

def is_closed():
    """ Returns True if the ball valve is fully closed."""
    switches = corehw.check_ball_valve()
    if switches < 0: return True
    return False

def reset_to_zero():
    """ Shuts Ball Valve to zero to start things off.  Non-blocking. Use is_closed() to
    determine when this operation is finished."""
    global reset_mode, fullon_mode, last_update_time, reverse_motion, forward_motion, target_position
    reset_mode = True
    fullon_mode = False
    last_update_time = time.monotonic_ns()
    reverse_motion = True
    forward_motion = False
    target_position = 0
    corehw.ball_valve_move(-1)

def reset_to_fullon():
    """ Opens up Ball Valve fully, regardless of timing. Non-blocking. Use is_fullon() to 
    determine when this operation is finished."""
    global reset_mode, fullon_mode, last_update_time, reverse_motion, forward_motion, target_position
    reset_mode = False
    fullon_mode = True
    last_update_time = time.monotonic_ns()
    reverse_motion = False
    forward_motion = True
    target_position = 100
    corehw.ball_valve_move(1)

def heartbeat():
    """ Call this at least once every 5 milliseconds to set valve."""
    global reset_mode, fullon_mode, last_update_time, reverse_motion, forward_motion, target_position, current_position
    global last_time_check, loop_count
    t = time.monotonic_ns()
    elp = (t - last_time_check) / 1_000_000
    if elp < 2: return       # Check at most once every 2 milliseconds
    # loop_count += 1 
    # if loop_count % 500 == 0: print_status()
    last_time_check = t 
    if forward_motion:
        elp = (t - last_update_time) / 1_000_000.0
        delta = elp / full_movement_time
        current_position += delta*100
        if current_position > 99: current_position = 99 
        if corehw.check_ball_valve() > 0:
            current_position = 100 
            corehw.ball_valve_move(0)
            forward_motion = False 
            reverse_motion = False
    if reverse_motion:
        elp = (t - last_update_time) / 1_000_000.0
        delta = elp / full_movement_time
        current_position -= (delta*100) 
        if current_position < 1: current_position = 1
        if corehw.check_ball_valve() < 0:
            current_position = 0 
            corehw.ball_valve_move(0)
            forward_motion = False 
            reverse_motion = False
    last_update_time = t 
    if reset_mode:
        if corehw.check_ball_valve() == -1:
            current_position = 0
            target_position = 0
            reverse_motion = False
            forward_motion = False
            reset_mode = False
            fullon_mode = False
            last_update_time = t 
            corehw.ball_valve_move(0)
        return
    if fullon_mode:
        if corehw.check_ball_valve() == 1:
            current_position = 100
            target_position = 100
            reverse_motion = False
            forward_motion = False
            reset_mode = False
            fullon_mode = False
            last_update_time = t 
            corehw.ball_valve_move(0)
        return
    if corehw.check_ball_valve() != 0:
        if corehw.check_ball_valve() < 0: 
            current_position = 0 
            last_update_time = t 
        if corehw.check_ball_valve() > 0:
            current_position = 100
            last_update_time = t 
    positional_error = target_position - current_position
    positional_error_abs = positional_error
    if positional_error_abs < 0: positional_error_abs = -1.0 * positional_error_abs
    if positional_error_abs < tollerance:
        corehw.ball_valve_move(0)
        forward_motion = False
        reverse_motion = False
        return
    # Head toward the target
    if positional_error > 0:
        corehw.ball_valve_move(1)
        forward_motion = True
        reverse_motion = False 
    else:
        corehw.ball_valve_move(-1)
        forward_motion = False
        reverse_motion = True

    
    

    

        

