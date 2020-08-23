#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json

with open('train.json', 'r') as f:
    content = f.read().strip()

content = json.loads(content)

ans_count = 0
null_count = 0

for info in content['data']:
    for qa in info['paragraphs'][0]['qas']:
        if qa['is_impossible']:
            null_count += 1
        else:
            ans_count += 1

print(f'Answer Count:{ans_count}\nNull Count: {null_count}')