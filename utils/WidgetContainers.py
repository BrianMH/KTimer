"""
WidgetContainers.py

The main file got too big and these only really serve to be encapsulating classes for particular tk
interfaces, so they will get pushed here as all of them serve a very similar purpose.
"""
import tkinter as tk
from PIL import ImageTk, Image

class Timer():
    """
        Creates a pseudo-control panel for timer widgets. Encapsulates them so that properties can be accessed
        easily and also gives them an optional string ID which can be used to identify specific timers.

        This method can take into account multiple times, but in order to do so will need to be provided a
        function that takes in no arguments and returns the appropriate indexer at any given moment.
    """
    def __init__(self, root: tk.Tk, timerStr: tk.StringVar, timerLab: tk.Label, initTime: list[int], redTime: int, autoReset: bool,
                 indSelector: callable):
        # Save our values which will be used for the timer processes
        self.timString = timerStr
        self.timLab = timerLab
        self.initTime = initTime
        self.redTime = redTime
        self.autoReset = autoReset
        self.indSelector = indSelector
        self.root = root

        # Our warning timer allows us to count down from 60s while maintaining the current timer underneath
        self.isWarning = False
        self.warningTime = 60

        # Holds our next callback's ID to potentially allow us to reset it
        self.nextCallback = None

        # We can associate callbacks outisde of here since we are constantly updating values
        self.zeroCallback = None
        self.calledFlag = False

        # And use this to be able to check whether the timer is currently running
        self.intTimer = 0
        self.prevTimer = -1
        self.timerLock = False      # used to prevent addTime from being added while memorizing old timer
        self.isRunning = False

        # And some class constants to be used later
        self.RED_COLOR = "red"
        self.BLACK_COLOR = "black"

    def resetTimer(self) -> None:
        """
            Starts the timer if it is not already running, and, if it is, simply resets it.
        """
        # if a process is already under way, we need to remove it so that the timer
        # properly counts the next second
        if self.nextCallback is not None:
            self.root.after_cancel(self.nextCallback)
            self.isRunning = False

        # reset time
        self.intTimer = self.initTime[self.indSelector()]
        self.render()

        # and make sure the timer is running if it's not
        if not self.isRunning:
            self.isRunning = True
            self.nextCallback = self.root.after(1000, self.updateTimer)

    def updateTimer(self) -> None:
        """
            Decrements the timer time by 1 second and updates the timer color 
        """
        # Reset if at 0 and auto-reset is enabled
        if self.intTimer == 0:
            if self.autoReset:
                self.resetTimer()
                self.calledFlag = False
        
            # run our zero callback only once
            if not self.calledFlag and self.zeroCallback:
                self.zeroCallback()
                self.calledFlag = True
            
            return
        
        # Otherwise simply decrement and change the label as necessary
        if self.isWarning:
            self.warningTime -= 1
            if self.intTimer > 60:
                self.intTimer -= 1
        else:
            self.intTimer -= 1
        self.render()

        # If previous time is no longer relevant, then remove the timer lock
        if self.timerLock and self.intTimer <= self.prevTimer:
            self.prevTimer = -1
            self.timerLock = False

        # And continue running this on a loop
        self.nextCallback = self.root.after(1000, self.updateTimer)

    def addTime(self, addTime: int) -> None:
        """
            Adds time to the timer. Does not memorize previous state like the
            apply/remove functions do.
        """
        # avoid writing when timer is locked
        if self.timerLock:
            return

        if self.nextCallback is not None:
            self.root.after_cancel(self.nextCallback)
        
        # Then just add the time and continue
        self.intTimer += addTime
        self.render()
        self.nextCallback = self.root.after(1000, self.updateTimer)

    def associateZeroTimerCallback(self, callback: callable, *args, **kwargs) -> None:
        """
            Allow a timer to have a certain callback executed the moment the timer reaches 0.
        """
        self.zeroCallback = lambda : callback(*args, **kwargs)

    def render(self) -> None:
        """ Redraws the timer"""
        if self.intTimer <= self.redTime or self.isWarning:
            self.timLab['fg'] = self.RED_COLOR
        else:
            self.timLab['fg'] = self.BLACK_COLOR

        if self.isWarning:
            self.timString.set("{:>2}".format(self.warningTime))
        else:
            self.timString.set("{:>2}".format(self.intTimer))

    def isLocked(self) -> bool:
        return self.timerLock
    
    def swapToWarning(self) -> None:
        """ Swaps the current timer display to the warning timer. """
        self.warningTime = 60
        self.intTimer = 60
        self.isWarning = True
        self.render()

    def swapToNormal(self) -> None:
        """ Disables warning time and presents the normal timer again """
        self.isWarning = False
        self.render()

    ############# PHASE CHECK FUNCTIONS #############
    def applyExtraTime(self, newTime: int) -> None:
        """ Applies extra time to the timer in seconds. Returns the incremented amount passed. """
        # If we have already added extra time, prevent us from doing it again
        if self.timerLock:
            return

        # First we want to reset the callback at this point so as get an accurate measure
        if self.nextCallback is not None:
            self.root.after_cancel(self.nextCallback)

        # We can memorize our previous location in case we need to remove the extra time
        self.prevTimer = self.intTimer

        # And then we can increment the timer by the requested amount of time
        self.intTimer += newTime
        self.timerLock = True
        self.render()
        self.nextCallback = self.root.after(1000, self.updateTimer)

        return newTime

    def removeExtraTime(self) -> None:
        """ If any additional time exists from what was added above, forces the timer to go back
            to its previous state (without any additional time). If all additional time has
             elapsed, then nothing is done. Returns the time differential. """
        if self.prevTimer >= self.intTimer:
            return
        
        # Otherwise pause our callback and return to the previous time before continuing
        if self.nextCallback is not None:
            self.root.after_cancel(self.nextCallback)
        
        # And then continue the timer
        differential = self.intTimer - self.prevTimer
        self.intTimer = self.prevTimer
        self.render()
        self.nextCallback = self.root.after(1000, self.updateTimer)
        self.timerLock = False

        return differential

class DeviceCounterWidget():
    """
        Like the timers, we encapsulate the four dots that represents the devices to make things easier
        for us. This will control the view and also allow us to bind a particular event using a 
        stringvar's trace method as a callback source.
    """
    def __init__(self, dotLabels: list[tk.Label], initDeviceCnt: int = 0):
        # image sources
        self.dotState = {0 : ImageTk.PhotoImage(Image.open("./resources/emptyDot.png")),
                         1 : ImageTk.PhotoImage(Image.open("./resources/redDot.png"))}

        # widget intrinsics
        self.curDeviceCnt = initDeviceCnt
        self.deviceStates = [1]*self.curDeviceCnt + [0]*(len(dotLabels)-self.curDeviceCnt)
        self.deviceLabels = dotLabels
        self.maxDeviceCallbackE = None
        self.maxDeviceCallbackL = None

        # finalize using a re-render
        self.forceRender()
    
    def incrementDevices(self):
        """ Increases the number of active devices by 1. """
        # Ignore if at max capacity already
        if self.curDeviceCnt == len(self.deviceStates):
            return
        
        # We can change only the single device that was adjusted
        self.deviceStates[self.curDeviceCnt] = 1
        self.deviceLabels[self.curDeviceCnt].configure(image = self.dotState[1])
        self.curDeviceCnt += 1

        # And run our callback if we just touched max device count
        if self.curDeviceCnt == len(self.deviceStates):
            self.maxDeviceCallbackE()
    
    def decrementDevices(self):
        # Ignore if at minimum capacity already
        """ Decreases the number of active devices by 1 """
        if self.curDeviceCnt == 0:
            return
        elif self.curDeviceCnt == len(self.deviceStates):
            self.maxDeviceCallbackL()
        
        # We can change only the single device that was adjusted
        self.curDeviceCnt -= 1
        self.deviceStates[self.curDeviceCnt] = 0
        self.deviceLabels[self.curDeviceCnt].configure(image = self.dotState[0])
    
    def forceRender(self) -> None:
        """ Forces tkinter to re-render the dot widget in its entirety (including non-changing objects) """
        for devInd, devLabel in enumerate(self.deviceLabels):
            devLabel.configure(image = self.dotState[self.deviceStates[devInd]])

    def associateMaxDeviceCallback(self, entryCallback: callable, leaveCallback: callable) -> None:
        """ Once the max number of devices has been reached or is no longer reached, executes a callback only 
        once until the device counter has been changed beyond the triggers."""
        self.maxDeviceCallbackE = entryCallback
        self.maxDeviceCallbackL = leaveCallback

class PhaseImageWidget():
    """
        This time we control the image that represents the current phase of the boss. This widget is
        entirely controlled by the overlay and this class only servers to encapsulate the methods
        that will be used to alter the state of the widget.
    """
    def __init__(self, master, phaseLabel: tk.Label, curPhase: int = 0):
        # constant for the image itself
        self.IMG_PADDING = 2
        self.PHASE_IMGS = ["./resources/2-1.png",
                           "./resources/2-2.png",
                           "./resources/2-3.png",
                           "./resources/2-4.png",
                           "./resources/2-5.png"]

        # First store our resources for use later
        self.curPhase = curPhase
        self.curLabel = phaseLabel
        self.root = master

        # And load all of our images since we will be using them all eventually
        self.sources, self.imageRefs = self.loadResources(self.PHASE_IMGS)
        self.forceRender()

    def loadResources(self, inSrcs: list[str]) -> list[ImageTk.PhotoImage]:
        """ Takes in a list of image sources and loads all of them into PhotoImage widgets for later use. """
        sourceImg = list()
        thumbImg = list()

        for src in inSrcs:
            sourceImg.append(Image.open(src))
            phaseThumb = sourceImg[-1].copy()
            phaseThumb.thumbnail((self.root.width - 2*self.IMG_PADDING, sourceImg[-1].size[1]))
            thumbImg.append(ImageTk.PhotoImage(phaseThumb))
        
        return sourceImg, thumbImg

    def resetPhase(self, newPhase: int) -> None:
        """
            Resets the image to represent the phase that is currently being observed.
        """
        self.curLabel.configure(image = self.imageRefs[newPhase])
        self.curPhase = newPhase

    def forceRender(self) -> None:
        """
            Forces the widget to re-render the image that represents the current phase.
            This can be due to the window status changing.
        """
        newThumbs = list()
        for src in self.sources:
            newThumbs.append(src.copy())
            newThumbs[-1].thumbnail((self.root.width - 2*self.IMG_PADDING, src.size[1]))

        # And replace all the thumbnails with the new size
        self.imageRefs = [ImageTk.PhotoImage(thumb) for thumb in newThumbs]
        self.curLabel.configure(image = self.imageRefs[self.curPhase])