import corehw
import conductor
import wsp_proc as proc
import ball_valve
from flask import Flask, render_template, request

period_inc = 100 
duration_inc = 20

prog_list = []

app = Flask("splash")

def find_program(prog):
    if prog is None: return ""
    if len(prog) > 2: 
        iprog = -1
        if prog[0:2] == "p_":
            try:
                iprog = int(prog[2:])
            except:
                iprog = -1
        if iprog >= 0 and iprog < len(prog_list):
            program_name = prog_list[iprog] 
            return program_name
    return ""

@app.route('/', methods = ['GET', 'POST'])
def index():
    print("Start Processing Input.  Method=%s" % request.method)
    action = ""
    padnum = -1 
    prog = ""
    prog_to_run = ""
    if request.method == "POST":
        data = request.get_json()
        pad = "-1"
        if "action" in data: action = data["action"]
        if "pad" in data: pad = data["pad"]
        if "program" in data: prog = data["program"]
        try:
            padnum = int(pad) 
        except:
            padnum = -1
        prog = find_program(prog)
        print("POSTED Data: Action=%s  Prog=%s  Pad=%d" % (action, prog, padnum))
    if request.method == "GET":
        # This is probably a simple refresh.  Therefore, don't screw up the
        # current settings.
        prog = request.args.get('program')
        print("1: " + prog)
        prog = find_program(prog)
        print("GET Data: Prog=%s" % prog)
    if action == "stop":
        conductor.command("stop")
    if action == "one_shot":
        if padnum >= 0 and padnum <= 13:
            conductor.command("one_shot", {"spout": padnum, "duration": corehw.duration})
    if action == "reset":
            conductor.command("reset")
    if action == "speed_down":
        corehw.period += period_inc
        if corehw.period < 100: corehw.period = 100
        if corehw.period > 10000: corehw.period = 10000
        conductor.update_arguments({"period": corehw.period})
    if action == "speed_up":
        corehw.period -= period_inc
        if corehw.period < 100: corehw.period = 100
        if corehw.period > 10000: corehw.period = 10000
        conductor.update_arguments({"period": corehw.period})
    if action == "flow_down":
        conductor.command("lower")
    if action == "flow_up":
        conductor.command("higher")
    if action == "jump_up":
        corehw.duration += duration_inc
        if corehw.duration > 10000: corehw.duration = 10000
        if corehw.duration < 20: corehw.duration = 20
        conductor.update_arguments({"duration": corehw.duration})
    if action == "jump_down":
        corehw.duration -= duration_inc
        if corehw.duration > 10000: corehw.duration = 10000
        if corehw.duration < 20: corehw.duration = 20
        conductor.update_arguments({"duration": corehw.duration})
    if action == "play":
        conductor.command("play", {"program": prog})
    if action == "normal":
        conductor.command("set_flow", {"position": 20})
        corehw.period = 800
        corehw.duration = 100
        conductor.update_arguments({"period": corehw.period, "duration": corehw.duration})
    if action == "agressive":
        conductor.command("set_flow", {"position": 40})
        corehw.period = 400
        corehw.duration = 200
        conductor.update_arguments({"period": corehw.period, "duration": corehw.duration})   
    p = conductor.get_status()
    psi1 = "%5.1f" % p["psi_input"]
    psi2 = "%5.1f" % p["psi_output"]
    flow = "%3.0f" % ball_valve.get_current_position()
    flow += "%"
    if corehw.check_ball_valve() > 0: flow = "Opened"
    if corehw.check_ball_valve() < 0: flow = "Closed"
    p2 = {"psi1": psi1, "psi2": psi2, "flow": flow, "speed": corehw.period, 
          "jump": corehw.duration, "progs": prog_list, "selected_prog": prog}
    return render_template('index.html', **p2)

@app.route('/play')
def play():
    corehw.ring(0.025, 0.075)
    return render_template('play.html')

@app.route('/status')
def status():
    p = conductor.get_status()
    return render_template('status.html', **p)

if __name__ == '__main__':
    conductor.init() 
    prog_list = proc.get_program_names()
    print("Number of programs in wsp_script folder: %d" % len(prog_list))
    print("Programs Found: ")
    for p in prog_list:
        print(p)
    print("\n")
    app.run(debug=False, host='0.0.0.0')

