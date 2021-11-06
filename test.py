#-*- coding = utf-8 -*-
#@TIme: 2021/6/1 2:47
#@Author: Celine
#@File: spider.py
#@Software: PyCharm
# 豆瓣这河里吗组爬虫（用户信息，帖子内容）
import random
import re
from bs4 import BeautifulSoup #网页解析，获取数据
import urllib.request, urllib.error #定制url，获取网页数据
import xlwt #进行excel操作
import sqlite3 #进行sqlite数据库操作

findTitle = re.compile(r'title="(.*?)"',re.S)# .S匹配包括换行符
findLink = re.compile(r'href="(.*?)"') # 全局变量，创建正则表达式对象 (.*?)表示任意多字符的非贪婪模式匹配,链接都放在一组()
findRCount = re.compile(r'<.*class="r-count".*>(.*?)</td>')
findRTime = re.compile(r'<.*class="time".*">(.*?)</td>') #??这里匹配很迷惑

findInfo = re.compile(r'<p.*>(.*?)</p>', re.S)  # 找到帖子详情信息，匹配换行符
findImgLink = re.compile(r'src="(.*?)"')  # 找到帖子附带的照片链接

#爬取网页
def getData(baseurl, pagecount):
    datalist = []
    for i in range(0, pagecount): #test时只爬一页 pagecount
        url = baseurl + str(i*25) + "&type=elite"# 网页地址递增，str()字符串转换后才能拼接, 每页帖子只显示25条
        html = askURL(url) #1) 获取网页源码
        # print(html) #test
        soup = BeautifulSoup(html, "html.parser") #2) 解析网页源码
        # 每次获取到网页信息后需逐一解析数据
        for item in soup.find_all("tr", class_=""): #找到每个帖子
            # print(item) #测试：查看全部信息
            data = []
            item = str(item)
            # print(item) # 测试：item

            title = re.findall(findTitle, item)[0] #帖子title
            # print(title)# 测试
            data.append(title)

            link = re.findall(findLink, item) #帖子详情链接
            # print(link) #测试

            #进入帖子中爬取详细内容
            info, imglink = getInfo(link[0])
            data.append(info)
            data.append(imglink)
            if(len(link) == 2): #发帖人有两种：已注销的没有主页链接
                data.append(link[0]) # 详情链接
                # alink = re.findall(findLink, item) #测试：查看link
                # print
                data.append(link[1]) # 发帖人链接
            else:
                data.append(link[0])
                data.append(' ') # 占位

            rcount = re.findall(findRCount, item)[0]
            # print(rcount) # 测试
            if rcount == '':
                data.append(0)
            else:
                data.append(int(rcount))

            rtime = re.findall(findRTime, item)[0]
            # print(rtime) # 测试
            data.append(rtime)

            datalist.append(data)
    # print(datalist) #测试
    return datalist

#得到制定一个url网页内容
def askURL(url):
    #headers伪装成浏览器访问豆瓣服务器， 用户代理：本质是告诉浏览器我们可以接受什么水平的文件内容
    # headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36 Edg/89.0.774.77"}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"}

    my_headers = [
        "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
        "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)",
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
        'Opera/9.25 (Windows NT 5.1; U; en)',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
        'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
        'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
        'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
        "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
        "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 "
    ]


    # req = urllib.request.Request(url=url, headers=headers)
    req = urllib.request.Request(url=url)
    req.add_header('User-Agent', random.choice(my_headers))
    html = ""
    try:
        response = urllib.request.urlopen(req) #返回的response对象包含整个网页信息
        html = response.read().decode("utf-8") #读取信息
        #print(html)
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"): #获取错误原因
            print(e.reason)
    return html

#进入每个帖子里爬取详细内容和照片链接
def getInfo(url):

    tempInfo = []
    info = ''
    tempImgLink = []
    tempImgLink = ''

    #正则获取帖子详情和照片链接

    html = askURL(url)
    soup = BeautifulSoup(html, 'html.parser')
    # topic = soup.find_all('div', class_='rich-content.topic-richtext')
    topic = soup.find_all('div', class_='topic-richtext')
    topic = str(topic)
    # print(topic) # test

    #详细内容
    tempInfo = re.findall(findInfo, topic)
    # print(tempInfo) # 测试
    print(tempInfo)
    print("------------")
    info = " , ".join(str(v) for v in tempInfo) # 帖子里详细内容会有换行，用逗号隔开

    #照片链接
    tempImgLink = re.findall(findImgLink, topic)
    imglink = " , ".join(str(v) for v in tempImgLink) # 多张照片 同理

    return info, imglink

#保存数据 excel
def saveDate(datalist,savePath, pagecount):
    workbook = xlwt.Workbook(encoding='utf-8', style_compression=0)
    worksheet = workbook.add_sheet("doubanGnz48Group", cell_overwrite_ok=True) # 单元格可以覆盖
    col = ("序号", "帖子名","详细内容","图片链接","帖子详情链接","发帖人主页链接","回帖数","最后回复时间") # 设定列标题
    for i in range(0,len(col)):
        worksheet.write(0, i, col[i])
    for i in range(0, 25 * pagecount):
        print("%d"%(i+1)) # 测试
        data = datalist[i] # 一个帖子的所有信息
        worksheet.write(i+1, 0, i+1) # 写入序号
        for j in range(0, len(data)):
                worksheet.write(i+1, j+1, data[j])
    workbook.save(savePath)

#保存数据 db
def saveDate2DB(datalist, savepath):
    """
    将解析后的数据保存在数据库文件中
    :param datalist: 网页解析后的数据
    :param dbpath: 数据库文件保存路径
    :return:
    """

    init_db(dbpath)  # 初始化数据库
    conn = sqlite3.connect(dbpath)  # 连接数据库
    cur = conn.cursor()  # 获取游标

    # 将数据逐一保存到数据库中
    for data in datalist:
        for index in range(len(data)):
            if index != 5:  # index为5的数据类型是int
                data[index] = '"' + data[index] + '"'  # 每项的字符串需要加上双引号或单引号
        # 插入字符串，以逗号隔开
        sql = '''
                insert into renting(
                title, introduction, img_link, title_link, person_link, re_count, re_time)
                values(%s)''' % ",".join(str(v) for v in data)
        # print(sql)
        cur.execute(sql)  # 执行数据库操作
        conn.commit()  # 提交
    cur.close()  # 关闭游标
    conn.close()  # 关闭连接

def init_db(savepath):
    #创建数据表
    # create table renting
    # 若不加if not exists，则每次运行程序需要先删除database；否则不用先删除，但无法更新sql里的格式
    sql = '''
            create table if not exists renting
            (
            id integer primary key autoincrement,
            title text,
            introduction text,
            img_link text,
            title_link text,
            person_link text,
            re_count numeric,
            re_time text
            )
        '''  # 创建数据表
    conn = sqlite3.connect(dbpath)  # 创建或连接数据库
    cursor = conn.cursor()  # 获取游标
    cursor.execute(sql)  # 执行数据库操作
    conn.commit()  # 提交
    cursor.close()  # 关闭游标
    conn.close()  # 关闭

def main():
    # 1.爬取网页
    # 2.逐一解析数据
    # 3.保存数据(excel/sqlite)
    baseurl = "https://www.douban.com/group/GNZ48/discussion?start="
    # baseurl = "https://www.douban.com/group/GNZ48/discussion?start=50&type=elite"
    pagecount = 1 # 爬取页数（每页25条帖子）
    datalist = getData(baseurl, pagecount)

    # savePath = "doubanGNZ48Group.xls"
    # saveDate(datalist, savePath, pagecount)

    # savepath = "doubanGNZ48Group.db"
    # saveDate2DB(datalist, savepath)

if __name__ == '__main__':
    # main()
    # init_db("test.db")
    main()
    # datalist = getData("https://www.douban.com/group/GNZ48/discussion?start=", 1)
    print("done!")