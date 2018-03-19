from socket import *
import time
PORT = 7734

class clientSocket:

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
