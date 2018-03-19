from socket import *
import os
import time
import signal
PORT = 7734

#This class contains functions for the Master socket
class serverSocket:

	#Function to create socket
	def create_socket(self):
		try:
			self.sock = socket(AF_INET,SOCK_STREAM)
			self.sock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
			self.sock.bind(('',PORT))

			self.sock.listen(10)
		except:
			print "creation failed"


	#Function to accept connections
	def accept_connections(self):

		try:
			(self.csock, self.caddr) = self.sock.accept()

		except:
			print "accept_connection failed!"
			self.closeServerSocketFromChild()
			os.system('kill %d' % os.getpid())

	"""
	#Function to send from server socket
	def send(self,str):
		#print "sending",str
		self.csock.send(str)

	#Function to recv from the client socket
	def recv(self):
		return self.csock.recv(1024)
	"""

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
	sobj = serverSocket()
	sobj.create_socket()

	while True:
		sobj.accept_connections()
		fval = os.fork()
		if fval == -1:
			print "Fork failed!"
			sobj.closeClientSocketFromParent()
			continue

		if fval == 0:
			sobj.closeServerSocketFromChild()
			child = Child(sobj.csock,sobj.caddr)
			child.register()
			time.sleep(5)
			child.close()
			os.system('kill %d' % os.getpid())
			
		sobj.closeClientSocketFromParent()

if __name__ == "__main__":
	main()





