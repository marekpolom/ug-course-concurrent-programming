from calendar import c
from pydoc import cli
import socket, pickle
from _thread import *
import sys
import numpy as np
from client import GameData, Reply


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server = "localhost"
port = 5555

game_data = GameData()

server_ip = socket.gethostbyname(server)

try:
    s.bind((server, port))

except socket.error as e:
    print(str(e))

s.listen(2)
print("Waiting for a connection")


def threaded_client(conn, address):
    global game_data

    if game_data.client_conn(conn, address) is None:
        conn.send(str.encode("Max server cappacity reached!"))
        conn.close()
        return

    client = game_data.get_client(address)

    conn.send(str.encode("Connected to the game server!"))

    msg = ""

    while True:
        reply = Reply(None, None)

        # try:
        data = conn.recv(4096)
        if not data:
            conn.send(str.encode("Goodbye"))
            break
        else:
            msg = pickle.loads(data)

            print(msg)

            if msg["type"] == "start_game":
                reply = Reply.start_game(client, msg)

            if msg["type"] == "wait_for_enemy_join":
                reply = Reply.wait_for_enemy_join(game_data, client)

            if msg["type"] == "wait_for_enemy_start":
                reply = Reply.wait_for_enemy_start(game_data, client)

            if msg["type"] == "first_player":
                reply = Reply.first_player(game_data, client)                

            if msg["type"] == "wait_for_enemy_move":
                reply = Reply.wait_for_enemy_move(game_data, client)

            if msg["type"] == "move":
                reply = Reply.make_move(game_data, client, msg["data"]["move"])

            if msg["type"] == "check_winner":
                reply = Reply.check_winner(game_data, client)

        conn.sendall(reply.parse_reply())
        # except:
        #     break

    print("Connection Closed")
    game_data.client_dc(address)
    conn.close()


while True:
    conn, addr = s.accept()
    print("Connected to: ", addr)

    start_new_thread(threaded_client, (conn, addr))
