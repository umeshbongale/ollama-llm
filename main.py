from fastapi import FastAPI
from routers import chat_router, whatsapp_router, ui_router, hr_router, it_router, finance_router
import logging

app = FastAPI()

app.include_router(chat_router.router)
app.include_router(whatsapp_router.router)
app.include_router(ui_router.router)
app.include_router(hr_router.router)
app.include_router(it_router.router)
app.include_router(finance_router.router)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
