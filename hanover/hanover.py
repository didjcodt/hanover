#!/usr/bin/env python3

import serial
import time
import numpy
import sys

class Display(object):
    '''
    Driver for the Hanover display.
    '''
    def __init__(self, serial, baudrate, address, columns, lines, debug=False):
        self.port = serial

        # Debug flag
        self.DEBUG = debug

        # Lines in a display are always multiple of 8
        # If not go to the next %8 block
        if lines % 8:
            lines = lines + (8-(lines % 8))
        self.lines = lines

        # Columns in a display are always multiple of 8
        # If not go to the next %8 block
        if columns % 8:
            columns = columns + (8-(columns % 8))
        self.columns = columns

        if self.DEBUG:
            print("Screen size is {}x{}".format(lines, columns))

        # Payload size for a packet in bytes
        # 1 LED takes 1 bit
        self.payload_size = int(((lines * columns) / 8))
        if self.DEBUG:
            print("Payload size: 0x{:02X}".format(self.payload_size))

        self.byte_per_column = int(lines / 8)
        if self.DEBUG:
            print("Bytes per column: {}".format(self.byte_per_column))

        # Header part:
        # SOT (0x02 added after the conversion, has no ascii representation)
        # Address + 16, Resolution
        self.header = [0x02] + self.__bytearray_to_ascii__([address + 16, self.payload_size])

        if self.DEBUG:
            print("Header:", ', '.join('0x{:02x}'.format(x) for x in self.header))

        # Data buffer initialized to 0
        self.buf = [0] * self.columns

        # Automatically connect to serial device
        self.connect(baudrate)

    def connect(self, baud):
        '''
        Connect to the serial device
        '''
        try:
            self.ser = serial.Serial(port=self.port, baudrate=baud)
        except:
            print(sys.exc_info())
            print("Error opening serial port")
            self.ser = None
        if self.DEBUG:
            print("Serial port:", self.ser)


    def erase_all(self):
        '''
        Erase all the screen
        '''
        if self.DEBUG:
            print("Erasing all")
        for i in range(len(self.buf)):
            self.buf[i] = 0

    def write(self, arr):
        '''
        Write the lines*columns matrix
        '''

        # Transpose array to make column-by-column processing after
        arr = numpy.array(arr).T
        if self.DEBUG:
            print("display: ")
            print(arr.T)

        # Iterate through columns and transform the array to a smaller bytearray
        # If the array is smaller, do not touch the buffer after
        for col_idx in range(min(self.columns, len(arr))):
            curr_col = arr[col_idx]
            cur_byte = 0
            # Only one line block is supported (8 LEDs high)
            for bit_idx in range(min(8, len(curr_col))):
                cur_byte |= (curr_col[bit_idx] == True) << bit_idx
            self.buf[col_idx] = cur_byte

    def __checksum__(self, payload):
        '''
        Compute the checksum of the data frame
        '''

        crc = 0

        # Sum all bytes
        for byte in payload:
            crc += byte

        # Result must be casted to 8 bits
        crc = crc & 0xFF

        # Checksum is the sum XOR 255 + 1. So, sum of all bytes + checksum
        # is equal to 0 (8 bits)
        fcrc = (crc ^ 255) + 1

        if self.DEBUG:
            print("SUM : {}, CRC : {}, SUM + CRC : {}".format(crc, fcrc, crc+fcrc))

        return fcrc

    def __bytearray_to_ascii__(self, array):
        '''
        Transform the array to its ASCII representation
        ex: array=[0x3E, 0x3E] returns [0x33, 0x45, 0x33, 0x45]
        CAUTION: The integers in the array cannot exceed 0xFF
        '''
        ascii_arr = []
        for num in array:
            # In the comment example, num would be 0x3E
            # Take the first digit (3), then the second
            # For that, iterate through the string representation
            strnum = str('{:02X}'.format(num))

            # To represent it correctly, 0x3BE must be represented like
            # '03BE', not as '3BE', a padding is necessary
            if len(strnum)%2:
                strnum = '0'+strnum

            # Use each digit ascii representation and append it in the array
            for digit in strnum:
                ascii_arr.append(ord(digit))

        return ascii_arr

    def send(self):
        '''
        Send the frame via the serial port
        '''

        # Add header + buffer + EOT in the full packet
        packet = self.header + self.__bytearray_to_ascii__(self.buf) + [0x03]

        # Compute CRC and add it at the end
        # Start Of Text must be removed
        crc = self.__checksum__(packet[1:])
        packet = packet + self.__bytearray_to_ascii__([crc])

        if self.DEBUG:
            print("SEND: ")
            print(packet)

        # Convert to bytearray
        packet = bytearray(packet)

        # Send the data
        self.ser.write(packet)
