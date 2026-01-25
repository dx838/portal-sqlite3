import os
import sys
from configparser import ConfigParser
#from typing import List, Dict, Any
import time

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sougou_dict_handler import SougouDictHandler
from wubi_utils import WubiCodeGenerator
from api_client import APIClient


class AutoAddWords:
    def __init__(self):
        # 读取配置
        self.config = ConfigParser()
        self.config_file = 'config.ini'
        
        if not os.path.exists(self.config_file):
            self._create_default_config()
        
        self.config.read(self.config_file, encoding='utf-8')
        
        # 初始化模块
        self.api_client = None
        self.sougou_handler = None
        self.wubi_generator = None
    
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
        
        # 初始化搜狗词库处理器
        try:
            categories = [x for x in self.config['category']['category'].split(',') if x != '' and ":" in x]
            self.sougou_handler = SougouDictHandler(categories=categories)
            print(f"搜狗词库处理器初始化成功，配置了 {len(categories)} 个类别")
        except Exception as e:
            raise Exception(f"初始化搜狗词库处理器失败: {str(e)}")
        
        # 初始化五笔编码生成器
        try:
            self.wubi_generator = WubiCodeGenerator()
            print("五笔编码生成器初始化成功")
        except Exception as e:
            raise Exception(f"初始化五笔编码生成器失败: {str(e)}")
    
    def _parse_dict(self, dict_path: str) -> list:
        """解析词库文件，提取词组"""
        phrases = []
        
        try:
            with open(dict_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    # 词库文件格式可能是：词组 频率
                    parts = line.split()
                    if parts:
                        phrase = parts[0]
                        # 只处理5个字符或更少的词组
                        if 2 <= len(phrase) <= 5:
                            phrases.append(phrase)
        except UnicodeDecodeError:
            # 尝试使用其他编码
            try:
                with open(dict_path, 'r', encoding='gbk') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        parts = line.split()
                        if parts:
                            phrase = parts[0]
                            if 2 <= len(phrase) <= 5:
                                phrases.append(phrase)
            except Exception as e:
                print(f"  解析词库文件失败: {dict_path}，错误: {str(e)}")
        except Exception as e:
            print(f"  解析词库文件失败: {dict_path}，错误: {str(e)}")
        
        return phrases
    
    def _get_category_id_for_dict(self, dict_path: str) -> str:
        """根据词库文件路径获取对应的类别ID"""
        filename = os.path.basename(dict_path)
        category_id = filename.split('.')[0].split('_')[-1].split('[')[0].split('【')[0]
        return category_id
    
    def run(self):
        """执行主流程"""
        # print("=" * 60)
        # print("词组自动添加程序")
        # print("=" * 60)
        
        total_added = 0
        total_phrases = 0
        processed_dicts = 0
        
        try:
            # 1. 初始化模块
            self.initialize_modules()
            
            # 2. 下载词库
            print("\n开始下载词库...")
            self.sougou_handler.download_dicts()
            
            # 3. 处理每个词库
            downloaded_dicts = self.sougou_handler.get_downloaded_dicts()
            print(f"\n共下载到 {len(downloaded_dicts)} 个词库文件")
            
            if not downloaded_dicts:
                print("没有找到可处理的词库文件")
                return
            
            batch_size = int(self.config['api'].get('batch_size', 100))

            # category_name  category_id 列表
            categorys = {x['name']:x['id'] for x in self.api_client.get_category()}
            #
            
            for dict_path in downloaded_dicts:
                processed_dicts += 1
                print(f"\n{processed_dicts}/{len(downloaded_dicts)} 处理词库: {os.path.basename(dict_path)}")
                
                # 4. 解析词库
                phrases = self._parse_dict(dict_path)
                parsed_count = len(phrases)
                max_words = int(self.config['sougou'].get('max_words', 3000))
                if parsed_count > max_words:
                    print(f"  词库文件太大，词组超过{max_words}，跳过  {os.path.basename(dict_path)}")
                    continue
                total_phrases += parsed_count
                print(f"  解析出 {parsed_count} 个词组")
                
                if not phrases:
                    print(f"  词库中没有可用的词组，跳过")
                    continue
                
                # 获取当前词库对应的类别ID
                category_name = self.sougou_handler.get_category_name(dict_path)
                if category_name in categorys:
                    category_id = categorys[category_name]
                else:
                    addresult = self.api_client.add_category(category_name)
                    if not addresult['success']:
                        print(f"  添加类别失败  {addresult['message']}")
                        return
                    categorys = {x['name']: x['id'] for x in self.api_client.get_category()}
                    print(categorys)
                    category_id = categorys[category_name]
                print(f"  词库类别: {category_name}, 类别ID: {category_id}")
                
                # 5. 过滤和生成编码
                valid_phrases = []
                
                # 先过滤掉基础词库中已存在的词组
                phrases_not_in_base = []
                for phrase in phrases:
                    if not self.wubi_generator.is_in_base_dict(phrase):
                        phrases_not_in_base.append(phrase)
                
                not_in_base_count = len(phrases_not_in_base)
                print(f"  基础词库中不存在的词组: {not_in_base_count} 个")
                
                if not phrases_not_in_base:
                    print(f"  所有词组都已存在于基础词库中，跳过")
                    continue
                
                # 获取数据库中所有已存在的词组
                print(f"  正在检查数据库中已存在的词组...")
                # 每次加载已经字入的词库，
                # words = set([x['word'] for x in self.api_client.get_words()])    # 后端会检查重复的词库
                # existing_count = len(words)
                # print(f"  数据库中已存在的词组: {existing_count} 个")
                
                # 生成五笔编码并添加到有效词组列表
                generated_count = 0
                code_failed_count = 0
                
                for phrase in phrases_not_in_base:
                    # 检查是否已在数据库中
                    # if phrase in words:  # 后端会检查
                    #     continue
                    
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
                
                print(f"  成功生成编码: {generated_count} 个，生成失败: {code_failed_count} 个")
                print(f"  最终符合条件的词组: {len(valid_phrases)} 个")
                
                # 6. 批量添加词组
                if valid_phrases:
                    print(f"  准备批量添加词组，每批 {batch_size} 个")
                    for i in range(0, len(valid_phrases), batch_size):
                        batch = valid_phrases[i:i+batch_size]
                        batch_num = i // batch_size + 1
                        total_batches = (len(valid_phrases) + batch_size - 1) // batch_size
                        print(f"\n  批次 {batch_num}/{total_batches}: 添加 {len(batch)} 个词组")
                        
                        try:
                            result = self.api_client.add_words(batch)
                            if result['success']:
                                added = result['data'].get('addedCount', 0)
                                total_added += added
                                print(f"  ✓ 批次添加成功，新增 {added} 个词组")
                            else:
                                print(f"  ✗ 批次添加失败: {result['message']}")
                        except Exception as e:
                            print(f"  ✗ 批次添加出错: {str(e)}")
                
                # 清理已处理的词库文件
                try:
                    if os.path.isfile(dict_path):
                        for _ in range(3):
                            try:
                                os.remove(dict_path)
                                print(f"  已删除处理完成的词库文件")
                                break
                            except Exception as e:
                                time.sleep(0.5)
                                continue
                except Exception as e:
                    print(f"  警告: 删除词库文件失败: {str(e)}")
        
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
        print(f"处理词库文件: {processed_dicts} 个")
        print(f"总解析词组: {total_phrases} 个")
        print(f"成功添加词组: {total_added} 个")


def main():
    """主函数"""
    try:
        app = AutoAddWords()
        app.run()
    except Exception as e:
        print(f"程序启动失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
