from msvcrt import getch
while True:
    kp = getch()
    if kp == b'\xe0':
        print('catched.')
        kp = getch()
        asc = kp.decode('ansi')
        print(asc)