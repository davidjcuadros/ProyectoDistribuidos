import paho.mqtt.client as mqtt
import math

class ServicioAsignacionTaxi:
    def __init__(self):
        self.client = mqtt.Client()
        self.taxi_positions = {}

    def connect(self):
        self.client.connect("10.43.100.135", 1883)
        print("Servicio de Asignación conectado al broker.")
        self.client.subscribe("/solicitud")
        self.client.subscribe("/posicion/taxi")

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        message = msg.payload.decode()

        if topic == "/posicion/taxi":
            taxi_id, x, y = message.split()
            self.taxi_positions[taxi_id] = (int(x), int(y))
            print(f"Posición de Taxi {taxi_id} actualizada: {self.taxi_positions[taxi_id]}")
        
        elif topic == "/solicitud":
            user_id, user_x, user_y = map(int, message.split())
            print(f"Solicitud recibida de Usuario {user_id} en posición ({user_x}, {user_y})")
            self.asignar_taxi(user_id, (user_x, user_y))

    def asignar_taxi(self, user_id, user_position):
        if not self.taxi_positions:
            print("No hay taxis disponibles.")
            return

        closest_taxi_id = None
        min_distance = float('inf')

        for taxi_id, position in self.taxi_positions.items():
            distance = math.hypot(user_position[0] - position[0], user_position[1] - position[1])
            if distance < min_distance:
                min_distance = distance
                closest_taxi_id = taxi_id

        if closest_taxi_id:
            print(f"Asignando Taxi {closest_taxi_id} al Usuario {user_id}")
            # Publica en el tema para que el usuario reciba el taxi asignado
            self.client.publish(f"/asignacion/usuario_{user_id}", f"Taxi asignado: {closest_taxi_id}")
            del self.taxi_positions[closest_taxi_id]  # Eliminar para simular que está ocupado

if __name__ == "__main__":
    servicio = ServicioAsignacionTaxi()
    servicio.connect()
    servicio.client.on_message = servicio.on_message
    servicio.client.loop_forever()
