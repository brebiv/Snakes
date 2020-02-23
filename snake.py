from random import randint
import curses


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
        super().draw(stdscr, char='#')

class Food(Point):

    # Use parents class method to draw
    def draw(self, stdscr):
        super().draw(stdscr, char='*')


class Snake:

    body = None
    length = None
    stdscr = None
    direction = None
    score = 0

    def __init__(self, stdscr):
        self.body = [Body(10, 12), Body(10, 11), Body(10, 10)]
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

    def draw_map(self, border_ch="@"):
        # Drawing score
        text = f"Score: {self.snake.score}"
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

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)
    timeout = 300

    h, w = stdscr.getmaxyx()

    snake = Snake(stdscr)
    game_area = Map(stdscr, h, w, snake)
    game_area.add_food()

    while True:
        ch = stdscr.getch()
        head = snake.body[0]
        stdscr.timeout(timeout)
        
        # Change direction if arrow key was hit 
        if ch == curses.KEY_DOWN:
            snake.turn_down()
            stdscr.timeout(int(timeout*1.5))
        elif ch == curses.KEY_UP:
            snake.turn_up()
            stdscr.timeout(int(timeout*1.5))
        elif ch == curses.KEY_LEFT:
            snake.turn_left()
        elif ch == curses.KEY_RIGHT:
            snake.turn_right()

        # Move head to next possition depends on direction
        if snake.direction == Directions.down:
            new_head = Body(head.y+1, head.x)
        elif snake.direction == Directions.up:
            new_head = Body(head.y-1, head.x)
        elif snake.direction == Directions.left:
            new_head = Body(head.y, head.x-1)
        elif snake.direction == Directions.right:
            new_head = Body(head.y, head.x+1)

        # Add new head
        snake.body.insert(0, new_head)
        # Remove last part of the body
        snake.body[-1].erase(stdscr)
        snake.body.pop()
        game_area.draw_map()
        snake.draw_snake()

        # Check if snake hit the wall
        if (new_head.x == game_area.ofset or new_head.y == game_area.ofset or
            new_head.x == game_area.width-game_area.ofset or 
            new_head.y == game_area.height-game_area.ofset):
            break
        
        # If snakes eats itself
        if snake.eats_itself():
            break
        
        # If snakes eats food
        if str(snake.body[0]) == str(game_area.food):
            snake.body.append(Body(0,0))
            snake.score += 1
            del game_area.food
            game_area.add_food()
            timeout = int(timeout * 0.9)
        

        stdscr.refresh()

curses.wrapper(main)