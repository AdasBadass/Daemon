from datetime import datetime, timedelta
import calendar
import math
import time
import os

DAEMON_FILE = __file__.replace(".py", ".time")
SLEEP_TIME = 5 # Sleep time in minutes. Must be lower than the granularity in the ".time" file.

def current_period(now, freq): # Calculate the start and end of the current time period.
    start = None
    end = None
    match freq:
        case 'W': # Weekly
            start = now - timedelta(days=now.weekday())
            end = start + timedelta(days=6)
        case 'M': # Monthly
            start = now - timedelta(days=now.day - 1)
            end = datetime(start.year, start.month, calendar.monthrange(start.year, start.month)[1])
        case 'Q': # Quarterly
            start = datetime(now.year, math.ceil(now.month / 3) * 3 - 2, 1)
            end = datetime(start.year, start.month + 2, calendar.monthrange(start.year, start.month + 2)[1])
        case _:
            raise Exception("Wrong use of the function.")
    return datetime(start.year, start.month, start.day), datetime(end.year, end.month, end.day)

def run_date(now, freq, day, runtime): # Returns the run date relative to the "now" argument.
    cp_start, cp_end = current_period(now, freq)
    cp_run = cp_start + timedelta(days=int(day) - 1, hours=runtime[0], minutes=runtime[1])
    if cp_run < now: # The task already ran in this period. Calculate run date for the next period.
        cp_run = run_date(cp_end + timedelta(days=1), freq, day, runtime)
    return cp_run

def get_next(arr): # Returns all of the processes that will run next (more processes can be scheduled to run at the same time) and their run time.
    to_run = []
    time_prev = None
    for elem in arr:
        if time_prev == None or time_prev == elem[0]:
            to_run.append(elem[1])
            time_prev = elem[0]
    return to_run, time_prev

next_printed = False
next_started = False

while True:
    runs = dict(runfreq=[], runday=[], runtime=[], runfile=[])
    keys = runs.keys()
    now = datetime.now()
    with open(DAEMON_FILE, 'r', encoding='utf8') as of:
        rows = [r for r in of.read().split('\n') if r[0] != '*']
        num_tasks = len(rows)
        for row in rows:
            rs = row.replace(' ', '').split('|')
            for i, key in enumerate(keys):
                runs[key].append(rs[i])
    ord_run = []
    for t in range(num_tasks):
        runtime = [int(d) for d in runs['runtime'][t].split(':')]
        if runs['runfreq'][t] != 'D': # Calculate the next run date.
            cp_run = run_date(now, runs['runfreq'][t], runs['runday'][t], runtime)
        else:
            cp_run = datetime(year=now.year, month=now.month, day=now.day, hour=runtime[0], minute=runtime[1])
            if cp_run < now:
                cp_run += timedelta(days=1)
        ord_run.append([cp_run, runs['runfile'][t]])
    proc_to_run, cp_run = get_next(sorted(ord_run, key=lambda x: x[0])) # Extract the path of the processes to run next.
    if not next_printed:
        print(f"Next procedure{'s' if len(proc_to_run) > 1 else ''} to run: {proc_to_run} [{cp_run.strftime('%Y-%m-%d %H:%M')}]")
        next_printed = True
    if not next_started and (now - timedelta(minutes=SLEEP_TIME) < cp_run < now + timedelta(minutes=SLEEP_TIME)):
        for sf in proc_to_run:
            print(f"Starting procedure \"{sf}\"...")
            try:
                os.startfile(sf)
            except:
                print(f"Error: Procedure \"{sf}\" doesn't exist.")
        if cp_run >= now:
            next_started = True
        next_printed = False
    else:
        next_started = False
    time.sleep(SLEEP_TIME * 60)