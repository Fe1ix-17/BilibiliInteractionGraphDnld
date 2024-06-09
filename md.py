import json
from json import loads

with open('config.json',encoding='UTF8') as f:others=loads(f.read())
with open('file.json',encoding='UTF8') as f:ans=loads(f.read())

aid=others['aid']

def unicodefy(txt):
    return '"'+txt.replace('#','#35;').replace('"','#34;')+'"'

def mermaid(ans):
    rtn='```mermaid\ngraph TD\n'
    for pos in ans.keys():
        data=ans[pos]
        typ=data['type']
        title=unicodefy(data['title'])
        if typ=='leaf':
            rtn+='{}[[{}]]\n'.format(pos,title)
        if typ=='direct':
            rtn+='{}({})==>{}\n'.format(pos,title,data['pos'])
        if typ=='choice':
            rtn+='{}({})\n'.format(pos,title)
            dft=data.get('default',None)
            for op in data.keys():
                if op in ['A','B','C','D']:
                    opd=data[op]
                    txt='{} {}'.format(op,opd['text'])

                    if opd.get('condition',[]):
                        cond=opd.get('condition',[])
                        op={'ge':'>=','le':'<=','eq':'=','lt':'<','gt':'>'}
                        s=''

                        for i in cond:
                            if s:s+='且'
                            s+=i['var']+op[i['op']]+str(i['num'])
                        txt='('+s+')'+txt

                    if opd.get('change',[]):
                        chg=opd.get('change',[])
                        op={'add':'+','set':'='}
                        s=''

                        for i in chg:
                            if s:s+='并'
                            if i['op']=='set':s+=i['var']+'='+str(i['num'])
                            elif i['num']<0:s+=i['var']+str(i['num'])
                            else:s+=i['var']+'+'+str(i['num'])
                        txt+='('+s+')'

                    txt=unicodefy(txt)
                    
                    if op==dft:
                        rtn+='{}=={}==>{}\n'.format(pos,txt,opd['pos'])
                    else:
                        rtn+='{}--{}-->{}\n'.format(pos,txt,opd['pos'])
        rtn+='\n'
    return rtn+'```'

with open('{}.md'.format(aid),'w',encoding='utf-8') as f:
    f.write(mermaid(ans))
