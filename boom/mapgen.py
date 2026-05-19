from random import randint
from typing import cast

from . import config, types


def find_bombs(equations: list[tuple[tuple[tuple[int, int], ...], int]]):
    variables = sorted(
        {var for vars_list, _ in equations for var in vars_list}
    )

    assignment = {}
    fixed_values = None
    solutions_count = 0

    def is_possible():
        """
        Проверка, можно ли ещё достроить текущее частичное решение.
        """
        for vars_list, rhs in equations:
            current_sum = 0
            unknown_count = 0

            for var in vars_list:
                if var in assignment:
                    current_sum += assignment[var]
                else:
                    unknown_count += 1
            if current_sum > rhs:
                return False
            if current_sum + unknown_count < rhs:
                return False

        return True

    def backtrack(index):
        nonlocal fixed_values, solutions_count

        if index == len(variables):
            solutions_count += 1

            if fixed_values is None:
                fixed_values = assignment.copy()
            else:
                for var in list(fixed_values.keys()):
                    if fixed_values[var] != assignment[var]:
                        fixed_values[var] = None
            return

        var = variables[index]

        for value in (0, 1):
            assignment[var] = value
            if is_possible():
                backtrack(index + 1)
            del assignment[var]

    backtrack(0)

    if solutions_count == 0:
        return {}
    fixed_values = cast(dict, fixed_values)
    return {
        var: value for var, value in fixed_values.items() if value is not None
    }


def test_map(field: types.Field):
    result = None

    while result is None:
        equations = []
        progress = False

        for y in range(config.FIELD_HEIGHT):
            for x in range(config.FIELD_HEIGHT):
                if isinstance(field.geomap[y][x], int):
                    roots = []
                    rhs = cast(int, field.geomap[y][x])

                    neighbors = field._find_neighbors(y, x)
                    for ny, nx in neighbors:
                        cell = field.geomap[ny][nx]

                        if isinstance(cell, types.HiddenCell):
                            roots.append((ny, nx))
                        elif isinstance(cell, types.Flag):
                            rhs -= 1

                    if roots:
                        equations.append((roots, rhs))

        bombs = find_bombs(equations)

        if bombs and all(v == 1 for v in bombs.values()):
            return types.Loss

        for (y, x), res in bombs.items():
            if res == 0:
                result = field.open_cell(y, x)
                progress = True
                if isinstance(result, types.Win):
                    return types.Win()
            elif res == 1:
                field.set_flag(y, x)

        if not progress:
            break


def gen_map(first: tuple[int, int]):
    while True:
        mines = []
        while len(mines) < config.MINES_COUNT:
            rand = (
                randint(0, config.FIELD_HEIGHT - 1),
                randint(0, config.FIELD_WIDTH - 1),
            )
            if rand != first:
                mines.append(rand)

        field = types.Field(mines, config.FIELD_HEIGHT, config.FIELD_WIDTH)

        field.open_cell(*first)

        if isinstance(test_map(field), types.Win):
            break
    return mines
