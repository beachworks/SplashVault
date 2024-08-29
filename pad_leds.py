# pad_leds.py -- Controls the status LEDs on the splash pad machine.  Keeps them blinking.
# dlb, Aug 2024

# Note: there are two Bulb LEDs on the control box, each of which has two actual internal LEDS.
# This meams the Bulb LEDs can have the following states: Off, Red, Green or Yellow.
# In effect, there are four independent LEDs -- three of which are controlled via software.
# The forth is connected direcly to power, to indicate power to the box.

# Here is how the LEDs are used.
#
# LED Bulb One:
#   Red -- Means box power is applied.  No software control.
#   Red / Yellow Blink -- Means that software is running.  This is under software control
#                         by this module.  
#
#
# LED Bulb Two:
#   Red -- Means water is flowing in at least one channel
#   Green/Red Blink -- Means a sequence is being played, with some water flowing
#   

import corehw
import time

last_time_check = time.monotonic_ns()
last_time_runled = time.monotonic_ns()
last_time_sequenceled = time.monotonic_ns()
run_period = 2000
run_duty = 0
run_on = False
flow_enabled = False
sequence_period = 2000
sequence_duty = 0
sequence_on = False 


def set_run_period(period_ms, duty):
    """ Sets the period and duty cycle of the Power Indicator LED."""
    global run_period, run_duty, run_on 
    run_period = period_ms 
    run_duty = period_ms * duty / 100
    last_time_runled = time.monotonic_ns() 
    if run_duty > 0: 
        corehw.run_led.on()
        run_on = True
    else: 
        corehw.run_led.off()
        run_off = True

def set_flow_activity(active):
    """ Sets the flow activity LED to on or off."""
    global flow_enabled
    flow_enabled = active
    if flow_enabled: corehw.activity_led_red.on()
    else: corehw.activity_led_red.off()
    
def set_sequence_activity(period_ms, duty):
    """ Sets the sequence activity. """
    global sequence_period, sequence_duty, sequence_on
    global last_time_sequenceled
    sequence_period = period_ms
    sequence_duty = period_ms * duty / 100    
    last_time_sequenceled = time.monotonic_ns()
    if sequence_duty > 0: 
        corehw.activity_led_green.on() 
        sequence_on = True
    else: 
        corehw.activity_led_green.off()
        sequence_on = False

def heartbeat():
    """ Keeps the LEDs blinking at the proper rate."""
    global last_time_check, last_time_runled, last_time_sequenceled
    global run_period, run_duty, run_on
    global sequence_on, sequence_duty, sequence_on
    t = time.monotonic_ns()
    if t - last_time_check < 2_000_000: return
    last_time_check = t
    if run_duty > 0:
        run_elp = (t - last_time_runled) / 1_000_000
        if run_elp > run_period:
            last_time_runled = t 
            corehw.run_led.on() 
            run_on = True
        elif run_elp > run_duty and run_on:
            corehw.run_led.off()
            run_on = False 
    if sequence_duty > 0:
        seq_elp = (t - last_time_sequenceled) / 1_000_000
        if seq_elp > sequence_period:
            last_time_sequenceled = t 
            corehw.activity_led_green.on()
            sequence_on = True 
        elif seq_elp > sequence_duty and sequence_on:
            corehw.activity_led_green.off()
            sequence_on = False

