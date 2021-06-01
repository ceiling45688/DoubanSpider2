#-*- coding = utf-8 -*- 
#@TIme: 2021/6/1 2:47
#@Author: Celine
#@File: spider.py
#@Software: PyCharm
# 豆瓣这河里吗组爬虫（用户信息，帖子内容）
import re
from bs4 import BeautifulSoup #网页解析，获取数据
import urllib.request, urllib.error #定制url，获取网页数据
import xlwt #进行excel操作
import sqlite3 #进行sqlite数据库操作

findTitle = re.compile(r'title="(.*?)"',re.S)# .S匹配包括换行符
findLink = re.compile(r'href="(.*?)"') # 全局变量，创建正则表达式对象 (.*?)表示任意多字符的非贪婪模式匹配,链接都放在一组()
findRCount = re.compile(r'<.*class="r-count".*>(.*?)</td>')
findRTime = re.compile(r'<.*class="time".*">(.*?)</td>') #??这里匹配很迷惑

findInfo = re.compile(r'<p>(.*?)</p>', re.S)  # 找到帖子详情信息，匹配换行符
findImgLink = re.compile(r'src="(.*?)"')  # 找到帖子附带的照片链接

#爬取网页
def getData(baseurl, pagecount):
    datalist = []
    for i in range(0, pagecount): #test时只爬一页 pagecount
        url = baseurl + str(i*25) # 网页地址递增，str()字符串转换后才能拼接, 每页帖子只显示25条
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
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36 Edg/89.0.774.77"}
    req = urllib.request.Request(url=url, headers=headers)
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
    topic = soup.find_all('div', class_='rich-content topic-richtext')
    topic = str(topic)

    #详细内容
    tempInfo = re.findall(findInfo, topic)
    print(tempInfo) # 测试
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
    init_db(savepath)
    conn = sqlite3.connect(savepath)
    c = conn.cursor()

    for data in datalist: #二维数组
        for index in range(len(data)): # 获取每一部电影的八个信息
            data[index] = '"' + data[index] + '"' # 字符串拼接：前后加双引号将列表内容转换为字符串插入数据表

        sql= '''
            insert into MoviesTop250(
            LINK, IMG, Ctitle, Otitle, RATING, JUDGE, QUOTE, BD
            )values(%s)''' % ",".join(data) #格式占位符，join逗号拼接
        # print(sql)
        c.execute(sql)
        conn.commit()
    conn.close()

def init_db(savepath):
    conn = sqlite3.connect(savepath) #打开数据库
    c = conn.cursor() #获取游标
    #创建数据表
    sql = '''
        create table MoviesTop250(
            id integer primary key autoincrement, 
            LINK MESSAGE_TEXT,
            IMG MESSAGE_TEXT,
            Ctitle message_text,
            Otitle message_text,
            RATING real,
            JUDGE real,
            QUOTE message_text,
            BD message_text
        );
    '''
    c.execute(sql) # 执行sql语句
    conn.commit() # 提交数据库操作
    conn.close() # 关闭连接

def main():
    # 1.爬取网页
    # 2.逐一解析数据
    # 3.保存数据(excel/sqlite)
    baseurl = "https://www.douban.com/group/GNZ48/discussion?start="
    pagecount = 1 # 爬取页数（每页25条帖子）
    datalist = getData(baseurl, pagecount)

    savePath = "doubanGNZ48Group.xls"
    saveDate(datalist, savePath, pagecount)

    # savepath = "doubanGNZ48Group.db"
    # saveDate2DB(datalist, savepath)

if __name__ == '__main__':
    # main()
    # init_db("movietest.db")
    main()
    # datalist = getData("https://www.douban.com/group/GNZ48/discussion?start=", 1)
    print("done!")