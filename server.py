import socket
import time
import random
import json

localIP     = "127.0.0.1"
localPort   = 20001
bufferSize  = 1024

msgFromServer = "Datagram Acepted"
bytesToSend = str.encode(msgFromServer)

buffer = [] # [id,ack,mensaje]

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))
print("Link Available")

paquetes_perdidos = 0
paquetes_exitosos = 0

while(True):
    print("===========================================================================")
    print("BUFFER: ", buffer)
    print("===========================================================================")
    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    message = bytesAddressPair[0]
    #print("IMPRIMIENDO bytesAddressPair[0]", bytesAddressPair[0]) #{"Id": 1, "ACK": false, "data": "J"}
    #print("IMPRIMIENDO bytesAddressPair[1]", bytesAddressPair[1]) # ('127.0.0.1', 60618)
    package = json.loads(bytesAddressPair[0]) ## se usa json para manejar diccionario de mejor forma, 
#print("Imprimiendo Package JSON LOADS ", package) # -> Package contiene: {'Id': 0, 'ACK': False, 'data': 'A'}
    duplicado = False
    
    address = bytesAddressPair[1]
    print("Link bussy")

    if (random.random() > 0.3):
        cliente_id = package['Id']
        indice = 0
        x = 0
        #Recorre el buffer donde se almacenan los clientes
        for i in buffer:
            if i[0] == cliente_id: # si Cliente[0] == id entonces existe
                x = indice
                break
            else:
                x = -1    
            indice +=1
        if not buffer: #validación para el caso inicial, donde el buffer esta vacio
                x = -1

        if x == -1 : # Cliente no existe 
            buffer.append([cliente_id, package['ACK'], package['data']]) # Se almacena una tupla Cliente [id,ack,mensaje]
            
        else: # Cliente si existe
            if (buffer[x][1] == package['ACK'] ): # Chequear duplicados -> ClienteX[ack] == package[ack]
                print("PAQUETE DUPLICADO \n")
                duplicado = True # Paquete se ignora al ser duplicado
                
            else: 
                buffer[x][1] = package['ACK'] # Se setea el campo ack de la tupla cliente X 
                buffer[x][2] += package['data'] # Actualiza la letra que llega con lo que tenia
        paquetes_exitosos += 1
        
        if not duplicado:
            clientMsg = format(package['data']) 
            clientACK = format(package['ACK'])

            # ESPERA 500ms <= timeout <= 3000ms
            timeout = random.randrange(5,30)/10
            print("Tiempo de espera: "+ str(timeout))
            time.sleep(timeout)
            
            # se envia el ack correspondiente
            message = {'ACK':clientACK, 'msg':"PAQUETE HA LOGRADO LLEGAR COMPLETO"}  
            p = json.dumps(message)# json.dumps permite enviar data desde python a json
            bytesToSend = str.encode(p) #codificamos el mensaje
            
            UDPServerSocket.sendto(bytesToSend, address)
            print("Paquete recibido por el cliente " + str(cliente_id)+" : " + clientMsg)
            print("Mensaje cliente: " + str(cliente_id) + " nombre: " +buffer[x][2])
            print("ENVIANDO ACK: " + clientACK)
    else:
        paquetes_perdidos += 1
        print("¡PAQUETE PERDIDO! "+ " -----> Numero de paquetes perdidos: " + str(paquetes_perdidos))
        
                    
    print("Link Available")
    tasa = (paquetes_perdidos/(paquetes_perdidos + paquetes_exitosos)) * 100
    tasa_perdida = "%.1f" % tasa
    print("Tasa de perdida del server: " + tasa_perdida + "%")

