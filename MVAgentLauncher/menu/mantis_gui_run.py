###########################################################################
#
#	Menu program for the MV calibration tool.
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
#   Version: 1.0.1
#
###########################################################################

from __future__ import absolute_import
from __future__ import print_function
import os

from PIL import ImageTk, Image
import six.moves.tkinter as tk

import logging
#import xmltodict

#from easygui import *

from MVAgentLauncher.menu.easygui import *

from MVAgentLauncher.menu import mantis_test_lib as lib

#sys.path.append('../calibration/')
#import calibration_manager  as calM

pathlog = ''

product_name = "MVAgentLauncher"
#current_dir = "..\\menu"
#log_location = "c:\MVLog"

config_file_name = "device.cfg"

pdfHelp = 'Readme.pdf'
pngAbout = 'About.png'
txtAbout = 'About.txt'

test_in_progress = "mantis_process_in_progress.py"

test_name="calibr_flow"
ircam_cam_capture_in_process = "False"
ircam_rig_capture_in_process = "False"

extern_test_directories = [ lib.input_location, lib.output_location, lib.lord_takes_location, lib.remote_location ]

logger = logging.getLogger('Harvesting Process Menu')
logger.setLevel(lib.LOGGING_LEVEL)
logger.addHandler(lib.logHandler)

choice_prev = []

def check_single_directory(checking_dir,perform_create_directory):

    if not os.path.exists(checking_dir):
        line_out = "Directory is not exist : " + (checking_dir)
        print(line_out)
        logger.error(line_out)
        # if the Output or Remote directory not exist
        if ( perform_create_directory == True):
            try:
                os.makedirs(checking_dir)
            except OSError:
                if not os.path.isdir(checking_dir):
                    line_out = "Create Directory problem : " + (checking_dir)
                    print(line_out)
                    logger.error(line_out)
                return False
        else:
            return False
    else:
        line_out = "Directory is exist : " + (checking_dir)
        print(line_out)
        logger.info(line_out)
        # clean output files *.* in directory \Outputs\...
        #for outfiles in glob.iglob(os.path.join(output_location, '*.*')):
        #    os.remove(outfiles)

    return True

def show_image(path):
    image_window = tk.Tk()
    img = ImageTk.PhotoImage(Image.open(path))
    panel = tk.Label(image_window, image=img)
    panel.pack(side="bottom", fill="both", expand="yes")
    image_window.mainloop()

FILE_LOCATION_NAME = 'harvest_location_local.txt'

def get_dir_location(param):

    ret_param = "False"

    key = 'TEMP'
    rootpath = os.getenv(key)

    FILE_LOCATION_PATH = rootpath + "\\" + FILE_LOCATION_NAME

    if os.path.isfile(FILE_LOCATION_PATH):
        with open(FILE_LOCATION_PATH) as fp:
            while True:
                line = fp.readline()
                if not line or line == "\n":
                    break
                else:
                    line_in = ' '.join(line.split())
                    name,value = line_in.split("=")
                    if (param == name):
                        ret_param = value
						
        fp.close()
    else:
        line_out = "There is the default input location !"
        print(line_out)
        logger.info(line_out)

    return ret_param

def update_dir_location(fields):

    key = 'TEMP'
    rootpath = os.getenv(key)

    FILE_LOCATION_PATH = rootpath + "\\" + FILE_LOCATION_NAME

    if os.path.isfile(FILE_LOCATION_PATH):
        line_out = "The dir location file exists !"
        print(line_out)
        logger.info(line_out)

        os.remove(FILE_LOCATION_PATH)

    with open(FILE_LOCATION_PATH,"w") as fp:
        fp.write("Input="  + fields[0] + "\n")
        fp.write("Output=" + fields[1]+ "\n")
        fp.write("Conf="  + fields[2] + "\n")
        fp.write("Remote=" + fields[3] + "\n")
        fp.write("Description=" + fields[4] + "\n")

    fp.close()

def display_about(path):

    f = open(path , "r")
    text = f.readlines()
    f.close()
#    msgbox(text)
    title = product_name
    msg = ""
    reply = textbox(msg, title, text)
    print(str(reply))

def read_the_result_file():
    title = product_name
    default = "c:/MVOutput/*.txt"
    filetypes = "*.txt"
    msg = ""
    res_file_name = fileopenbox(msg, title, default, filetypes)

    f = open(res_file_name, "r")
    text = f.readlines()
    f.close()
    msg = "Continue test ?"
    reply = textbox(msg, title, text)
    print(str(reply))

def cfg_change_parameters(takes_data,m_ntConfigParams, choice_prev,command):

    global product_name

    msg = "Select Takes for the Harvesting"

    if (command == "Delete"):
        msg = "Select Takes for the Delete"

    title = product_name

    fieldNames = []
    fieldValues = []  # we start with blanks for the values
    choices = []
    indx = 0
    for key, elem in m_ntConfigParams.items():
        if ( lib.DEBUG == True):
            print("Key: %s , Elem: %s" % (key, elem))
        choices.append(key)
        indx = indx + 1

    choice_msg = ""

    image = ""

#    msg_prev = "Do you want to use the previous setting?\n\n" + choice_msg
#    choices_res = ["Yes", "No"]
#    reply = buttonbox(msg_prev, image=image, choices=choices_res)
#
#    if (reply == "No"):


    while True:

        choice = multchoicebox(msg, title, choices)
        if choice == None:
            choice_prev = 0
            choice_msg = "Empty"
            return choice_prev,choice_msg
        lib.clearn_takes_data(takes_data)
        if ( len(choice) > 25):
            choice_prev = 0
            choice_msg = "Empty"
            line_out = "Error: Selected more than 25 Takes !!"
            print(line_out)
            logger.error(line_out)

            return choice_prev,choice_msg
        choice_prev = choice
        choice_msg = ""

        if (len(choice_prev) == 0):
            choice_msg = "Empty"
        else:
            for elem in choice_prev:
                choice_msg = choice_msg + str(elem) + "\n"

        indx = 0
        for key, elem in m_ntConfigParams.items():
            if (lib.DEBUG == True):
                print("Key: %s , Elem: %s" % (key, elem))
            for key_choice in choice:
                if (key_choice == key):
                    fieldNames.append(key)
                    #####fieldValues.append(elem)
                    if (command == "Select"):
                        fieldValues.append("1")
                    else:
                        if (command == "Delete"):
                            fieldValues.append("2")
                        else:
                            fieldValues.append("0")

            indx = indx + 1

        # gena: for my ver easygui
 #       fieldValues = multenterbox(msg, title, fieldNames, fieldValues)
        #fieldValues = multenterbox(msg, title, fieldNames)

#        if (fieldValues == None):
#            print("No selected takes !")
#        else:
        lib.replaceValueInTakesData(takes_data, fieldNames, fieldValues)
        msg_prev = "Are you sure ?\n\n" + choice_msg
        choices_res = ["Yes", "No","Cancel"]
        reply = buttonbox(msg_prev, image=image, choices=choices_res)
        if (reply == "No"):
            continue
        if (reply == "Yes"):
            break
        if (reply == "Cancel"):
            choice_prev = 0
            break


    return choice_prev,choice_msg

