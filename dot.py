# plan
# 1, collect choice response and reaction time
# 2, add EEG marker

from psychopy import core, monitors
from psychopy import visual, event, data, logging
import random, datetime, time
from psychopy.hardware import keyboard
import numpy as np

# set monitors
mon = monitors.Monitor('hospital6')
mon.setDistance(57)
mon.setSizePix([1920, 1080])
mon.setWidth(52.71)

# create a window
# assume
myWin = visual.Window([1920, 1080], units="deg", allowGUI=False, monitor=mon,winType='pyglet')
logging.console.setLevel(logging.WARNING)  # default, only Errors and Warnings are shown on the console
# run  specific
fileName = "data/dot" + datetime.datetime.now().strftime("%Y-%m-%dT%H_%M_%S") + ".dat"
dataFile = open(fileName, 'w')  # note that MS Excel has only ASCII .csv, other spreadsheets do support UTF-8
dataFile.write("#{}, {}, {}\n".format("position", "time", "response"))

instruction = visual.TextStim(myWin,
                              text='Press ← if you see an left motion  ' \
                                   'Press → if you see the right one. Press Escape to stop the ' \
                                   'experiment, or continue to the end. It takes about a minute.'.decode(
                                  "utf-8")
                              )

range = [0, 320]
direction = [-1, 1]  # -1,left;1, right
nTrialsPerCond = 50
nTrials = nTrialsPerCond * len(range) * len(direction)

# setup keyboard
kb = keyboard.Keyboard()
kb.clock.reset()

fixation = visual.GratingStim(win=myWin, size=0.5, pos=[0, 0], sf=0, rgb=-1)

dotsLeft = visual.DotStim(win=myWin, fieldSize=300, fieldShape='circle', coherence=100, dotSize=20, dir=0, speed=2)
dotsRight = visual.DotStim(win=myWin, fieldSize=300, fieldShape='circle', coherence=100, dotSize=20, dir=180, speed=2)
dotsBoundary = visual.DotStim(win=myWin, fieldSize=300, fieldShape='circle', coherence=100, dotSize=20, dir=320, speed=2)
randomIndex = 0
dotsRandom = visual.DotStim(win=myWin, fieldSize=300, fieldShape='circle', coherence=100, dotSize=20, dir=randomIndex, speed=2)

cond = np.arange(nTrials)
cond = cond %(len(range) * len(direction))

direction = np.empty(nTrials)
dirRange = np.empty(nTrials)
direction_random = np.empty(nTrials)

for iTrial in range(nTrials):  # loop trials
    # draw fixation
    fixation.draw()
    myWin.flip()
    core.wait(5)
    # show static image [1 2] s

    # moving dots 0.5s
    if cond[iTrial] == 0:#left
        dirRange[iTrial] = 0
        direction[iTrial] = 1
        dotsLeft.draw()

    elif cond[iTrial] == 1:
        dirRange[iTrial] = 0
        direction[iTrial] = 2
        dotsRight.draw()

    elif cond[iTrial] == 2:
        dirRange[iTrial] = 320
        direction[iTrial] = 1
        dotsBoundary.draw()

    elif cond[iTrial] == 3:
        dirRange[iTrial] = 320
        direction[iTrial] = 2
        randomIndex = random.randrange(320)
        direction_random[iTrial] = randomIndex
        dotsRandom.draw()
    # collect responses
    timeBefore = time.time()
    presses = event.waitKeys(3)  # wait a maximum of 3 seconds for keyboard input
    timeAfter = time.time()
    # handle keypress
    if not presses:
        # no keypress
        print
        "none"
        p = 0
    elif presses[0] == "left":
        p = -1
    elif presses[0] == "right":
        p = 1
    elif presses[0] == "escape":
        break
    else:
        # some other keypress
        print
        "other"
        p = 0
    dataFile.write("{}, {}, {}\n".format(x, timeAfter - timeBefore, p))
    # print x, timeAfter-timeBefore, p

myWin.close()
core.quit()
