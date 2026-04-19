import os
import sys
from configparser import ConfigParser
#from typing import List, Dict, Any
import time

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Sougou_dict_spider.SougouSpider import SougouSpider
from wubi_utils import WubiCodeGenerator
from api_client import APIClient


class AutoAddHotWords:
    def __init__(self,hotwords:list=[1,2,3,4]):
        # 读取配置
        self.config = ConfigParser()
        self.config_file = 'config.ini'
        
        if not os.path.exists(self.config_file):
            self._create_default_config()
        
        self.config.read(self.config_file, encoding='utf-8')
        
        # 初始化模块
        self.api_client = None
        self.wubi_generator = None
        self.hotwords = hotwords
    
    def _create_default_config(self):
        """创建默认配置文件"""
        default_config = {
            'category': {
                'category': '城市信息:167,自然科学:1'
            },
            'auth': {
                'email': 'test@163.com',
                'password': 'test'
            },
            'api': {
                'base_url': 'http://localhost:3000/portal/',
                'verify_ssl': 'false',
                'batch_size': '100'
            },
            'sougou': {
                'timeout': '30',
                'max_words': 3000
            }
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            for section, options in default_config.items():
                f.write(f'[{section}]\n')
                for key, value in options.items():
                    f.write(f'{key} = {value}\n')
                f.write('\n')
        
        print(f"创建默认配置文件: {self.config_file}")
        print("请根据实际情况修改配置文件后重新运行程序")
        sys.exit(0)
    
    def initialize_modules(self):
        """初始化各个模块"""
        print("\n初始化模块...")
        
        # 初始化 API 客户端
        try:
            self.api_client = APIClient(
                email=self.config['auth']['email'],
                password=self.config['auth']['password'],
                base_url=self.config['api']['base_url'],
                verify_ssl=self.config['api'].getboolean('verify_ssl', False)
            )
            print("API客户端初始化成功")
        except Exception as e:
            raise Exception(f"初始化 API 客户端失败: {str(e)}")
        
        # 初始化五笔编码生成器
        try:
            self.wubi_generator = WubiCodeGenerator()
            print("五笔编码生成器初始化成功")
        except Exception as e:
            raise Exception(f"初始化五笔编码生成器失败: {str(e)}")


    def run(self):
        """执行主流程"""
        # print("=" * 60)
        # print("词组自动添加程序")
        # print("=" * 60)
        
        total_added = 0
        total_phrases = 0
        processed_dicts = 1  # 热词列表视为一个词库文件
        
        try:
            # 1. 初始化模块
            self.initialize_modules()
            # 2. 获取词组
            ssdp = SougouSpider()
            phrases = ssdp.GetHotWordList(self.hotwords)
            if not phrases:
                print("  获取热词失败")
                return

            total_phrases = len(phrases)

            # category_name  category_id 列表
            categorys = {x['name']:x['id'] for x in self.api_client.get_category()}

            # 获取当前词库对应的类别ID
            category_name = "每日热词"
            if category_name in categorys:
                category_id = categorys[category_name]
            else:
                addresult = self.api_client.add_category(category_name)
                if not addresult['success']:
                    print(f"  添加类别失败  {addresult['message']}")
                    return
                categorys = {x['name']: x['id'] for x in self.api_client.get_category()}
                # print(categorys)
                category_id = categorys[category_name]
            print(f"  词库类别: {category_name}, 类别ID: {category_id} ",end="")
            
            # 过滤和生成编码
            valid_phrases = []
            
            # 先过滤掉基础词库中已存在的词组
            phrases_not_in_base = []
            for phrase in phrases:
                if not self.wubi_generator.is_in_base_dict(phrase):
                    phrases_not_in_base.append(phrase)
            
            not_in_base_count = len(phrases_not_in_base)
            print(f"  基础词库中不存在的词组: {not_in_base_count} 个 ",end="")
            
            if not phrases_not_in_base:
                print(f"  所有词组都已存在于基础词库中，跳过")
                return
            
            # 检查数据库中已存在的词组
            print(f"  正在检查数据库中已存在的词组...")
            existing_words = set([x['word'] for x in self.api_client.get_words()])
            existing_count = len(existing_words)
            print(f"  数据库中已存在 {existing_count} 个词组")
            
            # 生成五笔编码并添加到有效词组列表
            generated_count = 0
            code_failed_count = 0
            existing_in_db_count = 0
            
            for phrase in phrases_not_in_base:
                # 检查是否已在数据库中
                if phrase in existing_words:
                    existing_in_db_count += 1
                    continue
                
                # 生成五笔编码
                code = self.wubi_generator.generate_code(phrase)
                if code:
                    generated_count += 1
                    # 处理类别ID，确保它是有效的整数
                    category_id_value = 0  # 默认值
                    if category_id:
                        try:
                            category_id_value = int(category_id)
                        except ValueError:
                            print(f"  警告: 无效的类别ID '{category_id}'，使用默认值0")
                    
                    valid_phrases.append({
                        'word': phrase,
                        'code': code,
                        'priority': 0,
                        'up': 0,
                        'down': 0,
                        'comment': '',
                        'category_id': category_id_value  # 使用当前词库对应的类别ID
                    })
                else:
                    code_failed_count += 1
            
            print(f"  数据库中已存在: {existing_in_db_count} 个，成功生成编码: {generated_count} 个，词组不符合要求: {code_failed_count} 个")
            print(f"  最终符合条件的词组: {len(valid_phrases)} 个")
            
            # 6. 批量添加词组
            if not valid_phrases:
                return
            try:
                result = self.api_client.add_words(valid_phrases)
                if result['success']:
                    added = result['data'].get('addedCount', 0)
                    total_added += added
                    print(f"  ✓ 批次添加成功，新增 {added} 个词组")
                else:
                    print(f"  ✗ 批次添加失败: {result['message']}")
            except Exception as e:
                print(f"  ✗ 批次添加出错: {str(e)}")
        
        except KeyboardInterrupt:
            print("\n程序被用户中断")
        except Exception as e:
            print(f"\n程序执行失败: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            # 清理资源
            print("清理资源完成")
        # 输出统计信息
        print(f"处理词库文件: {processed_dicts} 个 ",end="")
        print(f"总解析词组: {total_phrases} 个 ",end="")
        print(f"成功添加词组: {total_added} 个")


def main():
    """主函数"""
    try:
        app = AutoAddHotWords([1])
        app.run()
    except Exception as e:
        print(f"程序启动失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
