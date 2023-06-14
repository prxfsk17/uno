#игральная карта
class Card:
    #аттрибуты - цвет, значение, позиция на экране(левый верхний угол)
    color : int
    value : int
    x : int
    y : int

    #конструктор карты
    def __init__(self, c: int, v: int):
        self.value = v
        self.color = c
        self.x = 0
        self.y = 0