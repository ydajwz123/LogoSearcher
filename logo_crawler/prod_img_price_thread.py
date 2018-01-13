# -*- coding:utf-8 -*-
from crawler_thread import *
    
def working():
    while True:
        prod, page = q.get().split('\t')
        if varLock.acquire():
            # print page
            varLock.release()
            content = get_page(page).decode('utf-8')
            if len(content) == 0:
                tmp_file = open('cannot_get.txt', 'w+')
                tmp_file.write(prod+'\t'+page)
                tmp_file.close()
                continue
            soup = BeautifulSoup(content, 'lxml')
            imgurl = 'no_pic'
            img = soup.find('img', itemprop='photo')
            if (img):
                imgurl = img.get('src')
            else:
                img = soup.find('div', class_='product-pics')
                if (img):
                    img = img.find('img')
                    imgurl = img.get('src')
            price = 'no_price'
            pri = soup.find('div', class_='price price-normal')
            if (pri):
                price = pri.span.get_text()
            else:
                pri = soup.find('div', class_='price price-sp-num')
                if (pri):
                    price = pri.span.get_text()
                else:
                    pri = soup.find('div', class_='price price-np-num')
                    if (pri):
                        price = pri.span.get_text()
            if varLock.acquire():
                prod_info[prod] = (imgurl, price)
                print prod, imgurl, price
                f.write(prod+'\t'+imgurl.encode('utf-8')+'\t'+price.encode('utf-8')+'\n') 
                if (imgurl == 'no_pic'):
                    print prod
                varLock.release()
        q.task_done()
        time.sleep(.500)

if __name__ == '__main__':
        
    #method = sys.argv[2]
    start = time.clock()
    NUM = 16
    crawled = []
    graph = {}
    prod_info = {} # item with (img, price)
    varLock = threading.Lock()
    q = Queue.Queue()
    f = open('prod_detail_url', 'r')
    prods_hrefs = f.readlines()
    f.close()
    for prod_href in prods_hrefs:
        if len(prod_href) < 10:
            continue
        q.put(prod_href)
    f = open('prod_info_dic.txt', 'a+')
    for i in range(NUM):
        t = threading.Thread(target=working)
        t.setDaemon(True)
        t.start()
    q.join()
    end = time.clock()
    f.close()
    print end-start
