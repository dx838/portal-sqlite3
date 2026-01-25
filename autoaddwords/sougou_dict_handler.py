import os
# import subprocess
# import tempfile
# import shutil
import sys
from typing import List

# 添加Sougou_dict_spider目录到Python路径，确保内部模块能被正确导入
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Sougou_dict_spider'))

# 直接从Sougou_dict_spider目录导入main函数
try:
    from rundownload import rundownload
    # print("成功导入 Sougou_dict_spider 中的 rundownload 函数")
except ImportError as e:
    print(f"导入 Sougou_dict_spider 中的 rundownload 函数失败: {e}")
    raise

class SougouDictHandler:
    def __init__(self, categories: List[str]):
        self.categories = categories
        # 使用项目目录下的scel文件夹作为下载目录
        self.download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scel')
        # 文本保存目录
        self.text_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'txt')
        # dict json 保存位置
        self.jsonfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'updatescel.json')
        # 由调用函数处理文件夹的创建检查。如果目录不存在，直接创建
        # os.makedirs(self.download_dir, exist_ok=True)  # 不需要检查下载目录是否存在
        # os.makedirs(self.text_dir, exist_ok=True)      # # 不需要检查
        self.downloaded_dicts = []
    

    def download_dicts(self):
        """下载指定类别的词库"""
        print(f"使用下载目录: {self.download_dir}")
        print(f"使用文本保存目录: {self.text_dir}")
        
        try:
            # 直接调用 Sougou_dict_spider 中的 main 函数
            # 该函数会处理所有类别的下载
            rundownload(self.categories, self.download_dir, self.text_dir,self.jsonfile)
            print(f"所有类别词库下载完成")
        except ValueError as e:
            print(f"类别配置格式错误，正确格式应为 '类别名称:类别ID': {e}")
        except Exception as e:
            print(f"下载词库失败: {str(e)}")
    
    def get_downloaded_dicts(self) -> List[str]:    # 获取已经下载的词库
        """获取已下载的词库文件列表"""
        # 更新已下载的词库文件列表
        self.downloaded_dicts = []
        for root, _, files in os.walk(self.text_dir):
            for file in files:
                if not file.endswith('.txt'):  # 不是 txt  文件 跳过
                    continue
                file_path = os.path.join(root, file)
                #category = file.split('.')[0].split('_')[-1].split('[')[0].split('【')[0]
                #print(f"{category}: {file_path}")  # 打印文件路径和类别ID
                self.downloaded_dicts.append(file_path)
        #
        return self.downloaded_dicts
    
    def get_category_name(self, dict_path: str) -> str:
        """根据词库文件路径获取对应的类别名称"""
        category_name = os.path.basename(dict_path).split('.')[0].split('_')[-1].split('[')[0].split('【')[0]
        return category_name


if __name__ == '__main__':
    sg = SougouDictHandler(['广州市地铁站名:198'])
    sg.download_dicts()