# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup
import urllib2
import re
import urlparse
import os
import urllib
import sys
import threading, Queue, time
import socket
import random
socket.setdefaulttimeout(10.0)


USER_AGENTS = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
]


def valid_filename(s):
    import string
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    s = ''.join(c for c in s if c in valid_chars)
    return s


def unzip(data):
    import gzip
    import StringIO
    data = StringIO.StringIO(data)
    gz = gzip.GzipFile(fileobj=data)
    data = gz.read()
    gz.close()
    return data

def change_encoidng(content):
    p = re.compile('<meta.*?charset="?(.+?)".*?>') # get charset of the page
    if not (p.search(content)):
    	print 'unknown encoding'
    	return content
    encoding = p.search(content).group(1)
    try:
        content = content.decode(encoding).encode('utf-8')
    except UnicodeDecodeError:
        try:
            content = content.decode('gbk').encode('utf-8')
        except UnicodeDecodeError:
            print 'unknown encoidng'
            content = ''
    return content

def get_page(page):
    content = ''
    # new code
    try:
        headers_post = {
            'User-Agent': random.choice(USER_AGENTS)}

        req = urllib2.Request(page, headers=headers_post)
        response = urllib2.urlopen(req, timeout=3)
        headers = response.info()
        rawData = response.read()
        content = rawData
        # unzip if neccessary
        if ('Content-Encoding' in headers and headers['Content-Encoding']) or \
                ('content-encoding' in headers and headers['content-encoding']):
            content = unzip(rawData)

        content = change_encoidng(content)

    except urllib2.URLError as error:
        print error.reason
        content = ''
    except Exception, e:
        content = ''
        print str(e)
    # end new code
    return content


def get_all_links(content, page):
    links = []
    content = content.decode('utf-8')
    soup = BeautifulSoup(content, 'lxml')
    for item in soup.findAll('a', {'href': re.compile('^http|^/')}):
        link = item.get('href')
        if (link[0] == 'h'):
            pass
        else:
            import urlparse
            link = urlparse.urljoin(page, link)
        link = link.rstrip('/')
        if (link not in links):
            links.append(link)
    return links


def add_page_to_folder(page, content):  # 将网页存到文件夹里，将网址和对应的文件名写入index.txt中
    index_filename = 'index.txt'  # index.txt中每行是'网址 对应的文件名'
    folder = 'html'  # 存放网页的文件夹
    filename = valid_filename(page)  # 将网址变成合法的文件名
    index = open(index_filename, 'a')
    index.write(page.encode('ascii', 'ignore') + '\t' + filename + '\n')
    index.close()
    if not os.path.exists(folder):  # 如果文件夹不存在则新建
        os.mkdir(folder)
    f = open(os.path.join(folder, filename), 'w')
    f.write(content)  # 将网页存入文件
    f.close()
    
def working():
    while True:
        page = q.get()
        if varLock.acquire():
            if page in crawled:
                varLock.release()
            elif len(page) < 255:
                print page
                varLock.release()
                content = get_page(page)
                outlinks = get_all_links(content, page)

                if varLock.acquire():
                    if (len(crawled) >= max_page):
                        while True and not q.empty():
                            q.get()
                            q.task_done()
                    else:
                        if content != '':
                            add_page_to_folder(page, content)
                        graph[page] = outlinks
                        crawled.append(page)
                        for link in outlinks:
                            # only add page that related to brand
                            p = re.compile('http://\w+.zol.com.cn/manu_\d+.*')
                            if p.match(link) and link not in crawled:
                                q.put(link)
                    varLock.release()
        q.task_done()
        time.sleep(.500)

if __name__ == '__main__':
        
    seed = sys.argv[1]
    #method = sys.argv[2]
    max_page = int(sys.argv[2])
    start = time.clock()
    NUM = 40
    crawled = []
    graph = {}
    varLock = threading.Lock()
    q = Queue.Queue()
    q.put(seed)
    for i in range(NUM):
        t = threading.Thread(target=working)
        t.setDaemon(True)
        t.start()
    q.join()
    print 'size of crawled:', len(crawled) #the page printed on screen may be more than expected
    end = time.clock()
    print end-start
