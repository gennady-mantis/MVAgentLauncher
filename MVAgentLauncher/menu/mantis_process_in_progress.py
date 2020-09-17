###########################################################################
#
#	run the process in progress the MV test tool.
#
#	         Mantis-Vision
#   Copyright 2018,  <gennady.oren@mantis-vision.com>.
#
#	This program is free software; you can redistribute it and/or
#	modify it under the terms of the GNU General Public License as
#	published by the Free Software Foundation; either version 2 of the
#	License, or (at your option) any later version.
#
#	This program is distributed in the hope that it will be useful, but
#	WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#	General Public License for more details.
##
###########################################################################


from __future__ import absolute_import
from __future__ import print_function
import time
#from colored import stylize, fg

import subprocess
import codecs

import colorama
from colorama import Fore, Back, Style

import sys
import time

#import lib.lib_mantis_calibr  as lib
#
#TOOL_DIR = "..\\tools\\"
#TOOL_NAME = "wintail.exe"
#TIME_OUT_INP = 5

def empty_loop():
    colorama.init()
    text = "  Process In Progress : "

    nowtime = time.strftime('%Y_%m_%d-%H.%M.%S')
    start_time = round(time.time(),2)

    while 1:

        now_time = round(time.time(), 2)
        running_time = round(now_time - float(start_time))
#        print("Running time : " + str(running_time) + " sec\n")
#        sys.stdout.write((Fore.GREEN + text + str(running_time) + "    " + Style.RESET_ALL))
        sys.stdout.write(text + str(running_time) + " sec")
        time.sleep(1)
        sys.stdout.write("                                                            \r")
        sys.stdout.flush()

#def tail_start():
#
#    command = TOOL_DIR + "\\" + TOOL_NAME
#
#    log_file = "..\\" + lib.folder_internal + "\\" + lib.log_file_name
#
#    p = subprocess.Popen([command , log_file], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#    output = p.communicate()
#    p.wait()  # wait for process to terminate
#    #new_output = codecs.decode(str(output[0]), 'unicode_escape')
#    #print(new_output)
#
#    time.sleep(TIME_OUT_INP)

if __name__ == '__main__':
   empty_loop()
   #tail_start()
