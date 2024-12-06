#!/usr/bin/env python3

'''
OPS445 Assignment 2
Program: assignment2.py
Author: Hassnain Mohammad
Semester: Fall 2024

The python code in this file is original work written by
"Hassnain Mohammad". No code in this file is copied from any other source
except those provided by the course instructor, including any person,
textbook, or on-line resource. I have not shared this python script
with anyone or anything except for submission for grading.
I understand that the Academic Honesty Policy will be enforced and
violators will be reported and appropriate action will be taken.

Description: Assignment 2 - Version A

'''

import argparse
import os, sys

def parse_command_args() -> object:
    "Set up argparse here. Call this function inside main."
    parser = argparse.ArgumentParser(description="Memory Visualiser -- See Memory Usage Report with bar charts",epilog="Copyright 2023")
    parser.add_argument("-H", "--human-readable", action="store_true", help="Prints sizes in human readable format")
    parser.add_argument("-l", "--length", type=int, default=20, help="Specify the length of the graph. Default is 20.")
    # add argument for "human-readable". USE -H, don't use -h! -h is reserved for --help which is created automatically.
    # check the docs for an argparse option to store this as a boolean.
    parser.add_argument("program", type=str, nargs='?', help="if a program is specified, show memory use of all associated processes. Show only total use if not.")
    args = parser.parse_args()
    return args
# create argparse function
# -H human readable
# -r running only

def percent_to_graph(percent: float, length: int=20) -> str:
    "turns a percent 0.0 - 1.0 into a bar graph"

#Validate if percentage is between 0.0 and 1.0
    if percent < 0.0:
        percent = 0.0

    elif percent > 1.0:
        percent = 1.0

#Total number of symbols to visualize
    symbol_count = int(percent * length)

#Creating the visual graph
    visual_graph = "." * symbol_count + " " * (length - symbol_count)

    return visual_graph
# percent to graph function


def get_sys_mem() -> int:
    "return total system memory (used or available) in kB"

#Finding the system memory
    file = open('/proc/meminfo', 'r')

    for data_line in file:

        if "MemTotal" in data_line:
            total_mem_kb = int(data_line.split()[1])
            file.close()
            return total_mem_kb

        file.close()


def get_avail_mem() -> int:
    "return total memory that is available"

#Finding the system memory
    file = open('/proc/meminfo', 'r')
    mem_free = 0
    swap_free = 0
    mem_available = False

    for data_line in file:

        if "MemFree" in data_line:
            mem_free = int(data_line.split()[1]) #For MemFree

        elif "SwapFree" in data_line:
            swap_free = int(data_line.split()[1]) #For SwapFree

        elif "MemAvailable" in data_line:
            mem_available = int(data_line.split()[1]) #For MemAvailable

#MemFree + SwapFree (for WSL)
    file.close()

    if mem_available == False:
        return mem_free + swap_free

    return mem_available


def pids_of_prog(app_name: str) -> list:
    "given an app name, return all pids associated with app"

#Getting the list of pids
    process_list = os.popen(f"pidof {app_name}").read()

#Generating a list of pids
    if process_list:
        return process_list.split()

#Return pid list
    return []


def rss_mem_of_pid(proc_id: str) -> int:
    "given a process id, return the resident memory used, zero if not found"

#Finding the status file
    status_line = f"/proc/{proc_id}/status"

    try:

#Opening the status file
        file = open(status_line, 'r')

#To see if the lines in the file is available
        for line in file:
            if line[0:5] == "VmRSS":  # First 5 characters
                file.close()
                return int(line.split()[1]) #Return resident memory

        file.close()

    except (FileNotFoundError, PermissionError):
        return 0

    return 0


def bytes_to_human_r(kibibytes: int, decimal_places: int=2) -> str:
    "turn 1,024 into 1 MiB, for example"
    suffixes = ['KiB', 'MiB', 'GiB', 'TiB', 'PiB']  # iB indicates 1024
    suf_count = 0
    result = kibibytes
    while result > 1024 and suf_count < len(suffixes):
        result /= 1024
        suf_count += 1
    str_result = f'{result:.{decimal_places}f} '
    str_result += suffixes[suf_count]
    return str_result

if __name__ == "__main__":
    args = parse_command_args()

#If program is not provided
    if not args.program:
        total_mem = get_sys_mem()  #Total system memory in kB
        free_mem = get_avail_mem()  # Get available free memory
        used_mem = total_mem - free_mem  # Find out the used memory
        mem_percent = used_mem / total_mem  # Find out used memory percentage
        mem_graph = percent_to_graph(mem_percent, args.length)

#Printing in human-readable format
        if args.human_readable:
            total_mem_h = bytes_to_human_r(total_mem)
            used_mem_h = bytes_to_human_r(used_mem)
            print(f"Mem         [{mem_graph} | {int(mem_percent * 100)}%] {used_mem_h}/{total_mem_h}")
        else:
            print(f"Mem         [{mem_graph} | {int(mem_percent * 100)}%] {used_mem}/{total_mem}")

    else:

#If program is provided
        process_ids = pids_of_prog(args.program)

        if not process_ids:
            print(f"{args.program} not found.")  #PIDs are not detected
        else:
            total_program_mem = 0
            total_mem = get_sys_mem()  #Show total system memory

#Calculate PID and memory usage
            for pid in process_ids:
                process_mem = rss_mem_of_pid(pid)  #Getting the memory
                total_program_mem += process_mem  # Adding process memory
                mem_percent = process_mem / total_mem  #Memory Percent
                mem_graph = percent_to_graph(mem_percent, args.length)  #Memory Graph

#Print usage
                if args.human_readable:
                    process_mem_h = bytes_to_human_r(process_mem)
                    total_mem_h = bytes_to_human_r(total_mem)
                    print(f"PID {pid}      [{mem_graph} | {int(mem_percent * 100)}%] {process_mem_h}/{total_mem_h}")
                else:
                    print(f"PID {pid}      [{mem_graph} | {int(mem_percent * 100)}%] {process_mem}/{total_mem}")

#Print total memory used
            if args.human_readable:
                total_program_mem_h = bytes_to_human_r(total_program_mem)
                total_mem_h = bytes_to_human_r(total_mem)
                print(f"{args.program} total memory used: {total_program_mem_h}/{total_mem_h}")
            else:
                print(f"{args.program} total memory used: {total_program_mem}/{total_mem}")

    # process args
    # if no parameter passed,
    # open meminfo.
    # get used memory
    # get total memory
    # call percent to graph
    # print

    # if a parameter passed:
    # get pids from pidof
    # lookup each process id in /proc
    # read memory used
    # add to total used
    # percent to graph
    # take total our of total system memory? or total used memory? total used memory.
    # percent to graph.
