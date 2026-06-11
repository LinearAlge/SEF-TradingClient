"""
功能1：登录与证书管理（实验大纲 4.1）

测试范围：
- 正确/错误账号密码登录
- 空参数校验
- 登录返回 investorId/fundAccountId/securityAccountId
- 客户端权限申请与查询
- 证书重绑身份校验
"""

import pytest
from conftest import api_request, TEST_ACCOUNT


class TestLogin:
    """登录基础功能"""

    def test_valid_login_returns_action(self, client):
        """TC-1.1 正确的账号密码登录 → 返回 ok=true 含 action"""
        status, data = api_request("POST", "/auth/login", {
            "account": TEST_ACCOUNT["account"],
            "password": TEST_ACCOUNT["trade_password"],
        })
        assert status == 200
        assert data["ok"] is True
        assert "action" in data

    def test_login_returns_account_ids(self, client):
        """TC-1.1a 登录成功返回 investorId、fundAccountId、securityAccountId"""
        status, data = api_request("POST", "/auth/login", {
            "account": TEST_ACCOUNT["account"],
            "password": TEST_ACCOUNT["trade_password"],
        })
        assert status == 200
        assert data["ok"] is True
        # 重构后新增字段
        assert data.get("fundAccountId") == TEST_ACCOUNT["fund_account_id"]
        assert data.get("securityAccountId") == TEST_ACCOUNT["security_account_id"]

    def test_wrong_password_rejected(self, client):
        """TC-1.2 错误密码 → 登录失败"""
        status, data = api_request("POST", "/auth/login", {
            "account": TEST_ACCOUNT["account"],
            "password": "wrong_password_999",
        })
        assert data["ok"] is False

    def test_empty_account_rejected(self, client):
        """TC-1.3 空账号 → 参数错误"""
        status, data = api_request("POST", "/auth/login", {
            "account": "",
            "password": "123456",
        })
        # 空账号可能返回 400 或 200+ok=false
        assert status >= 400 or data["ok"] is False

    def test_empty_password_rejected(self, client):
        """TC-1.4 空密码 → 参数错误"""
        status, data = api_request("POST", "/auth/login", {
            "account": "admin",
            "password": "",
        })
        assert status >= 400 or data["ok"] is False

    def test_get_account_profile(self, client):
        """TC-1.5 查询账户信息 GET /auth/me"""
        status, data = api_request("GET", "/auth/me?account=admin")
        assert status == 200
        assert data["ok"] is True
        assert "user" in data


class TestApplyAccess:
    """客户端权限申请"""

    def test_apply_client_access(self, client):
        """TC-1.6 申请客户端权限 → approved 或提示已开通"""
        status, data = api_request("POST", "/client/applications", {
            "account": TEST_ACCOUNT["account"],
            "password": TEST_ACCOUNT["trade_password"],
            "name": "admin",
            "phone": TEST_ACCOUNT["phone"],
            "idNumber": TEST_ACCOUNT["id_number"],
        })
        # 可以返回 approved 或 "账户已开通客户端权限"
        assert status < 500

    def test_list_applications(self, client):
        """TC-1.7 查询申请记录"""
        status, data = api_request("GET", "/client/applications?account=admin")
        assert status == 200
        assert data["ok"] is True
        assert "applications" in data


class TestRebind:
    """证书重绑"""

    def test_rebind_wrong_phone_rejected(self, client):
        """TC-1.8 证书重绑——手机号不匹配 → 身份校验失败"""
        status, data = api_request("POST", "/auth/rebind", {
            "account": TEST_ACCOUNT["account"],
            "password": TEST_ACCOUNT["trade_password"],
            "phone": "13900000000",  # 错误的手机号
            "idNumber": TEST_ACCOUNT["id_number"],
        })
        assert data["ok"] is False
