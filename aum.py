#--------------------------------------------------------------------
# Copyright 2018 Jason G. Pecor
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, 
# publish, distribute, sublicense, and/or sell copies of the Software, 
# and to permit persons to whom the Software is furnished to do so, 
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, 
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES 
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN 
# ACTION OF CONTRACT, TORT OR OTHERWISE, A RISING FROM, OUT OF OR IN 
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# File: aum.py
# 
#--------------------------------------------------------------------
# Created by: Jason Pecor
# Date: 09/28/18
#
# Description:
# Python script to set-up and run the xlr8reconfig tool for 
# flashing a new image on the FPGA.
#--------------------------------------------------------------------

import re
import subprocess
from serial.tools import list_ports

# Output from xlr8reconfig --help just for reminder:

# usage: xlr8reconfig [-h] [-v [VERBOSE]] [-p PORT | --list_ports]
#                     [--rpd_file RPD_FILE] [--load_image {0,1}]
#                     [--baud_rate BAUD_RATE]
#
# connect up to xlr8 board through usb
#
# optional arguments:
#   -h, --help            show this help message and exit
#   -v [VERBOSE], --verbose [VERBOSE]
#                         Increase verbosity. ex: -v, -vv, -vvv, -v 2
#   -p PORT, --port PORT  Required: specify port from command line
#   --list_ports          Optional: list out ports available and exit
#   --rpd_file RPD_FILE   Required: specify rpd file name to use to program XLR8
#   --load_image {0,1}    Forces xlr8 to load selected image. 1 = load
#                         application image ({cfm2,cfm1}), 0 = load factory
#                         image (cfm0)
#   --baud_rate BAUD_RATE
#                         Optional: Define serial transmission baud rate.
#                         Default = 115200


# Define path to tools and rpd files.
tool_path = "/Users/jason/Library/Arduino15/packages/alorium/tools/xlr8reconfig/1.3.0/"
rpd_path  = "/Users/jason/Library/Arduino15/packages/alorium/hardware/avr/1.9.0/fpga_images"

# Currently released images with rpd filename and description
sno_images  = {
    "sno_c16_oDefault_x0F_svn2637.rpd":"Snō 16MHz Standard (Float, NeoPixel, Servo, Quad)",  # Snō 16Mhz Standard (Float, NeoPixel, Servo, Quad)
    "sno_c32_oDefault_x0F_svn2637.rpd":"Snō 32MHz Standard (Float, NeoPixel, Servo, Quad)"}  # Snō 32Mhz Standard (Float, NeoPixel, Servo, Quad)
    
xlr8_images = {
    "xlr8_c16_oDefault_x0B_svn2637.rpd":"XLR8 16MHz Robotics (Float,Servo,Quad)",  # XLR8 16MHz Robotics (Float,Servo, Quad)
    "xlr8_c32_oDefault_x0B_svn2637.rpd":"XLR8 32MHz Robotics (Float,Servo,Quad)",  # XLR8 32MHz Robotics (Float,Servo, Quad)
    "xlr8_c16_oDefault_x04_svn2637.rpd":"XLR8 16MHz NeoPixel",                     # XLR8 16MHz NeoPixel
    "xlr8_c32_oDefault_x04_svn2637.rpd":"XLR8 32MHz NeoPixel",                     # XLR8 32MHz NeoPixel
    "xlr8_top_app07_16MHz_svn2141.rpd":"XLR8 16MHz Legacy",                        # XLR8 16MHz Legacy (Float,Servo, NeoPixel)
    "xlr8_top_app07_32MHz_svn2141.rpd":"XLR8 32MHz Legacy"}                        # XLR8 32MHz Legacy (Float,Servo, NeoPixel)


def main():

    subprocess.call("clear")
    print_banner()
    
    # Get board and rpd file
    (board, rpd_file) = get_fpga_image()
    port = get_prog_port() 
    
    # Configure xlr8reconfig command, confim and upload
    configure_and_upload(rpd_file, board, port)


def configure_and_upload(rpd_file, board, port):

    command  = "{}xlr8reconfig -v --rpd_file {}/{} --load_image 1 --port {}".format(tool_path,rpd_path,rpd_file,port)

    # Confirm and Upload
    if (board=='XLR8'):
        image_description = xlr8_images[rpd_file]
    elif (board == 'Snō'):
        image_description = sno_images[rpd_file]

    print("--------------------------------------------------")
    print("\nReady to program {} board with the {} image.".format(board,image_description))
    start = input("\nStart Upload ([Y]es/[N]o)? : ")

    if start.lower().strip() == 'y':    
        print("")
        print(command)
        subprocess.call(command,shell=True)
    elif start.lower().strip() == 'n':
        print("")
        print("Aborting Upload")

    print("")


def get_fpga_image():

    # Select board    
    board = input("\n\nWhat board is connected? [X]LR8 or [S]nō? ")

    if board.lower().strip() == 'x':
        images = xlr8_images
        board = 'XLR8'
    elif board.lower().strip() == 's':
        images = sno_images
        board = 'Snō'

    # Print image options for user selection    
    print("--------------------------------------------------")
    print('\nAvailable images for the {} board:\n'.format(board))
    for (idx, img) in enumerate(images):
        print('[{}] {}'.format(idx,images[img]))

    # Get user image selection
    num_images = len(images)
    loop_en = 1
    
    while (loop_en == 1):
        image_num = input("\nSelect the image to upload: ")
        if (int(image_num) >= num_images):
            print("\nNot a valid selection - try again.\n")
        else: 
            loop_en = 0

    for (idx, img) in enumerate(images):
        if (idx == int(image_num)):
            print('Image = {}'.format(images[img]))  
            rpd_file = img
    
    return (board, rpd_file)
    

def get_prog_port():

    print("--------------------------------------------------")
    print('\nAvailable programming ports :\n')

    num_ports = 0
    for (idx, comport) in enumerate(list_ports.comports()):
        print("[{}] port={}".format(idx, comport.device))
        num_ports += 1

    loop_en = 1
    while (loop_en == 1):
        prog_port = input("\nSelect programming port: ")
        if (int(prog_port) >= num_ports):
            print("\nNot a valid selection - try again.\n")
        else: 
            loop_en = 0

    for (idx, comport) in enumerate(list_ports.comports()):
        if (int(prog_port) == idx):
            port = comport.device
            print("Port = {}".format(comport.device))
    
    return port


def print_banner():

    print("--------------------------------------------------")
    print("- Alorium Technology")
    print("- XLR8 and Snō FPGA Updater")
    print("--------------------------------------------------")


# Call main
if __name__ == '__main__':
    main()
