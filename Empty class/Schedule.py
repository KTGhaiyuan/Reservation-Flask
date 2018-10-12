import requests
from  bs4  import BeautifulSoup
import re
import pymongo

# headers={
#         'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
#         'Cookie':'UM_distinctid=16648846caf80f-022df8bb40b3da-8383268-144000-16648846cb0153; JSESSIONID=adehQz6UcMFXO6ZhYyIzw',
#         'Host':'urp.hebau.edu.cn:9001'
# }


def get_scheule(url):
    # res=requests.get(url)
    soup=BeautifulSoup(url,'lxml')
    #print(soup)
    courss=soup.find_all('tr',class_='odd')
    #print(courss[0])
    info=[]
    for cours   in courss:
        room={}

        if len(cours.find_all('td')) < 17:
            room['classroom'] = cours.find_all('td')[6].string.strip()
            room['time'] = cours.find_all('td')[2].string.strip()
            date_day = cours.find_all('td')[0].string.strip()
        else:
            room['classroom'] = cours.find_all('td')[17].string.strip()
            room['time'] = cours.find_all('td')[13].string.strip()
            date_day = cours.find_all('td')[11].string.strip()


        date=re.findall('(\d+){0,2}-(\d+){0,2}',date_day)
        if len(date)==0:
            date=date_day.split('周')[0]
            date=date.split(',')
        #print(date)
        date_hour = []
        if len(date)==1:
            if type(date[0])==str:
                for k  in date:
                    date_hour.append(k)
            elif type(date[0]==tuple):
                for i in range(int(date[0][0]), int(date[0][1])):
                    date_hour.append(i)
        elif len(date)==2:
            if type(date[0])==str:
                for k  in date:
                    date_hour.append(k)
            else:
                for i  in  range(int(date[0][0]),int(date[0][1])):
                    date_hour.append(i)
                for i  in  range(int(date[1][0]),int(date[1][1])):
                    date_hour.append(i)
        elif  len(date)==3 and isinstance(date[0],tuple):
            for i in range(int(date[0][0]), int(date[0][1])):
                date_hour.append(i)
            for i in range(int(date[1][0]), int(date[1][1])):
                date_hour.append(i)
            for i in range(int(date[2][0]), int(date[2][1])):
                date_hour.append(i)
        else:
            for i  in  date:
                date_hour.append(i)
        #print(date_hour)
        room['date']=date_hour
        print(room)
        rooms.insert_one(room)


if __name__=='__main__':
    # url='http://urp.hebau.edu.cn:9001/xkAction.do?actionType=6'
    client = pymongo.MongoClient('localhost', 27017)
    schedules = client['schedule']
    rooms = schedules['course']
    for i in range(1, 20):
        with  open('class/学生选课结果{}.html'.format(i), 'r')  as  f:
            f = f.read()
            get_scheule(f)




