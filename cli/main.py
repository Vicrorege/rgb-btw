import os
import paho.mqtt.client as mqtt
import click
import sqlite3
from pathlib import Path

basedir = Path(__file__).parent.absolute()

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


if __name__ == '__main__':
    cli()