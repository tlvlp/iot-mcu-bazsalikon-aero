#import webrepl
#import webrepl_setup
import esp
import gc

esp.osdebug(None)       # turn off vendor O/S debugging messages
esp.osdebug(0)          # redirect vendor O/S debugging messages to UART(0)
gc.enable()             # enable automatic garbage collection

