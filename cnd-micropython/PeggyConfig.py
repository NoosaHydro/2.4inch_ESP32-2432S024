import network, socket, json, time, random,os, gc, io
import uasyncio, usocket
from uasyncio import core

gc.threshold(50000) # setup garbage collection
html_file = open('index_min.html','r')
html = html_file.read()
html_file.close()
cred_out = "PC_CREDENTIALS"
class PeggyConfig:
    #### PRIVATE ####
    def __init__(self, essid=None, save_credentials=True, pw_protected=False, pw="temp1234"):
        self.sta_if = network.WLAN(network.STA_IF)
        self.ap_if = network.WLAN(network.AP_IF)

        if essid is None:
            essid = "PeggyConfig_" + str(random.randint(0,255))

        self.essid = essid
        self.dns_server = None
        self.http_server = None
        self.ip = None
        self.socket = None
        self.server_port = 80
        self.dns_port = 53
        self.server_host = "0.0.0.0"
        self.save_credentials = save_credentials
        self.available_connections = []
        self.enable_pw = pw_protected
        self.pw = pw
        self.success = False
        self.sta_if.active(False)
    
    def _init_ap(self):
        self.ap_if.active(True)
        time.sleep(0.5)
        if self.enable_pw:
            self.ap_if.config(essid=self.essid, authmode=network.AUTH_WPA_WPA2_PSK, password=self.pw) 
        else:
            self.ap_if.config(essid=self.essid, authmode=network.AUTH_OPEN)
        self.ip = str(self.ap_if.ifconfig()[0])
        print("Hosting AP: " + self.essid)

    def _dinit_ap(self):
        self.ap_if.active(False)

    def _do_scan(self):
        self.available_connections = []
        self.sta_if.active(True)
        time.sleep(0.5)
        wifi_near = self.sta_if.scan()
        for conn in wifi_near:
            if (conn[0] == b'') or (conn[0].decode() == self.essid):
                continue
            self.available_connections.append(conn[0].decode('utf-8'))
            
    def _do_connect(self, ssid, pw):
        attempt = 0
        try:
            if self.sta_if.active() and self.sta_if.isconnected():
                self.sta_if.disconnect()
                time.sleep(0.5)
            
            self.sta_if.active(True)
            time.sleep(0.5)
            self.sta_if.connect(ssid,  pw)
            while not self.sta_if.isconnected():
                if attempt > 15:
                    self.sta_if.active(False)
                    time.sleep(0.5)
                    return False
                else:
                    time.sleep(1)
                    attempt = attempt + 1
                    pass
            return True
        except:
            self.sta_if.active(False)
            time.sleep(0.5)
            return False

    async def _dns_handler(self, socket, ip_address):
        while True:
            try:
                gc.collect()
                yield uasyncio.core._io_queue.queue_read(socket)
                request, self.client = socket.recvfrom(256)
                response = request[:2] # request id
                response += b"\x81\x80" # response flags
                response += request[4:6] + request[4:6] # qd/an count
                response += b"\x00\x00\x00\x00" # ns/ar count
                response += request[12:] # original request body
                response += b"\xC0\x0C" # pointer to domain name at byte 12
                response += b"\x00\x01\x00\x01" # type and class (A record / IN class)
                response += b"\x00\x00\x00\x3C" # time to live 60 seconds
                response += b"\x00\x04" # response length (4 bytes = 1 ipv4 address)
                response += bytes(map(int, ip_address.split("."))) # ip address parts
                socket.sendto(response, self.client)
            except Exception as e:
                print(e)
                uasyncio.sleep(1)
                
    async def _web_server(self, reader, writer):
        try:
            gc.collect()
            data = await reader.read(-1)
            message = data.decode()
            if len(message) > 0:
                response = 'HTTP/1.1 200 OK\r\n\r\n'
                if 'GET /AvailableWifi HTTP/1.1' in message:
                    self._do_scan()
                    response += ";".join(self.available_connections)
                elif 'POST /dataIn HTTP/1.1\r\n' in message:
                    request = io.BytesIO(message)
                    contentLength = 0
                    while True:
                        line = request.readline()
                        line_str = str(line)
                        if line_str.find('Content-Length:') != -1:
                            clStart = int(line_str.find('Content-Length:'))
                            clEnd = len(line_str)-5
                            contentLength = int(line_str[clStart+16:clEnd])
                        if (not line or line == b'\r\n') and (contentLength > 0):
                            data = request.read(contentLength)
                            credentials = json.loads(data)
                            self.success = self._do_connect(credentials["SSID"], credentials["PASSWORD"])
                            response = (f"HTTP/1.1 {200} {self.success}\r\n\r\n".encode("ascii"))
                            if self.success and self.save_credentials:
                                file = open(cred_out,'w')
                                file.write(data)
                                file.close()    
                            break
                else:
                    response += html

                yield from writer.awrite(response)

                yield from writer.aclose()
            time.sleep(2)
            if self.success:
                self._clean_up()
        except Exception as e:
            print(e)

    def _run_catchall(self):
        self.socket = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM)
        self.socket.setblocking(True)
        self.socket.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1)
        self.socket.bind(usocket.getaddrinfo(self.ip, self.dns_port, 0, usocket.SOCK_DGRAM)[0][-1])

        self.dns_server  = uasyncio.get_event_loop()
        self.dns_server.create_task(self._dns_handler(self.socket, self.ip))

    def _run_server(self):
        self.http_server = uasyncio.get_event_loop()
        self.http_server.create_task(uasyncio.start_server(self._web_server, self.server_host,  self.server_port))
        self.http_server.run_forever()
        self.http_server.close()
        
    def _clean_up(self):
        try:
            self._dinit_ap()
            self.dns_server.stop()
            self.socket.close()
            self.http_server.stop()
        except Exception as e:
            print(e)

    #### PUBLIC ####
    def doConfig(self):
        self._init_ap()
        self._run_catchall()
        self._run_server()
        return self.success

    def doConnect(self):
        try:
            if cred_out in os.listdir():
                f = open(cred_out, "r")
                credentials = json.loads(f.read())
                f.close()
                return self._do_connect(credentials['SSID'], credentials['PASSWORD'])
            else:
                return False
        except Exception as e:
            print(e)
