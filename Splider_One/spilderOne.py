# -*- coding: utf-8 -*-
# 此程序用于爬取人民日报下的数据资源。主页面需要提取包括1946年到2003年之间所有月份
# 次级页面是各个月份的所有报道
# 末级页面是报道内容
'''
Created on 2016年10月27日
@author: joe
'''

from time import clock
import urllib2, bs4, os, re


# 关于bs4解析url的方法
# 可以参看：http://www.crummy.com/software/BeautifulSoup/bs4/doc/index.zh.html
starturl = "http://www.xinhuanet.com/english/home.htm"
testMonthURL = "http://news.xinhuanet.com/english/2016-10/27/c_135785263.htm"

def getSoup(url):
    pape = urllib2.urlopen(url)
    soup = bs4.BeautifulSoup(''.join(pape), 'lxml')
    return soup

# 从主页面中读取每一年中每个月的URL组成一个URLLIST返回，
def getDataFromMainURL():
    urllist = []
    mainSoup = getSoup(starturl)
    alist = mainSoup.find_all('a', 'fnamecolor')
    for item in alist:
        urllist.append(starturl + item['href'])

    return urllist


# 处理每一个月的首页面，包括得到总的子页面数和当前文档URL
# 并把所有子页面返回的URLLIST组成总的URLLIST
# 根据得到URL为每一个月创建的一个文件夹。
def getDataFromMonth(monthURL):
    filepath = os.getcwd() + os.path.sep + "data" + os.path.sep
    urllist = []
    soup = getSoup(monthURL)
    title = soup.find('a', 'fl')  # 找到年月的标签位置
    month = title.contents[0]
    curpath = os.getcwd()
    # print month.encode('utf8')
    datapath = curpath + os.path.sep + "data" + os.path.sep + month.encode('utf8')
    if os.path.exists(datapath) == False:
        os.mkdir(datapath)  # 创建好当月文件夹

    pages = soup.find('div', 'pages').contents[-1]
    totalpage = pages.split(' ')[3].split('/')[1]  # 得到总页面数

    for num in range(int(totalpage)):
        curURL = monthURL + "&page=" + str(num)
        urllist += getDocementList(curURL)
    print "已载入当前月份的所有urllist"
    return datapath, urllist

# 得到当前页面的文档URL组成URLLIST返回
def getDocementList(curURL):
    urllist = []
    curSoup = getSoup(curURL)
    res = curSoup.find_all(id=re.compile("a_ajax_"))
    for item in res:
        urllist.append(starturl + item['href'])

    print "已载入当前页面的所有文档url"
    return urllist

# 得到docement中的内容并保存到文件中
def getDocement(docURL):
    docSoup = getSoup(docURL)
    title = docSoup.find('h1', 'fl').get_text()
    title = title.strip().split(' ')[0]
    cont_div = docSoup.find('div', 'tpc_content')
    cont = cont_div.get_text().strip()
    pattern = re.compile(r'<br/?>')
    # for item in cont_div:
        # print type(item)
        # if not re.match(str(item)):
            # cont+=str(item)
        # if str(item)!='<br/>' or str(item)!='<br>':
            # cont+=str(item)

    return title, cont


# 月份页面下的控制程序，输入为月份的URL。并把爬取的内容分别存入到文件中
def monthMain(monthURL):
    start = clock()
    datapath, urllist = getDataFromMonth(monthURL)
    print(datapath)
    print(urllist)
    for url in urllist:
        try:
            doc_title, doc_cont = getDocement(url)
            # print doc_title
            doc_title = doc_title.encode('utf8')
            filename = datapath + os.path.sep + doc_title + ".txt"
            print(filename)
            f = open(filename, 'w')
        except Exception as e:
            print e
            continue
        doc_cont = doc_cont.encode('utf8')
        f.write(doc_cont)
        f.close()
    end = clock()
    print "finish input data to " + datapath
    print "running time is " + str(end - start) + "s"


def main():
    starttime = clock()
    urllist = getDataFromMainURL()
    print(urllist)
    for url in urllist:
        try:
            monthMain(url)
        except Exception as e:
            print e
            continue
    endtime = clock()
    print "total running time is " + str(endtime - starttime) + "s"
if __name__ == "__main__":
    main()
  

