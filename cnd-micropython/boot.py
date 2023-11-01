# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import os

def __main__(args):
	num = 10
	if len(args) > 2:
		num = int(args[2])
		print("arg")
	print("main")
	
def ifup():
    print("Activating network")
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect('YOUR_WIFI_SSID_HERE', 'YOUR_PASSWORD_HERE') # this is non-blocking

    print("Starting webrepl")
    import webrepl
    webrepl.start()

    print("Starting IDE web service on http://" + wlan.ifconfig()[0] + "/") # this never works, because non-blocking above (wlan.isconnected())
    import weditor.start


if 'if.up' in os.listdir():
    ifup()
else:
    print("type ifup() t start net and web.  touch /if.up to auto-start at boot")
