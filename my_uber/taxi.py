import zmq
import time
import threading
import sys

class Taxi:
    def __init__(self, taxi_id, initial_position):
        self.taxi_id = taxi_id
        self.position = initial_position
        self.availability = "Disponible"
        self.context = zmq.Context()
        print(f"Taxi {self.taxi_id} creado en la posición {self.position}, Estado: {self.availability}")

    def update_position(self):
        # Socket para enviar la posición del taxi al servidor central
        sender = self.context.socket(zmq.PUSH)
        sender.connect("tcp://localhost:5558")  # Conectar al servidor central en el puerto 5558

        while True:
            # Escucha si se ha solicitado la posición del taxi
            subscriber = self.context.socket(zmq.SUB)
            subscriber.connect("tcp://localhost:5556")  # Conectar al servidor central en el puerto 5556
            subscriber.setsockopt_string(zmq.SUBSCRIBE, "")

            message = subscriber.recv_string()
            print(f"Taxi {self.taxi_id} recibió la solicitud: {message}")

            # Enviar posición al servidor central
            if self.availability == "Disponible":
                sender.send_string(f"{self.taxi_id} {self.position[0]} {self.position[1]}")
                print(f"Taxi {self.taxi_id} envió su posición: {self.position}")

            time.sleep(5)  # Simular el tiempo de espera antes de la próxima solicitud

    def listen_for_service(self):
        # Socket para escuchar asignaciones de servicios
        subscriber = self.context.socket(zmq.SUB)
        subscriber.connect("tcp://localhost:5559")  # Cambiar al nuevo puerto de asignación
        subscriber.setsockopt_string(zmq.SUBSCRIBE, f"Taxi {self.taxi_id}")

        while True:
            message = subscriber.recv_string()
            print(f"Taxi {self.taxi_id} recibió un servicio: {message}")
            self.availability = "Ocupado"
            print(f"Taxi {self.taxi_id} asignado a un servicio, ahora está {self.availability}.")
            time.sleep(30)  # Simula que está ocupado por 30 segundos
            self.availability = "Disponible"
            print(f"Taxi {self.taxi_id} completó el servicio, ahora está {self.availability}.")

def run_taxi(taxi_id, initial_position):
    taxi = Taxi(taxi_id, initial_position)
    position_thread = threading.Thread(target=taxi.update_position)
    service_thread = threading.Thread(target=taxi.listen_for_service)

    position_thread.start()
    service_thread.start()

    position_thread.join()
    service_thread.join()

if __name__ == "__main__":
    # Acepta parámetros de taxi_id y posición desde la línea de comandos
    taxi_id = int(sys.argv[1])
    initial_position = (int(sys.argv[2]), int(sys.argv[3]))
    run_taxi(taxi_id, initial_position)

