from random import randint
import curses
import sys


class Directions:
    """Abstract class with alliases for arrows"""
    down = 258
    up = 259
    left = 260
    right = 261 

class Point:

    y = None
    x = None

    def __init__(self, y, x):
        self.y = y
        self.x = x
    
    def draw(self, stdscr, char='1'):
        stdscr.addch(self.y, self.x, char)
    
    def erase(self, stdscr):
        stdscr.addch(self.y, self.x, ' ')

    def __str__(self):
        return f"({self.y},{self.x})"

class Body(Point):

    # Use parents class method to draw
    def draw(self, stdscr):
        super().draw(stdscr, char="#")

class Food(Point):

    # Use parents class method to draw
    def draw(self, stdscr):
        super().draw(stdscr, char='*')


class Snake:

    body = None
    length = None
    stdscr = None
    direction = None

    def __init__(self, stdscr):
        self.body = [Body(10, 12), Body(10, 11), Body(10, 10)]
        #self.body = []
        #for i in range(100):
        #    self.body.append(Body(20, 100-i))
        self.stdscr = stdscr
        self.direction = Directions.right  # by default

    def draw_snake(self):
        for i in self.body:
            i.draw(self.stdscr)

    def turn_left(self):
        self.direction = Directions.left
    def turn_right(self):
        self.direction = Directions.right
    def turn_up(self):
        self.direction = Directions.up
    def turn_down(self):
        self.direction = Directions.down

    def eats_itself(self):
        for i in self.body[1:]:
            if str(i) == str(self.body[0]):
                return True
        return False

class Map:

    height = None
    width = None
    ofset = None
    snake = None
    food = None

    def __init__(self, stdscr, h, w, snake: Snake, ofset=1):
        self.height = h
        self.width = w
        self.stdscr = stdscr
        self.ofset = ofset
        self.snake = snake

    def add_food(self):
        y = randint(self.ofset+1, self.height-self.ofset-1)
        x = randint(self.ofset+1, self.width-self.ofset-1)
        self.food = Food(y, x)

    def draw_map(self, score, border_ch="@"):
        # Drawing score
        text = f"Score: {score}"
        # Drawing border
        self.stdscr.addstr(0, self.width//2-(len(text)), text)
        for i in range(self.height-self.ofset*2):
            self.stdscr.addch(i+self.ofset, self.ofset, border_ch)
            self.stdscr.addch(i+self.ofset, self.width-self.ofset, border_ch)
        for i in range(self.width-self.ofset*2):
            self.stdscr.addch(self.ofset, i+self.ofset, border_ch)
            self.stdscr.addch(self.height-self.ofset, i+self.ofset, border_ch)
        # Drawing food
        self.food.draw(self.stdscr)

class Game:

    stdscr = None
    h, w = None, None
    game_area = None
    snake = None
    score = 0
    menu_list = ['Start', 'Exit']

    def __init__(self, stdscr, game_area: Map, snake: Snake):
        self.stdscr = stdscr
        self.h, self.w = stdscr.getmaxyx()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        self.game_area = game_area
        self.snake = snake

    def main(self):
        self.stdscr.clear()
        curses.curs_set(0)
        self.stdscr.nodelay(1)
        # width has more pixels than heigth
        k = int((self.w / self.h))
        game_speed = 500
        vertical_speed = game_speed * k
        self.stdscr.timeout(game_speed)
        self.game_area.add_food()

        while True:
            ch = self.stdscr.getch()
            head = self.snake.body[0]
            vertical_speed = game_speed * k

            # Change direction if arrow key was hit 
            if ch == curses.KEY_DOWN:
                self.snake.turn_down()
                self.stdscr.timeout(vertical_speed)
            elif ch == curses.KEY_UP:
                self.snake.turn_up()
                self.stdscr.timeout(vertical_speed)
            elif ch == curses.KEY_LEFT:
                self.snake.turn_left()
                self.stdscr.timeout(game_speed)
            elif ch == curses.KEY_RIGHT:
                self.snake.turn_right()
                self.stdscr.timeout(game_speed)

            # Move head to next possition depends on direction
            if self.snake.direction == Directions.down:
                new_head = Body(head.y+1, head.x)
            elif self.snake.direction == Directions.up:
                new_head = Body(head.y-1, head.x)
            elif self.snake.direction == Directions.left:
                new_head = Body(head.y, head.x-1)
            elif self.snake.direction == Directions.right:
                new_head = Body(head.y, head.x+1)

            # Add new head
            self.snake.body.insert(0, new_head)
            # Remove last part of the body
            self.snake.body[-1].erase(self.stdscr)
            self.snake.body.pop()
            self.game_area.draw_map(self.score)
            self.snake.draw_snake()

            # Check if snake hit the wall
            if (new_head.x == self.game_area.ofset or new_head.y == self.game_area.ofset or
                new_head.x == self.game_area.width-self.game_area.ofset or 
                new_head.y == self.game_area.height-self.game_area.ofset):
                self.game_over()
                break

            # If snakes eats itself
            if self.snake.eats_itself():
                self.game_over()
                break

            # If snakes eats food
            if str(self.snake.body[0]) == str(self.game_area.food):
                self.snake.body.append(Body(0,0))
                self.score += 1
                del self.game_area.food
                self.game_area.add_food()
                game_speed = int(game_speed * 0.9)
        
            self.stdscr.refresh()

    def main_menu(self):
        curses.curs_set(0)
        self.stdscr.nodelay(0)
        self.stdscr.clear()
        hh = self.h//2; hw = self.w//2
        curent_option = 0

        while True:
            for i, text in enumerate(self.menu_list):
                if i == curent_option:
                    self.stdscr.attron(curses.color_pair(1))
                    self.stdscr.addstr(hh-len(text), hw-len(text), text)
                    self.stdscr.attroff(curses.color_pair(1))
                else:
                    self.stdscr.addstr(hh-len(text), hw-len(text), text)
    
            ch = self.stdscr.getch()
            if ch == curses.KEY_DOWN and curent_option+1 < len(self.menu_list):
                curent_option += 1
            elif ch == curses.KEY_UP and curent_option > 0:
                curent_option -= 1
            elif ch == curses.KEY_ENTER or ch in [10, 13]:
                return self.menu_list[curent_option]

    def game_over(self):
        curses.curs_set(0)
        self.stdscr.nodelay(0)
        self.stdscr.clear()
        hh = self.h//2; hw = self.w//2
        text = "Game over"
        self.stdscr.attron(curses.color_pair(1))
        self.stdscr.addstr(hh-len(text), hw-len(text), text)
        self.stdscr.addstr(hh-len(text)+1, hw-len(text)+1, f"Score: {self.score}")
        self.stdscr.attroff(curses.color_pair(1))
        self.stdscr.refresh()
        self.stdscr.getch()


# Method to pass into wrapper to get stdscr object
def start_game(stdscr):
    h, w = stdscr.getmaxyx()
    snake = Snake(stdscr)
    game_area = Map(stdscr,h, w, snake)
    game = Game(stdscr, game_area, snake)
    choose = game.main_menu()
    if choose == "Start":
        game.main()
    elif choose == "Exit":
        sys.exit()

curses.wrapper(start_game)
