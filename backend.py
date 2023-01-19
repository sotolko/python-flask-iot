import random
import sqlite3
from Cryptodome.Cipher import AES
from base64 import b64decode
from paho.mqtt import client as mqtt_client
import json
import website.settings, website.secret
import os
import binascii

broker = website.settings.MQTT_BROKER
port = 1883
topic_prezencka = "home/prezencka"
topic_ospravedlnenie = 'home/ospravedlnenie'
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
username = website.secret.MQTT_NAME
password = website.secret.MQTT_PASS
cwd = os.getcwd()


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
        print(data['topic'])
        isic_crypted = json_object['isic']
        hodina = json_object['hodina_id']
        tyzden = json_object['week']

        cipher = AES.new(website.secret.AES_PRIVATE, AES.MODE_ECB)
        decrypted = cipher.decrypt(binascii.unhexlify(isic_crypted))
        isic = decrypted.decode('ascii').strip()
        if not tyzden.isnumeric() or int(tyzden) > 13 or int(tyzden) < 1 or not hodina.isnumeric():
            print("UPDATE ERROR")
            return

        if data['topic'] == 'home/prezencka':
            conn = sqlite3.connect(f"{cwd}\\instance\\database.db")
            cur = conn.cursor()
            sql = f"""UPDATE Attendance set Week_{tyzden} = 'P' WHERE student_id IN (SELECT id from Ziak where isic_number = '{isic}') AND Hodina_id = {hodina}"""

            cur.execute(sql)
            conn.commit()
            cur.close()
            conn.close()
            print("Prezencka updated!")
        elif data['topic'] == 'home/ospravedlnenie':
            conn = sqlite3.connect(f"{cwd}\\instance\\database.db")
            cur = conn.cursor()
            sql = f"""UPDATE Attendance set Week_{tyzden} = 'O' WHERE student_id IN (SELECT id from Ziak where isic_number = '{isic}') AND Hodina_id = {hodina}"""

            cur.execute(sql)
            conn.commit()
            cur.close()
            conn.close()
            print("Ospravedlnenie updated!")

    client.subscribe(topic_prezencka)
    client.subscribe(topic_ospravedlnenie)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()
