import socket

class Server:
    def __init__(self):
        addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
        self.s = socket.socket()
        self.s.bind(addr)
        self.s.listen()

    def accept(self, color, hue):
        cl, addr = self.s.accept()
        print("client connected from", addr)
        cl_file = cl.makefile('rwb', 0)
        
        while True:
            line = cl_file.readline()
            if not line or line == b'\r\n':
                break

        response = f"<html><body><h1>Current color:</h1><br><b>Color:</b>{color}<br><b>Hue:</b>{hue}</body></html>"
        cl.send("HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n")
        cl.send(response)
        cl.close()

