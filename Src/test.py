from os import system
from msvcrt import getch
system("echo \x1b[31m test \x1b[0m")
while True:
    if getch() == chr(27).encode():
        print("caught esc")