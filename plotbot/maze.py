import cairo
import click
import io
import numpy as np
import random


class Maze(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.walls = []
        self.cells = np.zeros((width, height), dtype=int)

        self.layout()

    def adjacent_list(self, point):
        x, y = point
        lst = []
        if x > 0:
            lst.append(point + [-1, 0])
        if y > 0:
            lst.append(point + [0, -1])
        if x < self.width - 1:
            lst.append(point + [1, 0])
        if y < self.height - 1:
            lst.append(point + [0, 1])
        return lst

    def addwalls(self, cell):
        for w in self.adjacent_list(cell):
            if self.cells[tuple(w)] == 0:
                self.walls.append(w)

    def find_maze_neighbors(self, wall):
        for neighbor in self.adjacent_list(wall):
            if self.cells[tuple(neighbor)] == 1:
                yield neighbor

    def connection_count(self, point):
        return sum(self.cells[tuple(n)] for n in self.adjacent_list(point))

    def can_break_wall(self, wall):
        return len(list(self.find_maze_neighbors(wall))) == 1

    def delist_wall(self, wall):
        self.walls = [w for w in self.walls if np.all(w != wall)]

    def break_wall(self, wall):
        self.cells[tuple(wall)] = 1
        self.delist_wall(wall)
        self.addwalls(wall)
        return wall

    def layout(self):
        sx = np.array([random.randint(0, self.width - 1),
                       random.randint(0, self.height - 1)])
        self.cells[tuple(sx)] = 1
        self.addwalls(sx)

        while len(self.walls) > 0:
            w = random.choice(self.walls)
            if self.can_break_wall(w):
                self.break_wall(w)
            else:
                self.delist_wall(w)

    def to_svg(self):
        s = 10

        f = io.BytesIO()
        surface = cairo.SVGSurface(f, self.width * s, self.height * s)
        c = cairo.Context(surface)

        c.rectangle(0, 0, self.width * s, self.height * s)

        c.set_line_width(0.1)
        c.set_source_rgb(0, 0, 0)

        def line(x0, y0, x1, y1):
            c.move_to(x0 * s, y0 * s)
            c.line_to(x1 * s, y1 * s)
            c.close_path()

        for x in range(self.width):
            for y in range(self.height):
                if self.cells[x, y] == 1:
                    if x > 0 and self.cells[x - 1, y] == 0:
                        line(x, y, x, y + 1)
                    if y > 0 and self.cells[x, y - 1] == 0:
                        line(x, y, x + 1, y)
                    if x < self.width - 1 and self.cells[x + 1, y] == 0:
                        line(x + 1, y, x + 1, y + 1)
                    if y < self.height - 1 and self.cells[x, y + 1] == 0:
                        line(x, y + 1, x + 1, y + 1)

        c.stroke()
        surface.finish()
        surface.flush()
        return f.getvalue()


@click.command(name='maze')
@click.option('--width', default=110, type=int, help='Width in cells')
@click.option('--height', default=85, type=int, help='Height in cells')
def run(width, height):
    m = Maze(width, height)
    open('foo.svg', 'wb').write(m.to_svg())
