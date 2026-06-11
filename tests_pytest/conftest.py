"""
测试基础设施

Base URL: http://localhost:8000/api/client (FastAPI unified backend)

使用前确保已启动后端:
    python -m uvicorn backend_fastapi.main:app --port 8000

测试账号（来自 backend_fastapi/mock_modules/data/mock-funds-db.json）：
    账号: admin
    交易密码: 123456
    取款密码: 654321
    手机号: 13800000000
    身份证号: 110101199001011234
    资金账户ID: FUND000001
    证券账户ID: SEC000001
"""

import json
import os
import subprocess
import sys
import time
from typing import Any, Dict, Optional, Tuple

import httpx
import pytest


# ── 配置常量 ──────────────────────────────────────────

BASE_URL = "http://localhost:8000/api/client"

TEST_ACCOUNT = {
    "account": "admin",
    "trade_password": "123456",
    "withdraw_password": "654321",
    "phone": "13800000000",
    "id_number": "110101199001011234",
    "fund_account_id": "FUND000001",
    "security_account_id": "SEC000001",
}


# ── HTTP 请求辅助 ──────────────────────────────────────

def api_request(
    method: str,
    path: str,
    body: Optional[Dict[str, Any]] = None,
    timeout: float = 15.0,
) -> Tuple[int, Dict[str, Any]]:
    """发送 HTTP 请求到客户端网关。

    Args:
        method: HTTP 方法 (GET/POST/PATCH/DELETE)
        path: API 路径 (如 /auth/login, /account/funds?account=admin)
        body: JSON 请求体（仅 POST/PATCH 使用）
        timeout: 超时秒数

    Returns:
        (status_code, response_json_dict)
    """
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}

    try:
        if method == "GET":
            resp = httpx.get(url, headers=headers, timeout=timeout)
        elif method == "POST":
            resp = httpx.post(url, json=body, headers=headers, timeout=timeout)
        elif method == "PATCH":
            resp = httpx.patch(url, json=body, headers=headers, timeout=timeout)
        elif method == "DELETE":
            resp = httpx.delete(url, headers=headers, timeout=timeout)
        else:
            raise ValueError(f"Unsupported method: {method}")

        data = resp.json() if resp.text else {}
        return resp.status_code, data
    except httpx.TimeoutException:
        return 0, {"ok": False, "message": "Request timeout"}
    except httpx.ConnectError:
        return 0, {"ok": False, "message": "Backend not reachable — start FastAPI with: python -m uvicorn backend_fastapi.main:app --port 8000"}
    except Exception as e:
        return 0, {"ok": False, "message": str(e)}


def unique_id(prefix: str = "TEST") -> str:
    """生成唯一标识，避免测试数据冲突。"""
    import random
    return f"{prefix}-{int(time.time() * 1000)}-{random.randint(0, 9999)}"


# ── Fixtures ───────────────────────────────────────────

@pytest.fixture(scope="session")
def backend_ready():
    """会话级别的 fixture：检查后端是否可访问。"""
    status, data = api_request("GET", "/../health", timeout=5.0)
    # 使用根路径的 health endpoint
    try:
        resp = httpx.get("http://localhost:8000/health", timeout=5.0)
        if resp.status_code == 200:
            return True
    except Exception:
        pass

    pytest.exit(
        "\n❌ Backend not reachable at http://localhost:8000\n"
        "   Start it with: python -m uvicorn backend_fastapi.main:app --port 8000",
        returncode=1,
    )


@pytest.fixture
def client(backend_ready):
    """每个测试的 fixture：验证后端可达。"""
    return backend_ready
