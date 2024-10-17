import zmq
import time
from multiprocessing import Process, Manager
import math

class ServidorCentral:
    def __init__(self, taxi_positions):
        self.context = zmq.Context()
        self.taxi_positions = taxi_positions  # Diccionario compartido para registrar taxis y sus posiciones
        print("ServidorCentral inicializado.")

    def run_publisher(self, publish_duration=10):
        publisher = self.context.socket(zmq.PUB)
        publisher.bind("tcp://*:5556")
        print("ServidorCentral listo para publicar solicitudes a los taxis en el puerto 5556.")

        start_time = time.time()

        while time.time() - start_time < publish_duration:
            message = "Solicitud de posición"
            publisher.send_string(message)
            print("Publicada solicitud de posición a todos los taxis.")
            time.sleep(1)
        
        print("Periodo de publicación completado. Saliendo del bucle de publicación.")

    def handle_taxi_positions(self):
        receiver = self.context.socket(zmq.PULL)
        receiver.bind("tcp://*:5558")  # Puerto para recibir posiciones de los taxis
        print("ServidorCentral listo para recibir posiciones de taxis en el puerto 5558.")

        while True:
            message = receiver.recv_string()
            taxi_id, x, y = message.split()
            self.taxi_positions[taxi_id] = (int(x), int(y))  # Actualiza la posición del taxi
            print(f"Posición de Taxi {taxi_id} actualizada a ({x}, {y})")
            
        if self.taxi_positions:
            print("Posiciones actuales de los taxis:")
            for taxi_id, position in self.taxi_positions.items():
                print(f"Taxi {taxi_id} - Posición: {position}")    
        
    def handle_requests(self):
        reply_socket = self.context.socket(zmq.REP)
        reply_socket.bind("tcp://*:5557")
        
        publisher = self.context.socket(zmq.PUB)
        publisher.bind("tcp://*:5559")  # Publicar asignaciones a taxis en este puerto

        print("ServidorCentral listo para recibir solicitudes de usuarios en el puerto 5557.")

        while True:
            print("Esperando solicitud de usuario...")
            message = reply_socket.recv_string()
            print(f"Solicitud recibida: {message}")

            user_id, user_x, user_y = message.split()  # El usuario envía su ID y posición
            user_x, user_y = int(user_x), int(user_y)

            self.run_publisher(publish_duration=10)
            
            print("///////////")

            # Lógica para asignar el taxi más cercano o en la misma posición
            if self.taxi_positions:
                closest_taxi_id = None
                min_distance = float('inf')

                for taxi_id, taxi_position in self.taxi_positions.items():
                    taxi_x, taxi_y = taxi_position
                    distance = math.hypot(user_x - taxi_x, user_y - taxi_y)

                    if distance == 0:
                        closest_taxi_id = taxi_id
                        break
                    elif distance < min_distance:
                        min_distance = distance
                        closest_taxi_id = taxi_id

                if closest_taxi_id is not None:
                    # Taxi asignado
                    assigned_taxi_id = closest_taxi_id
                    taxi_position = self.taxi_positions[assigned_taxi_id]
                    print(f"Taxi {assigned_taxi_id} asignado con posición {taxi_position}")

                    # Enviar respuesta al usuario
                    reply_socket.send_string(f"Taxi {assigned_taxi_id} asignado")
                    print(f"Taxi {assigned_taxi_id} asignado enviado como respuesta al usuario.")
                    
                    # Notificar al taxi que fue asignado
                    publisher.send_string(f"Taxi {assigned_taxi_id} asignado a Usuario {user_id}")
                    print(f"Notificación enviada al Taxi {assigned_taxi_id}")

                    # Elimina el taxi de la lista si quieres simular que está ocupado
                    del self.taxi_positions[assigned_taxi_id]
                else:
                    # Si no hay taxis disponibles, enviar un mensaje adecuado
                    reply_socket.send_string("No hay taxis disponibles en este momento")
                    print("No hay taxis disponibles para asignar.")
            else:
                reply_socket.send_string("No hay taxis disponibles en este momento")
                print("No hay taxis disponibles para asignar.")


# Función principal para ejecutar en procesos separados
def run_servidor():
    with Manager() as manager:
        taxi_positions = manager.dict()

        servidor = ServidorCentral(taxi_positions)

        p1 = Process(target=servidor.handle_requests)  
        p2 = Process(target=servidor.handle_taxi_positions)  

        p1.start()
        p2.start()

        p1.join()
        p2.join()

if __name__ == "__main__":
    try:
        run_servidor()
    except KeyboardInterrupt:
        print("Servidor interrumpido.")

