"""
ModKeyLisetener.py

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

        # And then our consts
        self.lInit = lambda lastSid = len(self.listeners): keyboard.hook(self.createGlobalQueueListener(self.keysFound, lastSid))
        self.debug = debugFlag

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
        for key in self.keysFound.keys():
            del self.keysFound[key]

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

# smoke test
if __name__ == "__main__":
    test = ModKeyListener(debugFlag=True)
    test.startNewCapture()

    while(True):
        time.sleep(100000)