# -*- coding: utf-8 -*-
'''
第二个版本，字词自己输入想要下载的视频链接，然后自动下载
'''
import os,glob,time
import config as C
def get_informs():

    if glob.glob('./InputList')==[]:
        os.mkdir('./InputList')
    if glob.glob('./InputList/result')==[]:
        os.mkdir('./InputList/result')
    ret1=[]
    ret2=[]
    ret3=[]
    
    with open("./InputList/will_download","a+",encoding="utf-8")as f: f.close()
    with open("./InputList/have_download","a+",encoding="utf-8")as h: h.close()
    with open("./InputList/cant_download","a+",encoding="utf-8")as i: i.close()

    for line in open("./InputList/will_download","r",encoding="utf-8"):
        if line.find('https://www.youtube.com/watch?v=')!=-1:#标准油管视频格式
            s=line.replace(' ','').strip('\n')
            ret2.append(s)
        

    for line in open("./InputList/have_download","r",encoding="utf-8"):
        if line.find('https://www.youtube.com/watch?v=')!=-1:
            s=line.replace(' ','').strip('\n')
            ret3.append(s)

    for s in ret3:
        if s in ret2:
            ret2.remove(s)

    print(ret2)
    return ret2

def get_video(ret2):
    ret=['1080p','720p','480p','360p','360/240p']
    if ret2:#非空
        for s in ret2:
            os.chdir('./InputList/result')
            print("正在尝试下载视频：%s"%s)
            i=0
            state=1
            n=137
            GO=True
            while state==1 and GO:
                print('尝试下载%s视频'%ret[i])
                cmd='youtube-dl -f %s+140 %s'%(n,s)
                state=os.system(cmd)
                print('无%s视频'%ret[i]))
                del(cmd)
                n -=1
                i +=1
                if i==5:
                    GO=False
                    print('视频%s可能为直播或者有版权限制，无法下载'%s)
                    os.chdir('../')
                    with open("cant_download","a+",encoding="utf-8")as i:
                        i.write('%s\n'%s)
                    os.chdir('../')
                    time.sleep(1)
            if GO:
                print('下载成功,视频+1')
                os.chdir('../')
                with open("have_download","a+",encoding="utf-8")as h:
                    h.write('%s\n'%s)
                os.chdir('../')
                time.sleep(1) 

if __name__=='__main__':
    #iname=C.input_config['input_name']
    ret2=get_informs()
    get_video(ret2)

















































































