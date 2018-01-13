import os
import urllib, urllib2
from bs4 import BeautifulSoup
pa = os.getcwd()
for root, dirnames, filenames in os.walk(os.path.join(pa, 'brands')):
    for filename in filenames:
        try:
            path = os.path.join(root, filename)
            file = open(path, 'a')
            contents = unicode(file.read(), 'utf-8')
            contents = contents.split('\n')
            pic = urllib.urlretrieve(contents[3])
            img = cv2.imread(pic[0], cv2.IMREAD_GRAYSCALE)
            imgca = canny(img)
            huju = hu(imgca)
            for i in range(0, 7):
                file.write('\n' + str(huju[i]))
            file.close()
        except Exception, e:
            print "Failed in indexDocs:", e
