import requests
import sys

class APIClient:
    def __init__(self, email, password, base_url='http://localhost:3000/portal/', verify_ssl=True):
        """
        初始化API客户端
        Args:
            email (str): 登录邮箱
            password (str): 登录密码
            base_url (str): API基础URL，默认为'http://localhost:3000/portal/'
            verify_ssl (bool): 是否验证SSL证书，默认为True
        """
        self.email = email
        self.password = password
        self.base_url = base_url
        self.verify_ssl = verify_ssl
        self.token = ''
        self.uid = 0
        # 添加session对象，用于保持cookie
        self.session = requests.Session()
        self._login()  # 初始化后立即登录
    
    def _login(self):
        """登录获取 token"""
        #
        #  curl -H "Host: localhost:3000" -H "Content-Type: application/json" -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) wubi-dict-editor/1.3.0 Chrome/112.0.5615.204 Electron/24.8.8 Safari/537.36" -H "Accept-Language: zh-CN" --data-binary "{\"email\":\"test@163.com\",\"password\":\"test\"}" --compressed "http://localhost:3000/portal//user/login"
        #
        url = f'{self.base_url}/user/login'
        payload = {
            'email': self.email,
            'password': self.password
        }

        headers = self._get_headers()
        headers['Content-Type']="application/json"

        try:
            # 使用session对象发送请求，保持cookie
            response = self.session.post(
                url, 
                json=payload, 
                verify=self.verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                # print(f"登录响应数据: {data}")
                
                # 检查响应头中的cookie
                # print(f"登录响应头: {response.headers}")
                
                if data['success']:
                    # 检查返回数据中是否包含token，可能在不同的字段中
                    if 'data' in data:    # 通过的检查 是使用的 加密后的password
                        self.token = data['data'].get('password')
                        self.uid = data['data'].get('uid')
                else:
                    raise Exception(f"登录失败: {data['message']}")
            else:
                raise Exception(f"登录请求失败: {response.status_code}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求失败: {str(e)}")
        except ValueError as e:
            raise Exception(f"解析响应失败: {str(e)}")

    def _get_headers(self):
        """获取请求头"""
        url = self.base_url          # http://localhost:3000/portal/
        if url.startswith('https://'):
            url = url.lstrip("https://")
            url = url.split('/')[0]
        elif url.startswith('http://'):
            url = url.lstrip("http://")
            url = url.split('/')[0]
        #
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) wubi-dict-editor/1.3.0 Chrome/112.0.5615.204 Electron/24.8.8 Safari/537.36",
            "Host":f"{url}",
            "Accept":"application/json, text/plain, */*",
            "Accept-Language":"zh-CN",
        }
        #
        if self.token:
            headers['Diary-Token'] = f"{self.token}"
        if self.uid:
            headers['Diary-Uid'] = f"{self.uid}"
        return headers
    

    
    def add_words(self, phrases)-> dict:
        """批量添加词组到数据库"""
        #
        # curl -H "Host: localhost:3000" -H "Accept: application/json, text/plain, */*" -H "Diary-Token: $2b$10$/1ks3X5Q48Vvr0wmfrbU9edHb/FlF6YQE0sRdhgEeuguIM5AtCnh." -H "Diary-Uid: 10" -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) wubi-dict-editor/1.3.0 Chrome/112.0.5615.204 Electron/24.8.8 Safari/537.36" -H "Content-Type: application/json" -H "Accept-Language: zh-CN" --data-binary "{\"category_id\":10,\"words\":[{\"id\":2,\"code\":\"wyth\",\"word\":\"浠ょ墝\",\"priority\":\"\",\"note\":\"\",\"indicator\":\"\"}]}" --compressed "http://localhost:3000/portal/wubi/word/add-batch"
        #
        # {"category_id":10,"words":[{"id":2,"code":"wyth","word":"浠ょ墝","priority":"","note":"","indicator":""}]}
        #
        url = f'{self.base_url}/wubi/word/add-batch'
        # 为了兼容参数格式，这里对参数进行预处理
        if type(phrases) is dict and 'category_id' in phrases and 'words' in phrases and type(phrases['words']) is list:
            payload = phrases
        elif type(phrases) is list and len(set([x['category_id'] for x in phrases]))==1:
            payload = {
                'category_id': [x['category_id'] for x in phrases][0],
                'words': phrases
                }
        else:
            raise Exception("参数错误")

        headers = self._get_headers()
        headers['Content-Type'] = 'application/json'
        
        try:
            # 使用session对象发送请求，保持认证状态
            response = self.session.post(
                url, 
                json=payload, 
                headers=headers,
                verify=self.verify_ssl,
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"添加词组失败: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求失败: {str(e)}")

    def get_words(self) -> list:
        """获取类别"""
        #
        # curl -H "Host: localhost:3000" -H "Accept: application/json, text/plain, */*" -H "Diary-Token: $2b$10$/1ks3X5Q48Vvr0wmfrbU9edHb/FlF6YQE0sRdhgEeuguIM5AtCnh." -H "Diary-Uid: 10" -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) wubi-dict-editor/1.3.0 Chrome/112.0.5615.204 Electron/24.8.8 Safari/537.36" -H "Accept-Language: zh-CN" --data "" --compressed "http://localhost:3000/portal/wubi/word/export-extra"
        #
        # 更新请求地址为正确的地址
        url = f'{self.base_url}/wubi/word/export-extra'

        try:
            # 使用session对象发送请求，保持认证状态
            response = self.session.post(
                url,
                json={},
                headers=self._get_headers(),
                verify=self.verify_ssl,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                # print(f"获取类别响应数据: {data}")
                if data['success']:
                    # print("获取类别成功")
                    return data['data']
                else:
                    print(f"获取类别失败: {data['message']}")
                    return []
            else:
                print(f"获取类别请求失败: {response.status_code} ")
                return []
        except requests.exceptions.RequestException as e:
            print(f"获取类别网络请求失败: {str(e)}")
            return []

    def add_category(self, name:str)->dict:
        """添加类别"""
        url = f'{self.base_url}/wubi/category/add-category'
        payload = {
            'name': name
        }
        try:
            # 使用session对象发送请求，保持认证状态
            response = self.session.post(
                url, 
                json=payload, 
                headers=self._get_headers(),
                verify=self.verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"添加类别失败: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求失败: {str(e)}")

    def get_category(self)->list:
        """获取类别"""
        #
        # curl -H "Host: localhost:3000" -H "Accept: application/json, text/plain, */*" -H "Diary-Token: $2b$10$/1ks3X5Q48Vvr0wmfrbU9edHb/FlF6YQE0sRdhgEeuguIM5AtCnh." -H "Diary-Uid: 10" -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) wubi-dict-editor/1.3.0 Chrome/112.0.5615.204 Electron/24.8.8 Safari/537.36" -H "Accept-Language: zh-CN" -H "If-None-Match: W/\"31-kyIYhrSCKT4wRcOilsNigsF8Lsk\"" --compressed "http://localhost:3000/portal/wubi/category/list"
        #
        # 更新请求地址为正确的地址
        url = f'{self.base_url}/wubi/category/list'
        
        try:
            # 使用session对象发送请求，保持认证状态
            response = self.session.get(
                url, 
                headers=self._get_headers(),
                verify=self.verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                # print(f"获取类别响应数据: {data}")
                if data['success']:
                    # print("获取类别成功")
                    return data['data']
                else:
                    print(f"获取类别失败: {data['message']}")
                    return []
            else:
                print(f"获取类别请求失败: {response.status_code} ")
                return []
        except requests.exceptions.RequestException as e:
            print(f"获取类别网络请求失败: {str(e)}")
            return []
    
    def delete_category(self, name: str)-> dict:
        """删除类别"""
        url = f'{self.base_url}/wubi/category/delete-category'
        payload = {
            'name': name
        }
        
        try:
            # 使用session对象发送请求，保持认证状态
            response = self.session.delete(
                url, 
                json=payload, 
                headers=self._get_headers(),
                verify=self.verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"删除类别失败: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求失败: {str(e)}")

if __name__ == '__main__':
    try:
        api = APIClient('test@163.com', 'test')
        # result = api.get_category()
        # print(f"   get_category方法调用结果: {result}")
        # print(f"   结果类型: {type(result)}")
        # add_result = api.add_category('测试类别')
        # print(f"   add_category方法调用结果: {add_result}")
        # result = api.get_category()
        # print(f"   get_category方法调用结果: {result}")
        # delete_result = api.delete_category('测试类别')
        # print(f"   delete_category方法调用结果: {delete_result}")
        # result1 = api.get_category()
        # print(f"   get_category方法调用结果: {result1}")
        result2 = api.get_words()
        print(f"   get_category方法调用结果: {result2}")
        # result3 = api.add_words({"category_id":10,"words":[{"id":1112,"code":"wyth111","word":"浠111ょ墝","priority":"","note":"","indicator":""},{"id":11112,"code":"wyth1111","word":"浠1111ょ墝","priority":"","note":"","indicator":""}]})
        # print(f"   add_words方法调用结果: {result3}")

    except Exception as e:
        print(f"   get_category方法调用失败: {str(e)}")
