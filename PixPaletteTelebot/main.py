import telebot
import json
from telebot import types
from PIL import Image as img
from transliterate import translit
from cpmaster import *
from convacolor import *


token = '6236206426:AAE9ELD0GpJDlGRkPkeQri6vNH5SWvjDqsI'
bot = telebot.TeleBot(token)


def intoStr(pal):
    result = ''
    x = 1
    for i in pal:
        r, g, b = i
        rgb = f'{r} {g} {b}'
        hex = get_hex(r, g, b)
        cmyk = " ".join(map(str, get_cmyk(r, g, b)))
        hsv = " ".join(map(str, get_hsv(r, g, b)))
        ncs = "".join(map(str, get_ncs(r, g ,b)))
        result += f'Цвет {x}:\n    RGB: <code>{rgb}</code>\n    HEX: <code>{hex}</code>\n    CMYK: <code>{cmyk}</code>\n    HSV: <code>{hsv}</code>\n    NCS: <code>{ncs}</code>\n'
        x += 1
    return result


@bot.message_handler(commands=['start'])
def start(message):

    with open('user_data.json', 'r') as f:
        data = json.load(f)
    data["data"][f'{message.from_user.id}'] = [5, translit(f'{message.from_user.first_name} {message.from_user.last_name}', language_code='ru', reversed=True)]

    with open('user_data.json', 'w') as f:
        json.dump(data, f, indent=4)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(text='О создателях')
    btn2 = types.KeyboardButton(text='Кол-во цветов')
    mess =  f'Привет, <b>{message.from_user.first_name}</b>, ты написал боту PixPalette! Со мной ты можешь получить коды в разных цветовых моделях основных цветов с фото, которое ты мне отправишь, также ты можешь выбрать количество нужных тебе цветов.'
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def func(message):
    try:
        amount = int(message.text)
        if 10 >= amount and 3 <= amount:
            with open('user_data.json', 'r') as f:
                data = json.load(f)
            data["data"][f'{message.from_user.id}'][0] = amount

            with open('user_data.json', 'w') as f:
                json.dump(data, f, indent=4)

            bot.send_message(message.chat.id, f'Установлено значение {amount}.')
        else:
            bot.send_message(message.chat.id, 'Данное число вне приемлемого диапазона.')
    except ValueError:
        if message.text == 'О создателях':
            inlinemarkup = types.InlineKeyboardMarkup()
            url_btn = types.InlineKeyboardButton(text="Наш вебсайт", url='https://github.com/misha153/PixPalette')
            inlinemarkup.add(url_btn)
            mess = 'PixPalette создана тремя студентами МТКП МГТУ им. Н. Э. Баумана, это были: Михаил Карпов, Глеб Свидорук и Виктор Андриевский.'
            bot.send_message(message.chat.id, mess, reply_markup=inlinemarkup)
        elif message.text == 'Кол-во цветов':
            with open('user_data.json', 'r') as f:
                data = json.load(f)["data"].get(f'{message.from_user.id}')

            bot.send_message(message.chat.id, f'Установите значение от 3 до 10. Сейчас установлено: {data[0]}.')
        else:
            bot.send_message(message.chat.id, 'Я тебя не понимаю, братишка...')

        
@bot.message_handler(content_types=['photo'])
def get_user_photo(message):
    '''
    Work in progress
    '''
    fileID = message.photo[-1].file_id
    file_info = bot.get_file(fileID)
    path = f'https://api.telegram.org/file/bot{token}/{file_info.file_path}'

    with open('user_data.json', 'r') as f:
        data = json.load(f)["data"].get(f'{message.from_user.id}')[0]

    bot.reply_to(message, "Определяю палитру...")
    bot.send_photo(message.chat.id, img.fromarray(output_palette_img(filepath=path, colors=data)))
    bot.send_message(message.chat.id, f'<b>{intoStr(output_palette(filepath=path, colors=data))}</b>', parse_mode='html')


if __name__ == '__main__':
    bot.polling(none_stop=True)