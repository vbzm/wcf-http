import pytest
import requests
import json
import os
from typing import Dict

# 测试配置
BASE_URL = "http://localhost:9999"  # 测试服务器地址
TEST_ROOM_ID = "48398681165@chatroom"  # 测试群ID
TEST_WXID = "filehelper"  # 测试用户ID
TEST_FILE_PATH = os.path.join(os.path.dirname(__file__), "test_files")  # 测试文件目录

# 创建测试文件目录
os.makedirs(TEST_FILE_PATH, exist_ok=True)

class TestCoreHttp:
    """WeChatFerry HTTP API 测试类"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """测试前置设置"""
        # 确保服务器在运行
        try:
            response = requests.get(f"{BASE_URL}/login")
            assert response.status_code == 200
        except:
            pytest.skip("测试服务器未启动")
            
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """发送HTTP请求并返回JSON响应"""
        url = f"{BASE_URL}/{endpoint.lstrip('/')}"
        response = requests.request(method, url, **kwargs)
        return response.json()
    
    # 用户认证相关测试
    def test_login_status(self):
        """测试获取登录状态"""
        response = self._make_request("GET", "/login")
        assert "status" in response
        assert "message" in response
        assert "data" in response
        assert "login" in response["data"]
        
    def test_get_wxid(self):
        """测试获取当前用户wxid"""
        response = self._make_request("GET", "/wxid")
        assert response["status"] == 0
        assert "wxid" in response["data"]
        
    def test_get_user_info(self):
        """测试获取用户信息"""
        response = self._make_request("GET", "/user-info")
        assert response["status"] == 0
        assert "ui" in response["data"]
        
    # 消息相关测试
    def test_send_text(self):
        """测试发送文本消息"""
        data = {
            "msg": "测试消息",
            "receiver": "filehelper",
            "aters": ""
        }
        response = self._make_request("POST", "/text", json=data)
        assert response["status"] == 0
        
    def test_send_text_with_at(self):
        """测试发送@消息"""
        data = {
            "msg": "测试@消息 @test",
            "receiver": TEST_ROOM_ID,
            "aters": TEST_WXID
        }
        response = self._make_request("POST", "/text", json=data)
        assert response["status"] == 0
        
    def test_send_image(self):
        """测试发送图片"""
        # 创建测试图片
        test_image = os.path.join(TEST_FILE_PATH, "test.png")
        with open(test_image, "wb") as f:
            f.write(b"test image content")
            
        data = {
            "path": test_image,
            "receiver": "filehelper"
        }
        response = self._make_request("POST", "/image", json=data)
        assert response["status"] == 0
        
    def test_send_file(self):
        """测试发送文件"""
        # 创建测试文件
        test_file = os.path.join(TEST_FILE_PATH, "test.txt")
        with open(test_file, "w") as f:
            f.write("test file content")
            
        data = {
            "path": test_file,
            "receiver": "filehelper"
        }
        response = self._make_request("POST", "/file", json=data)
        assert response["status"] == 0
        
    # 群聊相关测试
    def test_get_chatroom_members(self):
        """测试获取群成员"""
        response = self._make_request("GET", f"/chatroom-member?roomid={TEST_ROOM_ID}")
        assert response["status"] == 0
        assert "members" in response["data"]
        
    def test_add_chatroom_members(self):
        """测试添加群成员"""
        data = {
            "roomid": TEST_ROOM_ID,
            "wxids": TEST_WXID
        }
        response = self._make_request("POST", "/chatroom-member", json=data)
        assert response["status"] in [0, 1]  # 0或1都表示成功
        
    # 通讯录相关测试
    def test_get_contacts(self):
        """测试获取通讯录"""
        response = self._make_request("GET", "/contacts")
        assert response["status"] == 0
        assert "contacts" in response["data"]
        
    def test_get_friends(self):
        """测试获取好友列表"""
        response = self._make_request("GET", "/friends")
        assert response["status"] == 0
        assert "friends" in response["data"]
        
    # 数据库相关测试
    def test_get_dbs(self):
        """测试获取数据库列表"""
        response = self._make_request("GET", "/dbs")
        assert response["status"] == 0
        assert "dbs" in response["data"]
        
    def test_get_tables(self):
        """测试获取数据库表"""
        # 先获取一个可用的数据库
        dbs_response = self._make_request("GET", "/dbs")
        if dbs_response["data"]["dbs"]:
            db_name = dbs_response["data"]["dbs"][0]
            response = self._make_request("GET", f"/{db_name}/tables")
            assert response["status"] == 0
            assert "tables" in response["data"]
            
    def test_execute_sql(self):
        """测试执行SQL查询"""
        data = {
            "db": "MicroMsg.db",
            "sql": "SELECT * FROM sqlite_master LIMIT 1;"
        }
        response = self._make_request("POST", "/sql", json=data)
        assert response["status"] == 0
        assert "bs64" in response["data"]
        
    # 其他接口测试
    def test_get_msg_types(self):
        """测试获取消息类型"""
        response = self._make_request("GET", "/msg-types")
        assert response["status"] == 0
        assert "types" in response["data"]
        
    def test_callback_url(self):
        """测试回调URL的获取和设置"""
        # 测试获取
        get_response = self._make_request("GET", "/callback")
        assert "callback" in get_response
        
        # 测试设置
        set_data = {"callback": "http://test.callback.url"}
        set_response = self._make_request("POST", "/callback", json=set_data)
        assert "callback" in set_response
        assert set_response["callback"] == set_data["callback"]
        
    @classmethod
    def teardown_class(cls):
        """测试清理工作"""
        # 清理测试文件
        import shutil
        if os.path.exists(TEST_FILE_PATH):
            shutil.rmtree(TEST_FILE_PATH) 
