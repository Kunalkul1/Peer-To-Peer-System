import socket
import os
import threading
PORT = 7734
BUFFERSIZE = 1024
peerlist = []
list_of_rfcs = []

class serverSocket(threading.Thread):
    def __init__(self, peerinfo):
        threading.Thread.__init__(self)
        self.sockfd = peerinfo[0]
        self.address = peerinfo[1]

    def run(self):
        while True:
            payload = self.sockfd.recv(BUFFERSIZE)
            if payload.startswith("EXIT"):
                break
            if not payload:
                break
            self.process_request(payload)

    #Function to create socket
    def create_socket(self):
        try:
            self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            self.sock.bind(('',PORT))
            self.sock.listen(10)
        except:
            print "Socket creation failed"

    #Function to accept connections
    def accept_connections(self):
        try:
            (self.csock, self.caddr) = self.sock.accept()

        except:
            print "accept_connection failed!"
            self.closeServerSocketFromChild()
            os.system('kill %d' % os.getpid())

    def process_request(self, request):
        self.validate_request(request)
        if self.status_code == 200:
            split_request = request.split("\r\n")
            if not (split_request[1].lstrip('Host: '), split_request[2].lstrip('Port: ')) in peerlist:
                peerlist.append((split_request[1].lstrip('Host: '), split_request[2].lstrip('Port: ')))
                print "Appended to Peer List!\n"
            if request.startswith('ADD'):
                self.add_rfc(request)
            self.send_response(request)
        else:
            response = "P2P-CI/1.0 " + str(self.status_code) + " " + self.phrase
            self.sockfd.send(response)
        print "Peer list: " + str(peerlist)

    def validate_request(self, request):
        self.status_code = 0
        self.phrase = ""
        split_request = request.split("\r\n")
        if "P2P-CI/1.0" not in split_request[0]:
            self.status_code = 505
            self.phrase = "P2P-CI Version Not Supported"

        elif not ((split_request[0].startswith("ADD") or split_request[0].startswith("LOOKUP") or split_request[0].startswith("LIST")) and (split_request[1].startswith("Host: ") and split_request[2].startswith("Port: "))):
            self.status_code = 400
            self.phrase = "Bad Request"

        elif not split_request[0].startswith("LIST"):
            if not split_request[len(split_request) - 1].startswith("Title: "):
                self.status_code = 400
                self.phrase = "Bad Request"
            else:
                self.status_code = 200
                self.phrase = "OK"

        else:
            self.status_code = 200
            self.phrase = "OK"

    def add_rfc(self, request):
        split_request = request.split('\r\n')
        if (split_request[0].lstrip("ADD RFC ").replace(' P2P-CI/1.0', ''), split_request[len(split_request) - 1].lstrip("Title: "),
            split_request[1].lstrip("Host: ")) not in list_of_rfcs:
            list_of_rfcs.append((split_request[0].lstrip("ADD RFC ").replace(' P2P-CI/1.0', ''),
                                 split_request[len(split_request) - 1].lstrip("Title: "), split_request[1].lstrip("Host: ")))
            print "List of RFCs has been updated!\n"
        print "List of RFCs: " + str(list_of_rfcs)

    def lookup_RFC(self, split_request):
        rfclist = []
        for(rfc, title, host) in list_of_rfcs:
            if (rfc == split_request[0].lstrip("LOOKUP RFC ").replace(' P2P-CI/1.0', '') and (title == split_request[len(split_request) - 1].lstrip("Title: "))):
                rfclist.append((rfc, title, host))
        return rfclist

    def send_response(self, request):
        response = ""
        split_request = request.split('\r\n')
        if split_request[0].startswith("ADD"):
            response = response + "P2P-CI/1.0 " + str(self.status_code) + " " + self.phrase
            response = response + "\r\n" + split_request[0].lstrip("ADD ").rstrip("P2P-CI/1.0")
            response = response + split_request[len(split_request) - 1].lstrip("Title: ")
            response = response + split_request[1].lstrip("Host:") + split_request[2].lstrip("Port:")

        elif(split_request[0].startswith("LOOKUP")):
            lookup_results = self.lookup_RFC(split_request)
            if len(lookup_results) == 0:
                self.status_code = 404
                self.phrase = "Not Found"
                response = response + "P2P-CI/1.0 " + str(self.status_code) + " " + self.phrase
            else:
                response = response + "P2P-CI/1.0 " + str(self.status_code) + " " + self.phrase
                for(rfc, title, host) in lookup_results:
                    response = response + "\r\n" + "RFC " + rfc + " " + title + " " + host
                print response

        self.sockfd.send(bytes(response))

    #Function to close the Client connection from Parent process
    def closeClientSocketFromParent(self):
        self.csock.close()

    #Function to close the Server connection from the child process
    def closeServerSocketFromChild(self):
        self.sock.close()


#This class has all the functions performed by the Slave socket
class Child:
    def __init__(self,sock,addr):
        self.sock = sock
        self.addr = addr

    def register(self):
        print "Client registered!"

    def close(self):
        print "Closing connection from client with address ", self.addr
        self.sock.close()
        print "Connection closed!"

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', PORT))
    sock.listen(10)
    print "Server is up and running!\n"
    while True:
        try:
            server = serverSocket(sock.accept())
            print "Client registered!\n"
            server.start()
        except:
            print "Error in connecting/sending data to the client\n"

if __name__ == "__main__":
    main()





