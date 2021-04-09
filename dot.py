# plan
# 1, collect choice response and reaction time
# 2, add EEG marker

from psychopy import visual core event
import numpy as np

range = [0, 320]
direction = [1, 2] # 1,left;2, right
nTrialsPerCond = 50
nTrials = nTrialsPerCond * len(range) * len(direction)


#create a window to draw in
myWin = visual.Window((600,600), allowGUI=False)
cond = np.arange(nTrials)
cond = cond%4

direction = np.empty(nTrials)
dirRange = np.empty(nTrials)
for iTrial in range(nTrials): # loop trials
    # fixation
    
    # show static image [1 2] s
    
    
    # moving dots 0.5s
    if cond[iTrial] == 0
        dirRange[iTrial] = 0
        direction[iTrial] = 1
    elif cond[iTrial] == 1
        dirRange[iTrial] = 0
        direction[iTrial] = 2
    elif cond[iTrial] == 2
        dirRange[iTrial] =320
        direction[iTrial] = 1
    elif cond[iTrial] == 3
        dirRange[iTrial] =320
        direction[iTrial] = 2
    
    
    # collect responses
    
    
# save data
pickle.dump()
