import socket
import pygame
import random
from card import Card
import pygame_menu

#карты игрока, сопа и порядковый номер на сервере
myCards : list = []
enemySet : list = []
numberOfPl = 0

#add new card from deck to player
def incCards():
    newCard = Card(random.randint(1,4),random.randint(1,9))
    myCards.append(newCard)
    renewPos()

#all cards set new positions
def renewPos():
    stX = 800
    l = len(myCards)
    if (l % 2 != 0):
        stX = 750
    stX = stX - (l / 2) * 75
    for i in range(l):
        myCards[i].y = 850
        myCards[i].x = stX
        stX = stX + 100

#all enemy cards set new positions
def renewEnemyPos():
    stX = 800
    l = len(enemySet)
    if (l % 2 != 0):
        stX = 750
    stX = stX - (l / 2) * 75
    for i in range(l):
        enemySet[i].y = 0
        enemySet[i].x = stX
        stX = stX + 100

#проверка, можно ли положить данную карту
def canBePlayed(cardToPlay, mainCard) -> bool:
    if cardToPlay.color == mainCard.color:
        return True
    if cardToPlay.value == mainCard.value:
        return True
    return False

#удалить карту из рук игрока
def delFromPl(cardToPlay):
    try:
        myCards.remove(cardToPlay)
    except:
        pass

#чтобы извлечь имя спрайта
def getName(c : Card) -> str:
    name : str = 'images/'
    if c.color == 1:
        name = name + 'blue'
    elif c.color == 2:
        name = name + 'green'
    elif c.color == 3:
        name = name + 'red'
    elif c.color == 4:
        name = name + 'yellow'
    else:
        name = name + 'blue'
    name = name + str(c.value) + '.jpg'
    return name

#устанавливаем соединение с сервером
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
sock.connect(('localhost',10000))

WIDTH_WINDOW, HEIGHT_WINDOW = 1600, 1000

#создание окна игры
pygame.init()
bg_img = pygame.image.load('images/uno-card-game-btuowx697fmraih0.jpg')
bg2_img = pygame.image.load('images/resback.jpg')
screen = pygame.display.set_mode((WIDTH_WINDOW,HEIGHT_WINDOW))
pygame.display.set_caption('Uno Online')

#начало главного цикла игры
def start_the_game():
    background_surf = pygame.image.load('images/background.jpg')

    #функция для проверки на конец игры
    def isEnd(c1: int, c2: int) -> bool:
        if c1 == 0:
            return True
        if c2 == 0:
            return True
        return False

    #закончена ли игра
    isGameOver = False

    #выиграл ли этот клиент
    isMyWin = False

    #раздача первых карт клиенту
    # blue - 1, green - 2, red - 3, yellow - 4
    for i in range(7):
        v = random.randint(1, 9)
        c = random.randint(1, 4)
        card = Card(c, v)
        myCards.append(card)
        enemySet.append(Card(1, 1))
    renewPos()

    #игра в процессе
    isRunning = True

    #после сыгровки останется 1 карта
    isUno = False

    #ход данного клиента
    isMyPut = False

    #получаем начальную карту стола
    data = sock.recv(1024)
    data = data.decode()
    newCol = int(data[1])
    newVal = int(data[3])
    numberOfPl = int(data[0])

    #устанавливаем ее как главную и даем ей координаты
    mainCard = Card(newCol, newVal)
    mainCard.x = 750
    mainCard.y = 425
    cardToPlay = mainCard

    #пока идет игра
    while isRunning:

        isIncCards = False
        isPlayed = False

        #обработка событий
        for event in pygame.event.get():

            #если нажат крестик
            if event.type == pygame.QUIT:
                isRunning = False

            #если ход клиента
            if isMyPut:

                #проверяем клик по каждой из карточек
                if event.type == pygame.MOUSEBUTTONDOWN:

                    #позиция мышки
                    pos = pygame.mouse.get_pos()
                    for i in range(len(myCards)):
                        rect = pygame.rect.Rect(myCards[i].x, myCards[i].y, 100, 150)
                        backrect = pygame.rect.Rect(100, 425, 100, 150)
                        unorect = pygame.rect.Rect(1300, 450, 200, 100)
                        print(pos)

                        #проверяем возможные нажатия мыши
                        if (unorect.collidepoint(pos)) and (len(myCards) == 2):
                            isUno = True
                        if backrect.collidepoint(pos):
                            isIncCards = True
                        if rect.collidepoint(pos):
                            isPlayed = True
                            cardToPlay = myCards[i]
                            break

        #считываем команду игрока
        #если игрок забыл нажать уно
        if (len(myCards) == 1) and (isUno == False):
            incCards()
            incCards()

        #если игрок набирает карты
        if isIncCards:
            isUno = False
            incCards()
            isMyPut = False

        #если клиент играет карту
        if canBePlayed(cardToPlay, mainCard) and isPlayed:

            #удаляем из колоды игрока карту
            delFromPl(cardToPlay)

            renewPos()

            #отправляем команду на сервер
            st = str(numberOfPl).encode() + str(cardToPlay.color).encode()+ '/'.encode() + str(cardToPlay.value).encode()
            sock.send(st+str(len(myCards)).encode())
            isMyPut = False

        #если игрок набрал карту, на сервер отправляется другая команда
        elif isIncCards:
            sock.send('putting'.encode())
        else:

            #если ничего не произошло
            sock.send('nothing'.encode())

        #получаем от сервера новое состояние игрового поля
        try:

            #получает данные с сервера
            data = sock.recv(1024)
            data = data.decode()

            #узнаем количество карт игроков
            enemyCards1 = int(data[4])
            enemyCards2 = int(data[5])

            #узнаем количество карт соперника
            if numberOfPl == 1:
                enemyCards = enemyCards2
            else:
                enemyCards = enemyCards1

            #редактируем локально количество карт соперника
            if enemyCards<len(enemySet):
                enemySet.pop(0)
            if enemyCards>len(enemySet):
                enemySet.append(Card(1,1))

            #узнаем ход клиента ли сейчас
            if numberOfPl == int(data[0]):
                isMyPut = True
            else:
                isMyPut = False
        except:
            pass

        try:
            #кладем на стол новую карту если таковая есть
            newCol = int(data[1])
            newVal = int(data[3])
            mainCard = Card(newCol, newVal)
            mainCard.x = 750
            mainCard.y = 425

        except:
            pass

        #проверяем конец ли игры
        if (isGameOver) or isEnd(len(myCards), len(enemySet)):
            if len(myCards) == 0:
                isMyWin = True
            else:
                isMyWin = False
            #выходим с игрового стола
            break

        #рисуем новое состояние игрового поля
        screen.blit(background_surf, [0,0])

        #колода
        backside = pygame.image.load('images/backside.jpg')
        backside = pygame.transform.scale(backside, (100, 150))
        screen.blit(backside, [100, 425])

        #карты соперника
        renewEnemyPos()
        for i in range(len(enemySet)):
            backside = pygame.image.load('images/backside.jpg')
            backside = pygame.transform.scale(backside, (100, 150))
            backside = pygame.transform.rotate(backside, 180)
            screen.blit(backside, [enemySet[i].x, enemySet[i].y])

        #кнопка уно
        unobtn = pygame.image.load('images/UNO.png')
        unobtn = pygame.transform.scale(unobtn, (200, 100))
        screen.blit (unobtn, [1300, 450])

        #карты игрока
        playedCardImg = pygame.image.load(getName(mainCard))
        playedCardImg = pygame.transform.scale(playedCardImg, (100,150))
        screen.blit(playedCardImg, [mainCard.x, mainCard.y])
        for i in range(len(myCards)):
            background_surf = pygame.image.load('images/background.jpg')
            s = getName(myCards[i])
            cardToDraw = pygame.image.load(s)
            cardToDraw = pygame.transform.scale(cardToDraw, (100, 150))
            screen.blit(cardToDraw, [myCards[i].x, myCards[i].y])
            print(myCards[i].x, ' ', myCards[i].y)

        #обновляем экран
        pygame.display.update()

    #меню в конце игры
    menu2 = pygame_menu.Menu('Uno Online', 400, 300,
                            theme=pygame_menu.themes.THEME_BLUE)
    if isMyWin:
        #если клиент выиграл
        menu2.add.label('Вы выиграли!')
    else:
        #если клиент проиграл
        menu2.add.label('Вы проиграли!')
    menu2.add.button('Выйти из игры', pygame_menu.events.EXIT)
    while True:

        #отображаем меню концовки
        screen.blit(bg2_img, [0, 0])
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                exit()

        if menu2.is_enabled():
            menu2.update(events)
            menu2.draw(screen)

        #обновляем экран
        pygame.display.update()

#меню старта игры
menu = pygame_menu.Menu('Uno Online', 400, 300,
                       theme=pygame_menu.themes.THEME_BLUE)

menu.add.button('Играть', start_the_game)
menu.add.button('Выйти из игры', pygame_menu.events.EXIT)
while True:

    #обновляем картинку
    screen.blit(bg_img, [0,0])
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            exit()

    if menu.is_enabled():
        menu.update(events)
        menu.draw(screen)

    #обновляем экран
    pygame.display.update()

#выходим из игры
pygame.quit()
sock.close()