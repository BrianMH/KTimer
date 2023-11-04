"""
ModKeyListener.py

A class that is able to manage the recordings of various listeners. Keep in mind that these listeners do not have any
timers set to them, so the moment a new listener is created it will run until it records any number of modifiers plus
one non-modifier.
"""
import keyboard
import time

class ModKeyListener():
    '''
        Recreates the functionality of a key capturing screen. Essentially waits for an
        indefinite amount of time until a whole key sequence consisting of N modifiers and
        a single non-modifier is seen and is then no longer capturing.
    '''
    def __init__(self, * , debugFlag: bool = False):
        # First set up our class variables
        self.keysFound = dict()
        self.listeners = list()
        self.hotkeyListeners = dict()

        # And then our consts
        self.lInit = lambda : keyboard.hook(self.createGlobalQueueListener(self.keysFound, len(self.listeners)))
        self.debug = debugFlag

    def checkCaptureStatus(self, sid: int) -> bool:
        """ Reports whether or not the capture has terminated (written a value to the keysFound var) """
        return self.keysFound[sid] is not None
    
    def getCapturedKey(self, sid: int) -> str:
        """ Returns a string representation of the captured key config """
        return self.keysFound[sid]

    def startNewCapture(self) -> int:
        """
            Initializes a new capturing mechanism and returns the SID of the listening mechanism.
        """
        self.listeners.append(self.lInit())
        return len(self.listeners)-1

    def removeCaptures(self) -> None:
        """
            Removes any listeners currently active.
        """
        # First use the callback to remove all listeners regardless of state
        for listener in self.listeners:
            keyboard.unhook(listener)

        # then delete all saved keys found
        for key in list(self.keysFound.keys()):
            del self.keysFound[key]

        # And clean the listener list
        self.listeners = list()

    def getKeyCombinations(self) -> dict[int, str]:
        """
            Returns a dictionary representing the found keys along with the sids of the listeners
            that recorded them.
        """
        return self.keysFound.copy()
    
    def getTotalCaptureCount(self) -> int:
        """
            Returns the number of captures that are currently ongoing or have terminated and have
            saved their resposnes.
        """
        return len(self.listeners)

    def createGlobalQueueListener(self, kObj: dict, sid: int = 0) -> callable:
        """ 
            Creates a set that allows us to listen to key combinations that are 
            pressed from the keyboard. This allows us to infer complex key combinations
            that were pressed. Note that it only captures a single key combination into kObj
            and repeated calls must be made in order to capture more.

            In order to ensure that listeners do not overwrite the same variable,
            an sid should be provided to prevent collisions.
        """
        # closure container
        modSet = set()
        nonModKey = None

        # We would like to only register valid combinations where only modifiers and a single
        # non-modifier key can be pressed, so we can set that up here.
        isNonMod = lambda keyEvent: not keyboard.is_modifier(keyEvent.scan_code)

        # Since we created a new object, we should also let our class know of its future
        # availability
        self.keysFound[sid] = None

        def queueModifier(event : keyboard.KeyboardEvent) -> None:
            """
                Takes a keyboard event and appends it to the pressed set if it is a key down
                or removes it on key up.
            """
            # reference adjustment
            nonlocal nonModKey

            # If we have our non-mod key already set, then don't bother capturing anymore
            if nonModKey is not None:
                return

            # manage key ups
            if(event.event_type == keyboard.KEY_UP) and not isNonMod(event):
                modSet.remove(event.name)
            else:
                # and register key downs
                if isNonMod(event):
                    nonModKey = event.name

                    # And add it to our kObj[sid] to note the combination
                    kObj[sid] = "".join((mod+"+" for mod in modSet)) + nonModKey
                    if self.debug:
                        print("Listener (sid:{}) recorded key combination : {}".format(sid, kObj[sid]))
                else:
                    modSet.add(event.name)

        return queueModifier
    
    def createHotkeyCallback(self, hotkey: str, callback: callable) -> None:
        """
            Creates a global callback for a given hotkey and adds the callback to the class
            for potential removal.
        """
        self.hotkeyListeners[hotkey.lower()] = (keyboard.add_hotkey(hotkey.lower(), callback = callback))

    def removeHotkeyListeners(self) -> None:
        """
            Removes all hotkey listeners that are currently active.
        """
        # destroy the listener
        for listener in self.hotkeyListeners.values():
            keyboard.remove_hotkey(listener)

        # And erase all references
        self.hotKeyListeners = dict()

# smoke test
if __name__ == "__main__":
    test = ModKeyListener(debugFlag=True)
    test.startNewCapture()

    while(True):
        time.sleep(100000)