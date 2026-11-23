import sys
import os

import curses
import random
import time
import threading
import queue
import json
from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs


# Answers for Exercise 1:
#
# 1.The GET parameters are key and k.
# The key parameter is used by the server to know which key the client pressed and how to move the snake accordingly. This parameter is optional because the client does not have to press a key in every request.
# The k parameter is used by the server to know which screen updates the client has already received and which ones it still needs to receive. This parameter is **optional** because without it, we would have to send all the screen updates each time. It would be inefficient, but it would still work.
#
# 2.The response is a JSON array containing screen updates. Each update is an array of three values: y, x and char. y represents the row on the screen, x represents the column on the screen and char represents the character at that position







# Global shared queue for communication between HTTP server and Game Loop
requests_queue = queue.Queue()

updates = []

class Snake:
    """Snake class handles the position in a snake game"""

    def __init__(self,
                 screen_height,
                 screen_width,
                 initial_grow=5):
        """Init Snake position on the screen.
        Args:
            screen_height, screen_width - screen dimensions
            initial_grow - initial grow of the snake
        """
        self._body = [(screen_height // 2, screen_width // 2)]  # body contains (y,x) tuples
        self._grow = initial_grow
        self._screen_height = screen_height
        self._screen_width = screen_width

    def move_up(self):
        self.move((-1, 0))

    def move_down(self):
        self.move((1, 0))

    def move_left(self):
        self.move((0, -1))

    def move_right(self):
        self.move((0, 1))

    def move(self, direction_yx):
        if direction_yx[0] > 1 or direction_yx[0] < -1 or direction_yx[1] > 1 or direction_yx[1] < -1:
            raise ValueError("Invalid direction")
        hy, hx = self._body[-1]
        self._extend((hy + direction_yx[0]) % self._screen_height, (hx + direction_yx[1]) % self._screen_width)

    def _extend(self, y, x):
        if (y, x) in self._body:
            raise ValueError("Cannot move over myself")
        self._body.append((y, x))
        if self._grow <= 0:
            self._body.pop(0)
        else:
            self._grow -= 1

    def eat(self, grow=5):
        self._grow += grow

    def __len__(self):
        return len(self._body)

    def __contains__(self, item):
        return item in self._body

    def head(self):
        return self._body[-1]

    def tail(self):
        return self._body[0]


class SnakeGame:
    def __init__(self, screen_height, screen_width):
        self._snake = Snake(screen_height, screen_width, 5)
        self._screen_height = screen_height
        self._screen_width = screen_width
        self._direction_yx = (0, 1)
        self.food = self.food_position()

    def food_position(self):
        nf = None
        # try to find random position that is not in snake. When snake almos fills
        # the screen, it is better to use a loop to find a position that is not in snake
        n_try = self._screen_height * self._screen_width
        while nf is None or nf in self._snake:
            n_try -= 1
            if n_try == 0:
                break
            nf = (random.randint(1, self._screen_height - 2), random.randint(1, self._screen_width - 2))

        if nf:
            return nf
        # could not find via random - just loop the screen
        for y in range(self._screen_height):
            for x in range(self._screen_width):
                if (y, x) not in self._snake:
                    return (y, x)
        return None

    def progress(self, screen_update_func):
        try:
            old_tail = self._snake.tail()
            self._snake.move(self._direction_yx)
            new_head = self._snake.head()
            new_tail = self._snake.tail()
            screen_update_func(new_head[0], new_head[1], "#")
            if new_tail != old_tail:
                screen_update_func(old_tail[0], old_tail[1], " ")
        except ValueError as e:
            return False
        if self.food == self._snake.head():
            self._snake.eat()
            self.food = self.food_position()
            screen_update_func(self.food[0], self.food[1], "*")
        return True

    def set_direction(self, direction_yx):
        self._direction_yx = direction_yx


def is_quit_key(key):
    return key == 27 or key == ord('q') or key == ord('Q')


def update_direction(cur_dir, key):
    if key == -1:
        return cur_dir
    if key == curses.KEY_UP and cur_dir != (1, 0):
        return (-1, 0)
    if key == curses.KEY_DOWN and cur_dir != (-1, 0):
        return (1, 0)
    if key == curses.KEY_LEFT and cur_dir != (0, 1):
        return (0, -1)
    if key == curses.KEY_RIGHT and cur_dir != (0, -1):
        return (0, 1)
    return cur_dir


def show_game_over(game_io):
    screen_height, screen_width = game_io.getmaxyx()
    game_io.screen_update(screen_height // 2, screen_width // 2 - 5, "GAME OVER")
    game_io.screen_update(screen_height // 2 + 1, screen_width // 2 - 10, "Press any key to restart, Q to quit")
    game_io.refresh()
    # Wait for key press
    while True:
        key = game_io.get_key()
        if key != -1:
            return is_quit_key(key)
        time.sleep(0.1)
    return False


class GameIO:
    def __init__(self, stdscr):
        self._stdscr = stdscr
        curses.curs_set(0)
        self._stdscr.nodelay(1)  # make getch non-blocking

    def get_key(self):
        if not requests_queue.empty():
            tup = requests_queue.get()
            k = tup[1]
            q = tup[2]
            q.put(updates[k:])
            if tup[0] != None:
                return tup[0]

        return self._stdscr.getch()

    def screen_update(self, y, x, c):
        updates.append((y,x,c))
        self._stdscr.addstr(y, x, c)

    def refresh(self):
        self._stdscr.refresh()

    def getmaxyx(self):
        return self._stdscr.getmaxyx()


def snake_loop(stdscr):
    # Turn off cursor blinking (not implemented in webcurses but good practice)
    game_io = GameIO(stdscr)
    quit_game = False

    while not quit_game:
        stdscr.clear()
        screen_height, screen_width = stdscr.getmaxyx()
        snake_game = SnakeGame(screen_height, screen_width)
        speed_delay = 0.15
        # show intial food
        game_io.screen_update(snake_game.food[0], snake_game.food[1], "*")

        direction_yx = (0, 1)
        # starting a new game
        while True:
            key = game_io.get_key()
            direction_yx = update_direction(direction_yx, key)
            snake_game.set_direction(direction_yx)
            quit_game = is_quit_key(key)
            if quit_game:
                break

            if not snake_game.progress(game_io.screen_update):
                quit_game = show_game_over(game_io)
                break

            game_io.refresh()

            # Control game speed
            time.sleep(speed_delay)


class GameHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Silence server logging
        pass

    def do_GET(self):
        # Parse query parameters
        query = parse_qs(urlparse(self.path).query)
        # k is the index from which we want updates
        k_param = query.get('k', ['0'])[0]
        k = int(k_param) if k_param is not None else 0
        # key is the optional keycode to simulate
        key_param = query.get('key', [None])[0]
        key = int(key_param) if key_param is not None else None


        q = queue.Queue()
        request_item = (key, k, q)
        requests_queue.put(request_item)


        updates = q.get()
        # return updates


        response_data = json.dumps(updates)
        # Prepare and send response
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(response_data.encode("utf-8"))


def main():
    server_address = ("", 8080)  # Listen on all interfaces, port 8080
    # Use ThreadingHTTPServer to handle multiple requests concurrently
    httpd = ThreadingHTTPServer(server_address, GameHandler)
    print("Serving on port 8080...")
    # Create a thread object, targeting the serve_forever method
    server_thread = threading.Thread(target=httpd.serve_forever)
    # Set as a daemon thread so it exits when the main program does
    server_thread.daemon = True
    server_thread.start()
    curses.wrapper(snake_loop)


if __name__ == "__main__":
    main()

