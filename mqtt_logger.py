#!/usr/bin/env python3
"""
MQTT to MySQL Logger
Kuuntelee MQTT-viestejä ja tallentaa ne tietokantaan.
"""

import json
import logging
import paho.mqtt.client as mqtt
import mysql.connector
from mysql.connector import pooling

# Konfiguraatio
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "chat/messages"

DB_CONFIG = {
    "host": "localhost",
    "user": "mqtt_user",
    "password": "salasana123",  # vaihda!
    "database": "mqtt_chat",
}

# Lokitus
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Tietokantapooli
db_pool = pooling.MySQLConnectionPool(
    pool_name="mqtt_pool",
    pool_size=5,
    **DB_CONFIG,
)

def save_message(nickname: str, message: str, client_id: str) -> None:
    """Tallenna viesti tietokantaan."""
    conn = None
    cursor = None
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO messages (nickname, message, client_id)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (nickname, message, client_id))
        conn.commit()
        logger.info("Tallennettu: [%s] %s", nickname, message[:50])
    except mysql.connector.Error as err:
        logger.error("Tietokantavirhe: %s", err)
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

def on_connect(client, userdata, flags, rc):
    """MQTT-yhteys muodostettu."""
    if rc == 0:
        logger.info("Yhdistetty MQTT-brokeriin")
        client.subscribe(MQTT_TOPIC)
        logger.info("Tilattu: %s", MQTT_TOPIC)
    else:
        logger.error("Yhteysvirhe, koodi: %s", rc)

def on_message(client, userdata, msg):
    """Käsittele saapuva MQTT-viesti."""
    try:
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)

        nickname = str(data.get("nickname", "Tuntematon"))[:50]

        # hyväksy molemmat avaimet
        message = str(data.get("message") or data.get("text") or "").strip()

        client_id = str(data.get("clientId") or data.get("client_id") or "")[:100]

        if message:
            save_message(nickname, message, client_id)

    except json.JSONDecodeError:
        logger.warning("Virheellinen JSON: %s", msg.payload)
    except Exception as e:
        logger.error("Virhe: %s", e)

def main():
    """Pääohjelma."""
    logger.info("MQTT Logger käynnistyy...")

    # Testaa tietokantayhteys
    try:
        conn = db_pool.get_connection()
        conn.close()
        logger.info("Tietokantayhteys OK")
    except mysql.connector.Error as err:
        logger.error("Ei yhteyttä tietokantaan: %s", err)
        return

    client = mqtt.Client(client_id="mqtt_logger")
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        logger.info("Sammutetaan...")
    finally:
        try:
            client.disconnect()
        except Exception:
            pass

if __name__ == "__main__":
    main()
