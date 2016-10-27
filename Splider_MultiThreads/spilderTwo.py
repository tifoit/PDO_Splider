# -*- coding: utf-8 -*-
#此程序用于爬取人民日报下的数据资源。主页面需要提取包括1946年到2003年之间所有月份
#次级页面是各个月份的所有报道
#末级页面是报道内容
#使用多线程提高爬取效率
'''
Created on 2016年10月27日

@author: joe
'''

import threading, Queue
from time import clock
import urllib2, bs4, os, re


starturl="http://rmrbw.info/"
shareMonthQueue=Queue.Queue()  #存储月份url的公共队列
shareReportQueue=Queue.Queue() #c存储新闻url的公共队列
_WORK_MONTH_THREAD_NUM=3       #用于处理月份url的爬虫数量
_WORK_REPORT_THREAD_NUM_=10    #用于处理新闻url的爬虫数量
totalNum=0  #全局计数器
mutex=threading.Lock() #互斥锁
# tlist=[]<span style="white-space:pre">    </span>#线程列表
t1=clock()
t2=clock()
t3=clock()
t4=clock()


class monthSplider(threading.Thread):
    def __init__(self,name,dicPath = os.getcwd()+os.path.sep+"data"+os.path.sep):
        threading.Thread.__init__(self)
        self.name=name
        self.dicPath=dicPath
        self.TIMEOUT=10

    def run(self):
        start=clock()
        end=clock()
        while True:
            if shareMonthQueue.empty()==False:
                start=clock()
                monthurl=shareMonthQueue.get()
                try:
                    page=urllib2.urlopen(monthurl).read()
                    soup=bs4.BeautifulSoup(''.join(page),'lxml')
                except Exception as e:
                    print "loading url error at line 43"
                    print e
                    continue
                title=soup.find('a','fl')   #找到年月的标签位置
                month=title.contents[0]
                curpath=os.getcwd()
                #print month.encode('utf8')
                datapath=self.dicPath+month.encode('gbk')
                if os.path.exists(datapath)==False:
                    os.mkdir(datapath)                       #创建好当月文件夹

                pages=soup.find('div','pages').contents[-1]
                totalpage=pages.split(' ')[3].split('/')[1]   #得到总页面数
                templist=monthurl.split('=')
                curpage=templist[-1]
                curpage=int(curpage.strip())              #得到当前页面值
        
                #判断如果curpage小于totalpage，则把curpage+1得到下一个页面放入shareMonthQueue中
                if curpage<totalpage:
                    templist[-1]=str(curpage+1)
                    nexturl='='.join(templist)
                    shareMonthQueue.put(nexturl)
                #获取当前页面所有新闻的url,并把url放入shareReportQueue里
                res=soup.find_all(id=re.compile("a_ajax_"))
                for item in res:
                    shareReportQueue.put(starturl+item['href'])
            else:
                #在shareMonthQueue为空的情况下等待TIMEOUT秒后退出
                end=clock()
                if (end-start)>self.TIMEOUT:
                    break
                    
class reportSpider(threading.Thread):
    def __init__(self,name,dicPath = os.getcwd()+os.path.sep+"data"+os.path.sep):
        threading.Thread.__init__(self)
        self.name=name
        self.dicPath=dicPath
        self.TIMEOUT=10
        
    def run(self):
        start=clock()
        end=clock()
        while True:
            if shareReportQueue.empty()==False:
                start=clock()
                url=shareReportQueue.get()
                try:
                    page=urllib2.urlopen(url).read()
                    soup=bs4.BeautifulSoup(''.join(page),'lxml')
                except Exception as e:
                    print "loading url error at line 93"
                    print e
                    continue
                month=soup.find('a',href=re.compile('thread.php')).get_text().strip() #解析当前网页所在年月
                month=month.encode('gbk')
                title=soup.find('h1','fl').get_text() #解析当前网页的新闻标题

                title=title.strip().split(' ')[0]
                #print title.encode('utf8')
                cont_div=soup.find('div','tpc_content')
                cont=cont_div.get_text().strip()   #解析当前网页的新闻内容
                title=title.encode('gbk')
                cont=cont.encode('gbk')
                try:
                    filename=self.dicPath+month+os.path.sep+title+'.txt'
                    f=open(filename,'w')
                    f.write(cont)
                except Exception as e:
                    print str(e)+self.name
                    continue
                global totalNum
                global mutex
                if mutex.acquire(1):
                    totalNum+=1
                    mutex.release()
                #print self.name+"处理了一个页面"
                if totalNum%100==0:
                    global t3,t4
                    t4=clock()
                    print "已处理了"+str(totalNum)+"条数据,用时"+str(t4-t3)+'s'
            else:
                end=clock()
                if (end-start)>self.TIMEOUT:
                    break


def main():
    global t1,t2,t3,t4
    t1=clock()
    pape=urllib2.urlopen(starturl)
    mainsoup=bs4.BeautifulSoup(''.join(pape),'lxml')
    alist=mainsoup.find_all('a',class_='fnamecolor',limit=10)

    for item in alist:
        monthurl=item['href']+'&page=1'
        shareMonthQueue.put(starturl+monthurl)
    t2=clock()
    print "主页面爬取完成，用时"+str(t2-t1)+'s'

    for i in xrange(_WORK_REPORT_THREAD_NUM_):
        if i<_WORK_MONTH_THREAD_NUM:
            ms=monthSplider('ms'+str(i))
            tlist.append(ms)
        rs=reportSpider('rs'+str(i))
        tlist.append(rs)
    t3=clock()
    print "爬虫准备就绪,用时"+str(t3-t2)+'s'
    for t in tlist:
        t.start()
    for t in tlist:
        t.join()




if __name__=="__main__":
    main()