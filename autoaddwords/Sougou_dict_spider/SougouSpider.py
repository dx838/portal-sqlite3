#!/usr/bin/env python
# _*_ coding:utf-8 _*_
#
# @Version : 1.0
# @Time    : 2019/11/1
# @Author  : 圈圈烃
# @File    : SougouSpider
# @Description:
#
#
from bs4 import BeautifulSoup
from urllib.parse import unquote
import requests
import re
import time

class SougouSpider:

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }
        self.session = requests.Session()

    def GetHtml(self, url, isOpenProxy=False, myProxies=None, retries=8):
        """
        获取Html页面
        :param isOpenProxy: 是否打开代理，默认否
        :param Proxies: 代理ip和端口，例如：103.109.58.242:8080，默认无
        :return:
        """
        try:
            pattern = re.compile(r'//(.*?)/')
            hostUrl = pattern.findall(url)[0]
            self.headers["Host"] = hostUrl
            if isOpenProxy:
                proxies = {"http": "http://" + myProxies, }
                resp = requests.get(url, headers=self.headers, proxies=proxies, timeout=5)
            else:
                resp = requests.get(url, headers=self.headers, timeout=5)
            #
            resp.encoding = resp.apparent_encoding
            # print("GetHtml成功..." + url)
            time.sleep(6)  # 防止被waf判定为恶意
            return resp
        except requests.exceptions.ReadTimeout as e:
            print("GetHtml失败...尝试重连 " + url)  # 超时重连5次
            if retries > 0:
                time.sleep(5+retries)
                return self.GetHtml(url, isOpenProxy, myProxies, retries=retries-1)
            else:
                print("重连失败..." + url)
                print(e)

    def GetCategoryOne(self, resp):
        """获取大类链接"""
        categoryOneUrls = []
        soup = BeautifulSoup(resp.text, "html.parser")
        dict_nav = soup.find("div", id="dict_nav_list")
        dict_nav_lists = dict_nav.find_all("a")
        for dict_nav_list in dict_nav_lists:
            dict_nav_url = "https://pinyin.sogou.com" + dict_nav_list['href']
            categoryOneUrls.append(dict_nav_url)
        return categoryOneUrls

    def GetCategory2Type1(self, resp):
        """获取第一种类型的小类链接"""
        category2Type1Urls = {}
        soup = BeautifulSoup(resp.text, "html.parser")
        dict_td_lists = soup.find_all("div", class_="cate_no_child citylistcate no_select")
        for dict_td_list in dict_td_lists:
            dict_td_url = "https://pinyin.sogou.com" + dict_td_list.a['href']
            category2Type1Urls[dict_td_list.get_text().replace("\n", "")] = dict_td_url
        return category2Type1Urls

    def GetCategory2Type2(self, resp):
        """获取第二种类型的小类链接"""
        category2Type2Urls = {}
        soup = BeautifulSoup(resp.text, "html.parser")
        dict_td_lists = soup.find_all("div", class_="cate_no_child no_select")
        # 类型1解析
        for dict_td_list in dict_td_lists:
            dict_td_url = "https://pinyin.sogou.com" + dict_td_list.a['href']
            category2Type2Urls[dict_td_list.get_text().replace("\n", "")] = dict_td_url
        # 类型2解析
        dict_td_lists = soup.find_all("div", class_="cate_has_child no_select")
        for dict_td_list in dict_td_lists:
            dict_td_url = "https://pinyin.sogou.com" + dict_td_list.a['href']
            category2Type2Urls[dict_td_list.get_text().replace("\n", "")] = dict_td_url
        return category2Type2Urls



    def GetPage(self, resp):
        """获取页码"""
        soup = BeautifulSoup(resp.text, "html.parser")
        dict_div_lists = soup.find("div", id="dict_page_list")
        dict_td_lists = dict_div_lists.find_all("a")
        page = dict_td_lists[-2].string
        return int(page)

    def GetDownloadList(self, resp):
        """获取下载链接"""
        downloadUrls = {}
        pattern = re.compile(r'name=(.*)')
        soup = BeautifulSoup(resp.text, "html.parser")
        dict_dl_lists = soup.find_all("div", class_="dict_dl_btn")
        for dict_dl_list in dict_dl_lists:
            dict_dl_url = dict_dl_list.a['href']
            dict_name = pattern.findall(dict_dl_url)[0]
            dict_ch_name = unquote(dict_name, 'utf-8').replace("/", "-").replace(",", "-").replace("|", "-") \
                .replace("\\", "-").replace("'", "-")
            downloadUrls[dict_ch_name] = dict_dl_url
        return downloadUrls

    def GetDownloadListMoreInfo(self, resp):
        """获取下载链接"""
        # 结构 dict_detail_block
        #           dict_detail_title_block
        #               detail_title
        #           dict_detail_show
        #               dict_detail_content
        #                   show_title
        #                   show_content
        #               dict_dl_btn
        downloadUrls = {}
        pattern = re.compile(r'name=(.*)')
        soup = BeautifulSoup(resp.text, "html.parser")
        dict_detail_blocks = soup.find_all("div", class_="dict_detail_block")     # dict_detail_block
        for dict_detail_block in dict_detail_blocks:
            dict_detail_title_block = dict_detail_block.find("div", class_="dict_detail_title_block")   # dict_detail_title_block
            detail_title = dict_detail_title_block.find("div", class_="detail_title")    # detail_title
            dict_ch_name = detail_title.text
            #
            dict_detail_show = dict_detail_block.find("div", class_="dict_detail_show")      # dict_detail_show
            dict_show_content = dict_detail_show.find_all("div", class_="show_content")
            try:
                dict_ch_time = time.mktime(time.strptime([x.text for x in dict_show_content if len(x.text)==19 and x.text.startswith('20')][-1],"%Y-%m-%d %H:%M:%S"))    # 2013-07-18 10:37:47  转换为时间缀
            except Exception as e:
                dict_ch_time = 0
            dict_dl_btn = dict_detail_show.find("div", class_="dict_dl_btn")
            dict_dl_url = dict_dl_btn.a['href']
            # print("GetDownloadListMoreInfo",dict_ch_name, dict_dl_url, dict_ch_time)
            downloadUrls[dict_ch_name] = (dict_dl_url, dict_ch_time)

        # 旧实现
        # dict_dl_lists = soup.find_all("div", class_="dict_dl_btn")
        # for dict_dl_list in dict_dl_lists:
        #     dict_dl_url = dict_dl_list.a['href']
        #     dict_name = pattern.findall(dict_dl_url)[0]
        #     dict_ch_name = unquote(dict_name, 'utf-8').replace("/", "-").replace(",", "-").replace("|", "-") \
        #         .replace("\\", "-").replace("'", "-")
        #     downloadUrls[dict_ch_name] = dict_dl_url
        return downloadUrls

    def Download(self, downloadUrl, path, isOpenProxy=False, myProxies=None):
        """下载"""
        pattern = re.compile(r'//(.*?)/')
        hostUrl = pattern.findall(downloadUrl)[0]
        self.headers["Host"] = hostUrl
        if isOpenProxy:
            proxies = {"http": "http://" + myProxies, }
            resp = requests.get(downloadUrl, headers=self.headers, proxies=proxies, timeout=5)
        else:
            resp = requests.get(downloadUrl, headers=self.headers, timeout=5)
        with open(path, "wb") as fw:
            fw.write(resp.content)
        time.sleep(8)  # 防止被waf判定为恶意
