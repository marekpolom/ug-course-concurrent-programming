import socket

IP = "127.0.0.1"
port = 5001
bufSize = 2048

UDPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

UDPServerSocket.bind((IP, port))

clients = {
    "client_1": {
        "ip": "0.0.0.0",
        "port": 0,
        "connected": False,
        "score": 0,
        "last_move": "X",
        },
    "client_2": {
        "ip": "0.0.0.0",
        "port": 0,
        "connected": False,
        "score": 0,
        "last_move": "X",
        }
}

def check_result(a, b):
    if a == b:
        return "REMIS"
    elif (a == "K" and b == "P") or (a == "N" and b == "K") or (a == "P" and b == "N"):
        return "PRZEGRANA!"
    else:
        return "WYGRANA!"


print(f'Server running on {IP}:{port}...')

while(True):
    kom, adres = UDPServerSocket.recvfrom(bufSize)
    kom = kom.decode()

    if clients["client_1"]["connected"] and clients["client_2"]["connected"] and adres != (clients["client_1"]["ip"], clients["client_1"]["port"]) and adres != (clients["client_2"]["ip"], clients["client_2"]["port"]):
        odp = "Serwer pelny, nie mozesz dolaczyc do gry w czasie jej trwania!"
        UDPServerSocket.sendto(odp.encode(), adres)
    elif kom == "koniec":
        if clients["client_1"]["ip"] == adres[0] and clients["client_1"]["port"] == adres[1]:
            odp = "Opuszczanie gry..."

            UDPServerSocket.sendto(odp.encode(), (clients["client_1"]["ip"], clients["client_1"]["port"]))

            clients["client_1"]["ip"] = "0.0.0.0"
            clients["client_1"]["port"] = 0
            clients["client_1"]["connected"] = False
            clients["client_1"]["score"] = 0
            clients["client_1"]["last_move"] = "X"

            clients["client_2"]["score"] = 0
            clients["client_2"]["last_move"] = "X"

            odp_2 = "Przeciwnik opuscil gre!\nOczekiwanie na nowego gracza..."

            UDPServerSocket.sendto(odp_2.encode(), (clients["client_2"]["ip"], clients["client_2"]["port"]))

        elif clients["client_2"]["ip"] == adres[0] and clients["client_2"]["port"] == adres[1]:
            
            odp = "Opuszczanie gry..."

            UDPServerSocket.sendto(odp.encode(), (clients["client_2"]["ip"], clients["client_2"]["port"]))

            clients["client_2"]["ip"] = "0.0.0.0"
            clients["client_2"]["port"] = 0
            clients["client_2"]["connected"] = False
            clients["client_2"]["score"] = 0
            clients["client_2"]["last_move"] = "X"

            clients["client_1"]["score"] = 0
            clients["client_1"]["last_move"] = "X"

            odp_2 = "Przeciwnik opuscil gre!\nOczekiwanie na nowego gracza..."

            UDPServerSocket.sendto(odp_2.encode(), (clients["client_1"]["ip"], clients["client_1"]["port"]))
            
    else:
        if kom == "join":
            if not clients["client_1"]["connected"]:
                clients["client_1"]["ip"] = adres[0]
                clients["client_1"]["port"] = adres[1]
                clients["client_1"]["connected"] = True
                clients["client_1"]["score"] = 0
                clients["client_1"]["last_move"] = "X"

                odp = "Dolaczono do gry! Oczekiwanie na drugiego gracza..."

                UDPServerSocket.sendto(odp.encode(), adres)

            elif not clients["client_2"]["connected"]:
                clients["client_2"]["ip"] = adres[0]
                clients["client_2"]["port"] = adres[1]
                clients["client_2"]["connected"] = True
                clients["client_2"]["score"] = 0
                clients["client_2"]["last_move"] = "X"

                odp = "Dolaczono do gry!"

                odp_2 = "Drugi gracz dolaczyl do gry!"
                
                UDPServerSocket.sendto(odp.encode(), adres)
                UDPServerSocket.sendto(odp_2.encode(), (clients["client_1"]["ip"], clients["client_1"]["port"]))

        if kom in ["P", "K", "N"]:
            if clients["client_1"]["ip"] == adres[0] and clients["client_1"]["port"] == adres[1]:
                clients["client_1"]["last_move"] = kom[0]

                if clients["client_2"]["last_move"] != "X":
                    if check_result(clients["client_1"]["last_move"], clients["client_2"]["last_move"]) == "WYGRANA!":
                        clients["client_1"]["score"] += 1
                    elif check_result(clients["client_1"]["last_move"], clients["client_2"]["last_move"]) == "PRZEGRANA!":
                        clients["client_2"]["score"] += 1

                    odp = check_result(clients["client_1"]["last_move"], clients["client_2"]["last_move"])

                    odp_2 = check_result(clients["client_2"]["last_move"], clients["client_1"]["last_move"])

                    UDPServerSocket.sendto(odp.encode(), (clients["client_1"]["ip"], clients["client_1"]["port"]))
                    UDPServerSocket.sendto(odp_2.encode(), (clients["client_2"]["ip"], clients["client_2"]["port"]))

                    clients["client_1"]["last_move"] = "X"
                    clients["client_2"]["last_move"] = "X"

                    print(f'{clients["client_1"]["score"]}:{clients["client_2"]["score"]}')
                else:
                    odp = "Oczekiwanie na ruch przeciwnika..."

                    UDPServerSocket.sendto(odp.encode(), (clients["client_1"]["ip"], clients["client_1"]["port"]))

            elif clients["client_2"]["ip"] == adres[0] and clients["client_2"]["port"] == adres[1]:
                clients["client_2"]["last_move"] = kom[0]

                if clients["client_1"]["last_move"] != "X":
                    if check_result(clients["client_2"]["last_move"], clients["client_1"]["last_move"]) == "WYGRANA!":
                        clients["client_2"]["score"] += 1
                    elif check_result(clients["client_2"]["last_move"], clients["client_1"]["last_move"]) == "PRZEGRANA!":
                        clients["client_1"]["score"] += 1

                    odp = check_result(clients["client_1"]["last_move"], clients["client_2"]["last_move"])

                    odp_2 = check_result(clients["client_2"]["last_move"], clients["client_1"]["last_move"])

                    UDPServerSocket.sendto(odp.encode(), (clients["client_1"]["ip"], clients["client_1"]["port"]))
                    UDPServerSocket.sendto(odp_2.encode(), (clients["client_2"]["ip"], clients["client_2"]["port"]))

                    clients["client_1"]["last_move"] = "X"
                    clients["client_2"]["last_move"] = "X"

                    print(f'{clients["client_1"]["score"]}:{clients["client_2"]["score"]}')
                else:
                    odp = "Oczekiwanie na ruch przeciwnika..."

                    UDPServerSocket.sendto(odp.encode(), (clients["client_2"]["ip"], clients["client_2"]["port"]))
