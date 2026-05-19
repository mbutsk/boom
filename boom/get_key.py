import os
import sys

if os.name == "nt":
    import msvcrt

    def get_key():
        ch = msvcrt.getwch()

        if ch in ("\x00", "\xe0"):
            ch2 = msvcrt.getwch()
            mapping = {
                "H": "\x1b[A",
                "P": "\x1b[B",
                "M": "\x1b[C",
                "K": "\x1b[D",
            }
            return mapping.get(ch2, ch2.lower())

        return ch.lower()
else:
    import sys
    import termios
    import tty

    def get_key():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)

            if ch == "\x1b":
                ch2 = sys.stdin.read(1)
                ch3 = sys.stdin.read(1)
                return ch + ch2 + ch3

            return ch.lower()

        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
