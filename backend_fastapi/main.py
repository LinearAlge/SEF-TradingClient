from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend_fastapi.client.router import router as client_router
from backend_fastapi.core.request_context import request_id_middleware
from backend_fastapi.mock_modules.account_router import router as account_router
from backend_fastapi.mock_modules.trade_router import router as trade_router
from backend_fastapi.mock_modules.info_router import router as info_router
from backend_fastapi.mock_modules.admin_router import router as admin_router
from backend_fastapi.mock_modules.market_updater import start_market_updater
from backend_fastapi.mock_modules.seed_data import seed_defaults


def create_app() -> FastAPI:
    app = FastAPI(title="TradingClient Unified Backend", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.middleware("http")(request_id_middleware)

    app.include_router(client_router, prefix="/api/client", tags=["client"])
    app.include_router(account_router, prefix="/api/v1/account", tags=["account-mock"])
    app.include_router(trade_router, prefix="/api/v1/trade", tags=["trade-mock"])
    app.include_router(info_router, prefix="/api/v1/info", tags=["info-mock"])
    app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin-mock"])

    @app.get("/health")
    def health() -> dict:
        return {"service": "client-unified", "status": "UP"}

    return app


app = create_app()


@app.on_event("startup")
def _seed_data() -> None:
    seed_defaults()
    start_market_updater()
