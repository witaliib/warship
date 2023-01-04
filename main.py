from random import randint


# Классы исключения
class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"

class BoardWrongShipException(BoardException):
    pass


# Класс Dot
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"

# Класс Ship
class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l


    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots

# Класс - Board
class Board:

    # Параметры доски
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.count = 0

        self.field = [["O"] * size for _ in range(size)]

        self.busy = []
        self.ships = []

    # Рисуем доску
    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "O")
        return res

    # Проверка на то что точка находится вне доски
    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))




    # Контур корабля
    def contour(self, ship, verb=False):

        # Точки вокруг корабля
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]

        # Цикл прохода точки
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    # Добавление корабля
    def add_ship(self, ship):
        # Проверка за выход за границы и на занятость
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()

        # Песать коробля
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    # Метод - Стрельба
    def shot(self, d):

        # Проверка - выхода за границу
        if self.out(d):
            raise BoardOutException()

        # Проверка - точка занята?
        if d in self.busy:
            raise BoardUsedException()

        # Точка занята
        self.busy.append(d)

        # Проверка принадлежности точки к кораблю
        for ship in self.ships:
            if ship.shooten(d):
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []

    def defeat(self):
        return self.count == len(self.ships)


# Класс - Игрок
class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    # Бесконечная попытка сделать выстрел
    def move(self):
        while True:
            try:
                # Просим координаты
                target = self.ask()

                # Выполняем выстрел
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

# Класс AI (генерируем точку случайно)
class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d

# Класс Игрок
class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()


            # Запрос координат
            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            # Проверка на числа
            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            # Возвращаем точку с координатами (-1)
            return Dot(x - 1, y - 1)

# Класс Game
class Game:

    def __init__(self, size=6):

        # Указываем размер доски
        self.size = size

        # Генерируем доску для Игрока
        pl = self.random_board()

        # Генерируем доску для компьютера
        co = self.random_board()

        # Прячем доску компьютера для игрока
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def try_board(self):

        # Список длинн кораблей
        lens = [3, 2, 2, 1, 1, 1, 1]

        # Создаем доску
        board = Board(size=self.size)
        attempts = 0

        # Пытаемся расставить корабли
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    # Генерируем случайную доску
    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board


    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")


    # Игровой цикл
    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            print("-" * 20)
            if num % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.defeat():
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.board.defeat():
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()

g = Game()
g.start()
