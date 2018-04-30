#!usr/bin/env/python3
#-*-coding：utf-8 -*-

r'''

华为软件精英挑战赛期间，闲来无聊，写了个爬虫，把榜单上的信息全部爬下来，做了去重处理，每隔10秒一次，如果结果与上次一样，则不写入数据库，否则就写入。

需要用到 BeautiSoup 4.0（适配python3.5），其他的都是python自带的库。

请勿用做其他非法用途，由此产生的一切后果与本人无关。

比赛期间一直在我的树莓派上跑的

'''


from bs4 import BeautifulSoup
import re
import urllib.request
from urllib import parse

import sqlite3
import time

area = ['成渝','杭厦','京津东北','江山','上合','武长','西北','粤港澳']

url = "http://codecraft.devcloud.huaweicloud.com/Home/TeamScoreDisplays"
headers ={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
sql = r'''INSERT INTO HUAWEI 
                    (team_name,team_captain_nickname,team_school_name,team_slogan,team_score,record_date,team_area)
                    VALUES
                    (:team_name,:team_captain_nickname,:team_school_name,:team_slogan,:team_score,:record_date,:team_area)'''


conn = sqlite3.connect(r'/home/pi/Desktop/huawei/hauwei0421.db')
HWRTdata = conn.cursor()

#此处应该有try被我删了
HWRTdata.execute('''CREATE TABLE  IF NOT EXISTS HUAWEI
        (
        ID INTEGER PRIMARY KEY ,
        team_name              ,
        team_captain_nickname  ,
        team_school_name       ,      
        team_slogan            ,
        team_score      REAL   ,
        record_date            ,
        team_area            
        );'''
        )
conn.commit()

temp_init = []
for subkeynum in range(1,9): 
    record_date = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    temp1 = []  
    textmod={'stageKey':'复赛','stageType':1,'subKey':subkeynum}
    textmod = parse.urlencode(textmod).encode(encoding = 'utf-8')
    request = urllib.request.Request(url=url,data=textmod,headers=headers)
    response = urllib.request.urlopen(request)
    data = response.read().decode('utf-8')
    soup = BeautifulSoup(data, "html.parser").find_all('tr') 
    for i in soup:
        c = i.find_all('td')
        temp1.append([c[i].string for i in range(1,6)])
        HWRTdata.execute(sql,{'team_name':c[1].string,'team_captain_nickname':c[2].string,'team_school_name':c[3].string,'team_slogan':c[4].string,'team_score':c[5].string,'record_date':record_date,'team_area':area[subkeynum-1]})
    temp_init.append(temp1)    
conn.commit()
time.sleep(10)
# flag1 = 0
while True:
    a = 0
    record_date = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    temp_run = []
    try:
        for subkeynum in range(1,9): 
            temp1 = []  
            textmod={'stageKey':'复赛','stageType':1,'subKey':subkeynum}
            textmod = parse.urlencode(textmod).encode(encoding = 'utf-8')
            request = urllib.request.Request(url=url,data=textmod,headers=headers)
            response = urllib.request.urlopen(request)
            data = response.read().decode('utf-8')
            soup = BeautifulSoup(data, "html.parser").find_all('tr') 
            for i in soup:
                c = i.find_all('td')
                temp1.append([c[i].string for i in range(1,6)])
            temp_run.append(temp1)
        subkeynum = 1
        for i in temp_run:    
            for j in i:
                flag = False
                for x in temp_init:
                    if j in x:
                        flag = True
                if flag == False:   
                    HWRTdata.execute(sql,{'team_name':j[0],'team_captain_nickname':j[1],'team_school_name':j[2],'team_slogan':j[3],'team_score':j[4],'record_date':record_date,'team_area':area[subkeynum-1]})
            subkeynum += 1
        temp_init = temp_run[:]  
        conn.commit()
        time.sleep(10)
        print(record_date)
    except Exception as e:
        a+=1
        with open('D:\log.txt','a') as f:
            f.write(record_date)
            f.write(':'+str(e)+'\n')
        if a > 30:
            break
conn.close()
