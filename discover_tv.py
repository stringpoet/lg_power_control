import socket
import re

def discover_tv():
    ssdp_request = \
        'M-SEARCH * HTTP/1.1\r\n' \
        'HOST:239.255.255.250:1900\r\n' \
        'MAN:"ssdp:discover"\r\n' \
        'MX:2\r\n' \
        'ST:urn:lge-com:service:webos-second-screen:1\r\n' \
        '\r\n'

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.settimeout(5)
    sock.sendto(ssdp_request.encode('utf-8'), ('239.255.255.250', 1900))

    try:
        while True:
            data, addr = sock.recvfrom(65507)
            location = re.search(r'LOCATION: (.*)', data.decode('utf-8'), re.IGNORECASE)
            if location:
                print(f"Discovered TV at {addr[0]}")
                return addr[0]
    except socket.timeout:
        print("Discovery timeout")
        return None
