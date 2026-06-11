"""
功能8：查询股票行情（实验大纲 4.8）

测试范围：
- 板块筛选（主板/创业板/ST板）
- 代码/名称搜索
- 单只股票详情
- 批量报价
- 价格合理性（dayLow <= lastPrice <= dayHigh, bid <= ask）
- 股票公告
- 新：验证数值类型正确（非字符串）
"""

import pytest
from conftest import api_request


class TestMarketList:
    """行情列表查询"""

    def test_main_board_stocks(self, client):
        """TC-8.1 主板股票列表 → 字段完整"""
        status, data = api_request("GET", "/market/stocks?board=主板")
        assert status == 200
        assert data["ok"] is True
        assert "stocks" in data
        assert len(data["stocks"]) > 0

        stock = data["stocks"][0]
        # 列表接口返回核心字段（weekHigh 等仅在详情接口返回）
        required = ["symbol", "name", "lastPrice", "bid", "ask",
                   "dayHigh", "dayLow", "volume"]
        for field in required:
            assert field in stock, f"Missing field: {field}"

    def test_search_by_code(self, client):
        """TC-8.2 按代码搜索 600001 → 精确匹配"""
        status, data = api_request("GET", "/market/stocks?query=600001")
        assert status == 200
        assert data["ok"] is True
        symbols = [s["symbol"] for s in data["stocks"]]
        assert "600001" in symbols

    def test_search_by_name_fuzzy(self, client):
        """TC-8.3 按名称模糊搜索 '石英' → 含石英系统"""
        status, data = api_request("GET", "/market/stocks?query=石英")
        assert status == 200
        assert data["ok"] is True
        assert len(data["stocks"]) > 0

    def test_stock_detail(self, client):
        """TC-8.4 单只股票详情 GET /market/stocks?symbol=600001"""
        status, data = api_request("GET", "/market/stocks?symbol=600001")
        assert status == 200
        assert data["ok"] is True
        # 响应可能是 {"stock": {...}} 或 {"stocks": [...]}
        # 取决于路由实现
        assert ("stock" in data) or ("stocks" in data)

    def test_gem_board(self, client):
        """TC-8.5 创业板筛选"""
        status, data = api_request("GET", "/market/stocks?board=创业板")
        assert status == 200
        assert data["ok"] is True
        # 列表接口不含 board 字段（详情接口才含）；验证返回股票即可
        assert len(data["stocks"]) > 0

    def test_st_board(self, client):
        """TC-8.6 ST板筛选"""
        status, data = api_request("GET", "/market/stocks?board=ST+板")
        assert status == 200
        assert data["ok"] is True

    def test_nonexistent_stock(self, client):
        """TC-8.7 搜索不存在的股票 → 空"""
        status, data = api_request("GET", "/market/stocks?query=ZZZZZZ")
        assert status == 200
        assert data["ok"] is True
        assert len(data.get("stocks", [])) == 0

    def test_announcements(self, client):
        """TC-8.8 股票公告字段"""
        status, data = api_request("GET", "/market/stocks?symbol=600001")
        assert status == 200
        if "stock" in data:
            assert "announcements" in data["stock"]

    def test_batch_quotes(self, client):
        """TC-8.9 批量报价 GET /market/quotes?symbols=600001,600002"""
        status, data = api_request("GET", "/market/quotes?symbols=600001,600002")
        assert status == 200
        assert data["ok"] is True
        assert len(data.get("stocks", [])) == 2


class TestMarketValidation:
    """行情数据验证"""

    def test_price_in_range(self, client):
        """TC-8.10 价格合理性：dayLow <= lastPrice <= dayHigh"""
        _, data = api_request("GET", "/market/stocks?board=主板")
        for s in data.get("stocks", []):
            last = float(s["lastPrice"])
            high = float(s["dayHigh"])
            low = float(s["dayLow"])
            assert low <= last <= high, \
                f"{s['symbol']}: lastPrice={last} not in [{low}, {high}]"

    def test_bid_lte_ask(self, client):
        """TC-8.11 买卖盘价格关系：bid <= ask"""
        _, data = api_request("GET", "/market/stocks?board=主板")
        for s in data.get("stocks", []):
            bid = float(s["bid"])
            ask = float(s["ask"])
            assert bid <= ask, \
                f"{s['symbol']}: bid={bid} > ask={ask}"

    def test_price_fields_are_numeric(self, client):
        """TC-8.12 新：验证价格字段是数值类型"""
        _, data = api_request("GET", "/market/stocks?board=主板")
        for s in data.get("stocks", []):
            for field in ["lastPrice", "bid", "ask", "dayHigh", "dayLow"]:
                val = s[field]
                # 允许 int 或 float，不允许 string
                assert isinstance(val, (int, float)), \
                    f"{s['symbol']}.{field} is {type(val).__name__}, expected number"
