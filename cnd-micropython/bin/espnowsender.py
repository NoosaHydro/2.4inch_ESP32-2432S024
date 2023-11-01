import network
import espnow

# NOTE!: Need to check if this still works when wifi devices are connected using different radio channels

# A WLAN interface must be active to send()/recv()
sta = network.WLAN(network.STA_IF)  # Or network.AP_IF
sta.active(True)
sta.disconnect()      # For ESP8266

e = espnow.ESPNow()
e.active(True)
#\xbb\xbb\xbb\xbb\xbb\xbb'   # MAC address of peer's wifi interface
peer = b'\xff\xff\xff\xff\xff\xff' # broadcast mac address to all esp32's (not esp8266)
e.add_peer(peer)      # Must add_peer() before send()

e.send(peer, "Starting...")
for i in range(100):
    e.send(peer, str(i)*20, True) # Supposedly capable of 89250bytes/sec
e.send(peer, b'end')
