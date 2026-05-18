import socket
import pickle

# Servidor UDP básico para retransmitir datos
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(("0.0.0.0", 80)) # El puerto que te dé el hosting

print("Servidor Relay escuchando...")
clientes = {} # Guarda las direcciones de los jugadores

while True:
    try:
        data, addr = server.recvfrom(4096)
        pack = pickle.loads(data)
        room = pack.get("r")
        c_id = pack.get("id")
        
        # Registrar al cliente en la sala
        if room not in clientes:
            clientes[room] = {}
        clientes[room][c_id] = addr
        
        # Reenviar los datos al OTRO jugador de la sala
        for destino_id, destino_addr in clientes[room].items():
            if destino_id != c_id:
                server.sendto(data, destino_addr)
    except:
        pass
