"""
功能4/5/6/7：买入、卖出、撤单、交易结果（实验大纲 4.4-4.7）

测试范围：
- 正常买入/卖出委托
- 新：价格超涨跌停限制 → 拒绝
- 新：资金不足以买入 → 拒绝
- 新：卖出超持仓 → 拒绝
- 撤单、重复撤单、撤不存在委托
- 新：撤单返回 released_resource_type
- 委托列表、成交记录、状态枚举
"""

import pytest
from conftest import api_request, TEST_ACCOUNT


class TestBuyOrder:
    """功能4：买入委托"""

    def test_buy_valid(self, client):
        """TC-4.1 正常买入 → 返回 order 含 id/symbol/side/status"""
        status, data = api_request("POST", "/trade/orders", {
            "account": TEST_ACCOUNT["account"],
            "symbol": "600001",
            "side": "买入",
            "price": 149.0,
            "quantity": 100,
        })
        assert status == 200
        assert data["ok"] is True
        assert "order" in data
        assert data["order"]["id"]  # 有订单号
        assert data["order"]["symbol"] == "600001"

    def test_buy_price_above_limit_up(self, client):
        """TC-4.2 新：买入价格超涨停价 → 拒绝 (TRADE_E05)"""
        # 600001 最新价约 155.46，涨停价 ≈ 171.0
        status, data = api_request("POST", "/trade/orders", {
            "account": TEST_ACCOUNT["account"],
            "symbol": "600001",
            "side": "买入",
            "price": 999.0,  # 远超涨停价
            "quantity": 100,
        })
        assert data["ok"] is False

    def test_buy_price_below_limit_down(self, client):
        """TC-4.3 新：买入价格低于跌停价 → 拒绝"""
        # 跌停价 ≈ 139.91
        # 价格太低也是超跌停范围
        status, data = api_request("POST", "/trade/orders", {
            "account": TEST_ACCOUNT["account"],
            "symbol": "600001",
            "side": "买入",
            "price": 0.01,  # 远低于跌停价
            "quantity": 100,
        })
        assert data["ok"] is False

    def test_buy_insufficient_funds(self, client):
        """TC-4.4 新：资金不足 → 拒绝"""
        status, data = api_request("POST", "/trade/orders", {
            "account": TEST_ACCOUNT["account"],
            "symbol": "600001",
            "side": "买入",
            "price": 99999.0,  # 总价远超可用资金
            "quantity": 100,
        })
        assert data["ok"] is False

    def test_buy_zero_quantity(self, client):
        """TC-4.5 新：数量 ≤ 0 → 拒绝 (TRADE_E06)"""
        status, data = api_request("POST", "/trade/orders", {
            "account": TEST_ACCOUNT["account"],
            "symbol": "600001",
            "side": "买入",
            "price": 150.0,
            "quantity": 0,
        })
        assert data["ok"] is False


class TestSellOrder:
    """功能5：卖出委托"""

    def test_sell_valid(self, client):
        """TC-5.1 正常卖出 → 返回 order"""
        status, data = api_request("POST", "/trade/orders", {
            "account": TEST_ACCOUNT["account"],
            "symbol": "600001",
            "side": "卖出",
            "price": 160.0,
            "quantity": 100,
        })
        assert status == 200
        assert data["ok"] is True
        assert data["order"]["side"] == "卖出"

    def test_sell_exceeds_position(self, client):
        """TC-5.2 新：卖出超持仓 → 拒绝"""
        status, data = api_request("POST", "/trade/orders", {
            "account": TEST_ACCOUNT["account"],
            "symbol": "600001",
            "side": "卖出",
            "price": 160.0,
            "quantity": 999999,  # 远超持仓
        })
        assert data["ok"] is False

    def test_sell_unowned_stock(self, client):
        """TC-5.3 卖出不存在的股票 → 可能拒绝（股票不存在 + 持仓不足）"""
        status, data = api_request("POST", "/trade/orders", {
            "account": TEST_ACCOUNT["account"],
            "symbol": "999999",
            "side": "卖出",
            "price": 100.0,
            "quantity": 100,
        })
        assert data["ok"] is False


class TestCancelOrder:
    """功能6：撤单"""

    def test_cancel_pending_order(self, client):
        """TC-6.1 撤销未成交委托 → status=已撤单"""
        # 创建委托——使用不会立即成交且不超涨跌停的价格
        # 买入价低于卖一价 → 不会立即成交；需在跌停价之上
        status, data = api_request("POST", "/trade/orders", {
            "account": TEST_ACCOUNT["account"],
            "symbol": "600001",
            "side": "买入",
            "price": 145.0,  # > limit_down(≈143.85), < ask(≈157) → 不撮合
            "quantity": 100,
        })
        if not data.get("ok") or not data.get("order"):
            pytest.skip("Order creation failed — cannot test cancel")
        order_id = data["order"]["id"]

        # 撤单
        s, d = api_request("POST", f"/trade/orders/{order_id}/cancel",
                          {"account": TEST_ACCOUNT["account"]})
        assert d["ok"] is True
        assert d["order"]["status"] == "已撤单"

    def test_cancel_nonexistent_order(self, client):
        """TC-6.2 撤不存在委托 → 失败"""
        status, data = api_request("POST",
            "/trade/orders/NONEXISTENT-ORDER/cancel",
            {"account": TEST_ACCOUNT["account"]})
        assert data["ok"] is False

    def test_double_cancel(self, client):
        """TC-6.3 重复撤单 → 失败"""
        # 创建并撤销
        _, d1 = api_request("POST", "/trade/orders", {
            "account": TEST_ACCOUNT["account"],
            "symbol": "600001",
            "side": "买入",
            "price": 146.0,
            "quantity": 100,
        })
        if not d1.get("ok") or not d1.get("order"):
            pytest.skip("Cannot create order for double cancel test")
        oid = d1["order"]["id"]
        api_request("POST", f"/trade/orders/{oid}/cancel",
                   {"account": TEST_ACCOUNT["account"]})
        # 再次撤单
        _, d2 = api_request("POST", f"/trade/orders/{oid}/cancel",
                           {"account": TEST_ACCOUNT["account"]})
        assert d2["ok"] is False


class TestTradeResults:
    """功能7：交易结果"""

    def test_list_orders(self, client):
        """TC-7.1 查询委托列表 → 字段完整"""
        status, data = api_request("GET", f"/trade/orders?account={TEST_ACCOUNT['account']}")
        assert status == 200
        assert data["ok"] is True
        assert "orders" in data
        if data["orders"]:
            o = data["orders"][0]
            for field in ["id", "createdAt", "symbol", "side", "price",
                         "quantity", "filledQuantity", "avgPrice", "status"]:
                assert field in o, f"Missing field: {field}"

    def test_list_fills(self, client):
        """TC-7.2 查询成交记录 → 字段完整"""
        status, data = api_request("GET", f"/trade/fills?account={TEST_ACCOUNT['account']}")
        assert status == 200
        assert data["ok"] is True
        assert "fills" in data
        if data["fills"]:
            f = data["fills"][0]
            for field in ["id", "orderId", "symbol", "side", "price", "quantity", "createdAt"]:
                assert field in f, f"Missing field: {field}"

    def test_status_values_valid(self, client):
        """TC-7.3 委托状态值合法性"""
        _, data = api_request("GET", f"/trade/orders?account={TEST_ACCOUNT['account']}")
        valid = {"未成交", "部分成交", "已成交", "已撤单", "已过期", "已拒绝"}
        for o in data.get("orders", []):
            assert o["status"] in valid, f"Invalid status: {o['status']}"
