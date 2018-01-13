# -*- coding:utf-8 -*-
import sys, os
import pickle

prod_info = {}
f = open('prod_info_dic', 'r')
prod_info = pickle.load(f)
f.close()

store_dir = 'brands'
for root, dirnames, filenames in os.walk(store_dir):
    for filename in filenames:
        print filename
        path = os.path.join(root, filename)
        f = open(path, 'r+')
        lines = f.read().split('\n')
        for i in range(4, len(lines)):
            imgurl, prod, price = lines[i].strip('\n').split('\t')
            if prod_info.get(prod, 0) == 0: 
                continue
            if prod_info[prod][0][0] == 'h':
                imgurl = prod_info[prod][0]
            if price[0] == 'n':
                
                price = prod_info[prod][1].strip('\n')
            lines[i] = '\t'.join([imgurl, prod, price])
        f.seek(0)
        f.truncate()
        f.write('\n'.join(lines))
        f.close()