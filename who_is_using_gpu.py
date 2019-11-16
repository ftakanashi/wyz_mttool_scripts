#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
Usage: python who_is_using_gpu.py <pid>
The pid can be fetched by running command nvidia-smi.
'''

import re
import sys
import subprocess

def analyze_process(pid):
    cmd = 'ps -ef | grep -v grep | grep {}'.format(pid)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if err != '':
        raise Exception('Error Encountered while finding ppid.\n{}'.format(err))
    for row in out.strip().split('\n'):
        spans = row.split()
        if pid == int(spans[1]):
            return int(spans[2]), out.strip()
    raise Exception('Cannot find any process with pid [{}]'.format(pid))

def find_all_containers():
    cmd = 'docker ps -a --format \'{{.ID}} {{.Names}}\''
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if err != '':
        raise Exception('Failed to get container information:\n{}'.format(err))
    else:
        return {s.split(' ')[0]: s.split(' ')[1] for s in out.split('\n') if s}

def main():
    lowest_pid = int(sys.argv[1])
    ppid, content = analyze_process(lowest_pid)
    container_info = find_all_containers()
    while ppid != 0:
        m = re.search('io\.containerd\.runtime\.v1\.linux\/moby\/(.+?)$', content.strip())
        if m is None:
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
                print('Container [{}:{}] is using GPU!'.format(container_info[cid], cid))
            else:
                print('Locate [{}] but did not find any match containers in docker ps list.'.format(cid))
            return

    print('Cannot find any matched containers...')

if __name__ == '__main__':
    main()