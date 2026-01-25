
import os

class WubiCodeGenerator:
    def __init__(self):
        self.base_dict = self._load_base_dict()
        self.valid_chars = set('abcdefghijklmnopqrstuvwxy')  # 只使用a-y的25个字母
    
    def _load_base_dict(self):
        """加载基础词库，优化内存使用"""
        base_dict = {}
        dict_path = 'wubi86_jidian.dict.yaml'
        
        if not os.path.exists(dict_path):
            raise FileNotFoundError(f"基础词库文件不存在: {dict_path}")
        
        print(f"加载基础词库: {dict_path}")
        
        try:
            with open(dict_path, 'r', encoding='utf-8') as f:
                # 读取文件内容
                for content in f:
                    start = content.find('工\ta')
                    if start != -1:
                        line = content.strip()
                        line = line.strip()
                        if not line:
                            continue
                        # 处理词库条目
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            char = parts[0]
                            code = parts[1]
                            # 只保留单字的编码，跳过词组
                            # if len(char) == 1:  # 因为要对比词组是否存在，要加载全部词库
                            #    base_dict[char] = code
                            base_dict[char] = code
                
                # 跳过头部配置，直接读取词库内容
                # start = content.find('工\ta')
                # if start != -1:
                #     lines = content[start:].split('\n')
                #     for line in lines:
                #         line = line.strip()
                #         if not line:
                #             continue
                #
                #         # 处理词库条目
                #         parts = line.split('\t')
                #         if len(parts) >= 2:
                #             char = parts[0]
                #             code = parts[1]
                #             # 只保留单字的编码，跳过词组
                #             # if len(char) == 1:  # 因为要对比词组是否存在，要加载全部词库
                #             #    base_dict[char] = code
                #             base_dict[char] = code
        except UnicodeDecodeError:
            # 尝试使用其他编码
            print(f"UTF-8编码读取失败，尝试使用GBK编码")
            with open(dict_path, 'r', encoding='gbk') as f:
                # 读取文件内容
                for content in f:
                    start = content.find('工\ta')
                    if start != -1:
                        line = content.strip()
                        if not line:
                            continue
                        # 处理词库条目
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            char = parts[0]
                            code = parts[1]
                            # 只保留单字的编码，跳过词组
                            # if len(char) == 1:  # 因为要对比词组是否存在，要加载全部词库
                            #    base_dict[char] = code
                            base_dict[char] = code
        
        print(f"加载完成，共 {len(base_dict)} 个编码")
        return base_dict
    
    def is_in_base_dict(self, phrase):
        """检查词组是否在基础词库中"""
        return phrase in self.base_dict
    
    def generate_code(self, phrase):
        """生成五笔编码"""
        length = len(phrase)
        if length < 2:
            return None
        
        # 获取每个字的基础编码
        char_codes = []
        for char in phrase:
            if char not in self.base_dict:
                return None  # 有字没有编码，跳过
            char_codes.append(self.base_dict[char])
        
        # 根据字数生成编码
        if length == 2:
            # 两字词：每个字编码的前两个字母
            code = char_codes[0][:2] + char_codes[1][:2]
        elif length == 3:
            # 三字词：前两个字的第一个字母 + 第三个字的前两个字母
            code = char_codes[0][0] + char_codes[1][0] + char_codes[2][:2]
        elif length >= 4:
            # 四字及以上词：前三个字的第一个字母 + 最后一个字的第一个字母
            code = char_codes[0][0] + char_codes[1][0] + char_codes[2][0] + char_codes[-1][0]
        else:
            return None
        
        # 编码有效性检查
        if len(code) > 4:
            code = code[:4]
        
        # 检查编码是否只包含有效字符
        if not all(c in self.valid_chars for c in code):
            return None
        
        return code



if __name__ == '__main__':
    wb = WubiCodeGenerator()
    wbbm=wb.generate_code('五笔天天')
    print(wbbm)
