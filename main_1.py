# -*- coding: utf-8 -*-
import sys,os,glob,json,time,urllib.request,zipfile,shutil
from selenium import webdriver
import ffmpeg_split as fs
import config as C

#获取视频基本信息
def get_informs(driver,iname):
    #创建基本文件夹
    if glob.glob("./result")==[]:
        os.mkdir("./result")     
    if glob.glob("result\\%s"%iname)==[]:
        os.mkdir("result\\%s"%iname) 
        
    #网页下滚确保有足够的视频链接
    if C.input_config["step"]!=0:
        i=0         
        driver.maximize_window()
        time.sleep(1)
        num_p=True       
        while num_p:#循环网页下滚
            js="var q=document.documentElement.scrollTop=100000"#模拟下滑
            driver.execute_script(js)  
            i=i+1
            if i==C.input_config["step"]:
                num_p=False
            time.sleep(1)
            
    #基本量设置
    ret_1=[]
    ret_2=[]
    ret_3=[]
    dict1={}
    dict2={}
    path_0=driver.find_elements_by_xpath("//a[contains(@id,'thumbnail')]")#定位路径
    txt_0=driver.find_elements_by_xpath("//yt-formatted-string[contains(@class,'style-scope ytd-video-renderer')]")#定位文字信息
    
    #获取名字
    m=1
    for st in txt_0:
        if m%2==1:
            s=str(st.get_attribute('aria-label')).replace(' ','')
            j=k=0
            for i in s:#获取不变名
                if (65<=ord(i) and ord(i)<=90) or (97<=ord(i) and ord(i)<=122):           
                    j=k
                k=k+1
            #print('%s'%s[0:j+1])
            ret_1.append(s[0:j+1])#获取（不变）名字
        m=m+1
        
    #获取网址
    for st in path_0:
        s=st.get_attribute('href')
        if len(str(s))<=45:#广告爬
            ret_2.append(s)#获取网址
    
    #确保文件存在
    with open("./result/%s/下载好的%s"%(iname,iname),"a+",encoding="utf-8")as a: a.close()
    with open("./result/%s/分割好的%s"%(iname,iname),"a+",encoding="utf-8")as b: b.close() 
    with open("./result/%s/不能下的%s"%(iname,iname),"a+",encoding="utf-8")as c: c.close()
    with open("./result/%s/%s视频信息"%(iname,iname),"a+",encoding="utf-8")as f: f.close()
    
    #生成字典/列表并且保存
    for j,k in zip(ret_1,ret_2):#成对
        if j.find(C.input_config['ban_index_1'])==-1 and j.find(C.input_config['ban_index_2'])==-1:#剔除不需要的视频
            dict1[k]=j#{k:j}，即{网址：名字}
    for line in open("./result/%s/下载好的%s"%(iname,iname),"r",encoding="utf-8"):
        s=line.strip('\n')
        if s in dict1:
            del(dict1[s])#剔除重复
            
    #记录分割视频列表，并依此分割视频
    for line in open("./result/%s/分割好的%s"%(iname,iname),"r",encoding="utf-8"):
        s=line.strip('\n')
        ret_3.append(s)#分割的视频的文件夹列表，内容为文件夹名字

    #记录下载视频字典，并依此下载视频
    with open("./result/%s/%s视频信息"%(iname,iname),"a+",encoding="utf-8")as f:
        f.seek(0)
        i=len(f.readlines())+1
        print("视频信息这次前记录了%s行"%(i-1))
        for k,v in dict1.items():#无重复添加网址
            oname='%s_%s'%(iname,i)#保证接着上次序号的继续
            dict2.setdefault("%s"%oname,[]).append(v)
            dict2.setdefault("%s"%oname,[]).append(k)
            i=i+1
            f.write('%s————————%s————————%s\n'%(oname,v,k))#序号-名字-网址
    return dict2,ret_3
    
#下载视频
def get_video(dict2,iname):
    print("正在获取视频")
    path_1='./result/%s/'%iname#结果总目录下的目标目录
    j=C.input_config['max_num']
    #开始下载
    i=1
    for k,v in dict2.items():#k,v:序号，[v[0]名字，v[1]网址]
        
        if i<j:#限制视频数量
            if  i!=C.input_config['skip1'] and i!=C.input_config['skip2'] and i!=C.input_config['skip3']:#测试时排除第?个视频
                fname=path_1+'%s'%k#序号继承
                if glob.glob(fname)==[]:
                    os.makedirs(fname)        
                os.chdir(fname)#切换到文件夹的工作路径

                #循环下载，防止网络不好而导致下载出问题，限制3次都没有下载成功那么跳过
                state=1               
                try_time=0
                GO=True
                while state ==1 and GO==True:
                    try_time +=1
                    cmd='youtube-dl -f 134+140 %s'%v[1]
                    print("%s正在尝试下载视频：%s"%(k,v[1]))
                    print("第%s次尝试"%try_time)
                    state=os.system(cmd)
                    del(cmd)             
                    if state==1 and try_time==3: 
                        GO=False
                        print('视频%s：%s可能为直播或者有版权限制，无法下载'%(v[0],v[1]))
                        os.chdir('../')
                        os.rmdir(k)                    
                        with open("不能下的%s"%iname,"a+",encoding="utf-8")as c:
                            c.write('%s\n'%v[1])
                        os.chdir(C.input_config['path'])
                        time.sleep(1)

                #下载成功
                if GO==True:
                    vname1=glob.glob('./*.mp4')[0]
                    vname2='video.mp4'
                    os.rename(vname1,vname2)#改视频名为video.mp4 
                    print('下载视频+1')
                    os.chdir('../')#退出到上级目录
                    with open("下载好的%s"%iname,"a+",encoding="utf-8")as a:
                        a.write('%s\n'%v[1])
                    '''
                    with open("result\\%s\\%s视频信息"%(iname,iname),"a+",encoding="utf-8")as f:
                        f.seek(0)
                        oname=len(f.readlines())+1
                        f.write('%s————————%s————————%s\n'%(oname,v,k))
                    '''
                    os.chdir(C.input_config['path'])     
                    time.sleep(1)  
        i=i+1

#分割视频
def cut_video(ret_3,iname):
    print("正在分割视频")
    ret=[]
    path='./result/%s/'%iname
    dirs = os.listdir('./result/%s'%iname)
    for s in dirs:
        if os.path.isdir(path+s):#判断是不是文件夹
            ret.append(s)
    if ret:#空列表则不分割
        for s in ret:#s为文件夹名称
            if s not in ret_3:#确保s之前没有被分割
                os.chdir('./result/%s/%s'%(iname,s))#定位到文件夹内
                #vname2=glob.glob('./*.mp4')[0]
                fs_list=['-f', 'video.mp4', '-s', '%s'%C.input_config['time']]
                fs.main(fs_list)
                if C.input_config['kill']:
                    os.remove('video.mp4')
                print('分割视频+1')
                os.chdir('../')
                with open("分割好的%s"%iname,"a+",encoding="utf-8")as b:
                    b.write('%s\n'%s)#文件夹名
                os.chdir(C.input_config['path'])
                time.sleep(1)
        print('分割完毕')
    else: print("没有可以分割的视频")

#压缩文件夹
def zipDir(dirpath,outFullName,iname):
    os.chdir('./result')
    print("删除原%s压缩视频"%iname)
    fzip=glob.glob('./%s_zip.zip'%iname)
    if fzip!=[]:
            os.remove('./%s_zip.zip'%iname)
    print("正在压缩视频")
    zip1 = zipfile.ZipFile(outFullName,"w",zipfile.ZIP_DEFLATED)
    for path,dirnames,filenames in os.walk(dirpath):# 去掉目标根路径，只对目标文件夹下边的文件及文件夹进行压缩      
        fpath = path.replace(dirpath,'')
        for filename in filenames:
            zip1.write(os.path.join(path,filename),os.path.join(fpath,filename))
    zip1.close()        
    os.rename(zip1.filename,zip1.filename+'.zip')
    print('压缩的文件夹为：%s'%zip1.filename)
    os.chdir(C.input_config['path'])

#快进到remake
def remake():
    os.chdir(C.input_config['path'])
    if glob.glob("./result")!=[]:
        if os.listdir("result")==[]: shutil.rmtree("result")
        else: os.remove("result")
        
if __name__=="__main__":
    iname=C.input_config['input_name']#输入索引内容
    
    if C.input_config['remake']:
        remake()
        exit()#退出
        
    #确保索引内容没有空格，+代替空格保证符合搜索标准
    str1=iname
    str2=str1.strip(' ')
    str3=str2.replace(' ','+')
    
    #进入网址
    driver=webdriver.Chrome()
    driver.get("https://www.youtube.com/results?search_query=%s"%(iname))
    dict2,ret_3=get_informs(driver,iname)
    video=get_video(dict2,iname)
    print('下载完毕')
    #判断是否分割与解压
    if C.input_config['split']:
        cut_video(ret_3,iname)
        
    #判断是否压缩视频
    if C.input_config['zip']:
        zipDir('%s'%iname,'%s_zip'%iname,iname)
        













