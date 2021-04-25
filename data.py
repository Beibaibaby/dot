'''
A RDK EEG experiment

History:
    2021/04/25 RYZ use trial handler to deal with trials
    2021/04/25 RYZ add reaction time and data
    2021/04/24 RYZ rewrite the position
To do:
1. test connection to NetStation
'''

from psychopy import core, monitors, clock, visual, event, data
from psychopy.tools.coordinatetools import pol2cart, cart2pol
from psychopy.tools import monitorunittools
from psychopy.hardware import keyboard
from psychopy.visual import circle
import numpy as np
from functools import partial
import csv
from time import localtime, strftime
import pickle as pkl

# ======= parameter you want to change ========
subjID = 'RYZ' # initials of the subject, to save data
wantEEG = False # whether to use EEG
wantSave = False # save data or not
# from egi import simple as egi

# To send markers, we can use egi package or use pylsl package
"""
from pylsl import StreamInfo, StreamOutlet
info = StreamInfo(name='my_stream_name', type='Markers', channel_count=1,
                  channel_format='int32', source_id='uniqueid12345')
# Initialize the stream.
outlet = StreamOutlet(info)
"""
if wantEEG:
    ms_localtime = egi.ms_localtime
    ns = egi.Netstation()
    ns.connect('10.10.10.42', 55513) # sample address and port -- change according to your network settings
    ns.BeginSession()
    ns.sync()
    ns.StartRecording()

# ================ exp setting ==================
dirRange = [0, 320]
stimDir = [-1, 1]  # -1, left;1, right
fieldRadius = 10  # in deg
nTrialsPerCond = 1
maxDur = 5  # sec, longest stim duration or a key press comes first
delayDur = 1  # sec, delay of stim onset after fixation
staticDur = [1, 2]  # stimulus being static for 1-2s
speedDeg = 10.0  # deg/sec, shall convert to deg/frame
dotDensity = 0.6  # dots/deg^2
dotSize = 0.125  # deg, diameter
iti = 2  # intertrial interval
# ======= setup hardwares =======
mon = monitors.Monitor('hospital6')
mon.setDistance(57)  # View distance cm
mon.setSizePix([1920, 1080])
mon.setWidth(52.71)  # cm
myWin = visual.Window([1000, 1000], units='deg', monitor=mon, color=(-1, -1, -1), checkTiming=True)
fps = myWin.getActualFrameRate()

event.globalKeys.clear()
event.globalKeys.add(key='q', func=core.quit)  # global quit
globalClock = clock.Clock()
kb = keyboard.Keyboard()  # create kb object

# let's do some calculation before going further
speedFrame = speedDeg / fps  # how many deg/frame
speedPixFrame = monitorunittools.deg2pix(speedFrame, mon)
dotSizePix = monitorunittools.deg2pix(dotSize, mon)  # calculate dotSizePix for DotStim object
nDots = round(np.pi * fieldRadius ** 2 * dotDensity)  # calcuate nDots
maxFrames = round(maxDur / myWin.monitorFramePeriod)

# define trial handler
stimList = []
for t in dirRange:
    for d in stimDir:
        stimList.append({'dirRange':t, 'direction':d})
trials=data.TrialHandler(trialList=stimList, nReps=nTrialsPerCond)

#  ====== define stimulus components =======
# define fixation
fixation = circle.Circle(win=myWin, units='deg', radius=0.25, lineColor=0, fillColor=0)
# define coherent dots 
cohDots = visual.DotStim(win=myWin, nDots=nDots, units='deg', fieldSize=[fieldRadius * 2, fieldRadius * 2],
                         fieldShape='circle', coherence=1, dotSize=dotSizePix, dotLife=-1) # note here dotSize is in pixels
# Create stimulus array
chaosDots = visual.ElementArrayStim(myWin, elementTex=None, fieldShape='circle', \
                                    elementMask='circle', nElements=nDots, sizes=dotSize, units='deg', \
                                    fieldSize=[fieldRadius * 2, fieldRadius * 2])  # note here dotSize is in deg

# show left/right coherent dots
def showCohDots(dir=-1):        
    
    cohDots.dir = 180 if dir==-1 else 0

    # show static stim
    cohDots.speed = 0
    fixation.draw()
    cohDots.draw()
    myWin.flip()
    if wantEEG:
        sendTrigger()
    core.wait(np.random.rand() + 1)  # stay static 1-2s

    # show moving stim
    cohDots.speed = speedFrame  # reset speed per frame
    kb.clock.reset()  # reset the keyboard clock
    kb.start()  # keyboard start recoding
    for i in range(maxFrames):  #
        fixation.draw()
        cohDots.draw()
        myWin.flip()
        if i==0 and wantEEG:
            sendTrigger()
        keys = kb.getKeys(keyList=['left', 'right'])
        if keys:
            break
    if not keys:
        keys = kb.waitKeys(keyList=['left', 'right'])  # still waiting after stimulus
    kb.stop()

    rt = keys[0].rt
    cho = -1 if keys[0].name == 'left' else 1
    return rt, cho

# show initial Fixation
def showFixation():
    fixation.draw()
    myWin.flip()
    if wantEEG:
        sendTrigger()
    core.wait(1)

# calculate chaos dots position
def computeChaosPos(dir=-1):
    if dir == -1:  # left
        directionRange1 = [20, 180]
        directionRange2 = [180, 340]
    elif dir == 1:  # right
        directionRange1 = [0, 160]
        directionRange2 = [200, 360]

    # Initial parameters
    dotsTheta = np.random.rand(nDots) * 360  # deg
    dotsRadius = (np.random.rand(nDots) ** 0.5) * fieldRadius  # in deg
    dotsX, dotsY = pol2cart(dotsTheta, dotsRadius)  # in deg
    XYpos = np.empty((nDots, 2, maxFrames))
    for iFrame in range(maxFrames):
        # choose direction
        dir1 = np.random.rand(int(nDots / 2)) * (directionRange1[1] - directionRange1[0]) + directionRange1[0]
        dir2 = np.random.rand(int(nDots / 2)) * (directionRange2[1] - directionRange2[0]) + directionRange2[0]
        dirAll = np.hstack((dir1, dir2))
        # update position
        dotsX, dotsY = dotsX + speedFrame * np.cos(dirAll*np.pi/180), dotsY + speedFrame * np.sin(dirAll*np.pi/180)
        # convert catesian to polar
        dotsTheta, dotsRadius = cart2pol(dotsX, dotsY)
        outFieldDots = (dotsRadius > fieldRadius)  # judge dots outside
        if outFieldDots.any():
            dotsRadius[outFieldDots] = np.random.rand(sum(outFieldDots)) * fieldRadius
            dotsTheta[outFieldDots] = np.random.rand(sum(outFieldDots)) * 360  # deg
        dotsX, dotsY = pol2cart(dotsTheta, dotsRadius)
        XYpos[:, 0, iFrame] = dotsX
        XYpos[:, 1, iFrame] = dotsY

    return XYpos

# show chaos stim
def showChaosDots(XYpos):
    nFrame = XYpos.shape[-1]
    
    # show static stim
    chaosDots.setXYs(XYpos[:, :, 0])
    fixation.draw()
    chaosDots.draw()
    myWin.flip()
    if wantEEG:
        sendTrigger()
    core.wait(np.random.rand() + 1)  # stay static 1-2s

    # show moving stim
    kb.clock.reset()  # reset the keyboard clock
    kb.start()  # keyboard start recoding
    for iFrame in range(nFrame):
        chaosDots.setXYs(XYpos[:, :, iFrame])
        chaosDots.draw()
        fixation.draw()
        myWin.flip()
        if iFrame==0 and wantEEG:
            sendTrigger()
        keys = kb.getKeys(keyList=['left', 'right'])
        if keys:
            break
    if not keys:
        keys = kb.waitKeys(keyList=['left', 'right'])
    rt = keys[0].rt
    cho = -1 if keys[0].name == 'left' else 1
    return rt, cho

# define welcome instruction interface
instrText = \
    '欢迎参加这个实验!\n \
    您将在屏幕上看到一系列运动的点\n \
    一旦这些点开始运动您需要按方向键(左/右)来判断整体的运动方向。\n \
    您可以不等运动点消失直接按键, 每次您必须要按键反应，实验才能继续。\n \
    请您又快又准确的反应! \n \
    如果您理解了以上的话，请按空格键继续'
tex = visual.TextStim(win=myWin, text=instrText, font='SimHei')
tex.draw()
myWin.flip()
kb.start()
kb.waitKeys(keyList=['space'], waitRelease=True)
kb.stop()
myWin.flip()


# do it!!!
#  =========== main experiment loop ========
for trial in trials:
    # show fixation
    showFixation()
    # add 1000ms delay while calculating stim
    ISI = clock.StaticPeriod(screenHz=fps)
    ISI.start(delayDur)  # start a period of 0.5s
    if trial['dirRange'] == 0: # coherent dots 
        showFun = partial(showCohDots, dir=trial['direction'])
    elif trial['dirRange'] == 320: # chaos dots 
        showFun = partial(showChaosDots, XYpos=computeChaosPos(dir=trial['direction']))
    ISI.complete()  # finish the delay period

    # show the motion stimulus and get RT and choice
    rt, cho = showFun()

    # save data for this trial
    trial.addData('RT', rt)
    trial.addData('choice', cho)
    trial.addData('correct', 1 if trials.data['choice'][trials.thisIndex]==trial['direction'] else 0)


# ====cleanup and save data to csv======
if wantSave: # save data
    # we want to save direction, stimType, RT, choice into a CSV file
    fileName = strftime('%Y%m%d%H%M%S', localtime())
    fileName = f'{fileName}_{subjID}'

    # Save more information into a numpy file 
    expInfo = '''
        direction: -1,left; 1, right \n
        dirRange: 0, coherent dots; 320, chaos dots \n
        choice: -1, left; 1, right \n
        RT in secs related to onset of the motion stimulus
        correct: 1, correct; 0, wrong
    '''
    # create a result dict
    trials.extraInfo={
        'subjID': subjID,
        'time': strftime('%Y-%m-%d-%H-%M-%S', localtime()),
        'expInfo': expInfo,
    }
    trials.saveAsExcel(fileName, sheetName='rawData') # save data as excel
    trials.saveAsPickle(fileName) # save data as pickle

