from aiogram import Router
from .default_handlers.main import router as default_router
from .custom_handlers.contacts import router as contacts_router

main_router = Router()
main_router.include_router(default_router)
main_router.include_router(contacts_router)

__all__ = ["main_router"]
