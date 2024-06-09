import requests,json
from json import loads,dumps
from clipboard import copy,paste
import time
import random

VERSION='v2.0.2'

# v2.0.1: 添加版本号
# v2.0.2: 添加pause()函数
# v2.0.2: 添加bvid
# v2.0.2: 调整变量排序，使得"数值"开头的放到最后

# TODO: 打开本文件所在文件夹，选中对应文件夹，知识在https://blog.csdn.net/u011430225/article/details/59518278
# TODO: 指定文件夹

# thanks to https://blog.csdn.net/weixin_46428702/article/details/118905812

DATA='https://api.bilibili.com/x/web-interface/view?bvid={}'
GRAPH='https://api.bilibili.com/x/stein/edgeinfo_v2?bvid={}&edge_id=%s&graph_version={}&platform=pc&portal=0&screen=0&choices='
BUVID='' #buvid是cookies里的，不是必要的
CID='https://api.bilibili.com/x/player/pagelist?bvid={}&jsonp=jsonp'
VERSION='https://api.bilibili.com/x/player/v2?cid={}&bvid={}'

ua_list = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.62',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36 SE 2.X MetaSr 1.0'
]

def pause():
    input("pause: ")

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

def str2val(s):
    v=float(s)
    assert v==round(v)
    return round(v)

def find(bvid):
    ans=dict()
    titles=dict()
    others=dict()
    id2var=dict()

    others['version']=VERSION
    others['bvid']=bvid

    global vidata
    vidata=safe_get_text(DATA.format(bvid))    
    vidata=loads(vidata)['data']
    
    others['title']=vidata['title']
    cidata=loads(safe_get_text(CID.format(bvid)))['data']
    cid=cidata[0]['cid']
    verdata=loads(safe_get_text(VERSION.format(cid,bvid)))['data']
    others['aid']=verdata['aid']
    
    if 'interaction' not in verdata.keys():
        raise ValueError('{} is not an interactive video'.format(bvid))
    version=verdata['interaction']['graph_version']
    
    def find(api,cid,pos=''):
        if pos in ans.keys():
            return pos
        
        data=loads(safe_get_text(api%pos))['data']

        #print(dumps(data,ensure_ascii=False))

        edge_id=str(data['edge_id'])
        title=data['title']
        edge=data['edges']
        
        if pos=='': 
            pos=edge_id
            
            if 'hidden_vars' not in data.keys():
                others['advanced']=False
                print('不是高级功能')
            else:
                others['advanced']=True
                print('是高级功能')
                
                hid=data['hidden_vars']
                var=list()

                for i in hid:
                    var.append({
                        'name':i['name'],
                        'type':['','normal','random'][i['type']],
                        'id':i['id_v2']
                    })
                    if i['type']==1:
                        var[-1]['value']=i['value']
                        var[-1]['is_show']=bool(i['is_show'])
                def key(name):
                    try:# 默认的"数值"+数字
                        assert name[:2]=='数值'
                        return ('B: automatic',int(name[2:]))
                    except:
                        return ('A: changed',name)
                var.sort(key=lambda a:(a['type'][-3],key(a['name'])))

                others['vars']=dict()
                for i in range(len(var)):
                    cur='R'if i==0 else chr(64+i) if i<ord('R')-ord('A') else chr(65+i)
                    v=var[i]
                    ids=v['id']
                    del v['id']
                    id2var[ids]=cur
                    others['vars'][cur]=v
                    print('变量{}名为"{}"'.format(cur,v['name']))
                
            others['root']=pos

        if title in titles.keys():
            return titles[title]
        pos=str(pos)
        titles[title]=pos
        
        if data['is_leaf']:
            print('"{}"是叶子节点'.format(title))
            ans[pos]={'title':title,'cid':cid,'type':'leaf'}
        else:
            ans[pos]={'title':title,'cid':cid,'type':'choice'}
            question=edge['questions'][0]
            choice=question['choices']
            hasdft=question['duration']>0
            
            for i in choice:
                newpos=str(i['id'])
                newcid=i['cid']
                option=i['option']
                option,text=option[0],option[2:]

                if text=='':
                    print('"{}"跳转'.format(title))
                    a=find(api,newcid,newpos)
                    ans[pos]={'title':title,'cid':cid,'type':'direct','pos':a}
                    break
                
                ans[pos][option]={'text':text,'pos':newpos}

                if hasdft and i.get('is_default',0):
                    ans[pos]['default']=option

                if newpos not in ans.keys():
                    print('"{}"选{} {}'.format(title,option,text))
                    a=find(api,newcid,newpos)
                    ans[pos][option]['pos']=a
                    
                    #ans[pos][option]['full_data']=i

                    if others['advanced']:
                        cond=i['condition']
                        varcond=list()

                        if cond:
                            conds=''
                            for k in cond.split('&&'):
                                k=k.strip()
                                for j in id2var.keys():
                                    if k.startswith(j):
                                        break
                                cur=id2var[j]
                                k=k[len(j):]

                                op={'<=':'le','>=':'ge','==':'eq','<':'lt','>':'gt'}
                                for j in op:
                                    if k.startswith(j):
                                        break
                                k=str2val(k[len(j):])

                                varcond.append({'var':cur,'op':op[j],'num':k})

                                if conds:conds+='&'
                                conds+=cur+j+str(k)
                            ans[pos][option]['condition']=varcond
                            print('条件为{}'.format(conds))
                        
                        action=i['native_action']
                        varact=list()
                        if action:
                            acts=''
                            for i in action.split(';'):
                                for j in id2var.keys():
                                    if i.startswith(j):
                                        break
                                cur=id2var[j]
                                i=i[len(j)+1:]

                                if acts:acts+=';'

                                if not i.startswith(j):
                                    i=str2val(i)
                                    varact.append({'var':cur,'op':'set','num':i})
                                    acts+=cur+'='+str(i)
                                else:
                                    i=round(float(i[len(j):]))
                                    if round(float(i)):
                                        varact.append({'var':cur,'op':'add','num':i})
                                        acts+=cur+('+'if i>0 else '-')+'='+str(abs(i))
                            ans[pos][option]['change']=varact
                            print('改变为{}'.format(acts))
        
        #ans[pos]['full_data']=data

        return pos

    find(GRAPH.format(bvid,version),cid)

    #print(id2var)
    
    return ans,others

if __name__=='__main__':
    bvid=input('下载的bv号：')
    
    ans,others=find(bvid)
    aid=others['aid']
    print('av{}'.format(aid))

    import os
    os.system('md {}'.format(aid))
    path='./{}/'.format(aid)
    
    with open(path+'file.json','w',encoding='UTF-8') as f:f.write(dumps(ans,ensure_ascii=False,indent=4,sort_keys=True))
    with open(path+'config.json','w',encoding='utf8') as f:f.write(dumps(others,ensure_ascii=False,indent=4,sort_keys=True))
    
    #with open(path+'file_lined.json','w',encoding='UTF-8') as f:f.write(dumps(ans,ensure_ascii=False))
    #with open(path+'config_lined.json','w',encoding='utf8') as f:f.write(dumps(others,ensure_ascii=False))

    #os.system('pause')
