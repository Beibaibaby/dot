# plan
# 1, collect choice response and reaction time
# 2, add EEG marker

from psychopy import visual, core, monitors
from psychopy.hardware import keyboard
import numpy as np

# set monitors
mon = monitors.Monitor('hospital6')
mon.setDistance(57)
mon.setSizePix([1920, 1080])
mon.setWidth(52.71)

# create a window
# assume
myWin = visual.Window([1920, 1080], units="deg", allowGUI=False, monitor=mon)
range = [0, 320]
direction = [1, 2] # 1,left;2, right
nTrialsPerCond = 50
nTrials = nTrialsPerCond * len(range) * len(direction)

# setup keyboard
kb = keyboard.Keyboard()
kb.clock.reset()

# create some stimuli
fixation = visual.GratingStim(win=myWin, size=0.5, pos=[0,0], sf=0, rgb=-1)
dotsLeft = visual.DotStim(win=myWin, fieldSize=300, fieldShape='circle',coherence=100, dotSize=20, dir=0, speed=2)
dotsRight = visual.DotStim(win=myWin, fieldSize=300, fieldShape='circle',coherence=100, dotSize=20, dir=180, speed=2)

cond = np.arange(nTrials)
cond = cond%4

direction = np.empty(nTrials)
dirRange = np.empty(nTrials)

for iTrial in range(nTrials): # loop trials
    # draw fixation
    fixation.draw() 
    myWin.flip()
    core.wait(5)
    # show static image [1 2] s
    
    
    # moving dots 0.5s
    if cond[iTrial] == 0:
        dirRange[iTrial] = 0
        direction[iTrial] = 1
    elif cond[iTrial] == 1:
        dirRange[iTrial] = 0
        direction[iTrial] = 2
    elif cond[iTrial] == 2:
        dirRange[iTrial] =320
        direction[iTrial] = 1
    elif cond[iTrial] == 3:
        dirRange[iTrial] =320
        direction[iTrial] = 2
    
    
    # collect responses
    while 1:
        keys = kb.getKeys(['right', 'left', 'quit'], waitRelease=True) # collect keybutton
        if 'quit' in keys:
            # save the data before quit??
            core.quit()
        elif len(keys)~=0:
            

# save data
pickle.dump()
