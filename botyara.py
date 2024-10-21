
from aiogram import Bot, Dispatcher, executor, types
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext
import requests
import PyPDF2
import os
import sqlite3


pdf_list = set()

# Попытка закидывать BLOB в бд. Крайне хреновая. Отказ.
def take_blob(chat_id):
    try:
       sqlite_connection = sqlite3.connect('C:/Users/Brusnika_laptop/Desktop/telegram_bot/bot_database.db')
       cursor = sqlite_connection.cursor()
       print("Подключен к SQLite")
       sqlite_select_blob_querry = """SELECT file FROM bot_files WHERE chat_id = """ + str(chat_id)
       cursor.execute(sqlite_select_blob_querry)
       record = cursor.fetchall()
       print("Файл успешно получен")
       cursor.close()
       return record

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")


def insert_blob(name, file, chat_id):
    try:
        sqlite_connection = sqlite3.connect('C:/Users/Brusnika_laptop/Desktop/telegram_bot/bot_database.db')
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")

        sqlite_insert_blob_query = """INSERT INTO bot_files
                                  (name, file, chat_id) VALUES (?, ?, ?)"""
        
        # Преобразование данных в формат кортежа
        data_tuple = (name, file, chat_id)
      #   print(data_tuple)
        cursor.execute(sqlite_insert_blob_query, data_tuple)
        connection.commit()
        print("Файл успешно вставлен как BLOB в таблиу")
        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")


def remove_file(file_path):
    try:
        os.remove(file_path)
    except FileNotFoundError as Error:
        print('Ошбика: Файл ' +  file_path + ' не найден')


def merge_pdfs(input_pdfs, output_pdf):
    merger = PyPDF2.PdfMerger()
    try:
        for pdf in input_pdfs:
            merger.append(pdf)
        with open(output_pdf, 'wb') as merged_pdf:
            merger.write(merged_pdf)
        print(f'Merged PDFs successfully. Output saved to: {output_pdf}')
        merger.close()
    except Exception as e:
        print(f'Error merging PDFs: {e}')


API_TOKEN = '7432106426:AAFjSlodfC84jL4dMUwSkU-yg82fzvDoqx8'


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
   await message.reply("Привет!\nЯ бот для объединения PDF-файлов. Просто отправь мне PDF-файлы в порядке, в котором их необходимо объединить и я это сделаю!")
 

@dp.message_handler(content_types=['document'])
async def handle_docs(message: types.Message):
      file_info = (await bot.get_file(message.document.file_id)).file_path
      if file_info.endswith('.pdf'):
          downloaded_file = await bot.download_file(file_info)

         #  print(file_info)
         #  insert_blob(downloaded_name, downloaded_file.getvalue(), message.chat.id)
          src = 'C:/Users/Brusnika_laptop/Desktop/telegram_bot/Docs/' + message.document.file_name  
      
          global pdf_list
          while src in pdf_list:
              src +='1'
          pdf_list.add(src)

          with open(src, 'wb') as new_file:
             new_file.write(downloaded_file.getvalue())
          new_file.close()
          message_answer = 'Если ты прислал все PDF, жми команду "/merge"!'
         #  print(take_blob(message.chat.id))
      else: 
          message_answer = 'Я принимаю только PDF файлы!'
      await message.answer(message_answer)

      # await message.answer(merge_pdf(pdf_list))


@dp.message_handler(content_types=['photo'])
async def wrong_image(message: types.Message):
    await message.answer('Я принимаю только PDF файлы!')

        
@dp.message_handler(commands='Merge')
async def reply_to_merge(message: types.Message):
    global pdf_list
    result_file = 'C:/Users/Brusnika_laptop/Desktop/telegram_bot/Docs/result.pdf'
    merge_pdfs(pdf_list, result_file)    
    
    for file in pdf_list:
        try:
            remove_file(file)
            print ('    Остаточные файлы успешно удалены')
        except PermissionError as error:
            print('Не получилось удалить остаточные файлы')
    pdf_list.clear()
    await message.answer('Подожди пару секунд, сейчас всё сделаю!')
    await bot.send_document(message.chat.id, open(result_file, 'rb'))
    await message.answer('Готово!')
    remove_file(result_file)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

