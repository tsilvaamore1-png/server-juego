import socket
import pickle
import os

# Railway asigna automáticamente el puerto en la variable de entorno PORT
PORT = int(os.environ.get("PORT", 5555))
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("0.0.0.0", PORT))

print(f"Servidor Relay UDP iniciado en el puerto {PORT}")

# Estructura: {"nombre_sala": {"host": (ip, port), "clients": { "client_id": (ip, port) }}}
rooms = {}

while True:
    try:
        raw_data, addr = s.recvfrom(8192)
        try:
            pack = pickle.loads(raw_data)
            room = pack.get("r")
            sender_id = pack.get("id")
            data = pack.get("d")
        except:
            continue # Ignorar paquetes corruptos o pings random

        if not room or not sender_id: continue

        if room not in rooms:
            rooms[room] = {"host": None, "clients": {}}

        if sender_id == "HOST":
            rooms[room]["host"] = addr
            # Reenviar los datos del Host a todos los clientes de esta sala
            for c_addr in rooms[room]["clients"].values():
                s.sendto(data, c_addr)
        else:
            # Registrar al cliente
            rooms[room]["clients"][sender_id] = addr
            host_addr = rooms[room]["host"]
            
            # Si la sala ya tiene un Host activo, le reenviamos la acción del cliente
            if host_addr:
                s.sendto(pickle.dumps({"c_id": sender_id, "data": data}), host_addr)

    except Exception as e:
        pass