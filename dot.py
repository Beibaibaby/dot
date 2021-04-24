from psychopy import core, monitors
from psychopy import visual, event, logging
from psychopy.tools.coordinatetools import pol2cart, cart2pol
from psychopy.tools import monitorunittools
from psychopy.visual import circle
import numpy as np
from psychopy.hardware import keyboard
import pandas as pd
#from egi import simple as egi

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

# ================ exp setting ==================
dirRange = [0,320]
stimDir= [-1, 1] # -1, left;1, right
fieldRadius = 10 # in deg
nTrialsPerCond =  5 
maxDur =  5 # sec, longest stim duration or a key press comes first
delayDur = 1 # sec, delay of stim onset afte fixation
staticDur = [1, 2] # stimulus being static for 1-2s
speedDeg = 10.0 # deg/sec, shall convert to deg/frame
dotDensity = 0.6 # dots/deg^2
dotSize = 0.125 # deg, diameter
iti = 2 # intertrial interval
# ======= setup hardwares =======
mon = monitors.Monitor('hospital6')
mon.setDistance(57) # View distance cm
mon.setSizePix([1920, 1080])
mon.setWidth(52.71) # cm
myWin = visual.Window([1000, 1000], units='deg',monitor=mon, color=(-1, -1, -1), checkTiming=True)
fps = myWin.getActualFrameRate()
kb = keyboard.Keyboard() # create kb object
globalClock = core.Clock() # global Clock
respClock = core.Clock()

# let's do some calculation before going further
speedFrame = speedDeg/fps # how many deg/frame
speedPixFrame = monitorunittools.deg2pix(speedFrame, mon)
dotSizePix = monitorunittools.deg2pix(dotSize, mon) # calculate dotSizePix for DotStim object
nDots = round(np.pi* fieldRadius **2 * dotDensity) # calcuate nDots
maxFrames = round(maxDur/myWin.monitorFramePeriod)

nTrials = nTrialsPerCond * len(dirRange) * len(stimDir)
cond = np.arange(nTrials)
cond = cond %(len(dirRange) * len(stimDir))
np.random.shuffle(cond)
direction, stimType, RT, choice, = [np.empty(nTrials) for _ in range(4)]

#  ====== define stimulus components =======
# define fixation
fixation = circle.Circle(win=myWin, units='deg', radius=0.25, lineColor=0, fillColor=0)
# define coherent dots 
cohDots = visual.DotStim(win=myWin, nDots=nDots, units='deg', fieldSize=[fieldRadius*2, fieldRadius*2], fieldShape='circle', coherence=1, dotSize=dotSizePix, dotLife=-1)
# Create the stimulus array
chaosDots = visual.ElementArrayStim(myWin, elementTex=None, fieldShape='circle', \
                                   elementMask='circle', nElements=nDots, sizes=dotSize, units='deg', \
                                   fieldSize=[fieldRadius*2, fieldRadius*2]) # note here dotSize is in deg
 
# show left/right coherent dots
def showCohDots(dir=0): 
    cohDots.dir=dir # dir=0, right; dir=180, left
    # show static stim
    cohDots.speed=0
    fixation.draw()
    cohDots.draw()
    myWin.flip()
    core.wait(np.random.rand()+1) # stay static 1-2s
    
    # show moving stim
    cohDots.speed=speedFrame# reset speed
    #kb.start() # keyboard start recoding
    flipStamp = np.empty(maxFrames)
    for i in range(maxFrames): # 
        fixation.draw()
        cohDots.draw()
        flipStamp[i]=myWin.flip()    
    #kb.stop() # keyboard stop recoding 
    return flipStamp
# show initial Fixation
def showFixation(): 
    fixation.draw()
    myWin.flip()
    core.wait(1)

# calculate chaos dots position
def createChaosStim(dir=0):
    if dir == -1: # left
        directionRange1 = [-180, -20]
        directionRange2 = [20, 180]
    elif dir == 1: # right
        directionRange1 = [-160, 0]
        directionRange2 = [0, 160]

    # Initial parameters
    dotsTheta = np.random.rand(nDots) * 360 # deg
    dotsRadius = (np.random.rand(nDots) ** 0.5) * fieldRadius # in deg
    dotsX, dotsY = pol2cart(dotsTheta, dotsRadius) # in deg
    XYpos = np.empty((nDots, 2, maxFrames))
    for iFrame in range(maxFrames):
        # choose direction
        dir1 = np.random.rand(int(nDots / 2)) * (directionRange1[1] - directionRange1[0]) + directionRange1[0]
        dir2 = np.random.rand(int(nDots / 2)) * (directionRange2[1] - directionRange2[0]) + directionRange2[0]
        dirAll = np.hstack((dir1, dir2))
        # update position
        dotsX, dotsY = dotsX + speedFrame * np.cos(dirAll), dotsY + speedFrame*np.sin(dirAll)
        # convert catesian to polar
        dotsTheta, dotsRadius = cart2pol(dotsX, dotsY)        
        outFieldDots = (dotsRadius > fieldRadius) # judge dots outside
        if outFieldDots.any():
            dotsRadius[outFieldDots] = np.random.rand(sum(outFieldDots)) * fieldRadius
            dotsTheta[outFieldDots] = np.random.rand(sum(outFieldDots)) * 360 # deg
        dotsX, dotsY = pol2cart(dotsTheta, dotsRadius)
        XYpos[:, 0, iFrame] = dotsX
        XYpos[:, 1, iFrame] = dotsY
    
    return XYpos

# show chaos stim
def showChaosStim(XYpos):
    nFrame = XYpos.shape[-1]
    for iFrame in range(nFrame):
        chaosDots.setXYs(XYpos[:,:,iFrame])
        chaosDots.draw()
        myWin.flip()

    

# ======= connect and setup NetStation====




"""
# do it!!!
#  =========== main experiment loop ========
kb.clock.reset() # reset clock
wanttoquick = False
for iTrial in range(nTrials): 
    
    # draw fixation
    showFixation()
    # delay
    core.wait(delayDur)

    if cond[iTrial] == 0: # left
        direction[iTrial] = -1
        stimType [iTrial]= 1 # coherent stim
        dir2show = 180
        showFun = showCohDots
    elif cond[iTrial] == 1: # right
        direction[iTrial] = 1 # right
        stimType [iTrial]= 1 # coherent stim
        dir2show = 0
        showFun = showCohDots
    elif cond[iTrial] == 3:        
        direction[iTrial] = -1 # left
        stimType [iTrial]= 2 # chaos stim
        dir2show = 180
        showFun = showChaosDots
    elif cond[iTrial] == 4:
        direction[iTrial] =  1 # right
        dir2show = 0
        stimType [iTrial]= 2 # chaos stim
        showFun = showChaosDots
    
    # show the motion stimulus
    rt, choice_tmp = showFun(dir=dir2show)
    
    # record data
    RT[iTrial]=rt
    choice[iTrial]=choice_tmp
    
    if wanttoquick:
        core.quit()
    
    
"""

XYpos = createChaosStim(dir=-1)
showChaosStim(XYpos)
myWin.flip()
showCohDots(dir=0)

# ====cleanup and save data to csv======
