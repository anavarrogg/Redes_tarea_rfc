from os import wait
import socket
import json # para hacer diccionario
from threading import Thread, Semaphore 


# Proceso de cada cliente
def enviar(id, msgFromClient, ACK , serverAddressPort, bufferSize):
    # Create a UDP socket at client side
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPClientSocket.settimeout(2.0)  

    # recorre todo el nombre caracter por caracter
    for caracter in msgFromClient:
        # Se crea el paquete con sus datos
        package = {'Id': id, 'ACK':ACK, 'data':caracter}  
        paquete_serial = json.dumps(package)# json.dumps permite enviar data desde python a json
        bytesToSend = str.encode(paquete_serial) # se codifica el mensaje
        semaforo.acquire() # When invoked with the blocking argument set to True (the default), block until the lock is unlocked, then set it to locked and return True.
        # ESPERA POR UN ACK CORRECTO 
        while(True): 
            # TRY PARA MANEJAR EL TIMEOUT
            try:  
                print("CLIENTE "+ str(id) + " ENVIANDO: " + caracter)
                print("ENVIANDO CARACTER")
                # Send to server using created UDP socket
                UDPClientSocket.sendto(bytesToSend, serverAddressPort) # Envio de paquete

                msgFromServer = UDPClientSocket.recvfrom(bufferSize) # Wait for response
                message =json.loads(msgFromServer[0]) # message contiene: {'Id': id, 'ACK': Bool, 'data': 'char'}
                #print("MESSAGE JSONLOADS CLIENTE: ", message) # -> {'ACK': 'True', 'msg': 'PAQUETE HA LOGRADO LLEGAR COMPLETO'}
                serverACK = message['ACK'] # Se rescata el ACK enviado por el server
                print("ACK del servidor: " + serverACK)  
                # si el ACK enviado por el servidor es el mismo que espera el cliente
                if (serverACK == str(ACK)): 
                    print("ACK correcto\n")
                    if (ACK == True):
                        ACK = False # Se reinicia ACK
                    else:
                        ACK = True # Se reinicia ACK
                    break           
            # NO ACK -> Reenvio de paquete
            except socket.timeout: 
                print("ACK NO RECIBIDO, TIME OUT \n" + "ENVIANDO DE NUEVO...")
                
                continue
        semaforo.release() 
        print("=====================================================================")
    msg = "MENSAJE DEL SERVER: {}".format(message['msg']) # se confirma que llego el paquete desde el server
    print(msg)


class Hilo(Thread):
    def __init__(self,id , msg, ack, server, buffer): #Constructor de la clase
         Thread.__init__(self)
         self.id=id
         self.msg = msg
         self.ack = ack
         self.server = server
         self.buffer = buffer
    #Metodo que se ejecutara con la llamada start()
    def run(self):
          print("Cliente " + str(self.id) + " Tratando de enviar..")
          enviar(self.id,self.msg, self.ack, self.server,self.buffer)

serverAddressPort = ("127.0.0.1", 20001)
bufferSize = 1024
ACK = False            
semaforo = Semaphore(1) # creamos variable semaforo

#inicializacion de clientes
clientes = [Hilo(0,"Alvaro", ACK, serverAddressPort, bufferSize),
            Hilo(1,"Jorge", ACK, serverAddressPort, bufferSize),
            Hilo(2,"Rodrigo",ACK,serverAddressPort,bufferSize)]; 

for c in clientes: 
     c.start(); #Ejecutar todos los hilos