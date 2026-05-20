import json
import os

from boom import config
from boom.get_key import get_key
from boom.mapgen import gen_map
from boom.types import Field, Flag, HiddenCell, Loss, Mine, Win

logo = r"""________      _______      _______    ___     ___
|       \    /  ___  \    /  ___  \   |  \   /  |
|  | \   |  |   | |   |  |   | |   |  | |\\_//| | 
|  | |   |  |   | |   |  |   | |   |  | | \_/ | |
|  | /  /   |    \|   |  |   |/    |  | |     | |
|       |    \       /    \       /    \|     | |
|  | \   \    \     /      \     /            | |
|  | |   /     \   /        \   /             | |
|  | /  /       \_/          \_/              | |
|______/                                       \|"""


with open("boom/localization.json", encoding="utf-8") as fp:
    localization = json.load(fp)
info = [
    *["\033[1m" + i for i in logo.splitlines()],
    "",
    *localization[config.LANGUAGE]["info"],
]

colors = {
    1: "\033[94m" + "1",
    2: "\033[32m" + "2",
    3: "\033[91m" + "3",
    4: "\033[34m" + "4",
    5: "\033[31m" + "5",
    6: "\033[36m" + "6",
    7: "7",
    8: "\033[35m" + "8",
}


def be_out(geomap: list[list]):
    if config.CLEAR:
        os.system("cls" if os.name == "nt" else "clear")
    info_row = -1

    def dynamic_info_row():
        nonlocal info_row
        if config.SHOW_INFO and info_row + 1 < len(info):
            info_row += 1
            return info_space + info[info_row] + "\033[0m"
        return ""

    info_space = " " * 5
    print(
        "┌"
        + "┬".join(["─" * 3] * config.FIELD_WIDTH)
        + "┐"
        + dynamic_info_row()
    )
    for r, row in enumerate(geomap):
        out = ""
        for jr, j in enumerate(row):
            out += "│"
            if (
                r == selected_y
                and jr == selected_x
                and isinstance(j, HiddenCell)
            ):
                out += "\033[90m"
            elif r == selected_y and jr == selected_x:
                out += "\033[100m"
            if isinstance(j, Mine):
                out += " \033[31m☠ "
            elif isinstance(j, HiddenCell):
                out += "▓▓▓"
            elif isinstance(j, Flag):
                out += "╳\033[31m⫸ "
            elif j == 0:
                out += "   "
            else:
                out += " " + colors[j] + " "
            out += "\033[0m"
        print(out + "│" + dynamic_info_row())
        if r != config.FIELD_HEIGHT - 1:
            print(
                "├"
                + "┼".join(["─" * 3] * config.FIELD_WIDTH)
                + "┤"
                + dynamic_info_row()
            )
    print(
        "└"
        + "┴".join(["─" * 3] * config.FIELD_WIDTH)
        + "┘"
        + dynamic_info_row()
    )


def turn(y, x, is_flag):
    if is_flag:
        field.set_flag(y, x)
        return be_out(field.geomap)

    status = field.open_cell(y, x)
    if isinstance(status, Loss):
        be_out(field.opened_geomap)
        exit()
    elif isinstance(status, Win):
        be_out(field.opened_geomap)
        print("\033[1m")
        for line in localization[config.LANGUAGE]["victory"]:
            print(line)
        print("\033[0m")
        exit()
    be_out(field.geomap)


selected_y = 0
selected_x = 0


def walk():
    global selected_x, selected_y
    while True:
        key = get_key()
        old_x = selected_x
        old_y = selected_y
        if key in ["w", "k", "ц", "\x1b[A"]:
            selected_y = max(selected_y - 1, 0)
        elif key in ["a", "h", "ф", "\x1b[D"]:
            selected_x = max(selected_x - 1, 0)
        elif key in ["s", "j", "ы", "\x1b[B"]:
            selected_y = min(selected_y + 1, config.FIELD_HEIGHT - 1)
        elif key in ["d", "l", "в", "\x1b[C"]:
            selected_x = min(selected_x + 1, config.FIELD_WIDTH - 1)
        elif key in ["q", "й"]:
            exit()
        elif key in ["o", "щ", "ў", "\n", "\r"]:
            return

        if old_x != selected_x or old_y != selected_y:
            be_out(
                [
                    [HiddenCell() for _ in range(config.FIELD_WIDTH)]
                    for _ in range(config.FIELD_HEIGHT)
                ]
            )


be_out(
    [
        [HiddenCell() for _ in range(config.FIELD_WIDTH)]
        for _ in range(config.FIELD_HEIGHT)
    ]
)
walk()

mines = gen_map((selected_y, selected_x))
print("мины!!")
print(mines)
field = Field(mines, config.FIELD_HEIGHT, config.FIELD_WIDTH)

turn(selected_y, selected_x, False)
be_out(field.geomap)
while True:
    key = get_key()
    old_x = selected_x
    old_y = selected_y
    if key in ["w", "k", "ц", "\x1b[A"]:
        selected_y = max(selected_y - 1, 0)
    elif key in ["a", "h", "ф", "\x1b[D"]:
        selected_x = max(selected_x - 1, 0)
    elif key in ["s", "j", "ы", "\x1b[B"]:
        selected_y = min(selected_y + 1, config.FIELD_HEIGHT - 1)
    elif key in ["d", "l", "в", "\x1b[C"]:
        selected_x = min(selected_x + 1, config.FIELD_WIDTH - 1)
    elif key in ["q", "й"]:
        exit()
    elif key in ["o", "щ", "ў", "\n", "\r"]:
        turn(selected_y, selected_x, False)
    elif key in ["f", "а", " "]:
        status = field.set_flag(selected_y, selected_x)
        if isinstance(status, Win):
            be_out(field.opened_geomap)
            print("\033[1m")
            for line in localization[config.LANGUAGE]["victory"]:
                print(line)
            print("\033[0m")
            exit()
        be_out(field.geomap)

    if old_x != selected_x or old_y != selected_y:
        be_out(field.geomap)
