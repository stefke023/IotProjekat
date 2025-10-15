import socket
import struct

def send_activation_information(message, multicast_ip="239.1.1.1", port=5007):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)  

    for _ in range(3):
        sock.sendto(message.encode(), (multicast_ip, port))
    sock.close()


def get_activation_information(multicast_ip="239.1.1.1", port=5007, buffer_size=1024):
    substring="System ready: "
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', port))  

    mreq = struct.pack("4s4s", socket.inet_aton(multicast_ip), socket.inet_aton("0.0.0.0"))
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    
    while True:
        data, addr = sock.recvfrom(buffer_size)
        message = data.decode(errors='ignore')
        if substring in message:
            sock.close()
            if message == "System ready: TRUE":
                return True
            else: 
                return False 
