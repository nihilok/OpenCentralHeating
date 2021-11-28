from fastapi import APIRouter, Depends

from .authentication import get_current_active_user
from ..models import HouseholdMember
from ..secrets import initialized_config as config

router = APIRouter(prefix="/secrets")


@router.get("/telegram-bot-token/")
async def get_telegram_bot_token(
    user: HouseholdMember = Depends(get_current_active_user),
):
    return {
        "token": config["TELEGRAM_BOT"]["BOT_TOKEN"],
        "channel": config["TELEGRAM_BOT"]["CHANNEL_ID"],
    }
