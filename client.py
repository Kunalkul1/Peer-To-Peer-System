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
        self.add_RFC()
        print "Registered your RFC information on server!\n"
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
            choice = int(input("Choose an option: \n 1. LOOKUP RFC \n 2. LIST RFCs \n 3. DOWNLOAD RFC \n 4. Exit \n"))
            if choice == 1:
                self.lookup_RFC()
            if choice == 2:
                self.list_RFC()
            if choice == 3:
                self.download_RFC()
            if choice == 4:
                self.exit()
                break
            else:
                print "Invalid option. Please enter again!\n"

    def add_RFC(self):
        rfc_files = []
        for file in os.listdir("./RFC"):
            if file.startswith("RFC"):
                rfc_files.append(file)
        for file in rfc_files:
            rfc_title = raw_input("Enter Title for RFC " + file.lstrip("RFC ").lstrip() + ":\n")
            message = self.create_peer2server_message("ADD", self.host, self.port, file.lstrip("RFC ").lstrip().rstrip('.txt'), rfc_title)
            self.sock.send(bytes(message))
            payload = self.sock.recv(BUFFERSIZE)
            print payload + "\n"

    # def add_RFC(self):
    #     RFC_number = int(input("Enter the RFC number \n"))
    #     RFC_filename = "RFC " + str(RFC_number) + ".txt"
    #     RFC_title = raw_input("Enter RFC title \n")
    #     if RFC_filename in os.listdir("./RFC"):
    #         peer2server_message = self.create_peer2server_message("ADD", self.host, self.port, RFC_number, RFC_title)
    #         self.sock.send(peer2server_message)
    #         payload = self.sock.recv(BUFFERSIZE)
    #         print payload
    #
    #     else:
    #         print("RFC is not present in RFC directory. \n")

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
        print "The message that was sent:\n" + message + "\n"
        return message

    def lookup_RFC(self):
        RFC_number = int(input("Enter the RFC number to be looked up\n"))
        title = raw_input("Enter the RFC title too\n")
        message = self.create_peer2server_message("LOOKUP", self.host, self.port, RFC_number, title)
        self.sock.send(message)
        payload = self.sock.recv(BUFFERSIZE)
        print "Peers having the specified RFC:\n" + payload + "\n"

    def list_RFC(self):
        message = self.create_peer2server_message("LIST", self.host, self.port, 0)
        self.sock.send(message)
        payload = self.sock.recv(BUFFERSIZE)
        print "List of all RFCS:\n"
        print payload + "\n"

    def download_RFC(self):
        rfc = int(input("Enter RFC number \n"))
        title = raw_input("Enter RFC Title \n")
        lookup_message = self.create_peer2server_message("LOOKUP", self.host, self.port, rfc, title)
        self.sock.send(lookup_message)
        payload = self.sock.recv(BUFFERSIZE)
        download_ip, download_port = self.extract_info(payload, rfc, title)

        ###incomplete

    def extract_info(self, payload, rfc, title):
        info = payload.split("\r\n")
        if "OK" in info[0]:
            host_and_port = info[1].lstrip("RFC " + str(rfc) + " " + title)
            download_host = host_and_port.split(" ")[0]
            download_port = host_and_port.split(" ")[1]
            download_ip = gethostbyname(download_host)
            return download_ip, download_port
        else:
            return "", ""

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
