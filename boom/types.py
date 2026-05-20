from collections.abc import Sequence
from typing import cast


class Cell:
    def __init__(self):
        pass


class Mine(Cell):
    def __init__(self):
        pass


class HiddenCell(Cell):
    def __init__(self):
        pass


class Flag(Cell):
    def __init__(self):
        pass


class GameStatus:
    def __init__(self):
        pass


class Loss(GameStatus):
    def __init__(self):
        pass


class Win(GameStatus):
    def __init__(self):
        pass


class Field:
    def _map_gen(self, mines):
        matrix = [[0 for _ in range(self.width)] for i in range(self.height)]

        for y, x in mines:
            matrix[y][x] = 1

        return matrix

    def __init__(self, mines: Sequence[int], height: int, width: int):
        self.width: int = width
        self.height: int = height

        self.minemap: list[list[int]] = self._map_gen(mines)
        self.geomap: list[list[int | Flag | HiddenCell]] = [
            [HiddenCell() for _ in range(width)] for _ in range(height)
        ]

    @property
    def opened_geomap(self):
        return [
            [self._findout(i, j) for j in range(self.width)]
            for i in range(self.height)
        ]

    def _find_neighbors(self, y: int, x: int):
        offsets = [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        ]

        return [
            (y + oy, x + ox)
            for oy, ox in offsets
            if x + ox > -1
            and y + oy > -1
            and x + ox < self.width
            and y + oy < self.height
        ]

    def _findout(self, y: int, x: int):
        count = 0
        neighbors = self._find_neighbors(y, x)
        if self.minemap[y][x] == 1:
            return Mine()
        for y, x in neighbors:
            if self.minemap[y][x] == 1:
                count += 1
        return count

    def is_win(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.minemap[y][x] == 0 and not isinstance(
                    self.geomap[y][x], int
                ):
                    return False
        return True

    def open_cell(self, y: int, x: int):
        if isinstance(self.geomap[y][x], Flag):
            return
        if self.minemap[y][x] == 1:
            return Loss()
        if isinstance(self.geomap[y][x], int):
            flags = 0
            goal = cast(int, self.geomap[y][x])
            neighbors = self._find_neighbors(y, x)
            for ny, nx in neighbors:
                if flags > goal:
                    break
                if isinstance(self.geomap[ny][nx], Flag):
                    flags += 1
            if flags != goal:
                return
            for ny, nx in neighbors:
                if isinstance(self.geomap[ny][nx], HiddenCell) and isinstance(
                    self.open_cell(ny, nx), Loss
                ):
                    return Loss()

        count = cast(int, self._findout(y, x))
        self.geomap[y][x] = count
        if count == 0:
            for ny, nx in self._find_neighbors(y, x):
                ncount = cast(int, self._findout(ny, nx))
                if isinstance(self.geomap[ny][nx], HiddenCell) and ncount == 0:
                    self.open_cell(ny, nx)
                if not isinstance(self.geomap[ny][nx], Flag):
                    self.geomap[ny][nx] = ncount

        if self.is_win():
            return Win()

    def set_flag(self, y: int, x: int):
        if isinstance(self.geomap[y][x], int):
            return
        elif isinstance(self.geomap[y][x], Flag):
            self.geomap[y][x] = HiddenCell()
        else:
            self.geomap[y][x] = Flag()

        if self.is_win():
            return Win()
