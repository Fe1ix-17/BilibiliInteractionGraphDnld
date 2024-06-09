import requests,json,urllib,random
from urllib.request import urlretrieve,build_opener,install_opener
from urllib.error import HTTPError
from json import loads,dumps
    
ua_list = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.62',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36 SE 2.X MetaSr 1.0'
]

def download(link,path):
    #urlretrieve(link,path)
    opener=build_opener()
    opener.addheaders=[('User-Agent',random.choice(ua_list))]
    install_opener(opener)
    urlretrieve(link,path)

def safe_get_text(url):
    MAX_TRY=3
    for i in range(MAX_TRY):
        if i:time.sleep(random.random()*0.8*i+1)
        response=requests.get(url,headers={'User-Agent':random.choice(ua_list)})
        if response.status_code //100==4:
            print(response.status_code,response.reason,response.text)
            continue
        else:return response.text
    print('url= {}'.format(url))
    copy(url)
    text=input('Response: ')
    if not text:text=paste()
    return text

VIDEO='https://api.bilibili.com/x/player/playurl?avid=%s&cid={}&qn=1&type=&otype=json&platform=html5&high_quality=1'

with open('config.json',encoding='UTF8') as f:others=loads(f.read())
with open('file.json',encoding='UTF8') as f:ans=loads(f.read())

aid=others['aid']
vid=VIDEO%aid

s=set()
links=dict()

for pos in ans.keys():
    i=ans[pos]
    title=i['title']
    cid=i['cid']

    if cid in s:
        print('重复的剧情：{}'.format(title))
        continue
    s.add(cid)

    data=loads(safe_get_text(vid.format(cid)))
    data=data['data']
    link=data['durl'][0]['url']
    name='./video/{}.mp4'.format(pos)
    
    print('开始下载：{}'.format(title))

    while 1:
        try:
            download(link,name)
        except HTTPError as e:
            print(e)
        else:
            break

    links[pos]=link

with open('links.json','w',encoding='utf8') as f:
    f.write(dumps(links))
