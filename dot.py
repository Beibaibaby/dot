from psychopy import core, monitors
from psychopy import visual, event, logging
from psychopy.tools.coordinatetools import pol2cart
import numpy as np
import random
import time,csv
from psychopy.hardware import keyboard
from egi import simple as egi

#To send markers, we can use egi package or use pylsl package
"""
from pylsl import StreamInfo, StreamOutlet
info = StreamInfo(name='my_stream_name', type='Markers', channel_count=1,
                  channel_format='int32', source_id='uniqueid12345')
# Initialize the stream.
outlet = StreamOutlet(info)
"""

"""
ms_localtime = egi.ms_localtime
ns = egi.Netstation()
ns.connect('10.10.10.42', 55513) # sample address and port -- change according to your network settings
ns.BeginSession()
ns.sync()
ns.StartRecording()"""

kb = keyboard.Keyboard()
trialClock = core.Clock()
r_random = [0,320]
direction = [-1, 1]
nTrialsPerCond = 50
nTrials = nTrialsPerCond * len(r_random) * len(direction)
cond = np.arange(nTrials)
cond = cond %(len(r_random) * len(direction))
np.random.shuffle(cond)
direction = np.empty(nTrials)
dirRange = np.empty(nTrials)
direction_random = np.empty(nTrials)
choice = np.empty(nTrials)
mon = monitors.Monitor('hospital6')
mon.setDistance(57)
mon.setSizePix([1920, 1080])
mon.setWidth(52.71)
myWin = visual.Window([600, 600], units='pixels',monitor=mon, color=(0, 0, 0))
fixation1 = visual.GratingStim(win=myWin, size=0.5, pos=[0,0], sf=0, rgb=-1)

dotsLeftstop = visual.DotStim(win=myWin, nDots=50, units='pixels', fieldSize=200, fieldShape='circle', coherence=1, dotSize=10, dir=0, speed=0, dotLife=-1)
dotsLeft = visual.DotStim(win=myWin, nDots=50, units='pixels', fieldSize=200, fieldShape='circle', coherence=1, dotSize=10, dir=0, speed=2, dotLife=-1)


def stimulus_left():
    dotsRightstop.draw()
    myWin.flip()
    core.wait(2)
    for i in range(300):
      dotsLeft.draw()
      myWin.flip()

dotsRightstop = visual.DotStim(win=myWin, nDots=50, units='pixels', fieldSize=200, fieldShape='circle', coherence=1, dotSize=10, dir=180, speed=0, dotLife=-1)
dotsRight = visual.DotStim(win=myWin, nDots=50, units='pixels', fieldSize=200, fieldShape='circle', coherence=1, dotSize=10, dir=180, speed=2, dotLife=-1)

def stimulus_right():
   dotsRightstop.draw()
   myWin.flip()
   core.wait(2)
   for i in range(300):
      dotsRight.draw()
      myWin.flip()

random_index = 0

def stimulus_random(random_index):
    dotsRandomstop = visual.DotStim(win=myWin, nDots=50, units='pixels', fieldSize=200, fieldShape='circle',
                                    coherence=1, dotSize=10, dir=random_index, speed=0, dotLife=-1)
    dotsRandom = visual.DotStim(win=myWin, nDots=50, units='pixels', fieldSize=200, fieldShape='circle', coherence=1,
                                dotSize=10, dir=random_index, speed=2, dotLife=-1)


    dotsRandomstop.draw()
    myWin.flip()
    core.wait(2)
    for i in range(300):
      dotsRandom.draw()
      myWin.flip()

def cart2pol(x, y):
    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    return(rho, phi)

def fixation():
    fixation1.draw()
    myWin.flip()
    core.wait(1)

direction=1
def stimulus_chaos(direction):
    nDots = 50
    # The maximum speed of the dots
    maxSpeed = 10 # 10 is degree, should switch to pixels
    # The size of the field. Note that you also need to modify the `fieldSize`
    # keyword that is passed to `ElementArrayStim` below, due to (apparently) a bug
    # in PsychoPy
    fieldSize = 200
    # The size of the dots
    dotSize = 5
    # The number of frames
    nFrames = 1000
    # Initial parameters
    dotsTheta = np.random.rand(nDots) * 360
    dotsRadius = (np.random.rand(nDots) ** 0.5) * fieldSize
    dotsX, dotsY = pol2cart(dotsTheta, dotsRadius)
    speed = maxSpeed
    if direction == 1: # left
        directionRange1 = [-180, -20]
        directionRange2 = [20, 180]
    elif direction == 2: # right
        directionRange1 = [-160, 0]
        directionRange2 = [0, 160]
 
    # Create the stimulus array
    dots = visual.ElementArrayStim(myWin, elementTex=None, fieldShape='circle', \
                                   elementMask='circle', nElements=nDots, sizes=dotSize, units='pixels', \
                                   fieldSize=500)

    # Walk through each frame, update the dot positions and draw it
    dir1 = np.random.rand(int(nDots / 2)) * (directionRange1[1] - directionRange1[0]) + directionRange1[0]
    dir2 = np.random.rand(int(nDots / 2)) * (directionRange2[1] - directionRange2[0]) + directionRange2[0]

    dir = np.hstack((dir1, dir2))
    np.random.shuffle(dir)

    for frameN in range(5000):
        # draw random directions
      re = frameN % 10
      while re == 0:
            dir1 = np.random.rand(int(nDots/2))*(directionRange1[1]-directionRange1[0])+directionRange1[0]
            dir2 = np.random.rand(int(nDots/2))*(directionRange2[1]-directionRange2[0])+directionRange2[0]
            dir = np.hstack((dir1, dir2))

      # update position
      dotsX, dotsY = dotsX + speed*np.cos(dir), dotsY + speed*np.sin(dir)
      # convert catesian to polar
      dotsTheta, dotsRadius = cart2pol(dotsX, dotsY)
      # random radius where radius too large

      outFieldDots = (dotsRadius > fieldSize)
      dotsRadius[outFieldDots] = np.random.rand(sum(outFieldDots)) * fieldSize


      dotsX, dotsY = pol2cart(dotsTheta, dotsRadius)
      #坐标转换
      dots.setXYs(np.array([dotsX, dotsY]).transpose())
      dots.draw()
      myWin.flip()


f = open('numbers2.csv', 'w')
with f:
    writer = csv.writer(f)
    writer.writerow(['index_trial', 'condition', 'choice','reaction_time'])

"""for iTrial in range(nTrials):  # loop trials
    # draw fixation

    fixation()
    kb.clock.reset()  # timer (re)starts
    trialClock.reset()

    if cond[iTrial] == 0:#left
        direction[iTrial] = 0
        stimulus_left()
    elif cond[iTrial] == 1:
        stimulus_right()
        direction[iTrial] = 180
    elif cond[iTrial] == 3:
        stimulus_chaos()
        direction[iTrial] = -1
    elif cond[iTrial] == 2:
        random_index = random.randrange(320)
        direction[iTrial] = random_index
        stimulus_random(random_index)

    presses = event.waitKeys(keyList=["left", "right", "q"], timeStamped=trialClock)
    if presses[0] == "left":
        choice[iTrial] = -1
    elif presses[0] == "right":
        choice[iTrial] = 1
    elif presses[0] == "q":
        core.quit()
    reaction_time = trialClock.getLastResetTime()

    f = open('numbers2.csv', 'a')
    with f:
         writer = csv.writer(f)
         writer.writerow([iTrial,direction_random[iTrial], choice[iTrial], reaction_time])
  # ns.sync()
  # ns.SendSimpleTimestampedEvent(b'0051')"""
stimulus_chaos(direction)

myWin.close()
core.quit()
