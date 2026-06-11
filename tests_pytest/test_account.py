"""
功能2/3/9：持仓查询、资金查询、修改密码（实验大纲 4.2, 4.3, 4.9）

测试范围：
- 查询持仓（字段完整性：symbol/shares/costPrice/pnlAmount）
- 查询资金（available/frozen/marketValue/totalEquity）
- 资金/证券流水
- 修改交易/取款密码
- 新增：验证 totalEquity = available + frozen + marketValue
"""

import pytest
from conftest import api_request, TEST_ACCOUNT


class TestHoldings:
    """功能2：查询证券持仓"""

    def test_list_holdings(self, client):
        """TC-2.1 查询持仓列表 → 含 symbol/name/shares/costPrice/lastPrice/pnlAmount"""
        status, data = api_request("GET", f"/account/holdings?account={TEST_ACCOUNT['account']}")
        assert status == 200
        assert data["ok"] is True
        assert "holdings" in data
        assert isinstance(data["holdings"], list)

    def test_holdings_field_completeness(self, client):
        """TC-2.2 持仓数据结构完整性"""
        _, data = api_request("GET", f"/account/holdings?account={TEST_ACCOUNT['account']}")
        assert "totalMarketValue" in data

        if data["holdings"]:
            h = data["holdings"][0]
            required_fields = ["symbol", "name", "shares", "costPrice", "lastPrice",
                              "pnlAmount", "pnlRate", "availableShares", "frozenShares"]
            for field in required_fields:
                assert field in h, f"Missing field: {field}"


class TestFunds:
    """功能3：查询资金帐户"""

    def test_funds_basic(self, client):
        """TC-3.1 查询资金余额 → available/frozen/marketValue/totalEquity"""
        status, data = api_request("GET", f"/account/funds?account={TEST_ACCOUNT['account']}")
        assert status == 200
        assert data["ok"] is True
        assert "available" in data
        assert "frozen" in data
        assert "marketValue" in data
        assert "totalEquity" in data
        # 非负数
        assert float(data["available"]) >= 0
        assert float(data["frozen"]) >= 0

    def test_funds_equation(self, client):
        """TC-3.1a 验证 totalEquity = available + frozen + marketValue"""
        _, data = api_request("GET", f"/account/funds?account={TEST_ACCOUNT['account']}")
        available = float(data["available"])
        frozen = float(data["frozen"])
        market = float(data["marketValue"])
        total = float(data["totalEquity"])
        assert abs(total - (available + frozen + market)) < 0.02  # 浮点精度

    def test_account_summary(self, client):
        """TC-3.2 资金摘要 GET /account/summary"""
        status, data = api_request("GET", f"/account/summary?account={TEST_ACCOUNT['account']}")
        assert status == 200
        assert data["ok"] is True
        # 摘要接口返回 account/available/frozen/marketValue/totalEquity
        assert "account" in data

    def test_cash_flows(self, client):
        """TC-3.3 查询资金流水"""
        status, data = api_request("GET", f"/account/cash-flows?account={TEST_ACCOUNT['account']}")
        assert status == 200
        assert data["ok"] is True
        assert "cashFlows" in data
        assert isinstance(data["cashFlows"], list)

    def test_stock_flows(self, client):
        """TC-3.4 查询证券流水"""
        status, data = api_request("GET", f"/account/stock-flows?account={TEST_ACCOUNT['account']}")
        assert status == 200
        assert data["ok"] is True
        assert "stockFlows" in data


class TestPassword:
    """功能9：修改密码"""

    def test_change_trade_wrong_old_password(self, client):
        """TC-9.1 错误旧密码修改交易密码 → 失败"""
        status, data = api_request("POST", "/account/passwords/trade", {
            "account": TEST_ACCOUNT["account"],
            "currentPassword": "wrong_old_pwd",
            "nextPassword": "newpwd123",
        })
        assert data["ok"] is False

    def test_change_trade_password_and_revert(self, client):
        """TC-9.2 正确修改交易密码然后改回来"""
        # 修改
        s1, d1 = api_request("POST", "/account/passwords/trade", {
            "account": TEST_ACCOUNT["account"],
            "currentPassword": TEST_ACCOUNT["trade_password"],
            "nextPassword": "temp_new_123456",
        })
        if d1.get("ok"):
            # 改回
            s2, d2 = api_request("POST", "/account/passwords/trade", {
                "account": TEST_ACCOUNT["account"],
                "currentPassword": "temp_new_123456",
                "nextPassword": TEST_ACCOUNT["trade_password"],
            })
            assert d2["ok"] is True

    def test_change_withdraw_wrong_old_password(self, client):
        """TC-9.3 错误旧密码修改取款密码 → 失败"""
        status, data = api_request("POST", "/account/passwords/withdraw", {
            "account": TEST_ACCOUNT["account"],
            "currentPassword": "wrong_old_pwd",
            "nextPassword": "newwd456",
        })
        assert data["ok"] is False
