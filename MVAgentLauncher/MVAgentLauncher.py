###########################################################################
#
#	mantis studio system MVAgent management tool.
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
from __future__ import absolute_import
from __future__ import print_function

import sys
import os
import getopt

import datetime
import time

import shutil
import logging
import collections
from pathlib import Path
import subprocess
import ctypes
import threading
from subprocess import *
import codecs
import json
import pandas as pd

import MVAgentLauncher.menu.mantis_test_lib as lib
import MVAgentLauncher.menu.mantis_gui_run as menu
from MVAgentLauncher.menu.easygui import *

APPL_TIME_OUT = 1
SIZE_FIELD_PARAM = 100
TIME_TO_SLEEP = 5  # wait between the processes

test_in_progress = "menu\\mantis_process_in_progress.py"

TOOL_ZIP = "7z.exe"
TOOL_NAME = "XmlGraphRunner.exe"
JOINED_TOOL_NAME = "Mvx2FileJoinAfterHarvest.exe"
INFO_TOOL_NAME = "Mvx2FileInfo.exe"
MVGRAPH_API_DLL = "MVGraphAPI.dll"
MVX2BASICIO_DLL = "Mvx2BasicIO.dll"

DECODE_H264_XML_NAME = "decodeH264Master.xml"
DECODE_XML_NAME = "decode.xml"

if ( lib.SUPPORT_VER_AFTER_7_1_85 == True):
    JOIN_XML_FILE = "join_after_harvest.xml"
else:
    JOIN_XML_FILE = "join_after_harvest_w_audio.xml"

OUT_DIR_SESSIONS = "Sessions"
DEVICE_FILE_NAME = "device.json"
NUC_PARAM_FILE_NAME = "kiosk_nuc_param.json"
EXCEL_TOOL = "excel"

RESULT_FILE_NAME_HTML = "mv_harvest_result.html"
RESULT_FILE_NAME = "mv_harvest_result.csv"
REZULT_FIRST_STRING = "Session, Take, Status, Compression,  Joined Frames, Process Time, NUCs, Description, Date, Version\n"

SET_ZIP_FUNCTIONALITY = False

#logger = logging.getLogger()
logger = logging.getLogger('Harvest_Process')
logger.setLevel(lib.LOGGING_LEVEL)
logger.addHandler(lib.logHandler)

display_dm_image_in_progress = False
threads_dm = []

display_ply_image_in_progress = False
threads_ply = []

nuc_number_frames_array = []
frame_number_thresold = 10.0     # 5% from the joined frames number

def clean_image_directory(input_dir,file_name):
    res = "True"
    if (os.path.isdir(input_dir)):
        if os.path.isfile(input_dir + "\\" + file_name):
            try:
                os.remove(input_dir + "\\" + file_name)
            except OSError:
               line_out = "Error: Remove file problem : %s" ,input_dir + "\\" + file_name
               print(line_out)
               logger.error(line_out)
               res = "False"
    else:
        os.makedirs(input_dir)
    return res


def stop_test_processing(state):

     running_time = lib.get_running_time()
     line_out = "Running time : " + str(running_time) + " sec"
     print(line_out)
     logger.info(line_out)

     if (lib.DEBUG == True):
        stop_time = round(time.time(), 4)
        lib.send_run_time_command("end", stop_time, "TimeEnd")
        line_out = "System manager is stopped !"
        print(line_out)
        logger.info(line_out)

     if ( state == False ):
         sys.exit(1)
     else:
         sys.exit(0)


def test_harvest(str):
    time.sleep(10)
    os.system(str)
    return

def spread_graphs_to_nucs(input_dir,config_param):

    NUMBER_DEVICES = config_param["setup"]["NUMBER_DEVICES"]
    NUC_ONE = config_param["setup"]["NUC_ONE"]

    xml_file_array = [DECODE_H264_XML_NAME,DECODE_XML_NAME]

    ret = "0"

    print("Spread graphs: %s Started  !!!!" % input_dir)
    indx = 0
    nuc_num = int(NUC_ONE)
    while True:
        command_base = r'\\NUC%s\NUC%s' % (str(nuc_num),str(nuc_num))

        for xml_file in xml_file_array:
            xml_file_path = command_base + "\\" + xml_file
            if not os.path.isfile(xml_file_path):
                print("INFO: XML file: %s is not exists !" % xml_file)
                if (lib.DEBUG == True):
                    current_dir = "\\".join(__file__.split("/")[:-1])
                else:
                    current_dir = "\\".join(__file__.split("\\")[:-1])

                source_file = "%s\%s\%s" % ( current_dir, "spread\\NUCNUM",xml_file )

                if os.path.isfile(source_file):

                    command_out = r'copy %s  %s\%s' % (source_file, command_base, xml_file)

                    process = subprocess.Popen(command_out, stdout=subprocess.PIPE, stderr=None, shell=True)
                    output = process.communicate()
                    process.wait()  # wait for process to terminate
                    new_output = codecs.decode(str(output[0]), 'unicode_escape')

                    if (lib.DEBUG == True):
                        print(new_output)
        indx = indx + 1
        print("Spread GRAPHs finished for NUC%s" % nuc_num)
        if ( indx > NUMBER_DEVICES - 1):
            break
        nuc_num = nuc_num + 1
    print("Spread GRAPHs process is finished  !!!!" )



def spread_tools_to_ver(input_dir,config_param):

    NUMBER_DEVICES = config_param["setup"]["NUMBER_DEVICES"]
    NUC_ONE = config_param["setup"]["NUC_ONE"]

    tools_file_array = [TOOL_NAME,
                        INFO_TOOL_NAME,
                        MVGRAPH_API_DLL,
                        MVX2BASICIO_DLL
                       ]

    ret = "0"

    print("Spread tools to ver: %s Started  !!!!" % input_dir)
    indx = -1
    nuc_num = int(NUC_ONE)
    while True:
        if (indx == -1):
            command_base = r'c:\gen\%s' % input_dir
        else:
            command_base = r'\\NUC%s\NUC%s\%s' % (str(nuc_num), str(nuc_num), input_dir)

        for tool_file in tools_file_array:
            tool_file_path = command_base + "\\" + tool_file
            if not os.path.isfile(tool_file_path):
                print("INFO: TOOL file: %s is not exists !" % tool_file)
                if (lib.DEBUG == True):
                    current_dir = "\\".join(__file__.split("/")[:-1])
                else:
                    current_dir = "\\".join(__file__.split("\\")[:-1])

                source_file = "%s\%s\%s" % ( current_dir, "spread\\NUCNUM_VER",tool_file )

                if os.path.isfile(source_file):

                    command_out = r'copy %s  %s\%s' % (source_file, command_base,tool_file)

                    process = subprocess.Popen(command_out, stdout=subprocess.PIPE, stderr=None, shell=True)
                    output = process.communicate()
                    process.wait()  # wait for process to terminate
                    new_output = codecs.decode(str(output[0]), 'unicode_escape')

                    if (lib.DEBUG == True):
                        print(new_output)
        indx = indx + 1
        if (indx != 0):
            print("Spread TOOLs finished for NUC%s" % nuc_num)
            if ( indx > NUMBER_DEVICES - 1):
                break
            nuc_num = nuc_num + 1
        else:
            print("Spread TOOLs finished for LPORD" )

    print("Spread Tools process is finished  !!!!" )


def run_harv_decoding(input_dir,takes_name,root, subdir,config_param):

    NUMBER_DEVICES = config_param["setup"]["NUMBER_DEVICES"]
    PASSWORD = config_param["setup"]["PASSWORD"]
    USER = config_param["setup"]["USER"]
    NUC_ONE = config_param["setup"]["NUC_ONE"]
    IPADD_BASE = config_param["setup"]["IPADD_BASE"]
    COMPRESS = config_param["parameters"]["COMPRESS"]

    threads = []


    print("Decoding process: %s Started  !!!!" % takes_name)
    indx = 0
    while True:
        ip_addr = "%s.%s" % (IPADD_BASE, str(NUC_ONE + indx))
        command_base = "c:\\NUC%s\%s\%s" % (str(NUC_ONE + indx), input_dir, TOOL_NAME)
        # xml_name = "c:\\NUC%s\%s\localGraphs\\%s" % (str(NUC_ONE + indx), input_dir, XML_NAME)
        if (COMPRESS == "H264"):
            XML_NAME = DECODE_H264_XML_NAME
        else:
            XML_NAME = DECODE_XML_NAME

        xml_name = "c:\\NUC%s\\%s" % (str(NUC_ONE + indx), XML_NAME)
        nuc_num = indx + 1
        if (nuc_num > 9):
            HOSTID = "0%d" % nuc_num
        else:
            HOSTID = "00%d" % nuc_num
        out_str_wmic = r'wmic /node:%s /user:%s /password:%s process call create' % (ip_addr, USER, PASSWORD)
        line_out = os.path.join(root, subdir)
        print(line_out)
        #gena
        v_localStorage = "C:/STORAGE/localStorage"
        #v_localStorage = "c:/NUC%s/%s/localStorage" % (str(nuc_num),input_dir)
        out_str_cmd = r'"cmd /c %s %s --HOSTID %s --LOCALSTORAGE %s --SESSIONNAME %s --SESSIONS Sessions --TAKEID %s"' % (
            command_base, xml_name, HOSTID,v_localStorage, takes_name, subdir)
        command_out = "%s %s" % (out_str_wmic, out_str_cmd)
        print("Command line: %s" % command_out)
        command_out_2 = 'cmd /k "echo %s"' % nuc_num
        # process = threading.Thread(target=test_harvest, args=[command_out_2])
        process = threading.Thread(target=os.system, args=[command_out])
        # os.system(command_out)
        threads.append(process)
        process.start()
        time.sleep(1)
        # os.system('cmd /k "date"')
        indx = indx + 1
        nuc_num = nuc_num + 1
        if (nuc_num > NUMBER_DEVICES):
            break

    indx = 1

    for process_rt in threads:
        process_rt.join()
        print("Process: %s" % str(indx))
        indx = indx + 1
    print("Decoding process: %s is finished  !!!!" % takes_name)

def check_is_file_ready(input_take_file):

    ret = True
    access_enable = False
    while True:

        if os.path.isfile(input_take_file):  # is it a file or a dir?
            file_object = 0
            try:
                # print( "Trying to open %s." % input_take_file)
                buffer_size = 8
                # Opening file in append mode and read the first 8 characters.
                file_object = open(input_take_file, 'a', buffer_size)
                if file_object:
                    print("%s is not locked." % input_take_file)
                    access_enable = True
                    break
            except IOError:
                # print( "File is locked (unable to open in append mode)")
                access_enable = False
            finally:
                if file_object:
                    file_object.close()

            time.sleep(1)
        else:
            ret = False
            print("ERROR: File %s is not exists" % input_take_file)
            break

    return ret


def get_number_frames(ver_dir,mvx_file):

     ret = "0"

     if not os.path.isfile(mvx_file):
         print("Error MVX file: %s is not exists !" % mvx_file)
         return ret

     command = "%s\%s -c %s" % (ver_dir,INFO_TOOL_NAME,mvx_file)

     p = Popen(command, shell=False, stdout=PIPE, stderr=STDOUT)
     output = p.communicate()
     p.wait()
     new_output =  codecs.decode(str(output[0]), 'unicode_escape')

     if (lib.DEBUG == True):
         print(new_output)

     if (len(new_output) > 1):
         ret_num = new_output.split("\t")
         if (len(ret_num) > 1):
             line = ret_num[1]
             ret1 = line.replace("\n","")
             ret = ret1.replace("\r", "")
             ret = ret.replace("'", "")

     return ret

def percentage(part, whole):
    ret = 0
    if (whole == 0):
	    return ret
    perc_value = 100 * float(part)/float(whole)
    if (perc_value > 100.0):
        ret = perc_value - 100
    else:
        ret = 100 - perc_value
    return ret

def check_frame_number_state(joined_frame_number, nuc_number):
    global nuc_number_frames_array
    global frame_number_thresold

    ret = False

    nuc_number_frames_sum = 0
    indx = 0
    if ( len(nuc_number_frames_array) > 0):
        for elem in nuc_number_frames_array:
            nuc_number_frames_sum = nuc_number_frames_sum + int(elem)
            indx = indx + 1
            line_out = "NUC %s frames number = %s" % (str(indx),int(elem))
            print(line_out)
            logger.info(line_out)
        if (nuc_number > 0):
            average_value = nuc_number_frames_sum / nuc_number
            result = percentage(average_value, int(joined_frame_number))
            if (result > frame_number_thresold):
                ret = False
            else:
                ret = True
            line_out = "Check Frames Number result: NUCs average = %.2f deviation = %.2f %%" % (average_value,result)
            print(line_out)
            logger.info(line_out)

    return ret

def delete_takes( lord_dir,output_dir,  command,takes_data, config_param):

    ret = True
    NUMBER_DEVICES = config_param["setup"]["NUMBER_DEVICES"]
    NUC_ONE = config_param["setup"]["NUC_ONE"]
    IPADD_BASE = config_param["setup"]["IPADD_BASE"]
    command_out = ""
    file_name = ""

    if (command != "DELETE"):
        print("ERROR: Command: %s is unknown!!" % command)
        return False

    for root, dirs, _ in os.walk(lord_dir):

        for subdir in dirs:

            if (lord_dir == root):
                continue

            takes_name = lib.check_enable_harvesting(takes_data,root, subdir, "DELETE")
            if (takes_name == False):
                continue


#### cmd /c rd /s /q \\nuc125\STORAGE\localStorage\Sessions\Amit_APose_Take2\2019-11-19-17.25.18
            print("%s process: %s Started  !!!!" % (command, takes_name))

            lord_take_dir = "%s\\%s\\%s" % (lord_dir, takes_name, subdir)

            output_take_dir = "%s\\Sessions\\%s\\%s" % (output_dir, takes_name, subdir)

            indx = 0
            while True:

                ip_addr = "%s.%s" % (IPADD_BASE, str(NUC_ONE + indx))

                input_take_dir = Path(r'\\%s\STORAGE\localStorage\Sessions\%s\%s' % (ip_addr, takes_name, subdir))

                nuc_num = indx + 1
                if (nuc_num > 9):
                    HOSTID = "0%d" % nuc_num
                else:
                    HOSTID = "00%d" % nuc_num

                if (os.path.isdir(input_take_dir)):
                    shutil.rmtree(input_take_dir)
                    print("Deleted take: %s "  % input_take_dir)

                time.sleep(2)
                # os.system('cmd /k "date"')
                indx = indx + 1
                nuc_num = nuc_num + 1
                if (nuc_num > NUMBER_DEVICES):
                    break

            if (os.path.isdir(lord_take_dir)):
                shutil.rmtree(lord_take_dir)
                print("Deleted take from the LORD: %s" % lord_take_dir)
            else:
                print("Warning: LORD Take directory is NOT exist: %s" % lord_take_dir)

            if (os.path.isdir(output_take_dir)):
                shutil.rmtree(output_take_dir)
                print("Deleted take from the OUTPUT DIR: %s" % output_take_dir)
            else:
                print("Warning: OUTPUT Take directory is NOT exist: %s" % output_take_dir)

def get_frames_number_for_compress(command_out_xml):

    process = subprocess.Popen(command_out_xml, stdout=subprocess.PIPE, stderr=None, shell=True)
    # Launch the shell command:
    output = process.communicate()
    #                    print (output[0])

    process.wait()  # wait for process to terminate
#    new_output = codecs.decode(str(output[0]), 'unicode_escape')
    new_output = output[0].decode("ascii")

    if (new_output == ""):
        nuc_number_frames = 0
    else:
        frame_cnt_str = (new_output.split("=")[3]).split(" ")[0]
        frame_cnt = frame_cnt_str.split("-")[1]
        frame_cnt = frame_cnt.replace('"', "")
        nuc_number_frames = (int(frame_cnt) + 1)

    print("Frames number : %d" % nuc_number_frames)

    return nuc_number_frames

command_out_xml = ""
perform_get_after_copy2 = False

def run_spec_command(input_dir, takes_name,output_dir, command, subdir, config_param,nuc_param):


        global nuc_number_frames_array
        global command_out_xml
        global perform_get_after_copy2

        ret = True
        NUMBER_DEVICES = config_param["setup"]["NUMBER_DEVICES"]
        PASSWORD = config_param["setup"]["PASSWORD"]
        USER = config_param["setup"]["USER"]
        NUC_ONE = config_param["setup"]["NUC_ONE"]
        IPADD_BASE = config_param["setup"]["IPADD_BASE"]
        COMPRESS = config_param["parameters"]["COMPRESS"]
        command_out = ""
        file_name = ""
        nuc_number_frames = "0"


        if ( command != "COPY") and (command != "ZIP") and (command != "UNZIP") and (command != "NOP") and (command != "COPY2") :
            print("ERROR: Command: %s is unknown!!" % command)
            return False

        output_take_dir_base = output_dir + "\\" + takes_name
        if (not os.path.isdir(output_take_dir_base)):
            os.makedirs(output_take_dir_base)


        output_take_dir = output_dir + "\\" + takes_name + "\\" + subdir

        if (command == "COPY") or (command == "COPY2") :
            if (os.path.isdir(output_take_dir)):
                shutil.rmtree(output_take_dir)

            os.makedirs(output_take_dir)

        threads = []

        if ((COMPRESS == "H264") and (command == "COPY2"))\
                or ((COMPRESS == "NO_COMPRESS") and (command == "NOP")):
            nuc_number_frames_array.clear()

        print("%s process: %s Started  !!!!" % (command,takes_name))
        indx = 0
        while True:
            ip_addr = "%s.%s" % (IPADD_BASE, str(NUC_ONE + indx))
            #gena
            v_localStorage = "STORAGE"
            #v_localStorage = "NUC%s\\%s" % (str(NUC_ONE + indx), input_dir)
            input_take_dir = "\\%s\\%s\\localStorage\\Sessions\\%s\\%s" % (ip_addr , v_localStorage, takes_name, subdir)

            nuc_num = indx + 1
            # checkthe NUC is enable
            nuc_name = "NUC%s" %  str(nuc_num)
            nuc_is_enable = nuc_param[nuc_name]["Enable"]
            if (nuc_is_enable == "False"):
                indx = indx + 1
                nuc_num = nuc_num + 1
                if (int(nuc_num) > int(NUMBER_DEVICES)):
                    break
                else:
                    continue
            if (nuc_num > 9):
                HOSTID = "0%d" % nuc_num
            else:
                HOSTID = "00%d" % nuc_num

            if ( command == "COPY"):
                file_name = "%s_d%s.zip" %  (subdir,HOSTID)
                command_out = r'copy \%s\%s  %s\%s' % (input_take_dir, file_name,output_take_dir,file_name)

            if (command == "COPY2"):
                file_name = "%s_d%s.mvx" %  (subdir,HOSTID)
                file_name_xml = "%s_d%s.xml" %  (subdir,HOSTID)
                #command_out = r'copy \%s\%s  %s\%s' % (input_take_dir, file_name,output_take_dir,file_name)
                command_out = r'cmd /c robocopy \%s  %s %s' % (input_take_dir,output_take_dir,file_name)
                command_out_xml = r'type \%s\%s | findstr  "LookupTable"' % (input_take_dir, file_name_xml)
                perform_get_after_copy2 = True


            if ( command == "ZIP"):
                #   7z a -mx1 -tzip 2019-11-19-17.24.40_d001.zip 2019-11-19-17.24.40_d001.mvx
                file_name = "%s_d%s.mvx" % (subdir, HOSTID)
                file_name_out = "%s_d%s.zip" % (subdir, HOSTID)
                command_base_path = "C:\STORAGE\localStorage\Sessions\%s\%s" % (takes_name, subdir)
                out_str_wmic = r'wmic /node:%s /user:%s /password:%s process call create' % (ip_addr, USER, PASSWORD)
                out_str_cmd = r'"cmd /c %s a -mx1 -tzip %s\%s %s\%s"' % (
                    TOOL_ZIP, command_base_path,file_name_out,command_base_path, file_name)
                command_out = "%s %s" % (out_str_wmic, out_str_cmd)

            input_take_file = r'\%s\%s' % (input_take_dir, file_name)

            if (command == "UNZIP"):
                file_name = "%s_d%s.zip" % (subdir, HOSTID)
                file_name_out = "%s_d%s.mvx" % (subdir, HOSTID)
                command_out = r'cmd /c "%s e %s\%s -o%s"' % (TOOL_ZIP,output_take_dir, file_name, output_take_dir)
                input_take_file = "%s\%s" % (output_take_dir, file_name)

            if (command == "NOP"):
                file_name = "%s_d%s.mvx" % (subdir, HOSTID)
                command_out = r'cmd /c NOP'
                input_take_file = "%s\%s" % (output_take_dir,file_name)
                file_name_zip = "%s\%s_d%s.zip" % (output_take_dir,subdir, HOSTID)

            print("Command line: %s" % command_out)

            print("File for %s: %s" % (command,input_take_file))

            ret = check_is_file_ready(input_take_file)

            if (ret == False):
                return ret

            if ( command != "NOP"):
                size = os.path.getsize(r'\%s\%s' % (input_take_dir, file_name))
                print("File size: %s : %s" %(file_name,str(size)))

                process = threading.Thread(target=os.system, args=[command_out])
                # os.system(command_out)
                threads.append(process)
                process.start()
 ####

            else:
                # command == "NOP"
                # delete ZIP file

                if (perform_get_after_copy2 == True):
				
                    print("Check frame number after COPY2 !")
                    nuc_number_frames = get_frames_number_for_compress(command_out_xml)
                    nuc_number_frames_array.append(nuc_number_frames)
#                  perform_get_after_copy2 = False

                ver_dir = "c:\\gen\%s" % (input_dir)

                if ( not COMPRESS == "H264"):
                    nuc_number_frames = get_number_frames(ver_dir, input_take_file)
                    nuc_number_frames_array.append(nuc_number_frames)

                if os.path.isfile(file_name_zip):
                    try:
                        os.remove(file_name_zip)
                        print("Remove: ZIP file %s  !" % file_name_zip)
                    except OSError:
                        line_out = "Error: Remove file problem : %s", file_name_zip
                        logger.error(line_out)
                        print(line_out)


            time.sleep(1)
            # os.system('cmd /k "date"')
            indx = indx + 1
            nuc_num = nuc_num + 1
            if ( int(nuc_num) > int(NUMBER_DEVICES) ):
                break

        indx = 1

        if ( ret == True) and  (command != "NOP"):
            for process_rt in threads:
                process_rt.join()
                print("Process: %s" % str(indx))
                indx = indx + 1
            print("%s process: %s is finished  !!!!" % (command,takes_name))

        return ret

def create_joined_file(input_dir, takes_name, output_path_remote, output_path_dir, root, subdir):

#XmlGraphRunner.exe C:\gen\Genesis_master_7.0.122\localGraphs\join_after_harvest.xml
# --REMOTESTORAGE D:\Harvest  --LOCALSTORAGE d:/STORAGE/localStorage --SESSIONNAME Amit_APose_Take1 --SESSIONS Sessions --TAKEID 2019-11-19-17.24.40
    #command_base = "c:\\gen\%s\%s" % ( input_dir, JOINED_TOOL_NAME)

    output_remote = output_path_remote.replace("\\Sessions","")

    command_base = "c:\\gen\%s\%s" % ( input_dir, TOOL_NAME)
    xml_param = "c:\\gen\%s\localGraphs\%s" % ( input_dir, JOIN_XML_FILE)
    input_param_str = r'--REMOTESTORAGE %s  --LOCALSTORAGE %s --SESSIONNAME %s --SESSIONS Sessions --TAKEID %s' % (output_remote,output_path_dir,takes_name,subdir)
    #input_path = output_dir + "\\" + takes_name + "\\" + subdir

    if not os.path.isfile(command_base):
        print("Error: Tool %s is not exists !" % command_base )
        return


    if (not os.path.isdir(output_path_dir)):
        os.makedirs(output_path_dir)

    output_path_file = output_path_dir + "\\" + takes_name + "\\" + subdir + "\\" + subdir + "_joined.mvx"
    ## run the ool createing the joined file
    #out_str = "%s -i %s -o %s" % (command_base,input_path,output_path_file )
    out_str = "%s %s %s" % (command_base,xml_param, input_param_str)
    print("Command line: %s" % out_str)
    os.system(out_str)

def run_harvesting(input_dir,output_dir,lord_dir,remote_location,takes_data,config_param,nuc_param):
    #    '''
    #      wmic /node:192.168.34.101 /user:user /password:1 process call create "cmd /c C:\NUC101\Genesis_master_7.0.122\XmlGraphRunner.exe C:\NUC101\Genesis_master_7.0.122\localGraphs\decode.xml --HOSTID 001 --LOCALSTORAGE C:/STORAGE/localStorage --SESSIONNAME Amit_crossfit_Take5 --SESSIONS Sessions --TAKEID 2019-11-19-14.29.29"
    #     '''

    global perform_get_after_copy2

    ret = False
    number_failed_takes = 0

    if (lib.DEBUG == True):
        current_dir = "/".join(__file__.split("/")[:-1])
    else:
        current_dir = "\\".join(__file__.split("\\")[:-1])

    ZIP_MODE = config_param["parameters"]["ZIP_MODE"]
    COMPRESS =  config_param["parameters"]["COMPRESS"]
    NUMBER_DEVICES = config_param["setup"]["NUMBER_DEVICES"]
    user_description = config_param["parameters"]["Description"]

    if ( remote_location == ""):
        output_dir_sessions = lord_dir.replace("localStorage", "remoteStorage")
    else:
        if (os.path.isdir(remote_location)):
            output_dir_sessions = remote_location + "\\Sessions"
        else:
            output_dir_sessions = lord_dir.replace("localStorage", "remoteStorage")

    threads = []
    v_number_frames = 0

    fp = 0

    status = "OK"

    output_result_file = output_dir + "\\" + RESULT_FILE_NAME

    if (not os.path.isdir(output_dir)):
        os.makedirs(output_dir)

    if not os.path.isfile(output_result_file):
        try:
            fp = open(output_result_file, "w")
        except IOError:  # This means that the file does not exist (or some other IOError)
            print("Error: Open the file %s" % output_result_file)
            return

        fp.write(REZULT_FIRST_STRING)
    else:
        try:
            fp = open(output_result_file, "a")
        except IOError:  # This means that the file does not exist (or some other IOError)
            print("Error: Open the file %s" % output_result_file)
            return False

    if ( ZIP_MODE == "ZIP"):
        command_array = ["ZIP","COPY","UNZIP","NOP"]
    else:
        command_array = ["COPY2", "NOP"]

    for root, dirs, _ in os.walk(lord_dir):
        for subdir in dirs:
            if (lord_dir == root):
                continue
            takes_name = lib.check_enable_harvesting(takes_data,root, subdir,"HARVEST")
            if (takes_name == False):
                continue

            start_time = time.time()

            run_harv_decoding(input_dir,takes_name,root, subdir,config_param)

            time.sleep(1)

            detected_problem = False
            perform_get_after_copy2 = False
            for command in command_array:

                ret = run_spec_command(input_dir, takes_name, output_dir_sessions, command, subdir, config_param,nuc_param)

                if (ret == False):
                    print("ERROR: %s files is failure" % command)
                    if (command == "COPY2") or ( command == "NOP"):
                        continue
                    else:
                        detected_problem = True
                        break

                time.sleep(TIME_TO_SLEEP)

            if (detected_problem == True):
                print("ERROR: detected problem for the take : %s:%s" % (takes_name,subdir))
                status = "FAIL"
            else:

                process = subprocess.Popen(['python.exe', current_dir + "\\" + test_in_progress])

                create_joined_file(input_dir, takes_name, output_dir_sessions, output_dir, root, subdir)

                ver_dir = "c:\\gen\%s" % (input_dir)

                #output_path_sessions = lord_dir.replace("localStorage", "remoteStorage")

                if (not os.path.isdir(output_dir)):
                    print("ERROR: Outyput directory %s not exists" % output_dir)
                    continue

                output_path_take = output_dir + "\\" + OUT_DIR_SESSIONS + "\\" + takes_name + "\\" + subdir

                output_path_file = output_path_take + "\\" + subdir + "_joined.mvx"

                if os.path.isfile(output_path_file):

#                if ( COMPRESS == "H264"):
#                    nuc_number_frames = 0
#                    v_number_frames = "N.A."
#                    status = "Done"
#                else:#
                    if (COMPRESS == "H264"):
                        output_path_file_xml = output_path_file.replace("mvx","xml")
                        command_out_xml = r'type %s | findstr  "LookupTable"' % output_path_file_xml
                        v_number_frames = get_frames_number_for_compress(command_out_xml)
                    else:
                        v_number_frames = get_number_frames(ver_dir, output_path_file)
                    if ( check_frame_number_state(int(v_number_frames), int(NUMBER_DEVICES)) == True):
                        status = "Done"

                    else:
                        status = "Fail"
                        number_failed_takes = number_failed_takes + 1

                else:
                    v_number_frames = 0
                    status = "Fail"
                    number_failed_takes = number_failed_takes + 1

                ctypes.windll.kernel32.TerminateProcess(int(process._handle), -1)

            running_time = round(time.time() - start_time, 2)

            time_conventional = str(datetime.timedelta(seconds=running_time))
            now = datetime.datetime.now()
            now_date = now.strftime("%Y-%m-%d %H:%M")

            # Session, Take, Status, Compression,  Joined Frames, Process Time, NUCs, Description, Data, Version
            result_line_out = "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s \n" % (takes_name,subdir,status,COMPRESS,str(v_number_frames),
                                                                    str(time_conventional),str(NUMBER_DEVICES),user_description,now_date ,input_dir)
            print(result_line_out)
            fp.write(result_line_out)

    fp.close()
    if (number_failed_takes == 0):
        ret = True
    else:
        ret = False
    return ret

def system_manager(input_dir,output_dir,lord_dir,remote_location,config_param,nuc_param):

    nowtime = time.strftime('%Y_%m_%d-%H.%M.%S')
    print("Now time:%s" % nowtime)
    logger.info(nowtime)

    start_time = round(time.time(),2)
   #rootpath = os.getcwd()

#    lord_location = "c:\\gen\%s" % lord_dir

    if ( lib.check_conf_directories(input_dir, output_dir,logger) == False):
        stop_test_processing(False)
    else:

        line_out = "MVAgentLauncher system manager : Started "
        print(line_out)
        logger.info(line_out)
        lib.send_run_time_command("start", start_time, "TimeStart")
        takes_data = []
        takes_data,input_dir_def = lib.create_single_takes_data(input_dir)
        harvest_ret = run_harvesting(lord_dir,output_dir,input_dir_def,remote_location,takes_data,config_param,nuc_param)

        running_time = round(time.time() - start_time, 2)
        if (harvest_ret == True):
            line_out = "Harvesting is complited (Running time =" + str(running_time) + " )\n"
        else:
            line_out = "Error: Harvesting process has the problem (Running time = %s) \n  Check the results file \n" % str(
                running_time)
        print(line_out)
        logger.info(line_out)


def getParamsFromTakesData(takes_data, cm):

    indx = 0
    for line in takes_data:
        if ( lib.DEBUG == True):
            print("Index =" + str(indx))
        if (line != '\n'):
            line_in = ' '.join(line.split())
            if (line_in != ""):
                paramValList = line_in.split('=')
                #print(paramValList[0].strip() + " : " + paramValList[1].strip())
                if (paramValList[0].strip())[0] != ';' and (paramValList[0].strip())[0] != '%':
                    cm[paramValList[0].strip()] = paramValList[1].strip()
        indx = indx + 1
    print(cm)


def main_loop(input_location, output_location, lord_takes_location,remote_location,config_param,nuc_param):
    snbrnumber = ""

    current_dir = ""

    choice_prev = []
    
    takes_data = []

    takes_data = lib.create_takes_data(lord_takes_location)

    if (lib.DEBUG == True):
        current_dir = "/".join(__file__.split("/")[:-1])
    else:
        current_dir = "\\".join(__file__.split("\\")[:-1])

    #current_dir = "\\".join(__file__.split("\\")[:-1])  # os.getcwd()

    choice_msg = "Empty"
    ret = menu.get_dir_location("Description")
    if (ret != "False"):
        user_description = ret
    else:
        user_description = ""
    config_param["parameters"]["Description"] = user_description

#    spread_graphs_to_nucs(input_location, config_param)
#    spread_tools_to_ver(input_location, config_param)

    while 1:

        reply = ""
        image = current_dir + "\\menu\\mantis-logo.png"
        msg = "BRINGING 3D VISION TO ALL ! \n\n Selected Takes : \n" + choice_msg
        # title = " MVCalibration "
        title = menu.product_name
        #choices = ["Select Takes", "Run Harvesting", "Delete Takes", "Parameters","Config", "Setting", "Spread","Results", "Help", "About", "Exit"]
        choices = ["Run", "Stop", "Load", "Clean", "Spread Version","Spread Studio","Config", "Setting",
                   "Results", "Help", "About", "Exit"]
        reply = buttonbox(msg, title, choices, image)

        if reply == "Select Takes":
            start_time = time.time()

            takes_data = lib.create_takes_data(lord_takes_location)

            m_ntConfigParams = collections.OrderedDict()
            #strConfigFile = lib.CONFIG_FILE
            getParamsFromTakesData(takes_data,m_ntConfigParams)

            ret_ch,choice_msg = menu.cfg_change_parameters(takes_data,m_ntConfigParams,choice_prev,"Select")

            if (ret_ch == None):
                continue
            else:
                choice_prev = ret_ch

#            running_time = round(time.time() - start_time, 2)
#            line_out = "Calibration is complited (Running time =" + str(running_time) + " )\n"
#            print(line_out)
#            message = "Do you want to see the result file? (Running time = " + str(running_time) + " )"
#            title = menu.product_name
#            if boolbox(message, title, ["Yes", "No"]):
#                menu.read_the_result_file()
#            else:
#                msgbox("Calibration Process is completed  !")

        if reply == "Run Harvesting":
            harvest_ret = False
            start_time = time.time()
            # java -jar androidscreencast-0.0.12s-executable.jar
            harvest_ret = run_harvesting(input_location, output_location, lord_takes_location,remote_location, takes_data,config_param,nuc_param)

            running_time = round(time.time() - start_time, 2)
            if ( harvest_ret == True):
                line_out = "Harvesting is complited (Running time =" + str(running_time) + " )\n"
                msgbox(line_out)
            else:
                line_out = "Error: Harvesting process has the problem (Running time = %s) \n  Check the results file \n" %  str(running_time)
                msgbox(line_out, "red")

            print(line_out)
            logger.info(line_out)
            #gena msgbox(line_out)


        if reply == "Delete Takes":
            start_time = time.time()

            takes_data = lib.create_takes_data(lord_takes_location)

            m_ntConfigParams = collections.OrderedDict()
            #strConfigFile = lib.CONFIG_FILE
            getParamsFromTakesData(takes_data,m_ntConfigParams)

            ret_ch,choice_msg = menu.cfg_change_parameters(takes_data,m_ntConfigParams,choice_prev,"Delete")

            if (ret_ch == None) or (ret_ch == 0):
                continue
            else:
                choice_prev = ret_ch

            delete_takes(lord_takes_location,output_location, "DELETE",takes_data, config_param)

            running_time = round(time.time() - start_time, 2)
            line_out = "Delete Takes Operation is complited (Running time =" + str(running_time) + " )\n"
            print(line_out)
            msgbox(line_out)
            logger.info(line_out)


        if reply == "Parameters":
            if (SET_ZIP_FUNCTIONALITY == True):
                msg = "Select parameters? \n\n ZIP_MODE = %s \n COMPRESS = %s" % (config_param["parameters"]["ZIP_MODE"], config_param["parameters"]["COMPRESS"])
            else:
                msg = "Select parameters? \n\n COMPRESSION = %s" % (config_param["parameters"]["COMPRESS"])
            title = "MV Harvest"

            if ( SET_ZIP_FUNCTIONALITY == True):
                choices = ["1.No change", "2.NO_COMPRESS", "3.H264", "4.ZIP", "5.NOZIP"]
            else:
                choices = ["1.No change", "2.NO_COMPRESS", "3.H264"]

            choice = choicebox(msg, title, choices)
            if (choice == "2.NO_COMPRESS" ) or (choice == "3.H264"):
                choice_cl = choice.split(".")
                config_param["parameters"]["COMPRESS"] = choice_cl[1]
            if (SET_ZIP_FUNCTIONALITY == True):
                if (choice == "4.ZIP" ) or (choice == "5.NOZIP"):
                    choice_cl = choice.split(".")
                    config_param["parameters"]["ZIP_MODE"] = choice_cl


        if reply == "Config":
            #config_text = "Input:  " + input_location + "\nOutput: " + output_location + "\nConfig: " + lord_takes_location + "\nImage: " + image_name
            #           textbox(msg="Continue ?", title="Configure Parameters ", text=config_text, codebox=0)
            msg = "Enter Input Output information"
            title = "Input/Output configuration"
            fieldNames = [r'c:\gen\<Name>', "Output DIR", "Lord DIR","Remote DIR","Description"]
            fieldValuesPrev = [input_location, output_location, lord_takes_location,remote_location,user_description]  # we start with blanks for the values
# gena: for my ver easygui            fieldValues = multenterbox(msg, title, fieldNames, fieldValuesPrev,SIZE_FIELD_PARAM)
            fieldValues = multenterbox(msg, title, fieldNames, fieldValuesPrev,fieldW = 70)

            if (not fieldValues == None):
                msg_problem_dir = " "
                detected_problem = False
                checking_dir = "c:\\gen\\%s" % fieldValues[0]
                perform_create_directory = False
                if ( menu.check_single_directory(checking_dir,perform_create_directory) == True ):
                    input_location = fieldValues[0]
                    menu.extern_test_directories[0] = input_location
                else:
                    detected_problem = True
                    msg_problem_dir = checking_dir

                if (detected_problem == False):
                    if (menu.check_single_directory(fieldValues[1], True) == True):
                        output_location = fieldValues[1]
                        menu.extern_test_directories[1] = output_location
                    else:
                        detected_problem = True
                        msg_problem_dir = msg_problem_dir + output_location

                if (detected_problem == False):
                    if (menu.check_single_directory(fieldValues[2], False) == True):
                        lord_takes_location = fieldValues[2]
                        menu.extern_test_directories[2] = lord_takes_location
                    else:
                        detected_problem = True
                        msg_problem_dir = msg_problem_dir + lord_takes_location

                if (detected_problem == False):

                    if (remote_location != ""):
                        if (menu.check_single_directory(fieldValues[3], True) == True):
                            remote_location = fieldValues[3]
                            menu.extern_test_directories[3] = remote_location
                        else:
                            detected_problem = True
                            msg_problem_dir = msg_problem_dir + remote_location

                if (detected_problem == False):
                    line_out = "Test directories finished !"
                    print(line_out)
                    logger.info(line_out)
                    takes_data = lib.create_takes_data(lord_takes_location)

                    user_description = fieldValues[4]
                    config_param["parameters"]["Description"] = user_description
                    menu.update_dir_location(fieldValues)
                else:
                    line_out = "ERROR: Configuration problem ! Problem Directory : %s " % msg_problem_dir
                    print(line_out)
                    logger.error(line_out)
                    msgbox(line_out, "red")

        if reply == "Setting":

            dev_json_file_name = current_dir + "\\" + DEVICE_FILE_NAME

            msg = "Enter Setting information"
            title = "Setup Parameters"
            setfieldNames = ["NUMBER_NUCS","NUC_ONE","IP Base", "User","Password"]
            setfieldValuesPrev = [
                config_param["setup"]["NUMBER_DEVICES"],
                config_param["setup"]["NUC_ONE"],
                config_param["setup"]["IPADD_BASE"],
                config_param["setup"]["USER"],
                config_param["setup"]["PASSWORD"]
                ]  # we start with blanks for the values
            setfieldValues = multenterbox(msg, title, setfieldNames, setfieldValuesPrev)
            if (not setfieldValues == None):
                config_param["setup"]["NUMBER_DEVICES"] = int(setfieldValues[0])
                config_param["setup"]["NUC_ONE"] = int(setfieldValues[1])
                config_param["setup"]["IPADD_BASE"] = setfieldValues[2]
                config_param["setup"]["USER"] = setfieldValues[3]
                config_param["setup"]["PASSWORD"] = setfieldValues[4]

                with open(dev_json_file_name, 'w') as fp:
                    fp.write(json.dumps(config_param, indent=4,separators=(',', ': '), ensure_ascii=False))

                fp.close()

# start excel harvest_result.csv
        if reply == "Spread":

            msg = "There is the special functionality for :\n 1. the first installation or \n 2. the new application version \n"
            # title = " MVCalibration "
            title = menu.product_name
            choices = ["First Installation", "New Version", "Cancel"]
            reply_spread = buttonbox(msg, title, choices)

            if reply_spread == "First Installation":
                spread_graphs_to_nucs(input_location, config_param)
                spread_tools_to_ver(input_location, config_param)
                msgbox("Spread is done for the first installation  !")

            if reply_spread == "New Version":
                spread_tools_to_ver(input_location, config_param)
                msgbox("Spread is done for the new version  !")

            if reply_spread == "Cancel":
                msgbox("No operation  !")

        if reply == "Results":

            run_html_command = False
            output_result_file = output_location + "\\" + RESULT_FILE_NAME
            line_out = "Results file : %s" % output_result_file

            print(line_out)
            logger.info(line_out)

            display_results_command = "start " + EXCEL_TOOL + " " + output_result_file

            try:
                os.startfile(output_result_file)

            except OSError:
                print("excel command does not work")
                run_html_command = True

            if ( run_html_command == True):
                # Read the csv file in
                df = pd.read_csv(output_result_file)
                output_result_file_html = output_location + "\\" + RESULT_FILE_NAME_HTML
                # Save to file
                df.to_html(output_result_file_html)


                display_results_command_html = "start " + output_result_file_html
                os.system(display_results_command_html)

        if reply == "Help":

            pdfHelp_path = current_dir + "\\menu\\" + menu.pdfHelp
            line_out = "Help file : %s" % pdfHelp_path
            print(line_out)
            logger.info(line_out)
            os.system(pdfHelp_path)
        if reply == "About":
            txtAbout_path = current_dir + "\\menu\\" + menu.txtAbout
            line_out = "Help file : %s" % txtAbout_path
            print(line_out)
            logger.info(line_out)
            menu.display_about(txtAbout_path)
        if reply == "Exit":
            stop_test_processing(True)

    return True


def mantis_call_gui(config_param,nuc_param):
    rootpath = os.getcwd()

    ret = True

    ret = menu.get_dir_location("Input")
    if (ret != "False"):
        lib.input_location = ret
    ret = menu.get_dir_location("Output")
    if (ret != "False"):
        lib.output_location = ret
    ret = menu.get_dir_location("Conf")
    if (ret != "False"):
        lib.lord_takes_location = ret
    ret = menu.get_dir_location("Remote")
    if (ret != "False"):
        lib.remote_location = ret

    ret = main_loop(lib.input_location, lib.output_location, lib.lord_takes_location, lib.remote_location,config_param,nuc_param)

    return ret


def main(argv):
    input_dir = ''
    output_dir = ''
    lord_dir = ''
    opts = ''
    config_param = []
    nuc_param = []
    run_gui_mode = False
    program_name = sys.argv[0]
    try:
        opts, args = getopt.getopt(argv, "ghi:o:l:", ["idir=", "odir=","dfgfile="])
    except getopt.GetoptError:
        line_out = '%s -i <inputdir> -o <outputdir> -l <lorddir>' % (program_name)
        print(line_out)
        logger.error(line_out)
        stop_test_processing(False)
    for opt, arg in opts:
        if opt == '-h':
            print("Shell mode :")
            print('%s -i <inputdir> -o <outputdir> -l <lorddir>' % (program_name))
            print("FOR Graphical mode :")
            print('%s -g' % (program_name))
            stop_test_processing(True)
        elif opt == '-g':
            print('Running GUI mode !')
            run_gui_mode = True
        elif opt in ("-i", "--idir"):
            input_dir = arg
        elif opt in ("-o", "--odir"):
            output_dir = arg
        elif opt in ("-l", "--lorddir"):
            lord_dir = arg

        if (lib.DEBUG == True):
            current_dir = "/".join(__file__.split("/")[:-1])
        else:
            current_dir = "\\".join(__file__.split("\\")[:-1])

        dev_json_file_name = current_dir + "\\" + DEVICE_FILE_NAME

        print("Harvest: config  file = %s" % dev_json_file_name)

        with open(dev_json_file_name, 'r') as fp:
            config_param = json.load(fp)
            fp.close()

        nuc_param_json_file_name = current_dir + "\\" + NUC_PARAM_FILE_NAME

        with open(nuc_param_json_file_name, 'r') as fp_nuc:
            nuc_param = json.load(fp_nuc)
            fp_nuc.close()

    #lib.delete_config_File(lib.CONFIG_DIR)

    #debug
    #run_gui_mode = True

    if (run_gui_mode == True):
        mantis_call_gui(config_param,nuc_param)
        stop_test_processing(True)
    else:
        print('Input dir is "', input_dir)  # Genesis_master_7.0.122
        print('Output dir is "', output_dir)  # C:/STORAGE/localStorage
        #lord_location = "c:\\gen\%s" % lord_dir
        print('LORD Dir is "', lord_dir)  # d:\Storage\localStorage\Sessions\
        remote_location = ""
        # create takes config file
        #takes_data = lib.create_single_takes_data(input_dir)
        system_manager(input_dir,output_dir,lord_dir,remote_location,config_param,nuc_param)

#main()
#if ( lib.DEBUG == True):
if __name__ == "__main__":
###
        main(sys.argv[1:])
        stop_test_processing(True)

        print("System manager is stopped !")
