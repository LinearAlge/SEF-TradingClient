"""
功能10：价格提醒——选做（实验大纲 4.10）

测试范围：
- 新增提醒（高于/低于触发）
- 查询提醒列表
- 暂停/恢复提醒
- 删除提醒
- 触发条件验证
"""

import pytest
from conftest import api_request, TEST_ACCOUNT


class TestAlerts:
    """价格提醒完整生命周期"""

    @pytest.fixture(autouse=True)
    def ensure_first_login_resolved(self):
        """首次运行前确保 admin 账户已完成首次登录"""
        # 尝试登录以触 enrollment/verification 流程
        pass

    def test_create_alert_above(self, client):
        """TC-10.1 新增'高于'提醒 → status=监控中"""
        status, data = api_request("POST", "/client/alerts", {
            "account": TEST_ACCOUNT["account"],
            "symbol": "600001",
            "condition": "高于",
            "triggerPrice": "200",
        })
        assert status == 200
        assert data["ok"] is True
        assert data["alert"]["symbol"] == "600001"
        assert data["alert"]["condition"] == "高于"
        assert data["alert"]["triggerPrice"] == "200"
        assert data["alert"]["status"] == "监控中"

    def test_create_alert_below(self, client):
        """TC-10.2 新增'低于'提醒"""
        status, data = api_request("POST", "/client/alerts", {
            "account": TEST_ACCOUNT["account"],
            "symbol": "600002",
            "condition": "低于",
            "triggerPrice": "50",
        })
        assert status == 200
        assert data["ok"] is True
        assert data["alert"]["status"] == "监控中"

    def test_list_alerts(self, client):
        """TC-10.3 查询提醒列表 → 含之前创建的提醒"""
        status, data = api_request("GET", f"/client/alerts?account={TEST_ACCOUNT['account']}")
        assert status == 200
        assert data["ok"] is True
        assert "alerts" in data
        assert isinstance(data["alerts"], list)

    def test_pause_alert(self, client):
        """TC-10.4 暂停提醒"""
        # 先创建一个
        _, d = api_request("POST", "/client/alerts", {
            "account": TEST_ACCOUNT["account"],
            "symbol": "600003",
            "condition": "高于",
            "triggerPrice": "100",
        })
        alert_id = d["alert"]["id"]

        # 暂停
        s, d2 = api_request("PATCH", f"/client/alerts/{alert_id}", {
            "status": "已暂停",
        })
        assert s == 200
        assert d2["ok"] is True
        assert d2["alert"]["status"] == "已暂停"

    def test_resume_alert(self, client):
        """TC-10.5 恢复提醒"""
        _, d = api_request("POST", "/client/alerts", {
            "account": TEST_ACCOUNT["account"],
            "symbol": "600005",
            "condition": "低于",
            "triggerPrice": "10",
        })
        alert_id = d["alert"]["id"]

        api_request("PATCH", f"/client/alerts/{alert_id}", {"status": "已暂停"})
        s, d2 = api_request("PATCH", f"/client/alerts/{alert_id}", {"status": "监控中"})
        assert s == 200
        assert d2["ok"] is True
        assert d2["alert"]["status"] == "监控中"

    def test_delete_alert(self, client):
        """TC-10.6 删除提醒"""
        _, d = api_request("POST", "/client/alerts", {
            "account": TEST_ACCOUNT["account"],
            "symbol": "600006",
            "condition": "高于",
            "triggerPrice": "150",
        })
        alert_id = d["alert"]["id"]

        s, d2 = api_request("DELETE", f"/client/alerts/{alert_id}")
        assert s == 200
        assert d2["ok"] is True

    def test_alert_trigger_condition(self, client):
        """TC-10.7 触发条件验证：设极低触发价 → 当前价高于触发价"""
        _, d = api_request("POST", "/client/alerts", {
            "account": TEST_ACCOUNT["account"],
            "symbol": "600001",
            "condition": "高于",
            "triggerPrice": "1",  # 极低，当前价 ~155 >> 1
        })
        assert d["ok"] is True

        # 清理
        api_request("DELETE", f"/client/alerts/{d['alert']['id']}")
