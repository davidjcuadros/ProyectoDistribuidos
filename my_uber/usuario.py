import zmq
import sys

class Usuario:
    def __init__(self, user_id, position):
        self.user_id = user_id
        self.position = position
        self.context = zmq.Context()

    def request_taxi(self):
        requester = self.context.socket(zmq.REQ)
        requester.connect("tcp://localhost:5557")

        # Enviar la solicitud de taxi junto con la posición
        print(f"Usuario {self.user_id} solicitando taxi en la posición {self.position}")
        requester.send_string(f"{self.user_id} {self.position[0]} {self.position[1]}")

        try:
            # Esperar la respuesta del servidor (bloqueante)
            assigned_taxi_message = requester.recv_string()  # Elimina flags=zmq.NOBLOCK para esperar la respuesta
            print(f"Usuario {self.user_id} recibió respuesta: {assigned_taxi_message}")
        except zmq.Again:
            print(f"Usuario {self.user_id} no recibió respuesta en el tiempo límite. Terminando solicitud.")
            return

if __name__ == "__main__":
    user_id = int(sys.argv[1])
    user_position = (int(sys.argv[2]), int(sys.argv[3]))

    usuario = Usuario(user_id, user_position)
    usuario.request_taxi()

