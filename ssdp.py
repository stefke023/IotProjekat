import socket
import time
import struct
from datetime import datetime, timezone, timedelta


class SSDP:
    SSDP_ADDR = "239.255.255.250"
    SSDP_PORT = 1900
    LISTEN_TIME = 30
    INTERVAL = 5

    def __init__(self, st="ssdp:all", mx=3, usn = "ssdp:hos"):
        self.st = st
        self.mx = mx
        self.usn = usn


    def listen(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", self.SSDP_PORT))

        mreq = socket.inet_aton(self.SSDP_ADDR) + socket.inet_aton("0.0.0.0")
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        sock.settimeout(1) 

        st_set = set()
        start = time.time()

        while time.time() - start < self.LISTEN_TIME:
            try:
                data, addr = sock.recvfrom(1024)
                msg = data.decode(errors="ignore")
                

                for line in msg.splitlines():
                    if line.startswith("USN:"):
                        st = line.split(":", 1)[1].strip()
                        st_set.add(st)

            except socket.timeout:
                continue

        sock.close()
        return st_set
    
    def advertise(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

        message = (
            "NOTIFY * HTTP/1.1\r\n"
            f"HOST: {self.SSDP_ADDR}:{self.SSDP_PORT}\r\n"
            "NTS: ssdp:alive\r\n"
            f"ST: {self.st}\r\n"
            f"USN: {self.usn}\r\n"
            "\r\n"
        ).encode("utf-8")

        try:
            while True:
                sock.sendto(message, (self.SSDP_ADDR, self.SSDP_PORT))
                time.sleep(self.INTERVAL)
        except KeyboardInterrupt:
            pass
        finally:
            sock.close()


    def discover(self, st, wait_time = 5):
        ssdp_request = f"""M-SEARCH * HTTP/1.1\r
        HOST: {self.SSDP_ADDR}:{self.SSDP_PORT}\r
        MAN: "ssdp:discover"\r
        MX: {self.mx}\r
        ST: {st}\r
        USER-AGENT: Windows/11 UPnP/1.1 iotProjekat/1.0\r
        CPFN.UPNP.ORG: Stefan-PC\r 
        CPUUID.UPNP.ORG: uuid:550e8400-e29b-41d4-a716-446655440000\r
        \r
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.settimeout(wait_time)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
        
        for i in range(3):
            sock.sendto(ssdp_request.encode("utf-8"), (self.SSDP_ADDR, self.SSDP_PORT))
            time.sleep(0.02)

        devices = []
        try:
            while True:
                data, addr = sock.recvfrom(1024)
                response = data.decode("utf-8", errors="ignore")
                devices.append(response)
        except socket.timeout:
            print("Kraj pretrage.")
        
            
        return devices

    def serve(self, wait_time = 120):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", self.SSDP_PORT))
        mreq = struct.pack("4sl", socket.inet_aton(self.SSDP_ADDR), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        
        start_time = time.time()
        
        while time.time() < start_time + wait_time: 
                data, addr = sock.recvfrom(1024)
                msg = data.decode("utf-8", errors="ignore")
                
                if "M-SEARCH" in msg and f"ST: {self.st}" in msg:
                    response = f"""HTTP/1.1 200 OK\r
                    CACHE-CONTROL: max-age = 1800\r
                    EXT :\r
                    ST: {self.st}\r
                    USN: {self.usn}\r
                    \r
                    """

                    for i in range(3):
                        sock.sendto(response.encode("utf-8"), addr)
                        time.sleep(0.02)
                        
                    return addr[0]
        return 0
    
    
    
    
        