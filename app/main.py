from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth_routes
from app.routes.upload_routes import router as upload_router
from app.routes.product_routes import router as product_router
from app.routes.notification_routes import router as notification_router
from app.routes.industry_routes import router as industry_router
from app.routes.client_routes import router as client_router
from app.routes.certificate_routes import router as cert_router
from app.routes.about_routes import router as about_router
from app.routes.file_url_routes import router as file_url_router
from app.config.database import db
app = FastAPI(title="User Management API")

# ✔ FINAL WORKING CORS CONFIG
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*","http://localhost:3000","https://quest-crm.onrender.com/"],          # allow all origins
    allow_credentials=True,      # must be False when origins="*"
    allow_methods=["*"],          # allow all methods
    allow_headers=["*"],          # allow all headers
)

app.include_router(auth_routes.router)
app.include_router(upload_router)
app.include_router(product_router)
app.include_router(notification_router)
app.include_router(industry_router)
app.include_router(client_router)
app.include_router(cert_router)
app.include_router(about_router)
app.include_router(file_url_router)

def main():
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
