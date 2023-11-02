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

# Keyboard nonsense
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
                             "FMA Timer", "Breath Timer", "Bomb Timer",
                             "Dive Timer"]

        # Initialize some class variables that will be passed to our overlay eventually
        self.storedHotkeys = {argName:None for argName in self.expectedHotkeys}

        # Creat the GUI now
        self.generateGUI()

        # And change all backgrounds to match the overall window view
        self.changeColor(self["bg"])

        # And associate the overlay argument passing to the bottom button
        self.startOverlayButton.bind("<Button-1>", self.executeOverlay)

        # We will also need our key listener to be able to determine what keys we want to hotkey
        self.listenerClass = ModKeyListener.ModKeyListener(debug = True)

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
            self.entryElems[self.expectedArgs[argInd]] = tk.StringVar(self.defaultsFrame)
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
        self.overlay = Overlay()

    def changeColor(self, color, container=None):
        if container is None:
            container = self  # set to root window
        container.config(bg=color)
        for child in container.winfo_children():
            if child.winfo_children():
                self.changeColor(color, child)
            elif type(child) is tk.Label:
                child.config(bg=color)

class Overlay(tk.Toplevel):
    """
        Controls the kalos timer overlay. This contains all visuals regarding the timers and the
        phase controller. All keybinds are handled through external callbacks that affect the overlay
        (Note that the callbacks are registered to a keyboard listener, not through the tk event loop).

        This also has contains all the controls for the timers.
    """
    def __init__(self, *args, **kwargs):
        # Set some basic options for our new top level window
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.geometry("400x335")
        self.width, self.height = 400, 335
        self['bg'] = "#999999"
        self.wm_attributes("-topmost", True)
        self.overrideredirect(True) # prevents the WM from creating its decorations on this window

        # These are properties of the boss itself that may be modified by our hotkeys later
        self.curPhaseInd = 0
        self.deviceStates = ["inactive", "inactive", "inactive", "inactive"]

        # Then declare some constants that we will use later
        self.IMG_PADDING = 2
        self.PHASE_IMGS = ["./resources/2-1.png",
                           "./resources/2-2.png",
                           "./resources/2-3.png",
                           "./resources/2-4.png"]
        self.dotState = {"inactive" : ImageTk.PhotoImage(Image.open("./resources/emptyDot.png")),
                         "active" : ImageTk.PhotoImage(Image.open("./resources/redDot.png"))}
        self.timFont = tkFont.Font(self, family = "Helvetica", size = 40)
        self.dscrptFont = tkFont.Font(self, family = "Helvetica", size = 15)

        ######  Widget organization ########
        # First set up our hp meter on top with the divider image
        self.setupPhaseImageLabel()

        # Then we want to set up our next row which includes the device timer and the laser/arrow timers
        self.setupDevicesRow()

        # Next row includes the FMA and breath timers
        self.setupFMABreathRow()

        # And finally we can deal with the bomb and dive timers
        self.setupBombDiveRow()

        # Set up some proper colors so they are consistent across widgets
        self.changeColor(self['bg'])

        # Bind specific actions to certain functions
        self.hpImage.bind("<ButtonPress-1>", self.startMove)
        self.hpImage.bind("<ButtonRelease-1>", self.stopMove)
        self.hpImage.bind("<B1-Motion>", self.moveWindow)
        self.bind("<Configure>", self.resize)

    def setupPhaseImageLabel(self) -> None:
        self.hpFrame = tk.Frame(self)
        self.curPhaseImg = Image.open(self.PHASE_IMGS[self.curPhaseInd]) # need to save image to view
        self.curPhaseImgThumb = self.curPhaseImg.copy()
        self.curPhaseImgThumb.thumbnail((self.width - 2*self.IMG_PADDING, self.curPhaseImg.size[1]))
        self.frameModImg = ImageTk.PhotoImage(self.curPhaseImgThumb)
        self.hpImage = tk.Label(self.hpFrame, image = self.frameModImg)
        self.hpImage.pack(fill = "both", expand = True)
        self.hpFrame.grid(column = 0, columnspan = 4, row = 0)

    def setupDevicesRow(self) -> None:
        self.deviceFrame = tk.Frame(self, relief = "groove", borderwidth = 1)
        self.curDeviceTime = tk.StringVar(self.deviceFrame, value = "--")
        self.curDeviceLabel = tk.Label(self.deviceFrame, textvariable = self.curDeviceTime, font = self.timFont)
        self.curDeviceLabel.pack(side = "top", fill = "x", expand = True)
        self.descriptionFrame = tk.Frame(self.deviceFrame)
        self.deviceDots = list()
        for devInd in range(4):
            self.deviceDots.append(tk.Label(self.descriptionFrame, image = self.dotState[self.deviceStates[devInd]]))
            self.deviceDots[-1].pack(side = "left", fill = "y", expand = False)
        self.devDescriptLabel = tk.Label(self.descriptionFrame, text = "Devices", font = self.dscrptFont)
        self.devDescriptLabel.pack(side = "right", fill = "y", expand = True)
        self.descriptionFrame.pack(side = "bottom", fill = "x", expand = True)

        self.deviceFrame.grid(column = 0, columnspan = 3, row = 1, sticky = "WE")

        # laser/arrow timers
        self.laFrame = tk.Frame(self, relief = "groove", borderwidth = 1) # main frame

        self.laserFrame = tk.Frame(self.laFrame, ) # laser partition
        self.curLaserTime = tk.StringVar(self.laserFrame, value = "--")
        self.curLaserLab = tk.Label(self.laserFrame, textvariable = self.curLaserTime, font = self.timFont)
        self.curLaserLab.pack(side = "top", fill = "y", expand = True)
        self.lDescriptLabel = tk.Label(self.laserFrame, text = "Lasers", font = self.dscrptFont)
        self.lDescriptLabel.pack(side = "bottom", fill = "x", expand= True)
        self.laserFrame.pack(side = "left", fill = "both", expand = True, ipadx = 5)

        self.arrowFrame = tk.Frame(self.laFrame) # arrow partition
        self.curArrowTime = tk.StringVar(self.laFrame, value = "--")
        self.curArrowLab = tk.Label(self.arrowFrame, textvariable = self.curArrowTime, font = self.timFont)
        self.curArrowLab.pack(side = "top", fill = "y", expand = True)
        self.aDescriptLabel = tk.Label(self.arrowFrame, text = "Arrows", font = self.dscrptFont)
        self.aDescriptLabel.pack(side = "bottom", fill = "x", expand = True)
        self.arrowFrame.pack(side = "right", fill = "both", expand = True, ipadx = 5)

        self.laFrame.grid(column = 3, columnspan = 1, row = 1, sticky = "WE")

    def setupFMABreathRow(self) -> None:
        # first deal with FMA part
        self.fmaFrame = tk.Frame(self, relief = "groove", borderwidth = 1)
        self.curFMATime = tk.StringVar(self.fmaFrame, value = "--")
        self.curFMALab = tk.Label(self.fmaFrame, textvariable = self.curFMATime, font = self.timFont)
        self.curFMALab.pack(side = "top", fill = "y", expand = True)
        self.fmaDescriptLabel = tk.Label(self.fmaFrame, text = "FMA", font = self.dscrptFont)
        self.fmaDescriptLabel.pack(side = "bottom", expand = True)
        self.fmaFrame.grid(column = 0, columnspan = 2, row = 2, sticky = "WE")

        # And then the breath part
        self.breathFrame = tk.Frame(self, relief = "groove", borderwidth = 1)
        self.curBreathTime = tk.StringVar(self.breathFrame, value = "--")
        self.curBreathLab = tk.Label(self.breathFrame, textvariable = self.curBreathTime, font = self.timFont)
        self.curBreathLab.pack(side = "top", fill = "y", expand = True)
        self.breathDescriptLabel = tk.Label(self.breathFrame, text = "Breath", font = self.dscrptFont)
        self.breathDescriptLabel.pack(side = "bottom", expand = True)
        self.breathFrame.grid(column = 2, columnspan = 2, row = 2, sticky = "WE")

    def setupBombDiveRow(self) -> None:
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
        if container is None:
            container = self  # set to root window
        container.config(bg=color)
        for child in container.winfo_children():
            if child.winfo_children():
                self.changeColor(color, child)
            elif type(child) is tk.Label:
                child.config(bg=color)

if __name__ == "__main__":
    window = App()
    window.mainloop()