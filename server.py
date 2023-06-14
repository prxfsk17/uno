import socket
import pygame
from card import Card
import random

#Инициализируем первую карту
FPS = 100
WIDTH_SERVER_WINDOW, HEIGHT_SERVER_WINDOW = 300, 300
cardOnTable = Card(random.randint(1,4),random.randint(1,9))

#Объявляем игрока
class Player():
    def __init__(self, conn, addr, count):
        self.conn = conn
        self.addr = addr
        self.count = count

# главный сокет только для проверки подключения новых игроков
main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# отключает алгоритм Нейгла, чтобы сервер не отправлял данные в пакетах
main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

# IP address, port
# связали сокет с портом компьютера
main_socket.bind(('0.0.0.0', 10000))

# чтобы игра не прерывалась, пока игроки отправляют данные серверу
main_socket.setblocking(0)

# максимальное число игроков которые могут подключиться - 5, начинаем прослушку
main_socket.listen(5)

#Запускаем сервер
pygame.init()
screen = pygame.display.set_mode((WIDTH_SERVER_WINDOW, HEIGHT_SERVER_WINDOW))
clock = pygame.time.Clock()
print('socket created')
server_works = True
players=[]

#Подготавливаемся к отправке новым пользователям начальных данных
cardTable = str(cardOnTable.color).encode() + '/'.encode()+ str(cardOnTable.value).encode()
fl = False
currentPl = 1
enemyCards1 = 7
enemyCards2 = 7

while server_works:
    clock.tick(FPS)
    # проверим есть ли желающие  войти в игру
    # возвращает новый сокет под игрока и адрес подключивщегося игрока
    try:
        new_socket, addr = main_socket.accept()
        print('Подключился ', addr)
        new_socket.setblocking(0)
        new_player = Player(new_socket, addr, 7)
        players.append(new_player)

        #Отправляем новым игрокам первую карту и их личный номер
        new_socket.send(str(len(players)).encode() + cardTable)
    except:

        pass
    data = ''
    if not fl:
        cardToSendClients=cardTable
        fl = True

    # считываем команды игроков
    for player in players:

        #образец получаемых данных data: 11/39
        try:
            data = player.conn.recv(1024) #receive 1024 bytes
            data = data.decode()

            #если новой информации не поступило
            if data != 'nothing':

                #если игрок взял карту - смена хода
                if data == 'putting':
                    cpl = currentPl

                    if currentPl == 1:
                        currentPl = 2

                    elif cpl == 2:
                        currentPl = 1
                else:
                    currentPl = int(data[0])
                    if len(data) > 5:
                        enCards = int(data[4:6])
                    else:
                        enCards = int(data[4])

                    #получаем данные
                    data = data[1:4]
                    data = data.encode()

                    #если они новые
                    if data != cardToSendClients:
                        cardToSendClients = data
                        cpl = currentPl

                        #меняем ход и запоминаем количество карт у игроков
                        if currentPl == 1:
                            currentPl = 2
                            players[0].count=enCards

                        elif cpl == 2:
                            currentPl = 1
                            players[1].count = enCards

                        if enemyCards1 > 9:
                            enemyCards1 = 9
                        if enemyCards2 > 9:
                            enemyCards2 = 9
                        break
        except:
            pass

    # отправляем новое состояние игрового поля
    for player in players:
        try:

            #если уже подключились игроки
            if len(players) == 2:
                player.conn.send(str(currentPl).encode() + cardToSendClients+str(players[0].count).encode()+str(players[1].count).encode())
            else:
                #если игроки еще не подключились
                player.conn.send(str(currentPl).encode() + cardToSendClients+'77'.encode())

        except:
            #если не получилось отправить данные, скорее всего игрок отключился
            print('Player disconnected ')

    #если кто-то из игроков выиграл, закрываем их сокеты
    if enemyCards1 == 0:
        for sock in players:
            sock.close()
            players.remove(sock)
    if enemyCards2 == 0:
        for sock in players:
            sock.close()
            players.remove(sock)

    #если сервер закрыт
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            server_works = False

#удаляем еще подключенных игроков
for sock in players:
    sock.close()
    players.remove(sock)

#закрываем сервер
pygame.quit()
main_socket.close()