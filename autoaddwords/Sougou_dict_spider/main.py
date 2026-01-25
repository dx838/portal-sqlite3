#!/usr/bin/env python  
# _*_ coding:utf-8 _*_  
#  
# @Version : 1.0  
# @Time    : 2019/11/1
# @Author  : 圈圈烃
# @File    : main
# @Description:
#
#
import SougouSpider
import Scel2Txt
import os
import json


# 下载类别
# Categories = ['城市信息:167', '自然科学:1', '社会科学:76', '工程应用:96', '农林渔畜:127', '医学医药:132',
#               '电子游戏:436', '艺术设计:154', '生活百科:389', '运动休闲:367', '人文科学:31', '娱乐休闲:403']



def main(Categories,SavePath,txtSavePath,jsonfilepath='') -> None:
    # 缺少参数直接退出
    if not Categories or not SavePath or not txtSavePath:
        print(f"缺少参数，传入参数不完整。")
        exit()
    """搜狗词库下载"""
    SGSpider = SougouSpider.SougouSpider()
    # 创建保存路径
    # SavePath
    try:
        if os.path.exists(SavePath):
            if not os.path.isdir(SavePath):
                os.rmdir(SavePath)
                os.mkdir(SavePath)     #
        else:
            os.mkdir(SavePath)
    except Exception as e:
        print(e)
    #  txtSavePath
    try:
        if os.path.exists(txtSavePath):
            if not os.path.isdir(txtSavePath):
                os.rmdir(txtSavePath)
                os.mkdir(txtSavePath)      #
        else:
            os.mkdir(txtSavePath)
    except Exception as e:
        print(e)
    # 一个scel文件更新情况 ,存放在程序目录下
    if not jsonfilepath :
        jsonfilepath = os.path.join(os.path.dirname(__file__),'updatescel.json')
    if os.path.isfile(jsonfilepath):
        with open(jsonfilepath, 'r', encoding='utf-8') as f:
            sceljson = json.load(f)
    else:
        sceljson = dict()

    # # 我需要啥
    # myCategoryUrls = []
    # for mc in Categories:
    #     myCategoryUrls.append("https://pinyin.sogou.com/dict/cate/index/" + mc.split(":")[-1])
    # print(myCategoryUrls)
    # 将词库id和名称对应起来
    category_names = dict()
    for category in Categories:
        category_id = category.split(":")[-1]
        category_name = category.split(":")[0]
        if category_name in category_names:
            category_names[category_id].append(category_name)
        else:
            category_names[category_id] = [category_name]
    # 大类分类
    for category_id,category_name in category_names.items():
        # 创建保存路径 直接放一个目录下面
        # categoryOnePath = SavePath + "/" + category_id
        categoryOneUrl = f"https://pinyin.sogou.com/dict/cate/index/{category_id}"
        # try:
        #     os.mkdir(categoryOnePath)
        # except Exception as e:
        #     print(e)
        # 获取小类链接
        # resp = SGSpider.GetHtml(categoryOneUrl)
        # 判断该链接是否为"城市信息",若是则采取Type1方法解析
        # if categoryOneUrl == "https://pinyin.sogou.com/dict/cate/index/167":
        #     category2Type1Urls = SGSpider.GetCategory2Type1(resp)
        # else:
        #     category2Type1Urls = SGSpider.GetCategory2Type2(resp)
        # #
        # print('获取链接',category2Type1Urls)
        # 小类分类
        # for key, url in category2Type1Urls.items():
            # 创建保存路径
            # categoryTwoPath = SavePath + "/" + category_id + "_" + key
            # try:
            #     if os.path.exists(categoryTwoPath):
            #         if os.path.isdir(categoryTwoPath):
            #             pass
            #         else:
            #             os.rmdir(categoryTwoPath)
            #     else:
            #         os.mkdir(categoryTwoPath)
            # except Exception as e:
            #     print(e)
            # 获取总页数
        try:
            resp = SGSpider.GetHtml(categoryOneUrl)
            pages = SGSpider.GetPage(resp)
        except Exception as e:
            print(e)
            pages = 1
        # 已处理的词库
        already_download = []
        # 获取下载链接
        for page in range(1, pages + 1):
            pageUrl = categoryOneUrl + "/default/" + str(page)
            if page > 1:
                resp = SGSpider.GetHtml(pageUrl)
            # downloadUrls = SGSpider.GetDownloadList(resp)
            downloadUrls = SGSpider.GetDownloadListMoreInfo(resp)
            # 开始下载
            for keyDownload, urlDownload in downloadUrls.items():
                # 只下载指定的文件
                if keyDownload in category_names[category_id]:
                    already_download.append(keyDownload)   # 已下载
                    filePath = os.path.join(SavePath, category_id + "_" + keyDownload + ".scel")
                    if not os.path.isfile(filePath) or (os.path.isfile(filePath) and urlDownload[-1] > sceljson.get(keyDownload,0)):
                        # if os.path.exists(filePath):
                        #     print(keyDownload + " 文件已存在>>>>>>")
                        # else:
                        #     SGSpider.Download(urlDownload[0], filePath)
                        #     print(keyDownload + " 保存成功......")
                        SGSpider.Download(urlDownload[0], filePath)
                        print(f"{keyDownload}:{category_id}  保存成功......")
                        sceljson[keyDownload] = urlDownload[-1]
                    else:
                        print(f"{keyDownload}:{category_id}  已下载")
                    # 下载完指定的后就跳出，好下载下一个
                if not (set(category_names[category_id]) - set(already_download)) :  # 下载完指定的词库后退出
                    break
                # else:
                #     print(f'{category_name} {page} ',end='')
            if not (set(category_names[category_id]) - set(already_download) ):   # 下载完指定的词库后退出
                break
    # json 保存
    with open(jsonfilepath, 'w', encoding='utf-8') as f:
        json.dump(sceljson, f, ensure_ascii=False, indent=4)
    # 转scel为txt
    Scel2Txt.batch_filecs4(SavePath, txtSavePath)
    print("任务结束...")


if __name__ == '__main__':
    # 填写具体要下载的文件名：id
    # Categories = ['广州市地铁站名:198', '自然科学:1', '社会科学:76', '工程应用:96', '农林渔畜:127', '医学医药:132',
    #               '电子游戏:436', '艺术设计:154', '生活百科:389', '运动休闲:367', '人文科学:31', '娱乐休闲:403']
    Categories = ['广州市地铁站名:198']
    # Scel保存路径
    SavePath = r"D:\Program\WebProjects\portal\portal-sqlite3\autoaddwords\scel"

    # TXT保存路径
    txtSavePath = r"D:\Program\WebProjects\portal\portal-sqlite3\autoaddwords\txt"

    # 开始链接
    # startUrl = "https://pinyin.sogou.com/dict/cate/index/436"

    main(Categories,SavePath,txtSavePath)
