import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import LabeledPrice, PreCheckoutQuery, ContentType
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

API_TOKEN = '7711734873:AAHOnxncCEo5e2mFOioc8P530lHg-Y8I0hs'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# @dp.message(commands=['start'])
# async def process_pay_command(message: types.Message):
#     pass
# @dp.pre_checkout_query()
# async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
#     await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# @dp.message(content_types=ContentType.SUCCESSFUL_PAYMENT)
# async def process_successful_payment(message: types.Message):
#     payment_info = message.successful_payment
#     amount_in_stars = payment_info.total_amount
#     currency = payment_info.currency
#     transaction_id = payment_info.provider_payment_charge_id

#     await message.reply(
#         f"*🎉 Payment successful!*\n"
#         f"💲 *Amount:* {amount_in_stars}⭐️\n"
#         f"🆔 *Transaction ID:* `{transaction_id}`",
#         parse_mode='Markdown'
#     )


async def on_shutdown():
    await dp.storage.close()
    await dp.storage.wait_closed()

def create_app():
    app = web.Application()
    setup_application(app, dp, bot=bot)
    return app 