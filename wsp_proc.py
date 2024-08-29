# wsp_proc.py -- Parses and runs Water-Script-Programs
# dlb, Aug 2024

# Please see the "documentation.md" file.

import time 
import os
import corehw
import ball_valve
import random
import pad_leds

scrip_folder = "wsp_scripts"
programs = []                      # A table of all known programs
current_program = None             # Points to a map that defines the current program
current_line_num = 0               # Current line number for execution
new_statement = True               # Flag that indicates if the current_line_num is a new statement
variable_table = {}                # Holes the program variables
pause_time_start = 0               # Used for the pause and squirt statements
lasttime_check = time.monotonic_ns()


def split_line(line):
    """ Split line into words, while treating quoted text as one word and removing 
    comments that start with the hash mark #.  Also sets all characters outside of
    quotes to lowercase."""
    line = line.strip()  
    words = []
    current_word = ""
    inquotes = False 
    for c in line:
        if c == " ":
            if inquotes: current_word += c 
            else:
                if len(current_word) > 0: words.append(current_word)
                current_word = "" 
            continue
        if c == "#":
            if inquotes: 
                current_word += c 
                continue
            if len(current_word) > 0: words.append(current_word)
            return words 
        if c == '"':
            if inquotes: 
                inquotes = False 
                words.append(current_word)
                current_word = ""
            else: inquotes = True
            continue
        if inquotes: current_word += c 
        else: current_word += c.lower()
    if len(current_word) > 0: words.append(current_word)
    return words 


def read_program(filename):
    """ Reads and parses the program from the given file.  Returns a map or None if error.
    The map contains the name of the program, and a list of statements (or lines).  Each
    statement is a list of words. """
    fparts = filename.split(".")
    if len(fparts) != 2: return None 
    if fparts[1].lower() != 'wsp': return None
    prg_name = fparts[0] 
    try: 
        f = open(scrip_folder + '/' + filename)
        lines = f.readlines()
        f.close()
    except:
        return None
    prg_lines = [] 
    for line in lines:
        words = split_line(line) 
        if len(words) > 0: 
            prg_lines.append(words)
            if words[0] == "name":
                if len(words) > 1: prg_name = words[1]
    return {"program_name": prg_name, "lines": prg_lines }

def print_programs():
    "Print the contents of all the programs.  For debugging."
    for p in programs:
        print("\n")
        print("Name: %s" % p["program_name"])
        print("Number of statements: %d" % len(p["lines"]))
        count = 0
        for line in p["lines"]:
            ws = " " 
            for word in line:
                ws += "." + word + ".  "
            print("%03d -- %s" % (count, ws)) 
            count += 1

def read_programs():
    """ Reads in all the programs in the script folder, and parses them.  Must
    be called at startup. """
    progs = os.listdir(scrip_folder)
    for p in progs:
        prg = read_program(p) 
        if prg is not None:
            programs.append(prg)
    print("Number of loaded WSP Scripts: %d." % len(programs))


def get_program_names():
    """ Returns a list of program names that can be run. """
    names = [] 
    for p in programs:
        names.append(p["program_name"])
    return names

def get_current_program():
    """ Returns the name of the currently running program. If no
     program is active, None is returned. """
    if current_program is None: return None
    return current_program["program_name"]

def start_program(prog_name):
    """ Starts program with the given name. """
    global current_program, current_line_num, new_statement, variable_table
    print("wsp: STARTING PROGRAM: %s" % prog_name)
    if current_program is not None:
        corehw.all_off()
        current_program = None 
    for p in programs:
        if p["program_name"] == prog_name:
            current_program = p 
            current_line_num = 0 
            new_statement = True 
            variable_table = {}
            return

def abort_program():
    """ Stops (aborts) any running program."""
    global current_program
    print("wsp: ABORTING PROGRAM")
    if current_program is not None:
        corehw.all_off()
        current_program = None 

def check_arg_is_var(arg):
    """ Returns true if arg is a variable. """
    if type(arg) is not str: return False
    if len(arg) < 2: return False 
    if arg[0] != "*": return False 
    return True

def is_num(arg):
    """ Checks to make sure the argument is a simple integer."""
    if type(arg) is int: return True 
    if type(arg) is not str: return False 
    if len(arg) <= 0: return False 
    if arg[0] not in "+-0123456789": return False
    arg = arg[1:]
    for c in arg:
        if c not in "0123456789": return False
    return True
    
def make_int(arg):
    """ Converts the argument to a integer. Weird input returns zero."""
    if type(arg) is int: return arg  
    if type(arg) is not str: return 0 
    if len(arg) <= 0: return 0 
    neg = False 
    if arg[0] == '-': 
        neg = True 
        arg = arg[1:]
    elif arg[0] == '+': arg = arg[1:]
    v = 0
    for c in arg:
        if c not in "0123456789": return 0
        v = 10*v + ord(c) - ord('0')
    if neg: v = -v
    return v

def get_var_value(arg):
    """ Given a argument that should be a variable or a literal, return it's value. """
    if len(arg) <= 0: return 0 
    if arg[0] == '*':
        if arg == "*flow": ball_valve.get_current_position() 
        if arg == "*duration": return corehw.duration
        if arg == "*period": return corehw.period
        if arg in variable_table:
            return variable_table[arg]
        else:
            variable_table[arg] = 0
            return 0
    return make_int(arg)

def set_var_value(var, value):
    """ Sets the variable to the given value. var should be string. value can be string or int.
    If value is string, it can be a variable or a literal."""
    if not check_arg_is_var(var): return
    if var == "*flow": return 
    iv = 0 
    if type(value) is int: iv = value 
    else: iv = get_var_value(value)
    if var == "*duration":
        #print("wsp:    !! Setting corehw.duration = %d" % iv)
        corehw.duration = iv 
        return
    if var == "*period":
        #print("wsp:    !! Setting corehw.period = %d" % iv)
        corehw.period = iv
        return
    variable_table[var] = iv

def set_flow(args):
    """ Helper function to set flow."""
    v = 0
    if len(args) >= 1: v = get_var_value(args[0])
    #print("In set-flow. args[0]=%s, v=%d" % (args[0], v))
    #print(type(v))
    if v > 100: v = 100
    if v < 0: v = 0
    if v == 0: ball_valve.reset_to_zero()
    elif v == 100: ball_valve.reset_to_fullon()
    else: ball_valve.set_position(v)
    return

def set_spout(spout_name, enable=True):
    """ Turns on or Off a Spout, given the name as a string. """
    if "[" in spout_name:
        indx = spout_name.index("[")
        basename = spout_name[:indx]
        extension = spout_name[indx:]
        if extension[-1] != ']': 
            advance_line()
            return
        v = get_var_value(extension[1:-1])
        spout_name = basename + str(v)
    if spout_name in corehw.spout_names:
        if enable: corehw.turn_pattern_on(spout_name)
        else:      corehw.turn_pattern_off(spout_name)
    else:
        if check_arg_is_var(spout_name):
            v = get_var_value(spout_name)
            if enable: corehw.turn_pattern_on(v)
            else: corehw.turn_pattern_off(v)
        else:
            if is_num(spout_name): 
                if enable: corehw.turn_pattern_on(make_int(spout_name))
                else: corehw.turn_pattern_off(make_int(spout_name))

def advance_line():
    """ Helper function to advance line."""
    global current_program, current_line_num, new_statement
    current_line_num += 1 
    new_statement = True

def goto_line(label):
    """ Helper function to jump to a label. """
    global current_program, current_line_num, new_statement
    if type(label) is not str: 
        advance_line()
        return
    if current_program is None: return 
    lines = current_program["lines"]
    for i, words in enumerate(lines):
        if len(words) < 2: continue
        if words[0] == "label" and words[1] == label:
            current_line_num = i 
            new_statement = True
            current_statement_start_time = time.monotonic_ns()
            return 
        
def print_line_status(cmd, args):
    # s = "wsp: cmd=%s  nargs=%d:  " % (cmd, len(args))
    # for a in args:
    #     s += a + "  "
    # print(s)
    pass

def print_wsp_debug(msg):
    #print("wsp:    %s" % msg)
    pass

def heartbeat():
    """ Come here to run the current program. Must be called every few millisconds."""
    global current_program, current_line_num, new_statement, pause_time_start
    global lasttime_check
    t = time.monotonic_ns()
    elp = (t - lasttime_check) / 1_000_000
    if elp < 2: return 
    lasttime_check = t 
    if current_program is None: return 
    lines = current_program["lines"]
    if current_line_num >= len(lines):
        # Program has come to a end. Shut it down
        corehw.all_off()
        current_program  = None 
        return
    words = lines[current_line_num]
    if len(words) <= 0:
        advance_line() 
        return 
    cmd = words[0]
    args = words[1:]
    # ===================  Process Statement Below.  
    # Note, that the statement might be already "in process" or it might be
    # a "new_statement" as indicated by the new_statement variable.
    if cmd == "name":
        print_line_status(cmd, args)
        advance_line()
        return
    if cmd == "set":
        print_line_status(cmd, args)
        if len(args) >= 2: 
            set_var_value(args[0], args[1])
            print_wsp_debug("%s = %s" % (args[0], args[1]))
        advance_line()
        return
    if cmd == "inc":
        print_line_status(cmd, args)
        step = 1 
        if len(args) > 1: 
            step = get_var_value(args[1])
            print_wsp_debug("step = %d" % step)
        v = get_var_value(args[0])
        v = v + step 
        set_var_value(args[0], v)
        print_wsp_debug("%s = %s" % (args[0], v))
        advance_line()
        return 
    if cmd == "dec":
        print_line_status(cmd, args)
        step = 1 
        if len(args) > 1: 
            step = get_var_value(args[1])
            print_wsp_debug("step = %d" % step)
        v = get_var_value(args[0])
        v = v - step 
        set_var_value(args[0], v)
        print_wsp_debug("%s = %s" % (args[0], v))
        advance_line()
        return 
    if cmd == "all-off":
        print_line_status(cmd, args)
        corehw.all_off()
        advance_line()
        return
    if cmd == "set-flow":
        if new_statement:
            print_line_status(cmd, args)
            set_flow(args)
            new_statement = False
            pause_time_start = time.monotonic_ns()
            return
        t = time.monotonic_ns()
        elp = (t - pause_time_start) / 1_000_000 
        if elp > 10000:
            print_wsp_debug("!!! Timeout while waiting for ball valve.")
            advance_line() 
            return
        if ball_valve.in_motion(): return
        advance_line()
        return 
    if cmd == "change-flow":
        print_line_status(cmd, args)
        set_flow(args)
        advance_line()
        return
    if cmd == "label":
        print_line_status(cmd, args)
        advance_line()
        return
    if cmd == "goto":
        print_line_status(cmd, args)
        if len(args) >= 1:
            goto_line(args[0])
        else: advance_line()
        return
    if cmd == "if-zero":
        print_line_status(cmd, args)
        if len(args) < 2:
            advance_line()
            return
        label = args[1]
        v = 0 
        if len(args) >= 2:
            v = get_var_value(args[0])
            print_wsp_debug("%s=%d" % (args[0], v))
        if v == 0: goto_line(label)
        else: advance_line()
    if cmd == "if-not-zero":
        print_line_status(cmd, args)
        if len(args) < 2:
            advance_line()
            return
        label = args[1]
        v = 0 
        if len(args) >= 2:
            v = get_var_value(args[0])
            print_wsp_debug("%s=%d" % (args[0], v))
        if v != 0: goto_line(label)
        else: advance_line()
    if cmd == "pause":
        if new_statement:
            print_line_status(cmd, args)
            pause_time_start = time.monotonic_ns() 
            new_statement = False 
            if len(args) <= 0: v = corehw.period
            else: v = get_var_value(args[0])
            print_wsp_debug("delay=%d" % v)
            return 
        if len(args) <= 0: v = corehw.period
        else: v = get_var_value(args[0])
        t = time.monotonic_ns()
        elp = (t - pause_time_start) / 1_000_000 
        if elp > v: advance_line()
        return
    if cmd == "spout-on":
        print_line_status(cmd, args)
        if len(args) > 0:
            set_spout(args[0], True)
        advance_line()
        return
    if cmd == "spout-off":
        print_line_status(cmd, args)
        if len(args) > 0:
            set_spout(args[0], False)
        advance_line()
        return
    if cmd == "squirt":
        if len(args) <= 0:
            print_line_status(cmd, args)
            print_wsp_debug("no args.")
            advance_line()
            return 
        if new_statement:
            print_line_status(cmd, args)
            duration = corehw.duration 
            if len(args) >= 2: 
                print_wsp_debug("Using Duration from args. duration=%d" % duration)
                duration = get_var_value(args[1])
            else:
                print_wsp_debug("Using Duration from global. duration=%d" % duration)
            pause_time_start = time.monotonic_ns()
            set_spout(args[0], True)
            new_statement = False 
            return
        else:
            t = time.monotonic_ns()
            elp = (t - pause_time_start) / 1_000_000
            duration = corehw.duration 
            if len(args) >= 2: duration = get_var_value(args[1])
            if elp > duration:
                set_spout(args[0], False)
                advance_line() 
            return
    if cmd == "random":
        print_line_status(cmd, args)
        if len(args) >= 1:
            if check_arg_is_var(args[0]):
                i1 = 0
                i2 = 13
                if len(args) >= 2: i1 = get_var_value(args[1])
                if len(args) >= 3: i2 = get_var_value(args[2])
                v = random.randint(i1, i2)
                set_var_value(args[0], v)
                print_wsp_debug("%s = %d" % (args[0], v))
        advance_line()
        return
    if cmd == "hold":
        if new_statement:
            print_line_status(cmd, args)
            new_statement = False
        return 
    if cmd == "exit":
        print_line_status(cmd, args)
        corehw.all_off()
        current_program  = None 
        return
    



    

