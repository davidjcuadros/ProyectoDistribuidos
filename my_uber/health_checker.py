import zmq
import time

class HealthChecker:
    def __init__(self):
        self.context = zmq.Context()

    def check_server(self):
        # Socket para verificar el estado del servidor
        health_socket = self.context.socket(zmq.REQ)
        health_socket.connect("tcp://localhost:5558")

        while True:
            try:
                health_socket.send_string("Are you alive?")
                response = health_socket.recv_string(flags=zmq.NOBLOCK)
                print(f"Servidor respondió: {response}")
            except zmq.Again:
                print("Servidor no responde, activando réplica...")
                # Activar réplica
            time.sleep(5)  # Verifica cada 5 segundos
