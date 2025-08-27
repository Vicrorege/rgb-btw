import os
import paho.mqtt.client as mqtt_client
import random
import click
import sqlite3
from pathlib import Path

basedir = Path(__file__).parent.absolute()

def connect_mqtt(username, password, broker, port):
    def on_connect(client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            print("Connected to MQTT Broker!")
        else:
            print(f"Failed to connect, return code {reason_code}")

    # Создаем клиента с указанием версии callback API (рекомендуется VERSION2)
    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2, client_id=str(random.randint(0, 1000)))
    
    # Устанавливаем логин и пароль
    client.username_pw_set(username, password)
    
    # Назначаем callback функцию для подключения
    client.on_connect = on_connect
    
    # Подключаемся к брокеру
    client.connect(broker, port)
    return client

@click.group()
def cli():
    """CLI client for rgb-btw"""
    pass

@cli.command()
def init():
    """Initializes database"""
    click.echo(click.style("Creating database...", fg="yellow"))
    try:
        db = sqlite3.connect(basedir / "db.db")
        db_cur = db.cursor()
        db_cur.execute("""CREATE TABLE IF NOT EXISTS devices(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR UNIQUE,
        host VARCHAR,
        port INTEGER,
        user VARCHAR,
        passwd VARCHAR,
        topic VARCHAR,
        is_default INTEGER
        )""")
        db.commit()
        db_cur.close()
        db.close
        click.echo(click.style("Database created successfully!", fg="green"))
    except Exception as e:
        click.echo(click.style(f"Error while creating database: {e}", fg="red"))

@cli.command()
@click.argument("name")
@click.option("--host", "-h", required=True, help="MQTT server address")
@click.option("--port", "-p", type=int, default=1883, help="MQTT server port (default 1883)")
@click.option("--user", "-U", help="MQTT username")
@click.option("--passwd", "-P", help="MQTT password")
@click.option("--topic", "-t", required=True, help="MQTT topic")
def add(name, host, port, user, passwd, topic):
    """Adds device"""
    click.echo(click.style("Trying to write new device in database...", fg="yellow"))
    try:
        db = sqlite3.connect(basedir / "db.db")
        db_cur = db.cursor()
        db_cur.execute(f'''INSERT INTO devices(name, host, port, user, passwd, topic, is_default) VALUES ("{name}", "{host}", {port}, "{user}", "{passwd}", "{topic}", 0)''')
        db.commit()
        db_cur.close()
        db.close
        click.echo(click.style("New device wrote successfully!", fg="green"))
    except Exception as e:
        click.echo(click.style(f"Error while writing device: {e}", fg="red"))

@cli.command()
@click.argument("name")
@click.option("--toggle", "-t", is_flag=True, help="Toggles on/off strip condition")
@click.option("--color", "-c", default="-1", help="Sets binded color")
@click.option("--rgbR", "-R", default=-1, help="Sets R-component in RGB palette")
@click.option("--rgbG", "-G", default=-1, help="Sets G-component in RGB palette")
@click.option("--rgbB", "-B", default=-1, help="Sets B-component in RGB palette")
@click.option("--brightness", "-b", default=-1, type=int, help="Sets brightness")
@click.option("--rainbow", "-r", is_flag=True, help="Sets rainbow color")
def set(name, toggle, color, rgbr, rgbg, rgbb, brightness, rainbow):
    """Set condition of the strip"""
    binds = {
        "red": (255, 0, 0),
        "green": (0, 255, 0),
        "blue": (0, 0, 255),
        "white": (255, 255, 255),
        "black": (0, 0, 0),
        "yellow": (255, 255, 0),
        "cyan": (0, 255, 255),
        "magenta": (255, 0, 255),
        "orange": (255, 165, 0),
        "purple": (128, 0, 128),
        "pink": (255, 192, 203),
        "brown": (165, 42, 42),
        "gray": (128, 128, 128),
        "lightgray": (211, 211, 211),
        "darkgray": (169, 169, 169),
        "lime": (0, 255, 0),
        "maroon": (128, 0, 0),
        "navy": (0, 0, 128),
        "olive": (128, 128, 0),
        "teal": (0, 128, 128)
    }
    try:
        db = sqlite3.connect(basedir / "db.db")
        db_cur = db.cursor()
        db_cur.execute(f'''SELECT host, port, user, passwd, topic FROM devices WHERE name="{name}"''')
        out = db_cur.fetchall()
        db_cur.close()
        db.close
        # print(out)
        if out!=[]:
            if (color!="-1") ^ (rgbr!=-1 or rgbb!=-1 or rgbg!=-1) ^ rainbow:
                R=rgbr
                G=rgbg
                B=rgbb
                if color != "-1":
                    if color in list(binds.keys()):
                        R=binds[color][0]
                        G=binds[color][1]
                        B=binds[color][2]
                    else:
                        raise Exception("Color not found!")
                msg="$"+":".join(
                    [
                        "s",
                        str(toggle),
                        str(R),
                        str(G),
                        str(B),
                        str(rainbow),
                        str(brightness)
                    ]
                )

                broker = out[0][0]
                port = out[0][1]
                user = out[0][2]
                passwd = out[0][3]
                topic = out[0][4]
                
                connection = connect_mqtt(user, passwd, broker, port)
                result = connection.publish(topic, str(msg), qos=1)
                if result[1] == 1:
                    click.echo(click.style("Request sent successfully!", fg="green"))
            else:
                raise Exception("Choose only one color variant")
        else:
            raise Exception("Device is not found!")
    except Exception as e:
        click.echo(click.style(f"Error while sending request: {e}", fg="red"))

if __name__ == '__main__':
    cli()