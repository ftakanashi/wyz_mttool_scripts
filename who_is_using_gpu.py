#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
Basic Usage: python who_is_using_gpu.py -p <pid>
The pid can be fetched by running command nvidia-smi.
'''

import argparse
import re
import subprocess
import sys

def analyze_process(pid):
    cmd = 'ps -ef | grep -v grep | grep {}'.format(pid)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if err != '':
        raise Exception('Error Encountered while finding ppid.\n{}'.format(err))
    for row in out.strip().split('\n'):
        spans = row.split()
        if pid == int(spans[1]):
            return int(spans[2]), row.strip()
    raise Exception('Cannot find any process with pid [{}]'.format(pid))

def find_all_containers():
    cmd = 'docker ps -a --format \'{{.ID}} {{.Names}}\''
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if err != '':
        raise Exception('Failed to get container information:\n{}'.format(err))
    else:
        return {s.split(' ')[0]: s.split(' ')[1] for s in out.split('\n') if s}

def analyze_lowest_process(lowest_pid, show_process_tree=False):
    try_count = 0
    ppid, content = analyze_process(lowest_pid)
    container_info = find_all_containers()
    while ppid != 0:
        m = re.search('io\.containerd\.runtime\.v1\.linux\/moby\/(.+?)$', content.strip())
        if m is None:
            if show_process_tree:
                print('{}**{}'.format('  ' * try_count, content.strip()))
                print('{}||'.format('  ' * try_count))
            try_count += 1
            ppid, content = analyze_process(ppid)
        else:
            cid = m.group(1)
            if len(cid) < 12:
                cid_len = len(cid)
                stripped_container_info = {k[:cid_len]: v for k,v in container_info.items()}
                container_info = stripped_container_info
            else:
                cid = cid[:12]
            if cid in container_info:
                if show_process_tree:
                    print('{}**{}'.format('  ' * try_count, content.strip()))
                print('Container ({})[{}:{}] is using GPU!'.format(lowest_pid, container_info[cid], cid))
            else:
                print('Locate [{}] but did not find any match containers in docker ps list.'.format(cid))
            return

    print('Cannot find any matched containers for [{}]...'.format(lowest_pid))

def get_all_gpu_processes():
    res = []
    cmd = 'nvidia-smi'
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if err:
        raise Exception('Error encoutered while getting all gpu processes:\n{}'.format(err))

    if sys.version[0] == '3':
        out = str(out, encoding='utf-8')
    rows = out.split('\n')
    flag_line = '|  GPU       PID   Type   Process name                             Usage      |'
    flag_index = rows.index(flag_line)

    if flag_index == -1:
        raise Exception('I bet your nvidia-smi has some problem...')

    content = rows[flag_index+2:-2]
    for row in content:
        spans = row.split()
        if spans[3] == 'C':
            # yield spans[2]
            res.append(int(spans[2]))

    return res


def main():

    args = argparse.ArgumentParser()
    args.add_argument('-p', '--pid', default=-1, type=int,
                      help='Specify the pid to find container.')
    args.add_argument('--show-process-tree', action='store_true', default=False,
                      help='Show the process tree based on backtrace route.')

    opt = args.parse_args()

    # lowest_pid = int(sys.argv[1])
    lowest_pid = int(opt.pid)
    if lowest_pid == -1:
        pids = get_all_gpu_processes()
        if len(pids) == 0:
            print('Cannot find any gpu process.')
            return
        for pid in pids:
            analyze_lowest_process(pid, opt.show_process_tree)
    else:
        analyze_lowest_process(lowest_pid, opt.show_process_tree)


if __name__ == '__main__':
    main()