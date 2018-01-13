# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup
import urllib2
import re
import socket

from crawler_thread import unzip, change_encoidng, get_page
socket.setdefaulttimeout(10.0)
    

def get_company_info_of(company_name):
    # solve situation such as 'MSI微星', 'Acer宏碁'
    u_company_name = company_name.decode('utf-8')
    en_name_p = re.compile(u'^[a-zA-Z0-9-]+')
    if en_name_p.search(u_company_name):
        company_name = en_name_p.search(u_company_name).group(0).encode('utf-8')
    if '苹果' in company_name:
        company_name = '苹果公司'
    page = 'http://baike.baidu.com/item/'+company_name
    print 'crawling', page
    content = get_page(page)
    soup = BeautifulSoup(content.decode('utf-8'), 'lxml')
    # solve situation where company name polysemant
    taget_page = ''
    polysemantList = soup.find('ul', class_='polysemantList-wrapper')
    if polysemantList != None:
        for child in polysemantList.children:
            if child.name == 'li':
                if not child.a:
                    continue
                title = child.a.get('title').encode('utf-8')
                taget_page = child.a.get('href')
                if ('品牌' in title or '公司' in title or '制造商' in title or '集团' in title or '企业' in title)\
                    and company_name in title:
                    page = 'http://baike.baidu.com'+taget_page
    if taget_page != '':
        content = get_page(page)
        soup = BeautifulSoup(content.decode('utf-8'), 'lxml')

    item = soup.find('div', class_='lemma-summary')
    if (item):
        for sup in item(['sup']):
            sup.extract()
        res = item.get_text().encode('utf-8')
        res = res.split()

        res = ''.join(res)
        if '公司' in res or '集团' in res:
            return res
        else:
            return ''
    else:
        print 'failed to get info of', company_name
        return ''


# crawled = []
# graph = {}

if __name__ == '__main__':
    print get_company_info_of(u'OPPO')
