#!/usr/bin/env python
# -*- coding:utf-8 -*-

import xlrd
import sys

fn = sys.argv[1]
idx = int(sys.argv[2])

wk = xlrd.open_workbook(fn, 'r')
st = wk.sheet_by_index(idx)

for i in range(st.nrows):
    values = st.row_values(i)
    print('|{}|'.format('|'.join([str(v) for v in values])))
