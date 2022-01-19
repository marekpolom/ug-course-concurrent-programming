import socket

serwerAdresPort = ("127.0.0.1", 5001)
klientAdresPort = ("127.0.0.1", 5003)

bufSize = 2048

score = 0

UDPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while(True):
    komA = str.encode(input())
    UDPClientSocket.sendto(komA, serwerAdresPort)
    odp, adres = UDPClientSocket.recvfrom(bufSize)
    odp = odp.decode()

    print(odp)

    if odp == "WYGRANA!":
        score += 1
        print(f'Twoje punkty {score}')
    elif odp in ["REMIS", "PRZEGRANA!"]:
        print(f'Twoje punkty {score}')

    if odp == "Dolaczono do gry! Oczekiwanie na drugiego gracza...":
        odp, adres = UDPClientSocket.recvfrom(bufSize)
        odp = odp.decode()

        print(odp)

    if odp == "Przeciwnik opuscil gre!\nOczekiwanie na nowego gracza...":
        odp, adres = UDPClientSocket.recvfrom(bufSize)
        odp = odp.decode()

        print(odp)

    if odp == "Serwer pelny, nie mozesz dolaczyc do gry w czasie jej trwania!":
        break

    if odp == "Oczekiwanie na ruch przeciwnika...":
        odp, adres = UDPClientSocket.recvfrom(bufSize)
        odp = odp.decode()

        print(odp)

        if odp == "WYGRANA!":
            score += 1
            print(f'Twoje punkty {score}')
        elif odp in ["REMIS", "PRZEGRANA!"]:
            print(f'Twoje punkty {score}')

    if odp == "Opuszczanie gry...":
        break
