from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_auth import router as auth_router
from app.api.routes_billing import router as billing_router
from app.api.routes_brands import router as brands_router
from app.api.routes_geo import router as geo_router
from app.api.routes_health import router as health_router
from app.api.routes_reports import router as reports_router
from app.api.routes_workspaces import router as workspaces_router
from app.core.config import settings
from app.db import Base, models  # noqa: F401
from app.db.session import engine

app = FastAPI(title=settings.app_name)

app.add_middleware(
	CORSMiddleware,
	allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
	Base.metadata.create_all(bind=engine)


app.include_router(health_router)
app.include_router(auth_router)
app.include_router(workspaces_router)
app.include_router(brands_router)
app.include_router(geo_router)
app.include_router(reports_router)
app.include_router(billing_router)
