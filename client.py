from socket import *
import time
import threading
PORT = 7734

class clientSocket:
	def __init__(self, port):
		threading.Thread.__init__(self)
		self.port = port
		self.host = gethostname()

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

	def main_menu(self):
		while(1):
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
		RFC_title = raw_input("Enter RFC title")
		if RFC_filename in os.listdir("."):
			peer2server_message = self.create_peer2server_message("ADD", self.host, self.port, RFC_number, RFC_title)

	def create_peer2server_message(self, request_type, host, port, RFC_number, RFC_title=""):
		message = ""
		message = message + request_type + " "
		if RFC_number != 0:
			message = message + "RFC " + str(RFC_number) + " "
		message = message + "Host: " + host + "\r\n"
		message = message + "Port: " + str(port)

		if RFC_title:
			message = message + "\r\n" + "Title: " + RFC_title
		print message
		return message

def main():
	sobj = clientSocket()
	sobj.create_socket()
	sobj.start_connections('localhost',PORT)
	"""sent = raw_input("Enter: ")
				sobj.send(sent)
				mod = sobj.recv()
				print "From serevr", mod"""
	time.sleep(5)
	sobj.close()

if __name__ == "__main__":
	main()
