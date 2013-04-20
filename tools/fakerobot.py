import socket
import threading
import socketserver
import time

class RequestHandler(socketserver.BaseRequestHandler):
    #def __init__(self, *args, **kwargs):
        #print(self, *args, **kwargs)
        #print("Got connection from {}".format( self.client_address[0]) )
        #socketserver.BaseRequestHandler.__init__(self, *args, **kwargs)

    def handle(self):
        try:
            data = str(self.request.recv(1024), 'ascii')
        except Exception as ex:
            print("Got exception", ex)
        else:
            cur_thread = threading.current_thread()
            print(cur_thread.name, "received: ", data, )

    def setup(self):
        print("Got new connection from {}".format( self.client_address) )
        self.server.handlers.append(self)

    def finish(self):
        print("Connection from {} lost".format( self.client_address) )
        self.server.handlers.remove(self)

class Server(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def init(self):
        """
        __init__ should not be overriden
        """
        self.handlers = []

    def cleanup(self):
        for handler in self.handlers:
            handler.request.shutdown(socket.SHUT_RDWR)
            handler.request.close()
        self.shutdown()




if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    host, port = "localhost", 30002 # this is the standard secondary port for a UR robot

    server = Server((host, port), RequestHandler)
    server.init()
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    print("Fake Universal robot running at ", host, port)
    try:
        f = open("packet.bin", "rb")
        packet = f.read()
        f.close()
        while True:
            time.sleep(0.09) #The real robot published data 10 times a second
            for handler in server.handlers:
                handler.request.sendall(packet)
    finally:
        print("Shutting down server")
        server.cleanup()