import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import datetime
from datetime import timedelta
import time
import codecs
import csv
from aiogram import Bot, Dispatcher, executor, types



logging.basicConfig(filename="logging.log", level=logging.INFO)

def from_csv_to_list(file_name):
    with codecs.open(file_name, "r", "utf-8") as file:
        reader = sum(list(csv.reader(file, skipinitialspace=True)),[])
    return reader

tickers_list=from_csv_to_list("tickers.csv")

TOKEN = ""
MSG = "Введите тикер акции для просмотра цен за неделю."

bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)
user_id=""

@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    global user_id
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    user_name = message.from_user.first_name
    logging.info(f"{user_id=} {user_full_name=} , {time.asctime()} ")
    await message.reply(f"Привет, {user_full_name}")

    await bot.send_message(user_id, MSG.format(user_name))

    @dp.message_handler(lambda message: int(message.text) not in tickers_list)
    async def check_empty(message: types.Message):
        return await message.reply("Такого тикера нет в списке акций")

    @dp.message_handler(lambda message: int(message.text) in tickers_list)
    async def check_handler(message: types.Message):
        global user_id
        asset= message.text


        previous_date=datetime.date.today()-timedelta(1)
        week_date=datetime.date.today()-timedelta(8)

        link="https://www.moex.com/ru/issue.aspx?board=TQBR&code="+f"{asset}"


        options = Options()
        options.headless = True
        options.add_argument("--window-size=1920,1200")
        DRIVER_PATH = ("chromedriver.exe")

        driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
        driver.get("https://www.moex.com/ru/marketdata/#/mode=instrument&secid="+f"{asset}"+"&boardgroupid=57&mode_type=history&date_from="+f"{week_date}"+"&date_till="+f"{previous_date}")


        time.sleep(1)
        element = driver.find_element(By.LINK_TEXT ,"Согласен")
        element.click()
        time.sleep(20)
        #driver.get_screenshot_as_file('screen.png')

        newelement=driver.find_element(By.CSS_SELECTOR, 'div.ui-table')
        newelement.screenshot("Security price.png")

        driver.quit()

        await bot.send_message(user_id, "Информация об акции ниже по ссылке")
        await bot.send_message(user_id, link)
        await bot.send_message(user_id, "Хотите получить информацию по другой акции? Нажмите /start")



if __name__ == "__main__":
    executor.start_polling(dp)