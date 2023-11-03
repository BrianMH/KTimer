"""
    KalosTimer.py

    The entry point for the timer program. The goal of this program is to first set up a GUI that makes it 
    easy to interpret timers, but also make it much easier to manage timers by associating certain
    keypresses with given timer activations/resets/etc.

    Just keep in mind that while numpad selections could have been valid, it's not worth considering because
    MS itself doesn't quite act properly when it comes to keypad inputs.
"""
# GUI stuff
import tkinter as tk
import tkinter.font as tkFont
from PIL import ImageTk, Image

# Keyboard listener nonsense
from utils import ModKeyListener

class App(tk.Tk):
    """
        The main window for the app. This will only hold the available settings options and allow the user
        to initialize the overlay for use.
    """
    def __init__(self, * , defalultBG = "#999999"):
        # Initialize our window
        tk.Tk.__init__(self)
        self["bg"] = defalultBG
        self.nhFont = tkFont.Font(self, family = "Helvetica", size = 12)
        self.headerFont = tkFont.Font(self, family = "Helvetica", size = 30)

        # Initialize our class constants
        self.expectedHotkeys = ["Start Timers", "Begin Check", "Fail Check", "10s Bind", "15s Bind",
                        "Clear Device", "Reset Breath", "Reset Dive", "Reset Laser", "Reset Arrows",
                        "Reset Bombs", "Force FMA"]
        self.expectedArgs = ["Device Timer", "Laser Timer", "Arrow Timer",
                             "FMA Timer", "Breath Timers", "Bomb Timer",
                             "Dive Timer"]
        self.expArgsDefs = ["60", "15", "15", "150", "60, 45, 20, 20", "10", "20"]

        # Initialize some class variables that will be passed to our overlay eventually
        self.storedHotkeys = {argName:None for argName in self.expectedHotkeys}

        # Creat the GUI now
        self.generateGUI()

        # And change all backgrounds to match the overall window view
        self.changeColor(self["bg"])

        # And associate the overlay argument passing to the bottom button
        self.startOverlayButton.bind("<Button-1>", self.executeOverlay)

        # We will also need our key listener to be able to determine what keys we want to hotkey
        self.listenerClass = ModKeyListener.ModKeyListener(debugFlag = True)

    def recordHotkey(self, topLevelName: str) -> None:
        """
            Opens a new top-level window that tells us what key combination was given to the program.

            The key is stored inside the class in self.storedHotkeys[topLevelName].
        """
        tempHKWindow = tk.Toplevel(self, bg = self["bg"])
        tk.Label(tempHKWindow, text = "Setting Hotkey for ...".format(topLevelName), font = self.nhFont).pack(side = "top")

        # start a new listener which will send a callback to set the hotkey for this window
        listenerSID = self.listenerClass.startNewCapture()
        

    def generateGUI(self) -> None:
        """
            Gui creation is a bit of an eyesore so it will be hidden in here. Since this GUI in particular is not that
            complex, it will all remain inside of this function.
        """
        # This window should only contain usage information and hotkey settings
        self.introFrame = tk.Frame(self, relief = "groove", borderwidth = 1)
        self.infoLabel = tk.Label(self.introFrame, text = "Kalos Timer Configs", font = self.headerFont)
        self.infoLabel.pack(side = "top")
        self.descrLabel = tk.Label(self.introFrame, text = "Set initial timers and hotkeys in this box.", font = self.nhFont)
        self.descrLabel.pack(side = "bottom")
        self.introFrame.grid(column = 0, columnspan = 2, row = 0, sticky = "WE")

        # Allow the setting of initial timers on the left side
        self.defaultsFrame = tk.Frame(self)
        tk.Label(self.defaultsFrame, text = "Default Timers", font = self.nhFont).grid(column = 0, columnspan = 2, row = 0)
        self.entryElems = dict()
        for argInd, argName in enumerate(self.expectedArgs):
            curLabel = tk.Label(self.defaultsFrame, text = argName+":", font = self.nhFont)
            curLabel.grid(column = 0, columnspan = 1, row = 1 + argInd, rowspan = 1, ipadx = 4)
            self.entryElems[self.expectedArgs[argInd]] = tk.StringVar(self.defaultsFrame, value = self.expArgsDefs[argInd])
            curEntry = tk.Entry(self.defaultsFrame, textvariable = self.entryElems[self.expectedArgs[argInd]], font = self.nhFont,
                                    width = 10)
            curEntry.grid(column = 1, columnspan = 1, row = 1 + argInd, rowspan = 1, ipadx = 4)
        self.defaultsFrame.grid(column = 0, row = 1, sticky = "W")

        # And the hotkeys on the right side
        self.hotkeyFrame = tk.Frame(self)
        tk.Label(self.hotkeyFrame, text = "Default Hotkeys", font = self.nhFont).grid(column = 0, columnspan = 2, row = 0)
        self.hkButtons = dict() # used to store the buttons for action adjustment
        for argInd, argName in enumerate(self.expectedHotkeys):
            curLabel = tk.Label(self.hotkeyFrame, text = argName, font = self.nhFont)
            curLabel.grid(column = 0, columnspan = 1, row = 1 + argInd, rowspan = 1, ipadx = 4)
            self.hkButtons[self.expectedHotkeys[argInd]] = tk.Button(self.hotkeyFrame, text = "Set", font = self.nhFont, 
                                                                     command = lambda : self.recordHotkey(self.expectedHotkeys[argInd]))
            self.hkButtons[self.expectedHotkeys[argInd]].grid(column = 1, columnspan = 1, row = 1 + argInd, rowspan = 1, ipadx = 4)
        self.hotkeyFrame.grid(column = 1, row = 1, sticky = "E")

        # And finally a button to ultimately start the overlay with the given parameters
        self.buttonFrame = tk.Frame(self, pady = 4)
        self.startOverlayButton = tk.Button(self.buttonFrame, text = "Start Overlay", font = self.nhFont)
        self.startOverlayButton.pack(side = "bottom", fill = "x", expand = False)
        self.buttonFrame.grid(column = 0, columnspan = 2, row = 2, sticky = "WE", padx = 10)

    def executeOverlay(self, event):
        """
            Starts the overlay along with all the relevant arguments passed to the window.
        """
        # first we need to collect the arguments that were given to the window to pass into the overlay
        expectedArgOrder = ["device", "laser", "arrow", "fma", "breath", "bomb", "dive"]
        initTimeArgs = {argName:[int(val) for val in self.entryElems[self.expectedArgs[argInd]].get().split(",")] for argInd, argName in enumerate(expectedArgOrder)}

        # And combine that with some pre-specified defaults to package into a full argument sequence
        redTimeArgs = {"device": 10, 
                      "laser": 5,
                      "arrow": 5,
                      "fma": 20,
                      "breath": 5,
                      "bomb": 5,
                      "dive": 5}
        autoResetArgs = {"device": True,
                         "laser": True,
                         "arrow": True,
                         "bomb": True}
        fullArgs = {argName:{"initTime": initTimeArgs[argName],
                             "redTime": redTimeArgs[argName],
                             "autoReset": autoResetArgs.get(argName, False)} for argName in expectedArgOrder}

        # And then pass these collected values to the overlay
        self.overlay = Overlay(fullArgs)

    def changeColor(self, color, container=None):
        """
            Revursively changes the background colors of all widgets within a given container.
        """
        if container is None:
            container = self  # set to root window
        container.config(bg=color)
        for child in container.winfo_children():
            if child.winfo_children():
                self.changeColor(color, child)
            elif type(child) is tk.Label:
                child.config(bg=color)

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

        # And use this to be able to check whether the timer is currently running
        self.intTimer = 0
        self.isRunning = False

        # And some class constants to be used later
        self.RED_COLOR = "red"
        self.BLACK_COLOR = "black"

    def resetTimer(self) -> None:
        """
            Starts the timer if it is not already running, and, if it is, simply resets it.
        """
        # reset time
        self.intTimer = self.initTime[self.indSelector()]
        self.timLab['fg'] = self.BLACK_COLOR
        self.timString.set("{:>2}".format(self.intTimer))

        # and make sure the timer is running if it's not
        if not self.isRunning:
            self.isRunning = True
            self.root.after(1000, self.updateTimer)

    def updateTimer(self) -> None:
        """
            Decrements the timer time by 1 second and updates the timer color 
        """
        # Reset if at 0 and auto-reset is enabled
        if self.intTimer == 0 and self.autoReset:
            self.resetTimer()
            self.root.after(1000, self.updateTimer)
            return
        elif self.intTimer == 0:
            return # do nothing if autoreset is not enabled
        
        # Otherwise simply decrement and change the label as necessary
        self.intTimer -= 1
        self.timString.set("{:>2}".format(self.intTimer))
        if self.intTimer <= self.redTime:
            self.timLab['fg'] = self.RED_COLOR

        # And continue running this on a loop
        self.root.after(1000, self.updateTimer)

class deviceCounterWidget():
    """
        Like the timers, we encapsulate the four dots that represents the devices to make things easier
        for us. This will control the view and also allow us to bind a particular event using a 
        stringvar's trace method as a callback source.
    """
    def __init__(self):
        raise NotImplementedError
    
    def resetPhase(self):
        raise NotImplementedError

class phaseImageWidget():
    """
        This time we control the image that represents the current phase of the boss. This widget is
        entirely controlled by the overlay and this class only servers to encapsulate the methods
        that will be used to alter the state of the widget.
    """
    def __init__(self):
        raise NotImplementedError

    def resetPhase(self):
        """
            Resets the image to represent the phase that is currently being observed.
        """
        raise NotImplementedError

class Overlay(tk.Toplevel):
    """
        Controls the kalos timer overlay. This contains all visuals regarding the timers and the
        phase controller. All keybinds are handled through external callbacks that affect the overlay
        (Note that the callbacks are registered to a keyboard listener, not through the tk event loop).

        This also has contains all the controls for the timers and expects the user inputs to be
        passed in from the main window for processing.

        The timerArgs argument expects a dictionary that maps each one of the known timer types: 
            ["device", "laser", "arrow", "fma", "breath", "bomb", "dive"]

        That maps to the following expected input argument values
            (initTime, redTime, autoReset)
    """
    ALL_TIMERS = ["device", "laser", "arrow", "fma", "breath", "bomb", "dive"]
    
    def __init__(self, timerArgs: dict, *args, **kwargs):
        # Set some basic options for our new top level window
        tk.Toplevel.__init__(self, *args, **kwargs)

        # These are properties of the boss itself that may be modified by our hotkeys later
        self.curPhaseInd = 0
        self.deviceStates = ["inactive", "inactive", "inactive", "inactive"]

        # Then declare some constants that we will use later
        self.IMG_PADDING = 2
        self.MULT_PHASE_TIMER = {"breath"}
        self.PHASE_IMGS = ["./resources/2-1.png",
                           "./resources/2-2.png",
                           "./resources/2-3.png",
                           "./resources/2-4.png"]
        self.dotState = {"inactive" : ImageTk.PhotoImage(Image.open("./resources/emptyDot.png")),
                         "active" : ImageTk.PhotoImage(Image.open("./resources/redDot.png"))}
        self.timFont = tkFont.Font(self, family = "Helvetica", size = 40)
        self.dscrptFont = tkFont.Font(self, family = "Helvetica", size = 15)

        # Set up the UI now and encapsulate returned objects
        timerRefs, self.imageRefs = self.setupGUI()
        self.timObjs = self.encapsulateTimers(timerRefs, timerArgs)

        for key in self.timObjs.keys():
            self.timObjs[key].resetTimer()

    def encapsulateTimers(self, allTimers: dict[str, tuple[tk.StringVar, tk.Label]], timerArgs: dict) -> dict[str, Timer]:
        """
            Takes in our timers as tuples of the string time representations and labels along with the
            passed in user input specifications and creates an encapsulated timer that is much easier
            to move around the class.
        """
        objTimers = dict()
        for key in allTimers.keys():
            objTimers[key] = Timer(self, allTimers[key][0], allTimers[key][1], 
                                   timerArgs[key]["initTime"], timerArgs[key]["redTime"], timerArgs[key]["autoReset"],
                                   indSelector = (lambda : self.getCurrentPhase()) if key in self.MULT_PHASE_TIMER else (lambda : 0))
            
        return objTimers

    def setupGUI(self) -> None:
        """
            The main function that sets up all UI elements and encapsulates all functional return values 
            along with their potentially bound functions.
        """
        ######  Window Properties ########
        self.geometry("400x335")
        self.width, self.height = 400, 335
        self['bg'] = "#999999"
        self.wm_attributes("-topmost", True)
        self.overrideredirect(True) # prevents the WM from creating its decorations on this window

        ######  Widget organization ########
        # First set up our hp meter on top with the divider image
        imageObject = self.setupPhaseImageLabel()

        # Then we want to set up our next row which includes the device timer and the laser/arrow timers
        laTimers, dotObjects = self.setupDevicesRow()

        # Next row includes the FMA and breath timers
        fbTimers = self.setupFMABreathRow()

        # And finally we can deal with the bomb and dive timers
        bdTimers = self.setupBombDiveRow()

        # Set up some proper colors so they are consistent across widgets
        self.changeColor(self['bg'])

        # Bind specific actions to certain functions
        self.bind("<ButtonPress-1>", self.startMove)
        self.bind("<ButtonRelease-1>", self.stopMove)
        self.bind("<B1-Motion>", self.moveWindow)
        self.bind("<Configure>", self.resize)

        return ({"device": laTimers["device"],
                "laser": laTimers["laser"],
                "arrow": laTimers["arrow"],
                "fma": fbTimers["fma"],
                "breath": fbTimers["breath"],
                "bomb": bdTimers["bomb"],
                "dive": bdTimers["dive"]},
                {"phaseRefs" : imageObject,
                 "dotRefs" : dotObjects})

    def setupPhaseImageLabel(self) -> tuple[ImageTk.PhotoImage, tk.Label]:
        """
            Sets up the phase display for kalos. Returns the PhotoImage object that is rendered by
            the label.
        """
        hpFrame = tk.Frame(self)
        curPhaseImg = Image.open(self.PHASE_IMGS[self.curPhaseInd]) # need to save image to view
        curPhaseImgThumb = curPhaseImg.copy()
        curPhaseImgThumb.thumbnail((self.width - 2*self.IMG_PADDING, curPhaseImg.size[1]))
        frameModImg = ImageTk.PhotoImage(curPhaseImgThumb)
        hpImageLab = tk.Label(hpFrame, image = frameModImg)
        hpImageLab.pack(fill = "both", expand = True)
        hpFrame.grid(column = 0, columnspan = 4, row = 0)

        return frameModImg, hpImageLab

    def setupDevicesRow(self) -> tuple[dict[str, tuple[tk.StringVar, tk.Label]], list[tk.Label]]:
        """
            Sets up the device row and returns both the elements used to keep the timers
            and the widgets used to represents the devices.
        """
        deviceFrame = tk.Frame(self, relief = "groove", borderwidth = 1)
        curDeviceTime = tk.StringVar(deviceFrame, value = "--")
        curDeviceLabel = tk.Label(deviceFrame, textvariable = curDeviceTime, font = self.timFont)
        curDeviceLabel.pack(side = "top", fill = "x", expand = True)
        descriptionFrame = tk.Frame(deviceFrame)
        deviceDots = list()
        for devInd in range(4):
            deviceDots.append(tk.Label(descriptionFrame, image = self.dotState[self.deviceStates[devInd]]))
            deviceDots[-1].pack(side = "left", fill = "y", expand = False)
        devDescriptLabel = tk.Label(descriptionFrame, text = "Devices", font = self.dscrptFont)
        devDescriptLabel.pack(side = "right", fill = "y", expand = True)
        descriptionFrame.pack(side = "bottom", fill = "x", expand = True)

        deviceFrame.grid(column = 0, columnspan = 3, row = 1, sticky = "WE")

        # laser/arrow timers
        laFrame = tk.Frame(self, relief = "groove", borderwidth = 1) # main frame

        laserFrame = tk.Frame(laFrame) # laser partition
        curLaserTime = tk.StringVar(laserFrame, value = "--")
        curLaserLab = tk.Label(laserFrame, textvariable = curLaserTime, font = self.timFont)
        curLaserLab.pack(side = "top", fill = "y", expand = True)
        lDescriptLabel = tk.Label(laserFrame, text = "Lasers", font = self.dscrptFont)
        lDescriptLabel.pack(side = "bottom", fill = "x", expand= True)
        laserFrame.pack(side = "left", fill = "both", expand = True, ipadx = 5)

        arrowFrame = tk.Frame(laFrame) # arrow partition
        curArrowTime = tk.StringVar(laFrame, value = "--")
        curArrowLab = tk.Label(arrowFrame, textvariable = curArrowTime, font = self.timFont)
        curArrowLab.pack(side = "top", fill = "y", expand = True)
        aDescriptLabel = tk.Label(arrowFrame, text = "Arrows", font = self.dscrptFont)
        aDescriptLabel.pack(side = "bottom", fill = "x", expand = True)
        arrowFrame.pack(side = "right", fill = "both", expand = True, ipadx = 5)

        laFrame.grid(column = 3, columnspan = 1, row = 1, sticky = "WE")

        return ({"device": (curDeviceTime, curDeviceLabel),
                 "laser" : (curLaserTime, curLaserLab), 
                 "arrow" : (curArrowTime, curArrowLab)},
                deviceDots)

    def setupFMABreathRow(self) -> dict[str,tuple[tk.StringVar, tk.Label]]:
        """
            Sets up the third row and returns the respective timers and labels.
        """
        # first deal with FMA part
        fmaFrame = tk.Frame(self, relief = "groove", borderwidth = 1)
        curFMATime = tk.StringVar(fmaFrame, value = "--")
        curFMALab = tk.Label(fmaFrame, textvariable = curFMATime, font = self.timFont)
        curFMALab.pack(side = "top", fill = "y", expand = True)
        fmaDescriptLabel = tk.Label(fmaFrame, text = "FMA", font = self.dscrptFont)
        fmaDescriptLabel.pack(side = "bottom", expand = True)
        fmaFrame.grid(column = 0, columnspan = 2, row = 2, sticky = "WE")

        # And then the breath part
        breathFrame = tk.Frame(self, relief = "groove", borderwidth = 1)
        curBreathTime = tk.StringVar(breathFrame, value = "--")
        curBreathLab = tk.Label(breathFrame, textvariable = curBreathTime, font = self.timFont)
        curBreathLab.pack(side = "top", fill = "y", expand = True)
        breathDescriptLabel = tk.Label(breathFrame, text = "Breath", font = self.dscrptFont)
        breathDescriptLabel.pack(side = "bottom", expand = True)
        breathFrame.grid(column = 2, columnspan = 2, row = 2, sticky = "WE")

        return {"fma" : (curFMATime, curFMALab), 
                "breath" : (curBreathTime, curBreathLab)}

    def setupBombDiveRow(self) -> dict[str, tuple[tk.StringVar, tk.Label]]:
        """
            Finally, sets up the fourth row and returns the respective timers and labels
        """
        # like before deal with the bomb part
        self.bombFrame = tk.Frame(self, relief = "groove", borderwidth = 1)
        self.curBombTime = tk.StringVar(self.bombFrame, value = "--")
        self.curBombLab = tk.Label(self.bombFrame, textvariable = self.curBombTime, font = self.timFont)
        self.curBombLab.pack(side = "top", fill = "y", expand = True)
        self.bombDescriptLabel = tk.Label(self.bombFrame, text = "Bombs", font = self.dscrptFont)
        self.bombDescriptLabel.pack(side = "bottom", expand = True)
        self.bombFrame.grid(column = 0, columnspan = 2, row = 3, sticky = "WE")

        # And the diving timer
        self.diveFrame = tk.Frame(self, relief = "groove", borderwidth = 1)
        self.curDiveTime = tk.StringVar(self.diveFrame, value = "--")
        self.curDiveLab = tk.Label(self.diveFrame, textvariable = self.curDiveTime, font = self.timFont)
        self.curDiveLab.pack(side = "top", fill = "y", expand = True)
        self.diveDescriptLabel = tk.Label(self.diveFrame, text = "Dive", font = self.dscrptFont)
        self.diveDescriptLabel.pack(side = "bottom", expand = True)
        self.diveFrame.grid(column = 2, columnspan = 2, row = 3, sticky = "WE")

        return {"bomb" : (self.curBombTime, self.curBombLab), 
                "dive" : (self.curDiveTime, self.curDiveLab)}

    def resize(self, event):
        if(event.widget == self and
            (self.width != event.width or self.height != event.height)):
            self.width, self.height = event.width, event.height

            # resize image on resize
            self.curPhaseImgThumb = self.curPhaseImg.copy()
            self.curPhaseImgThumb.thumbnail((self.width - 2*self.IMG_PADDING, self.curPhaseImg.size[1]))
            self.frameModImg = ImageTk.PhotoImage(self.curPhaseImgThumb)
            self.hpImage.configure(image = self.frameModImg)

            # We can do the same with text potentially
            # TODO: Try text adjustment via ratio differences

    def startMove(self, event):
        self.x = event.x
        self.y = event.y

    def stopMove(self, event):
        self.x = None
        self.y = None

    def moveWindow(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

    def changeColor(self, color, container=None):
        """
            Revursively changes the background colors of all widgets within a given container.
        """
        if container is None:
            container = self  # set to root window
        container.config(bg=color)
        for child in container.winfo_children():
            if child.winfo_children():
                self.changeColor(color, child)
            elif type(child) is tk.Label:
                child.config(bg=color)

    def getCurrentPhase(self) -> int:
        """ Function for retrieving the current phase. (Used in passing current phase values to callbacks.) """
        return self.curPhaseInd

if __name__ == "__main__":
    window = App()
    window.mainloop()