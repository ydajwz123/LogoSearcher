import pickle

prod_info = {}

f = open('prod_info_dic.txt', 'r')
for prod_with_info in f.xreadlines():
    prod, imgurl, price = prod_with_info.split('\t')
    prod_info[prod] = (imgurl, price)

f.close()

f = open('prod_info_dic', 'w+')
pickle.dump(prod_info, f)
f.close()