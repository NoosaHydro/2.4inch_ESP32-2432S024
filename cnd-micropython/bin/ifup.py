if 1:
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
