import random
import sqlite3
from paho.mqtt import client as mqtt_client
import json
import website.settings, website.secret

broker = website.settings.MQTT_BROKER
port = 1883
topic = "home/test"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
username = website.secret.MQTT_NAME
password = website.secret.MQTT_PASS


def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        data = dict(
            topic=msg.topic,
            payload=msg.payload.decode()
        )

        json_object = json.loads(data['payload'])
        isic = json_object['isic']
        hodina = json_object['hodina_id']

        conn = sqlite3.connect("C:\\Users\\tomas\\Desktop\\projects\\iot\\instance\\database.db")
        cur = conn.cursor()
        sql = f"""UPDATE Attendance set Week_3 = 1 where student_id = (SELECT id from Ziak where isic_number = {isic}) AND Hodina_id = {hodina}"""

        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
        print("Updated")
        # ziak = results.query.filter(isic == Ziak.isic_number).first()
        # prezencka = Attendance.query.filter(hodina == Attendance.Hodina_id, ziak.id == Attendance.student_id)
        # prezencka.Week_1 = 'P'
        # with app.app_context().push():
        #     db.session.merge(prezencka)
        #     db.session.commit()
        #     print("UPDATED!")

    client.subscribe(topic)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()
