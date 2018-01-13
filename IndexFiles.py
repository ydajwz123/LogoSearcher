#!/usr/bin/env python
# -*- coding:utf-8 -*-

INDEX_DIR = "IndexFiles.index"

import sys, os, lucene, threading, time
from datetime import datetime

from java.io import File
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.analysis.cn.smart import SmartChineseAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version

import jieba

"""
This class is loosely based on the Lucene (java implementation) demo class 
org.apache.lucene.demo.IndexFiles.  It will take a directory as an argument
and will index all of the files in that directory and downward recursively.
It will index on the file path, the file name and the file contents.  The
resulting Lucene index will be placed in the current directory and called
'index'.
"""

class Ticker(object):

    def __init__(self):
        self.tick = True

    def run(self):
        while self.tick:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1.0)

class IndexFiles(object):
    """Usage: python IndexFiles <doc_directory>"""

    def __init__(self, root, storeDir, analyzer):

        if not os.path.exists(storeDir):
            os.mkdir(storeDir)

        store = SimpleFSDirectory(File(storeDir))
        analyzer = LimitTokenCountAnalyzer(analyzer, 1048576)
        config = IndexWriterConfig(Version.LUCENE_CURRENT, analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        writer = IndexWriter(store, config)
        self.indexDocs(root, writer)
        ticker = Ticker()
        print 'commit index',
        threading.Thread(target=ticker.run).start()
        writer.commit()
        writer.close()
        ticker.tick = False
        print 'done'

    def indexDocs(self, root, writer):
        t1 = FieldType()
        t1.setIndexed(True)
        t1.setStored(True)
        t1.setTokenized(False)
        t1.setIndexOptions(FieldInfo.IndexOptions.DOCS_AND_FREQS)
        
        t2 = FieldType()
        t2.setIndexed(True)
        t2.setStored(False)
        t2.setTokenized(True)
        t2.setIndexOptions(FieldInfo.IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

        t3 = FieldType()
        t3.setIndexed(False)
        t3.setStored(True)
        t3.setTokenized(False)
        t3.setIndexOptions(FieldInfo.IndexOptions.DOCS_ONLY)

        t4 = FieldType()
        t4.setIndexed(True)
        t4.setStored(True)
        t4.setTokenized(True)
        t4.setIndexOptions(FieldInfo.IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

        for root, dirnames, filenames in os.walk(root):
            for filename in filenames:
                print "adding", filename
                try:
                    path = os.path.join(root, filename)
                    file = open(path)
                    contents = unicode(file.read(), 'utf-8')
                    file.close()
                    doc = Document()
                    doc.add(Field("path", root, t1))
                    if len(contents) > 0:
                        tmp = contents.split('\n')
                        name1 = list(tmp[0].split())[0]
                        name2 = list(tmp[0].split())[1]
                        tmp2 = tmp[1].split('.')
                        for i in range(len(tmp2)):
                            if tmp2[i] == "www":
                                content.append(tmp2[i + 1])
                        homepage = tmp[1]
                        intro = tmp[2]
                        
                        content = []
                        for i in range(20):
                            content.append(name1)
                            content.append(name2)
                        content.extend(jieba.cut(tmp[2]))

                        logo = tmp[3]
                        goods = ""
                        if len(tmp) > 4:
                            goods = '\n'.join(tmp[4 :])
                            
                            for i in range(len(tmp)):
                                if i > 3:
                                    tmp3 = tmp[i].split()
                                    content.extend(jieba.cut(tmp3[1]))
                        content = ' '.join(content)

                        name1_field = Field("name1", name1, t4)
                        name1_field.setBoost(1.9)
                        doc.add(name1_field)
                        name2_field = Field("name2", name2, t4)
                        name2_field.setBoost(1.9)
                        doc.add(name2_field)
                        doc.add(Field("homepage", homepage, t3))
                        intro_field = Field("intro", intro, t4)
                        doc.add(intro_field)
                        doc.add(Field("intro", intro, t4))
                        doc.add(Field("logo", logo, t3))
                        doc.add(Field("goods", goods, t4))
                        
                        contents_field = Field("contents", content, t2)
                        doc.add(contents_field)

                    else:
                        print "warning: no content in %s" % filename
                    writer.addDocument(doc)
                except Exception, e:
                    print "Failed in indexDocs:", e

if __name__ == '__main__':
    """
    if len(sys.argv) < 2:
        print IndexFiles.__doc__
        sys.exit(1)
    """
    vm_env = lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    vm_env.attachCurrentThread()
    print 'lucene', lucene.VERSION
    start = datetime.now()
    try:
        """
        base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        IndexFiles(sys.argv[1], os.path.join(base_dir, INDEX_DIR),
                   StandardAnalyzer(Version.LUCENE_CURRENT))
                   """
        analyzer = SmartChineseAnalyzer(Version.LUCENE_CURRENT)
        IndexFiles("brands", "index", analyzer)
        end = datetime.now()
        print end - start
    except Exception, e:
        print "Failed: ", e
        raise e
