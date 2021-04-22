from psychopy import core, monitors
from psychopy import visual, event, logging
from psychopy.tools.coordinatetools import pol2cart
import numpy as np
import random
import time,csv

r_random = [0,320]
direction = [-1, 1]
nTrialsPerCond = 50
nTrials = nTrialsPerCond * len(r_random) * len(direction)
cond = np.arange(nTrials)
cond = cond %(len(r_random) * len(direction))
direction = np.empty(nTrials)
dirRange = np.empty(nTrials)
direction_random = np.empty(nTrials)

mon = monitors.Monitor('hospital6')
mon.setDistance(57)
mon.setSizePix([1920, 1080])
mon.setWidth(52.71)
myWin = visual.Window([600, 600], units='pixels',monitor=mon)
fixation1 = visual.GratingStim(win=myWin, size=0.5, pos=[0,0], sf=0, rgb=-1)

dotsLeftstop = visual.DotStim(win=myWin, nDots=50, units='pixels', fieldSize=200, fieldShape='circle', coherence=1, dotSize=10, dir=0, speed=0, dotLife=-1)
dotsLeft = visual.DotStim(win=myWin, nDots=50, units='pixels', fieldSize=200, fieldShape='circle', coherence=1, dotSize=10, dir=0, speed=2, dotLife=-1)


def stimulus_left():
    dotsRightstop.draw()
    myWin.flip()
    core.wait(3)
    for i in range(500):
      dotsLeft.draw()
      myWin.flip()

dotsRightstop = visual.DotStim(win=myWin, nDots=50, units='pixels', fieldSize=200, fieldShape='circle', coherence=1, dotSize=10, dir=180, speed=0, dotLife=-1)
dotsRight = visual.DotStim(win=myWin, nDots=50, units='pixels', fieldSize=200, fieldShape='circle', coherence=1, dotSize=10, dir=180, speed=2, dotLife=-1)

def stimulus_right():
   dotsRightstop.draw()
   myWin.flip()
   core.wait(3)
   for i in range(500):
      dotsRight.draw()
      myWin.flip()

random_index = 0
dotsRandomstop = visual.DotStim(win=myWin, nDots=50, units='pixels', fieldSize=200, fieldShape='circle', coherence=1, dotSize =10, dir=random_index, speed=0, dotLife=-1)
dotsRandom = visual.DotStim(win=myWin, nDots=50, units='pixels', fieldSize=200, fieldShape='circle', coherence=1, dotSize =10, dir=random_index, speed=2, dotLife=-1)

def stimulus_random():
   dotsRandomstop.draw()
   myWin.flip()
   core.wait(3)
   for i in range(500):
      dotsRandom.draw()
      myWin.flip()


def fixation():
    fixation1.draw()
    myWin.flip()
    core.wait(3)

def stimulus_chaos():
    nDots = 50
    # The maximum speed of the dots
    maxSpeed = 10
    # The size of the field. Note that you also need to modify the `fieldSize`
    # keyword that is passed to `ElementArrayStim` below, due to (apparently) a bug
    # in PsychoPy
    fieldSize = 200
    # The size of the dots
    dotSize = 10
    # The number of frames
    nFrames = 1000

    # Initial parameters
    dotsTheta = np.random.rand(nDots) * 360
    dotsRadius = (np.random.rand(nDots) ** 0.5) * 200
    speed = np.random.rand(nDots) * maxSpeed

    # Create the stimulus array
    dots = visual.ElementArrayStim(myWin, elementTex=None, fieldShape='circle', \
                                   elementMask='circle', nElements=nDots, sizes=dotSize, units='pix', \
                                   fieldSize=10000)

    # Walk through each frame, update the dot positions and draw it
    for frameN in range(100):
        # update radius
          dotsRadius = (dotsRadius + speed)
        # random radius where radius too large
          outFieldDots = (dotsRadius >= fieldSize)
          dotsRadius[outFieldDots] = np.random.rand(sum(outFieldDots)) * fieldSize
          dotsX, dotsY = pol2cart(dotsTheta, dotsRadius)
          dots.setXYs(np.array([dotsX, dotsY]).transpose())
          dots.draw()
          myWin.flip()



for iTrial in range(nTrials):  # loop trials
    # draw fixation
    fixation()
    # show static image [1 2] s
    # moving dots 0.5s

    if cond[iTrial] == 0:#left
        direction_random[iTrial] = 0
        stimulus_left()

    elif cond[iTrial] == 1:
        stimulus_right()
        direction_random[iTrial] = 180
    elif cond[iTrial] == 3:
        stimulus_chaos()
        direction_random[iTrial] = -1
    elif cond[iTrial] == 4:
        randomIndex = random.randrange(320)
        direction_random[iTrial] = randomIndex
        dotsRandom.draw()

    timeBefore = time.time()
    presses = event.waitKeys(3)  # wait a maximum of 3 seconds for keyboard input
    timeAfter = time.time()

    if not presses:
        # no keypress
        print
        "none"
        choice = 0
    elif presses[0] == "left":
        choice = -1
    elif presses[0] == "right":
        choice = 1
    elif presses[0] == "escape":
        break
    else:
        # some other keypress
        print
        "other"
        choice = 0

    reaction_time = timeAfter - timeBefore

    with open('resultdata.csv', 'w', newline='') as csvfile:
        fieldnames = ['index_trial', 'condition', 'choice','reaction_time']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({'index_trial': iTrial, 'condition': direction_random[iTrial],
                         'choice': choice,'reaction_time':reaction_time })

myWin.close()
core.quit()


