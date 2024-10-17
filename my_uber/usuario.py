import paho.mqtt.client as mqtt
import sys

class Usuario:
    def __init__(self, user_id, position):
        self.user_id = user_id
        self.position = position
        self.client = mqtt.Client()

    def connect(self):
        self.client.connect("10.43.100.135", 1883)
        print(f"Usuario {self.user_id} conectado al broker.")
        # El usuario se suscribe a su tema de asignación para recibir el ID del taxi asignado
        self.client.subscribe(f"/asignacion/usuario_{self.user_id}")
        self.client.on_message = self.on_message

    def request_taxi(self):
        topic = "/solicitud"
        message = f"{self.user_id} {self.position[0]} {self.position[1]}"
        print(f"Usuario {self.user_id} solicitando taxi en {self.position}")
        self.client.publish(topic, message)

    def on_message(self, client, userdata, msg):
        # Recibe la asignación del taxi y la imprime
        print(f"Usuario {self.user_id} recibió asignación: {msg.payload.decode()}")

if __name__ == "__main__":
    user_id = int(sys.argv[1])
    user_position = (int(sys.argv[2]), int(sys.argv[3]))

    usuario = Usuario(user_id, user_position)
    usuario.connect()
    usuario.request_taxi()
    usuario.client.loop_forever()  # Mantener la conexión abierta para recibir la asignación
