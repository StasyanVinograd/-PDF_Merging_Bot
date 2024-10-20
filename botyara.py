
from aiogram import Bot, Dispatcher, executor, types
API_TOKEN = '7395364689:AAHt2rZ-Zz-uZkQPgyCkTLyCuSG-YI8k5ic'
 
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
 
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
   await message.reply("Привет!\nЯ Эхо-бот от Skillbox!\nОтправь мне любое сообщение, а я тебе обязательно отвечу.")
 
@dp.message_handler()
async def echo(message: types.Message):
   answer = message.text
   if message.text == 'nigger':
      answer = 'сам ты ниггер'
      
   await message.answer(answer)

if __name__ == '__main__':
   executor.start_polling(dp, skip_updates=True)