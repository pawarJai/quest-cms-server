from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os
from app.routes import auth_routes
from app.routes.upload_routes import router as upload_router
from app.routes.product_routes import router as product_router
from app.routes.notification_routes import router as notification_router
from app.routes.industry_routes import router as industry_router
from app.routes.client_routes import router as client_router
from app.routes.certificate_routes import router as cert_router
from app.routes.news_routes import router as news_router
from app.routes.about_routes import router as about_router
from app.routes.file_url_routes import router as file_url_router
from app.routes.quote_routes import router as quote_router

app = FastAPI(title="User Management API")

# ✔ FINAL WORKING CORS CONFIG
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://quest-crm.onrender.com",
        "https://quest-crm-admin-panel.netlify.app",
        "https://qfc-eta.vercel.app/",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(upload_router)
app.include_router(product_router)
app.include_router(notification_router)
app.include_router(industry_router)
app.include_router(client_router)
app.include_router(cert_router)
app.include_router(about_router)
app.include_router(news_router)
app.include_router(file_url_router)
app.include_router(quote_router)
uploads_dir_str = os.environ.get("UPLOADS_DIR")
uploads_root = (
    Path(uploads_dir_str)
    if uploads_dir_str
    else (Path(__file__).resolve().parents[1] / "uploads")
)
uploads_root.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_root)), name="uploads")


def main():
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
