###########################################################################
#
#	mantis system test library of the MV verification tool.
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

#@mfunction("res")

import os
from subprocess import *

import time


import codecs
import copy

import shutil
import sys

import logging
import logging.handlers as handlers

DEBUG = True
SUPPORT_VER_AFTER_7_1_85 = True

input_location = "Genesis_release_7.1.85"
output_location = "c:\\MVAgentLauncher_Output"
lord_takes_location = "c:\\STORAGE\\localStorage\\Sessions"
remote_location = ""
    ### "c:\\STORAGE\\remoteStorage\\Sessions"
image_location = "c:\MVInput"
log_location = "c:\MVLog"

CONFIG_FILE_NAME = "takes_config.txt"
CONFIG_TEMP_FILE_NAME = "config_temp.txt"
CONFIG_PREV_FILE_NAME = "config_prev.txt"

dic_time = []

EMPTY_VALUE = 0.0
MIS_CONV_CHANNEL = 1


status_file_name = "harvest_process_status.log"
folder_internal = "log"
key = 'TEMP'
rootpath = os.getenv(key)
#rootpath = os.getcwd()
log_folder = rootpath + "\\" + folder_internal
# Open the output file
log_file_name = log_folder + "\\" + status_file_name

CONFIG_DIR = rootpath + "\\config"
CONFIG_FILE = CONFIG_DIR + "\\" + CONFIG_FILE_NAME

LOGGING_LEVEL = logging.DEBUG

print("log_folder : %s" % log_folder)

# Here we define our formatter
if not (os.path.isdir(log_folder)):
    os.mkdir(log_folder)
if not os.path.isfile(log_file_name):
    fp = open(log_file_name,"w")
    fp.write("Log file. \n")
    fp.close()

#print("Logger  define started !!!!!!!!!!!!!! ")

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logHandler = handlers.WatchedFileHandler(log_file_name)

logHandler.setLevel(LOGGING_LEVEL)
# Here we set our logHandler's formatter
logHandler.setFormatter(formatter)
#logger.addHandler(logHandler)

logger_lib = logging.getLogger('Test_Lib')
logger_lib.setLevel(LOGGING_LEVEL)
logger_lib.addHandler(logHandler)

#print("Logger  is defined !!!!!!!!!!!!!! ")

dic = {}
dic_val = {}

#comp = re_compile("^\d+?\.\d+?$")

nowtime = time.strftime('%Y_%m_%d-%H.%M.%S')

TEMP_OUTPUT_DIR = os.getenv('TEMP') + "\\mv_cam_control_" + str(nowtime)

FILE_PATH_LOCATION = TEMP_OUTPUT_DIR + '\\location_local.txt'

print("Harvest Start time : %s" % str(nowtime))

def get_param_from_file(param,file_location):
    ret_param = "False"

    if os.path.isfile(file_location):
        with open(file_location) as fp:
            while True:
                line = fp.readline()
                if not line or line == "\n":
                    break
                else:
                    line_in = ' '.join(line.split())
                    name, value = line_in.split("=")
                    if (param == name):
                        ret_param = value

        fp.close()
    else:
        print("Error: Params file is not exist !")

    return ret_param

def update_dir_location(fields):

    if not (os.path.isdir(TEMP_OUTPUT_DIR)):
        os.mkdir(TEMP_OUTPUT_DIR)

    if os.path.isfile(FILE_PATH_LOCATION):
        print("The dir location file exists !")
        os.remove(FILE_PATH_LOCATION)

    with open(FILE_PATH_LOCATION, "w") as fp:
        fp.write("Output=" + fields[0] + "\n")
    fp.close()


def device_conf_read(dev_file_name):

        indx = 0

        if os.path.isfile(dev_file_name):
            indx = 0
            with open(dev_file_name, "r") as fp:
                for line in fp:
                    if not line or line == "\n":
                        break
                    (key, val) = line.split("=")
                    dic[indx] = key
                    dic_val[indx] = val
                    indx = indx + 1
        else:
            print("Error : Device configuration file is not exist  !" + dev_file_name )


def get_parameter_from_config(dev_n, dev_l, param):
    index = 0
    ret_val = EMPTY_VALUE
    param_exists = "False"
    while index < len(dev_l):
        element = dev_n[index]
        element = element.strip()
        if ( element == param ):
            ret_val = dev_l[index]
            ret_val = ret_val.strip()
            ret_val = ret_val.strip('\n')
            break
        index += 1
    return ret_val

def get_running_time():
    running_time = 0
    for line in dic_time:
        if not line or line == "\n":
            break
        name, start_time = line.split(" ")
        now_time = round(time.time(), 4)
        running_time = round(now_time - float(start_time),4)
        break
    return running_time

def send_run_time_command(sys_command,time_value, test_name):
    if ( sys_command  == "start"):
        line = test_name + " " + str(time_value) + "\n"
        dic_time.append(line)

    if (sys_command == "end"):
        output_line_format = "{0:6}  {1:18}  {2:6}  {3:8} {4:7} {5:8}"
        running_time = get_running_time()
        out_line = "Running time : " + str(running_time) + " sec"
        print(out_line)
        logger_lib.info(out_line)
        line = test_name + " " + str(running_time) + "\n"
        dic_time.append(line)

        indx = 0
        prev_value = 0
        for dic_line in dic_time:
            line_in = ' '.join(dic_line.split())
            name,value = line_in.split(" ")
            if (indx == 0):
                value = 0
            delta = round(float(value) - prev_value,4)
            res_line_out = copy.copy(output_line_format)
            line_out = res_line_out.format("Test :", name, "Time :", str(delta),"Stop :", value)
            #print( "Test : %s, Time: %s (%s) " % (name,str(delta),value))
            print(line_out)
            logger_lib.info(line_out)
            prev_value = float(value)
            indx = indx + 1

    if (sys_command == "set"):
        line = test_name + " " + str(time_value) + "\n"
        dic_time.append(line)

def set_time_test(test_name):

    sys_command = "set"
 
    time_value = get_running_time()
    send_run_time_command(sys_command,time_value, test_name)

def delete_config_File(indir):

    infile = indir + "\\" + CONFIG_FILE_NAME
    prevfile = indir + "\\" + CONFIG_PREV_FILE_NAME

    if (os.path.isfile(infile)):
         os.remove(infile)

    if (os.path.isfile(prevfile)):
         os.remove(prevfile)

def replaceValueInTakesData(takes_data, selectedParam, value_in):

    lineout = ""

    for param_in in selectedParam:
        print(param_in)

    for _value in value_in:
        print(_value)

    indx_takes = 0

    for line in takes_data:
        # check if line is not empty
        if (not line) or (line == ""):
            break
        if (line == "\n") or (line == ";"):
            continue
        if (len(line) > 1):
            if (line[0] == ";"):
                 continue
            else:
               line_in = ' '.join(line.split())
               param, value = line_in.split(" = ")
               index = 0
               for param_i in selectedParam:
                   if (param == param_i):
                        value = value_in[index]
                        lineout = str(param) + " = " + str(value) + "\n"
                        takes_data[indx_takes] = lineout
                        if (DEBUG == True):
                            print("New value : %s Index = %d" % (lineout,indx_takes))

                   index = index + 1
        indx_takes = indx_takes + 1
    print("replaceValueInTakesData : is finished")

def create_takes_data(lord_dir):

    takes_data = []

    if not (os.path.isdir(lord_dir)):
        print("Directory is not exists : %s", lord_dir)
        return

#    if not (os.path.isdir(CONFIG_DIR)):
#        os.mkdir(CONFIG_DIR)
#
#    if os.path.isfile(CONFIG_FILE):
#        print("The take file config exists !")
#        return
#        #os.remove(CONFIG_FILE)
#
#    fp = open(CONFIG_FILE, "w")

    for root, dirs, _ in os.walk(lord_dir):
        for subdir in dirs:
            if (lord_dir == root):
                continue

            root_parts = root.split("\\")
            if (len(root_parts) > 1):
                name_indx = len(root_parts) -1
                name_take = root_parts[name_indx]
                take_dir = os.path.join(root, subdir)
                print(take_dir)
                line_out = "%s:%s = 0 \n" % (name_take,subdir)
                takes_data.append(line_out)
                #fp.write(line_out)

    #fp.close()
    return takes_data


def create_single_takes_data(lord_dir):

    takes_data = []

    if not (os.path.isdir(lord_dir)):
        print("Directory is not exists : %s", lord_dir)
        return

    # get take name from the directory name
    directory_name_arr = lord_dir.split("\\")
    len_dir_arr = len(directory_name_arr)
    if (len_dir_arr > 0):
        take_name_def = directory_name_arr[len_dir_arr - 1]

        lord_dir_def = lord_dir.replace(take_name_def,"")

        for root, dirs, _ in os.walk(lord_dir_def):
            for subdir in dirs:
                if (lord_dir_def == root):
                    continue

                root_parts = root.split("\\")
                if (len(root_parts) > 1):
                    name_indx = len(root_parts) -1
                    name_take = root_parts[name_indx]
                    take_dir = os.path.join(root, subdir)
                    print(take_dir)
                    if (name_take == take_name_def):
                        line_out = "%s:%s = 1 \n" % (name_take,subdir)
                        takes_data.append(line_out)
                        break
                    #fp.write(line_out)

    #fp.close()
    return takes_data,lord_dir_def



def clearn_takes_data(takes_data):
    indx_takes = 0

    if (len(takes_data) == 0):
        return

    for line in takes_data:

        if not line or line == "\n":
            break
        else:
            line_in = ' '.join(line.split())
            name, value = line_in.split(" = ")
            lineout = ( name + " = 0") + "\n"
            takes_data[indx_takes] = lineout

            if (DEBUG == True):
                print("New value : %s Index = %d" % (lineout, indx_takes))
        indx_takes = indx_takes + 1

def check_enable_harvesting(takes_data,root,subdir,command):

    ret = False
    com_value = ""

    if ( command == "DELETE" ):
        com_value = "2"
    if ( command == "HARVEST"):
        com_value = "1"

    root_parts = root.split("\\")

    if (len(root_parts) > 1):
        name_indx = len(root_parts) - 1
        name_take = root_parts[name_indx]
    else:
        return ret

    param = "%s:%s" % (name_take,subdir)

    for line in takes_data:

        if not line or line == "\n":
            break
        else:
            line_in = ' '.join(line.split())
            name, value = line_in.split(" = ")
            if (param == name):
                #value_out = ' '.join(value.split())
                if (value == com_value):
                    ret = name_take
                    print("Enable Harvesting Command: %s %s" % (command,name))
                    break

    return ret


def check_conf_directories(input_dir,output_dir,logger):
    ret = True
    if ( not os.path.isdir(input_dir)):
        ret = False
        line_out = "Input directory not exists %s " % input_dir
        logger.error(line_out)
        print(line_out)

    if ( not os.path.isdir(output_dir)):
        ret = False
        line_out ="Output directory not exists %s " % output_dir
        logger.error(line_out)
        print(line_out)

    return ret
