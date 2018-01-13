# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup
import os
import re
import threading, Queue, time

from crawler_company import get_company_info_of

devices_var = ['笔记本电脑', '投影机', '数码摄像机', '手机', '移动电源\(充电宝\)', '台式电脑',
               '内存', '显卡', '平板电脑', '摄像头', '平板电视', '主板', 'MP3', '上网本',
               '数码相机', 'MP4', '服务器', '光驱', '冰箱', '洗衣机', '空调', '闪存卡',
               '电子书', '激光打印机', '打印机', '电纸书', '音箱', '显示器', '耳机', '固态硬盘',
               '智能手环', '数码相框', '一体电脑', 'NAS网络存储', '插座', '散热器', 'CPU',
               'DIY组装电脑', '超极本','一体台式机', '数字标牌', '专业显示器', '液晶显示器', '工作站',
               'DVD播放机']

def valid_filename(s):
    res = []
    for char in s:
        if char != '/':
            res.append(char)
    return ''.join(res)

def getPartialInfoFromType1(soup):
    
    brand_website = soup.find('a', rel='nofollow')
    if brand_website:
        brand_website = brand_website.get('href').encode('utf-8')
    else:
        brand_website = 'no_brand_website'
    # first try 
    hot_prod_list = soup.find('div', class_='aside imageLazyLoad')
    hot_products = []
    if not(hot_prod_list):
        pass
    else:
        hot_prod_list = hot_prod_list.find('div', class_='section')
        if (hot_prod_list) and '排行榜' in str(hot_prod_list):
            for child in hot_prod_list.ul.children:
                if child.name == 'li':
                    img = child.a.img.get('src')
                    name = child.a.img.get('alt')
                    price = child.find('a', class_='r-buy')
                    target = child.a.get('href')
                    if price == None:
                        price = 'no_price'
                    else:
                        price = price.get_text()
                    # print child
                    hot_products.append([img, name, price, target])
    return brand_website, hot_products


def getPartialInfoFromType2(soup):
    try:
        brand_website = ''
        intro_p = soup.find('div', class_='brand_logo clearfix')
        brand = intro_p.h1.get_text().encode('utf-8').strip()
        try:
            brand_website = intro_p.ul.find('a').get('href')
            # print brand_website
        except:
            brand_website = 'no_brand_website' 

        diff_devices_hot_prods = soup.findAll('div', class_='top10')
        diff_kinds_hot_products = [] # (dev_var, hot_products)
        for one_kind_hot_prods in diff_devices_hot_prods:
            dev_var = one_kind_hot_prods.dl.dt.get_text().encode('utf-8')
            dev_var = dev_var.split()[-2]
            hot_prod_list = one_kind_hot_prods.find('ul', {'id': re.compile('p_ph_\d_1')})
            if not (hot_prod_list):
                # print 'no hot products'
                return brand, brand_website, []
            hot_products = []
            for child in hot_prod_list.children:
                if child.name == 'li' and len(child) > 2:
                    pic = child.a.img.get('src').encode('utf-8')
                    name = child.p.get_text().encode('utf-8')
                    price = child.find('em').get_text().encode('utf-8')
                    hot_products.append([pic, name, price])
                elif child.name =='li' and len(child) == 2:
                    pic = 'no_pic'
                    name = child.a.get('title').encode('utf-8')
                    price = child.span.get_text().encode('utf-8')
                    target = child.a.get('href').encode('utf-8')
                    hot_products.append([pic, name, price, target])
            diff_kinds_hot_products.append((dev_var, hot_products))

        #brand_website = intro_p.next_sibling.name
        #print brand_website
        return brand, brand_website, diff_kinds_hot_products
    except Exception as e:
        print e

def working():
    while True:
        filename = q.get()
        if not filename.startswith('http'):
            continue
        print 'adding', filename
        #try:
        if True:
            path = os.path.join(root, filename)
            file = open(path)
            contents = unicode(file.read(), 'utf-8')
            file.close()

            if len(contents) > 0:
                brand_name = ''
                brand_img = ''
                brand_intro = ''
                brand_website = ''
                hot_products = []
                diff_kinds_hot_products = []
                brand = ''
                devices_variety = ''
                soup = BeautifulSoup(contents, 'lxml')
                brand_tag = soup.find('img', id='logo_img')
                if not (brand_tag):
                    print 'no logo'
                    continue
                brand_name = brand_tag.get('alt').encode('utf-8')
                brand_img = brand_tag.get('src').encode('utf-8')
                intro_span = soup.find('span', class_='sub-title-text')
                site_type = 1
                if not (intro_span):
                    # print 'no span'
                    # maybe type 2
                    site_type = 2
                    intro_span = soup.findAll('p', class_='p')
                    if not (intro_span) or len(intro_span) == 1:
                        site_type = 0
                        continue
                    else:
                        intro_span = intro_span[1]

                brand_intro = intro_span.get_text().encode('utf-8').strip()

                if site_type == 1:
                    brand_website, hot_products = \
                    getPartialInfoFromType1(soup)
                elif site_type == 2:
                    brand, brand_website, diff_kinds_hot_products = \
                    getPartialInfoFromType2(soup)
                if len(hot_products) == 0 and len(diff_kinds_hot_products) == 0:
                    continue

                if site_type == 1:           
                    patt = re.compile(('(.*?)('+'|'.join(devices_var)+')').decode('utf-8'))
                    match_res = patt.match(brand_name.decode('utf-8'))
                    # print brand_name
                    brand = match_res.group(1).encode('utf-8')
                    devices_variety = match_res.group(2).encode('utf-8')
                    print brand, devices_variety
                    company_intro = get_company_info_of(brand)
                    if company_intro:
                        brand_intro = company_intro
                    store_path = os.path.join(store_dir, brand_name)
                    if not os.path.exists(store_dir):
                        os.mkdir(store_dir)

                    file = open(store_path, 'w+')
                    file.write(brand+'\t')
                    file.write(devices_variety)
                    file.write('\n')
                    file.write(brand_website)
                    file.write('\n')
                    file.write(brand_intro)
                    file.write('\n')
                    file.write(brand_img)
                    for hot_product in hot_products:
                        file.write('\n')
                        file.write(hot_product[0].encode('utf-8').strip())
                        file.write('\t')
                        file.write(hot_product[1].encode('utf-8').strip())
                        file.write('\t')
                        file.write(hot_product[2].encode('utf-8').strip())
                        if varLock.acquire():
                            f_prod_href.write(hot_product[1].encode('utf-8').strip()+'\t')
                            f_prod_href.write(hot_product[3].encode('utf-8').strip()+'\n')
                            varLock.release()
                    file.close()
                elif site_type == 2:
                    company_intro = get_company_info_of(brand)
                    if company_intro:
                        brand_intro = company_intro
                    for dev_var, hot_products in diff_kinds_hot_products:

                        if brand in dev_var:
                            dev_var = dev_var[len(brand):]
                        
                        # print brand_name
                        dev_var = valid_filename(dev_var)
                        print brand, dev_var
                        brand_name = brand+dev_var
                        store_path = os.path.join(store_dir, brand_name)
                        if not os.path.exists(store_dir):
                            os.mkdir(store_dir)
                        file = open(store_path, 'w+')
                        file.write(brand+'\t'+dev_var+'\n')
                        file.write(brand_website)
                        file.write('\n')
                        file.write(brand_intro)
                        file.write('\n')
                        file.write(brand_img)
                        for hot_product in hot_products:
                            file.write('\n')
                            file.write(hot_product[0].strip())
                            file.write('\t')
                            file.write(hot_product[1].strip())
                            file.write('\t')
                            file.write(hot_product[2].strip())
                            if len(hot_product[0]) < 10:
                                if varLock.acquire():
                                    f_prod_href.write(hot_product[1].strip()+'\t')
                                    f_prod_href.write(hot_product[3].strip()+'\n')
                                    varLock.release()
                        file.close()
        q.task_done()
        time.sleep(.500)
if __name__ == '__main__':

    root = 'html'
    store_dir = 'brands'
    NUM = 8
    q = Queue.Queue()
    for root, dirnames, filenames in os.walk(root):
        for filename in filenames:
            q.put(filename)
    f_prod_href = open('prod_detail_url.txt', 'a+')
    varLock = threading.Lock()
    for i in range(NUM):
        t = threading.Thread(target=working)
        t.setDaemon(True)
        t.start()
    q.join()
    f_prod_href.close()