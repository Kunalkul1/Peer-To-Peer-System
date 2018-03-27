from socket import *
import threading
import os
BUFFERSIZE = 1024000

class clientSocket(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port
        self.host = gethostname()

    def run(self):
        self.create_socket()
        self.start_connections('localhost', 7734)
        self.show_main_menu()

    #Function to create client socket
    def create_socket(self):
        self.sock = socket(AF_INET,SOCK_STREAM)

    #Function to connect
    def start_connections(self,serverName,port):
        self.sock.connect((serverName,port))

    def send(self,str):
        #print str
        self.sock.send(str)
        #print "sent"

    def recv(self):
        try:
            #time.sleep(0.1)
            s = self.sock.recv(1024)
            return s
        except:
            print "recv failed"

    def close(self):
        self.sock.close()

    def show_main_menu(self):
        while True:
            choice = int(input("Choose an option: \n 1. ADD RFC \n 2. LOOKUP RFC \n 3. LIST RFCs \n 4. DOWNLOAD RFC \n 5. Exit \n"))
            if choice == 1:
                self.add_RFC()
            if choice == 2:
                self.lookup_RFC()
            if choice == 3:
                self.list_RFC()
            if choice == 4:
                self.download_RFC()
            if choice == 5:
                self.exit()
                break
            else:
                print "Invalid option. Please enter again!\n"

    def add_RFC(self):
        RFC_number = int(input("Enter the RFC number \n"))
        RFC_filename = "RFC " + str(RFC_number) + ".txt"
        RFC_title = raw_input("Enter RFC title \n")
        if RFC_filename in os.listdir("./RFC"):
            peer2server_message = self.create_peer2server_message("ADD", self.host, self.port, RFC_number, RFC_title)
            self.sock.send(peer2server_message)
            payload = self.sock.recv(BUFFERSIZE)
            print payload

        else:
            print("RFC is not present in RFC directory. \n")

    def create_peer2server_message(self, request_type, host, port, RFC_number, RFC_title = ""):
        message = ""
        message = message + request_type + " "
        if RFC_number != 0:
            message = message + "RFC " + str(RFC_number) + " "
        message = message + "P2P-CI/1.0" + "\r\n"
        message = message + "Host: " + host + "\r\n"
        message = message + "Port: " + str(port)

        if RFC_title:
            message = message + "\r\n" + "Title: " + RFC_title
        print "The message that was sent:\n" + message
        return message

    def lookup_RFC(self):
        RFC_number = int(input("Enter the RFC number to be looked up\n"))
        RFC_filename = raw_input("Enter the RFC title too\n")
        message = self.create_peer2server_message("LOOKUP", self.host, self.port, RFC_number, RFC_filename)
        self.sock.send(message)
        payload = self.sock.recv(BUFFERSIZE)
        print "Peers having the specified RFC:\n" + payload

    def list_RFC(self):
        message = self.create_peer2server_message("LIST", self.host, self.port, 0)
        self.sock.send(message)
        payload = self.sock.recv(BUFFERSIZE)
        print "List of all RFCS:\n"
        print payload

    def exit(self):
        print "Exiting!\n"
        self.sock.close()
        return

def main():
    upload_port = input("Enter the upload port number of this client:\n")
    sobj = clientSocket(upload_port)
    sobj.start()

if __name__ == "__main__":
    main()
