#!/usr/bin/env python3

from hanover.hanover import Display
import hanover.fonts as fonts
import time

disp = Display("/dev/ttyUSB0", 4800, 5, 96, 8, True)

while True:
    arr = [[0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0]]
    for line in range(len(arr)):
        for pixel in range(len(arr[0])):
            arr[line][pixel] = 1

            disp.write(arr)
            disp.send()
