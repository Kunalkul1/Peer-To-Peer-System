from socket import *
import threading
import thread
import os
import time
import platform
BUFFERSIZE = 1024

class clientSocket(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port
        self.host = gethostname()

    def run(self):
        self.create_socket()
        thread.start_new_thread(self.start_uploader,())
        self.start_connections('192.168.1.21', 7734)
        self.add_RFC()
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

    def create_file_with_header(self,title,fil):
        #print "inside func()"
        RFC_filename = "RFC "+title+".txt"
        #print RFC_filename,fil
        if RFC_filename in os.listdir("./RFC"): 
            #print "inside if"
            try:
                f = open(fil,"r")
                con = f.read()
                f.close()
                #print con
            except IOError as e:
                print e
                msg = "P2P-CI/1.0 404 Not Found"
                print msg
                return msg
            #print "file opened!"
            
            msg = "P2P-CI/1.0 200 OK\r\n"
            #print "1"
            msg = msg + "Date: " + time.ctime() + "\r\n"
            #print "2"
            msg = msg + "OS: "+ platform.system()+" "+platform.release() + "\r\n"
            #print "half",msg
            msg = msg + "Last-Modified: " + time.ctime(os.path.getmtime(fil)) + "\r\n"
            #print "4"
            msg = msg + "Content-Length: "+ str(len(con)) + "\r\n"
            #print "5"
            msg = msg + "Content-Type: text/text" + "\r\n"
            #print "6"
            msg = msg + con
            #print msg
            return msg

        else:
            msg = "P2P-CI/1.0 404 Not Found"
            print msg
            return msg

    def start_uploader(self):

        sock = socket(AF_INET, SOCK_STREAM)
        sock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
        sock.bind(('', 0))
        self.port = sock.getsockname()[1]
        print "Upload port chosen is ",self.port
        sock.listen(10)
        
        while True:
            try:
                #print "Accepting connections for upload on port",self.port
                rsock,r_ip = sock.accept()

                msg = ""
                #print "Uploading start"
                while True:
                    msg = msg + rsock.recv(BUFFERSIZE)
                    print msg
                    #print ord(msg[-1])
                    if msg.endswith("\r\n\r\n"):
                        break


                #print "msg"
                #print msg
                info = msg.split('\r\n')
                title = msg.split('\r\n')[0].split(' ')[2]
                #print "Required RFC is ", title
                 
                fil = "./RFC/RFC "+title+".txt"
                #f = open(fil,"r")

                st = self.create_file_with_header(title,fil)
                #st = st + f.read()                
                #f.close()
                rsock.send(st)

                rsock.close()

                #print "Uploaded!!\n"
                
            except:
                print "Error in connecting/sending data to the client\n"


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
            #if choice == 1:
            #    self.add_RFC()
            #    continue
            if choice == 1:
                self.lookup_RFC()
                continue
            if choice == 2:
                self.list_RFC()
                continue
            if choice == 3:
                self.download_RFC()
                continue
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

    def recv_handle_msg(self,typ):
        if typ == "ADD":
            #Expecting one response from the server
            msg = ""
            print "Recving"
            while True:
                msg = msg + self.sock.recv(BUFFERSIZE)
                #print msg
                #print ord(msg[-1])
                if msg.endswith("\r\n\r\n") and len(msg.split('\r\n\r\n')) > 1:
                    break


            print "msg"
            print msg

            parts = msg.split('\r\n\r\n')

            info = parts[0].split(' ') #info will have version response number and phrase

            if info[1] == "200":
                print "Add operation success that is ",info[2]

            elif info[1] == "400":
                print "Bad request error", info[2]

            elif info[1] == "404":
                print "Not found error that is ",info[2]

            elif info[1] == "505":
                print "Version error that is ", info[2]

            else:
                print "Invalid error!", info[1]

        elif typ == "LOOKUP":

            #Can have multiple responses
            msg = ""
            print "Recving lookup"
            while True:
                msg = msg + self.sock.recv(BUFFERSIZE)
                print msg
                if msg.endswith("\r\n\r\n") and len(msg.split('\r\n\r\n')) > 1:
                    break
                if len(msg.split('\r\n\r\n')) == 1:
                    if msg.split('\r\n\r\n')[0].split(" ")[1] == 404 or msg.split('\r\n\r\n')[0].split(" ")[1] == 400 or msg.split('\r\n\r\n')[0].split(" ")[1] == 505:
                        break


            print len(msg)
            print msg

            parts = msg.split('\r\n\r\n')

            info = parts[0].split(' ') #info will have version response number and phrase

            if info[1] == "200":
                print "Lookup operation success that is ",info[2]

                

                rfc_info = parts[1].split('\r\n') #Fetching RFC information

                temp = rfc_info[0].split(' ')   #Just to extract RFC file information

                file_name = ""
                for i in range(2,len(temp)-2):
                    file_name += temp[i]
                print "RFC number:",temp[1], " File: ",file_name

                print "Printing peer(s) information and their upload ports: "
                print "\tHOST NAME\t\tPort number\n"
                for i in range(len(rfc_info)):
                    temp = rfc_info[i].split(' ')
                    print "\t",temp[-2],"\t\t",temp[-1]

                print "\r\n"
                return temp
            elif info[1] == "400":
                print "Bad request error", info[2]

            elif info[1] == "404":
                print "Not found error that is ",info[2]

            elif info[1] == "505":
                print "Version error that is ", info[2]

            else:
                print "Invalid error!", info[1]
        
        elif typ == "LIST":
             #Can have multiple responses
            msg = ""
            #print "LISTING"
            while True:
                msg = msg + self.sock.recv(BUFFERSIZE)

                if msg.endswith("\r\n\r\n") and len(msg.split('\r\n\r\n')) > 1:
                    break

                if len(msg.split('\r\n\r\n')) == 1:
                    if msg.split('\r\n\r\n')[0].split(" ")[1] == 404:
                        break


            print "Recieved Message is: "
            print msg

            parts = msg.split('\r\n\r\n')

            info = parts[0].split(' ') #info will have version response number and phrase

            if info[1] == "200":
                print "Lookup operation success that is ",info[2]

                

                rfc_info = parts[1].split('\r\n') #Fetching RFC information
                print "Total entries:",len(rfc_info)
                print "Printing rfc number, file name and peer(s) information and their respective upload ports: "
                print "\tRFC number\tFile Name\tHOST NAME\t\tPort number\n"
                for i in range(len(rfc_info)):
                    temp = rfc_info[i].split(' ')
                    file_name = ""
                    for j in range(2,len(temp)-2):
                        file_name += temp[j]
                    print "\t", temp[1],"\t",file_name,"\t",temp[-2],"\t\t",temp[-1]

                print "\r\n"
                return rfc_info
            elif info[1] == "400":
                print "Bad request error!"
                return None

            elif info[1] == "404":
                print "Not found error!"
                return None

            elif info[1] == "505":
                print "Version error"
                return None

            else:
                print "Invalid error!"    
                return None

        else:
            print "Incorrect Type!"



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
        title = raw_input("Enter the RFC title too\n")
        message = self.create_peer2server_message("LOOKUP", self.host, self.port, RFC_number, title)
        self.sock.send(message)
        #payload = self.sock.recv(BUFFERSIZE)
        self.recv_handle_msg("LOOKUP")
        #print "Peers having the specified RFC:\n" + payload

    def list_RFC(self):
        message = self.create_peer2server_message("LIST", self.host, self.port, 0)
        self.sock.send(message)
        #payload = self.sock.recv(BUFFERSIZE)
        self.recv_handle_msg("LIST")
        #print "List of all RFCS:\n"
        #print payload


    def recv_file(self,s,rfc,title):
        #print "recving file!"
        msg = ""
        while True:
            msg = msg + s.recv(BUFFERSIZE)
            #print msg
            if len(msg.split('\r\n')) >= 1:
                if msg.split('\r\n')[0].split(' ')[1] != "200":
                    break
            if len(msg.split('\r\n')) >= 6:
                break

        #print "ithe alo!"
        info = msg.split('\r\n')

        ver = info[0].split(' ')
        
        

        if ver[1] == '200':
            file_len = 0
            for i in range(6):
                if "Content-Length:" in info[i]:
                    file_len =  int(info[i].split(' ')[1])
                    break
            content = ""
            #print "I am here!"
            for i in range(6,len(info)):
                content = content + info[i]

            #print content

            while True:
                if len(content) >= file_len:
                    break

                content = content + s.recv(BUFFERSIZE)

            s.close()

            fil = open("./RFC/RFC "+str(rfc)+".txt","w")
            #print content
            fil.write(content[:file_len])
            fil.close()



            message = self.create_peer2server_message("ADD", self.host, self.port, str(rfc), title)
            self.sock.send(bytes(message))
            payload = self.sock.recv(BUFFERSIZE)
        
            print payload + "\n"

        else:
            print "Error in receiving file!"






    def download_RFC(self):
        rfc = int(input("Enter RFC number \n"))
        title = raw_input("Enter RFC Title \n")
        lookup_message = self.create_peer2server_message("LOOKUP", self.host, self.port, rfc, title)
        self.sock.send(lookup_message)
        info = self.recv_handle_msg("LOOKUP")
        print "heree",info
        if len(info) > 0:
            #print "hi"
            download_ip = info[-2]
            download_port = int(info[-1])

            s = socket(AF_INET,SOCK_STREAM)
            s.connect((download_ip,download_port))

            msg = self.create_peer2peer_message("GET",self.host,platform.system()+" "+platform.release(),rfc)
            s.send(msg)

            self.recv_file(s,rfc,title)
        else:
            print "Error in file information!"

        #payload = self.sock.recv(BUFFERSIZE)
        #download_ip, download_port = self.extract_info(payload, rfc, title)

        ###incomplete

    def create_peer2peer_message(self, request_type, host, OS, RFC_number):
        message = ""
        message = message + request_type + " "
        if RFC_number != 0:
            message = message + "RFC " + str(RFC_number) + " "
        message = message + "P2P-CI/1.0" + "\r\n"
        message = message + "Host: " + host + "\r\n"
        message = message + "OS: " + OS + "\r\n\r\n"

        print "The message that was sent:\n" + message
        return message


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
        message = "EXIT " + str(self.host) + " " + str(self.port) + "\r\n"
        self.sock.send(message)
        self.sock.close()
        return

def main():
    #upload_port = input("Enter the upload port number of this client:\n")
    sobj = clientSocket(0)
    try:
        sobj.start()
    except KeyboardInterrupt:
        sobj.exit()

if __name__ == "__main__":
    main()
