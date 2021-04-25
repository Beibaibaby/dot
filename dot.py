"""
history:
   2021/04/24 RYZ rewrite the position

To do:
1. figure out how to accurately recor reaction time
2. how to save data into a CSV file
3. test connection to NetStation
"""

 

from psychopy import core, monitors, clock
from psychopy import visual, event
from psychopy.tools.coordinatetools import pol2cart, cart2pol
from psychopy.tools import monitorunittools
from psychopy.visual import circle
import numpy as np
from psychopy.hardware import keyboard
import pandas as pd
from functools import partial
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
nTrialsPerCond =  1
maxDur =  20 # sec, longest stim duration or a key press comes first
delayDur = 1 # sec, delay of stim onset afte fixation
staticDur = [1, 2] # stimulus being static for 1-2s
speedDeg = 10.0 # deg/sec, shall convert to deg/frame
dotDensity = 0.6 # dots/deg^2
dotSize = 0.125 # deg, diameter
iti = 2 # intertrial interval
# ======= setup hardwares =======
mon = monitors.Monitor('hospital6')
mon.setDistance(57) # View distance cm
mon.setSizePix([1920, 1080]) # pixels
mon.setWidth(52.71) # cm
myWin = visual.Window([1000, 1000], units='deg',monitor=mon, color=(-1, -1, -1), checkTiming=True)
fps = myWin.getActualFrameRate()

event.globalKeys.clear()
event.globalKeys.add(key='q', func=core.quit) # global quit
globalClock = clock.Clock()
kb = keyboard.Keyboard() # create kb object

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
direction, stimType, RT, choice = [np.empty(nTrials) for _ in range(4)]

#  ====== define stimulus components =======
# define fixation
fixation = circle.Circle(win=myWin, units='deg', radius=0.25, lineColor=0, fillColor=0)
# define coherent dots 
cohDots = visual.DotStim(win=myWin, nDots=nDots, units='deg', fieldSize=[fieldRadius*2, fieldRadius*2], fieldShape='circle', coherence=1, dotSize=dotSizePix, dotLife=-1) # note here dotSiz is in pixels
# define stimulus array
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
    cohDots.speed=speedFrame# reset speed per frame
    kb.clock.reset() # reset the keyboard clock
    kb.start() # keyboard start recoding
    for i in range(maxFrames): # 
        fixation.draw()
        cohDots.draw()
        myWin.flip()
        keys=kb.getKeys(keyList=['left','right'])
        if keys:
            break
    if not keys:
        keys=kb.waitKeys(keyList=['left','right']) # still waiting after stimulus
    kb.stop()
    
    rt = keys[0].rt
    cho=-1 if keys[0].name=='left' else 1
    return rt, cho
# show initial Fixation
def showFixation(): 
    fixation.draw()
    myWin.flip()
    core.wait(1)

# calculate chaos dots position
def computeChaosPos(dir=0):
    if dir == -1: # left
        directionRange1 = [20, 180]
        directionRange2 = [180, 340]
    elif dir == 1: # right
        directionRange1 = [0, 160]
        directionRange2 = [200, 360]

    # Initial parameters
    dotsTheta = np.random.rand(nDots) * 360 # deg
    dotsRadius = (np.random.rand(nDots) ** 0.5) * fieldRadius # in deg
    dotsX, dotsY = pol2cart(dotsTheta, dotsRadius) # in deg

#    # choose direction
    #dir1 = np.random.rand(int(nDots / 2)) * (directionRange1[1] - directionRange1[0]) + directionRange1[0]
    #dir2 = np.random.rand(int(nDots / 2)) * (directionRange2[1] - directionRange2[0]) + directionRange2[0]
    #dirAll = np.hstack((dir1, dir2))
    
    #dirAll  = np.ones(nDots) * -90
    XYpos = np.empty((nDots, 2, maxFrames))
    for iFrame in range(maxFrames):
        # # choose direction
        dir1 = np.random.rand(int(nDots / 2)) * (directionRange1[1] - directionRange1[0]) + directionRange1[0]
        dir2 = np.random.rand(int(nDots / 2)) * (directionRange2[1] - directionRange2[0]) + directionRange2[0]
        dirAll = np.hstack((dir1, dir2))
        # update position
        dotsX, dotsY = dotsX + speedFrame * np.cos(dirAll*np.pi/180), dotsY + speedFrame*np.sin(dirAll*np.pi/180)
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
def showChaosDots(XYpos):
    nFrame = XYpos.shape[-1]
    kb.clock.reset() # reset the keyboard clock
    kb.start() # keyboard start recoding
    for iFrame in range(nFrame):
        chaosDots.setXYs(XYpos[:,:,iFrame])
        chaosDots.draw()
        fixation.draw()
        myWin.flip()
        keys=kb.getKeys(keyList=['left','right'])
        if keys:
            break
    if not keys:
        keys=kb.waitKeys(keyList=['left','right'])
    rt = keys[0].rt
    cho=-1 if keys[0].name=='left' else 1
    return rt, cho
    

# ======= connect and setup NetStation====


# do it!!!
#  =========== main experiment loop ========
# for iTrial in range(nTrials): 
    
#     # draw fixation
#     showFixation()

#     # add 1000ms delay while calculating stim
#     ISI = clock.StaticPeriod(screenHz=fps)
#     ISI.start(delayDur)  # start a period of 0.5s
#     if cond[iTrial] == 0: # left
#         direction[iTrial] = -1
#         stimType [iTrial]= 1 # coherent stim
#         showFun = partial(showCohDots, dir=180)
#     elif cond[iTrial] == 1: # right
#         direction[iTrial] = 1 # right
#         stimType [iTrial]= 1 # coherent stim
#         dir2show = 0
#         showFun = partial(showCohDots, dir=0)
#     elif cond[iTrial] == 2:        
#         direction[iTrial] = -1 # left
#         stimType [iTrial]= 2 # chaos stim
#         showFun = partial(showChaosDots, XYpos=computeChaosPos(dir=-1))
#     elif cond[iTrial] == 3:
#         direction[iTrial] =  1 # right
#         dir2show = 0
#         stimType [iTrial]= 2 # chaos stim
#         showFun = partial(showChaosDots, XYpos=computeChaosPos(dir=1))
#     ISI.complete()  # finish the delay period

#     # show the motion stimulus
#     rt, cho=showFun(dir=dir2show)
    
#     # save data for this trial
#     RT[iTrial]=rt
#     choice[iTrial]=cho
    
# test
XYpos = computeChaosPos(dir=-1)
showChaosDots(XYpos)
myWin.flip()
#showCohDots(dir=30)

# ====cleanup and save data to csv======
# we want to save direction, stimType, RT, choice into a CSV file