import socket
import pickle
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- 1. MINISERVIDOR HTTP PARA ENGAÑAR A RENDER ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Servidor de juego online")

def run_http_server():
    # Render te pasa el puerto obligatorio por una variable de entorno llamada PORT
    # Si no existe (local), usa el 8080
    import os
    port = int(os.environ.get("PORT", 8080))
    httpd = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    print(f"Servidor HTTP falso escuchando en el puerto {port} para Render...")
    httpd.serve_forever()

# --- 2. TU SERVIDOR UDP ORIGINAL ---
def run_udp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Escuchamos en el puerto 80 (o el que quieras manejar para el juego)
    server.bind(("0.0.0.0", 80)) 
    
    print("Servidor Relay UDP escuchando para el juego...")
    clientes = {} 

    while True:
        try:
            data, addr = server.recvfrom(4096)
            pack = pickle.loads(data)
            room = pack.get("r")
            c_id = pack.get("id")
            
            if room not in clientes:
                clientes[room] = {}
            clientes[room][c_id] = addr
            
            for destino_id, destino_addr in clientes[room].items():
                if destino_id != c_id:
                    server.sendto(data, destino_addr)
        except:
            pass

# --- 3. ARRANQUE EN PARALELO ---
if __name__ == "__main__":
    # Lanzamos el HTTP en un hilo secundario para que Render no tire Timed Out
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()
    
    # Corremos el servidor UDP principal en el hilo de siempre
    run_udp_server()
