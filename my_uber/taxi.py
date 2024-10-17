import paho.mqtt.client as mqtt
import time
import sys

class Taxi:
    def __init__(self, taxi_id, initial_position):
        self.taxi_id = taxi_id
        self.position = initial_position
        self.availability = "Disponible"
        self.client = mqtt.Client()

    def connect(self):
        self.client.connect("localhost", 1883)
        print(f"Taxi {self.taxi_id} conectado al broker.")
        self.client.subscribe(f"/asignacion/{self.taxi_id}")

    def update_position(self):
        while True:
            topic = "/posicion/taxi"
            message = f"{self.taxi_id} {self.position[0]} {self.position[1]}"
            print(f"Taxi {self.taxi_id} reportando posición: {self.position}")
            self.client.publish(topic, message)
            time.sleep(5)

    def on_message(self, client, userdata, msg):
        print(f"Taxi {self.taxi_id} recibió asignación: {msg.payload.decode()}")
        self.availability = "Ocupado"
        print(f"Taxi {self.taxi_id} ahora está {self.availability}.")
        time.sleep(30)  # Simula el servicio
        self.availability = "Disponible"
        print(f"Taxi {self.taxi_id} completó el servicio y está disponible nuevamente.")

if __name__ == "__main__":
    taxi_id = int(sys.argv[1])
    initial_position = (int(sys.argv[2]), int(sys.argv[3]))

    taxi = Taxi(taxi_id, initial_position)
    taxi.connect()
    taxi.client.on_message = taxi.on_message

    # Iniciar la actualización de posición en paralelo
    taxi.update_position()
