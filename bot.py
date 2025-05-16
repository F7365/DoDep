from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, \
    InlineKeyboardMarkup, ContentType
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.filters import Command
import asyncio
import datetime
import random
import requests

bot = Bot(token='5568857923:AAH_UmlpH3Ue5BBC6oOW4qJ5O071YSnneyQ')
dp = Dispatcher()

user_info = []
cinfo = {}
cur_dep = {}
cur_perm = {}
usm = {}
CATS = ['Спорт','Киберспорт','Финансы и Рынок','Другое']
domain = '127.0.0.1:5000'

def hi():
    if len(user_info)==0:
        return 'У вас нет Dep-ов'
    for i in user_info:
        if i['active']==0:
            return 'У вас есть незавершенные Dep-ы'
    return 'Все Dep-ы Активны'
def start_kb():
    builder = InlineKeyboardBuilder()
    for i in user_info:
        if i['active']==1:
            builder.button(text=f"{str(i['title'])}-Active", callback_data=str(i['r']))
        else:
            builder.button(text=f"{str(i['title'])}", callback_data=str(i['r']))
    builder.button(text="Новый Dep", callback_data='new')
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)
def menu_kb(idd):
    builder = InlineKeyboardBuilder()
    if cur_dep[idd]['active'] == 0:
        if cur_dep[idd]['title'] is None:
            builder.row(InlineKeyboardButton(text="Название", callback_data='title'))
        else:
            builder.row(InlineKeyboardButton(text=cur_dep[idd]['title'], callback_data='title'))
        if cur_dep[idd]['desc'] is None:
            builder.row(InlineKeyboardButton(text="Описание", callback_data='desc'))
        else:
            builder.row(InlineKeyboardButton(text=cur_dep[idd]['desc'], callback_data='desc'))
        if cur_dep[idd]['theme'] is None:
            kb1=InlineKeyboardButton(text="Категории", callback_data='theme')
        else:
            kb1=InlineKeyboardButton(text=cur_dep[idd]['theme'], callback_data='theme')
        if cur_dep[idd]['period'] is None:
            kb2=InlineKeyboardButton(text="Период", callback_data='period')
        else:
            kb2=InlineKeyboardButton(text=f"{cur_dep[idd]['period']} ч", callback_data='period')
        builder.row(kb1,kb2)
        if cur_dep[idd]['title'] is not None and cur_dep[idd]['desc'] is not None and cur_dep[idd]['theme'] is not None and cur_dep[idd]['period'] is not None:
            builder.row(InlineKeyboardButton(text="Активация", callback_data='act'),
                        InlineKeyboardButton(text="Удалить", callback_data='del'))
        else:
            builder.row(InlineKeyboardButton(text="Удалить", callback_data='del'))
        builder.row(InlineKeyboardButton(text="Обратно", callback_data='back'))
    elif cur_dep[idd]['active'] == 1:
        builder.row(InlineKeyboardButton(text="Раздать", callback_data='razdacha'),
                    InlineKeyboardButton(text="Обратно", callback_data='back'))
    return builder.as_markup(resize_keyboard=True)
def theme_kb():
    builder = InlineKeyboardBuilder()
    for i in CATS:
        builder.button(text=i, callback_data=i)
    builder.button(text="Обратно", callback_data='back1')
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)
razdach_kb = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Да", callback_data='YES'),
                      InlineKeyboardButton(text="Нет", callback_data='NO'),
                      InlineKeyboardButton(text="Неизвестно", callback_data='UNKNOWN')],
                     [InlineKeyboardButton(text="Обратно", callback_data='back1')]], resize_keyboard=True)
back1_kb = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Обратно", callback_data='back1')]], resize_keyboard=True)

@dp.message(Command("start"), F.chat.type == "private")
async def start_handler(msg: Message):
    cur_perm[msg.chat.id] = False
    await msg.answer("Добро Пожаловать в Админ Панель!")
    usm[msg.chat.id]=await msg.answer(f'{hi()}',reply_markup=start_kb())


@dp.callback_query(lambda c: c.data == 'new' and F.chat.type == 'private')
async def form_handler(c: CallbackQuery):
    cur_perm[c.message.chat.id] = False
    cur_dep[c.message.chat.id]={'title':None,'desc':None,'theme':None,'period':None,'time':None,'active':0,'r':str(random.randint(100000000,999999999))}
    cinfo[cur_dep[c.message.chat.id]['r']]=cur_dep[c.message.chat.id]
    index1=None
    for i in user_info:
        if i['r'] == cur_dep[c.message.chat.id]['r']:
            index1=user_info.index(i)
    if index1 is None:
        user_info.append(cur_dep[c.message.chat.id])
    else:
        user_info[index1] = cur_dep[c.message.chat.id]
    usm[c.message.chat.id]=await c.message.edit_text(f'Новый Dep',reply_markup=menu_kb(c.message.chat.id))


@dp.callback_query(lambda c: c.data == 'back' and F.chat.type == 'private')
async def back_handler(c: CallbackQuery):
    cur_perm[c.message.chat.id] = False
    if c.message.chat.id in cur_dep:
        del cur_dep[c.message.chat.id]
        usm[c.message.chat.id]=await c.message.edit_text(f'{hi()}',reply_markup=start_kb())
    else:
        usm[c.message.chat.id]=await c.message.edit_text(f'{hi()}',reply_markup=start_kb())


@dp.callback_query(lambda c: c.data == 'del' and F.chat.type == 'private')
async def del_handler(c: CallbackQuery):
    cur_perm[c.message.chat.id] = False
    if c.message.chat.id in cur_dep:
        if cur_dep[c.message.chat.id]['r'] in cinfo:
            del cinfo[cur_dep[c.message.chat.id]['r']]
        if cur_dep[c.message.chat.id] in user_info:
            user_info.remove(cur_dep[c.message.chat.id])
        del cur_dep[c.message.chat.id]
        usm[c.message.chat.id]=await c.message.edit_text(f'{hi()}',reply_markup=start_kb())
    else:
        usm[c.message.chat.id]=await c.message.edit_text(f'{hi()}',reply_markup=start_kb())


@dp.callback_query(lambda c: c.data in cinfo and F.chat.type == 'private')
async def dep_handler(c: CallbackQuery):
    try:
        cur_perm[c.message.chat.id] = False
        cur_dep[c.message.chat.id]=cinfo[c.data]
        if cur_dep[c.message.chat.id]['active']==0:
            usm[c.message.chat.id]=await c.message.edit_text(f'Dep {cur_dep[c.message.chat.id]["title"]}',reply_markup=menu_kb(c.message.chat.id))
        else:
            usm[c.message.chat.id]=await c.message.edit_text(f'Dep {cur_dep[c.message.chat.id]["title"]}\n'
                                                             f'{cur_dep[c.message.chat.id]["desc"]}\n'
                                                             f'Тема: {cur_dep[c.message.chat.id]["theme"]}\n'
                                                             f'Период: {cur_dep[c.message.chat.id]["period"]} ч\n'
                                                             f'Создание: {cur_dep[c.message.chat.id]["time"]}',reply_markup=menu_kb(c.message.chat.id))
    except Exception:
        usm[c.message.chat.id]=await c.message.edit_text(f'{hi()}',reply_markup=start_kb())


@dp.callback_query(lambda c: c.data == 'back1' and F.chat.type == 'private')
async def back1_handler(c: CallbackQuery):
    try:
        cur_perm[c.message.chat.id] = False
        if cur_dep[c.message.chat.id]['active']==0:
            usm[c.message.chat.id]=await c.message.edit_text(f'Dep {cur_dep[c.message.chat.id]["title"]}',reply_markup=menu_kb(c.message.chat.id))
        else:
            usm[c.message.chat.id]=await c.message.edit_text(f'Dep {cur_dep[c.message.chat.id]["title"]}\n'
                                                             f'{cur_dep[c.message.chat.id]["desc"]}\n'
                                                             f'Тема: {cur_dep[c.message.chat.id]["theme"]}\n'
                                                             f'Период: {cur_dep[c.message.chat.id]["period"]} ч\n'
                                                             f'Создание: {cur_dep[c.message.chat.id]["time"]}',reply_markup=menu_kb(c.message.chat.id))
    except Exception:
        usm[c.message.chat.id]=await c.message.edit_text(f'{hi()}',reply_markup=start_kb())


@dp.callback_query(lambda c: c.data == 'title' and F.chat.type == 'private')
async def title_handler(c: CallbackQuery):
    if c.message.chat.id in cur_dep:
        if cur_dep[c.message.chat.id]['active']==0:
            cur_perm[c.message.chat.id] = 'title'
            usm[c.message.chat.id]=await c.message.edit_text(f'Придумайте назавние Dep-а',reply_markup=back1_kb)
    else:
        cur_perm[c.message.chat.id] = False
        usm[c.message.chat.id]=await c.message.edit_text(f'{hi()}',reply_markup=start_kb())


@dp.callback_query(lambda c: c.data == 'desc' and F.chat.type == 'private')
async def desc_handler(c: CallbackQuery):
    if c.message.chat.id in cur_dep:
        if cur_dep[c.message.chat.id]['active']==0:
            cur_perm[c.message.chat.id] = 'desc'
            usm[c.message.chat.id]=await c.message.edit_text(f'Придумайте описание Dep-а',reply_markup=back1_kb)
    else:
        cur_perm[c.message.chat.id] = False
        usm[c.message.chat.id]=await c.message.edit_text(f'{hi()}',reply_markup=start_kb())


@dp.callback_query(lambda c: c.data == 'theme' and F.chat.type == 'private')
async def theme_handler(c: CallbackQuery):
    cur_perm[c.message.chat.id] = False
    if c.message.chat.id in cur_dep:
        if cur_dep[c.message.chat.id]['active']==0:
            usm[c.message.chat.id]=await c.message.edit_text(f'Выберите тематику Dep-а',reply_markup=theme_kb())
    else:
        usm[c.message.chat.id]=await c.message.edit_text(f'{hi()}',reply_markup=start_kb())


@dp.callback_query(lambda c: c.data == 'period' and F.chat.type == 'private')
async def period_handler(c: CallbackQuery):
    if c.message.chat.id in cur_dep:
        if cur_dep[c.message.chat.id]['active']==0:
            cur_perm[c.message.chat.id] = 'period'
            usm[c.message.chat.id]=await c.message.edit_text(f'Выберите период активности Dep-а (в часах)',reply_markup=back1_kb)
    else:
        cur_perm[c.message.chat.id] = False
        usm[c.message.chat.id]=await c.message.edit_text(f'{hi()}',reply_markup=start_kb())


@dp.callback_query(lambda c: c.data in CATS and F.chat.type == 'private')
async def category_handler(c: CallbackQuery):
    cur_perm[c.message.chat.id] = False
    cur_dep[c.message.chat.id]['theme'] = c.data
    usm[c.message.chat.id]=await c.message.edit_text(f'Dep {cur_dep[c.message.chat.id]["title"]}',reply_markup=menu_kb(c.message.chat.id))


@dp.callback_query(lambda c: c.data == 'act' and F.chat.type == 'private')
async def activate_handler(c: CallbackQuery):
    cur_perm[c.message.chat.id] = False
    if c.message.chat.id in cur_dep:
        if cur_dep[c.message.chat.id]['title'] is not None and cur_dep[c.message.chat.id]['period'] is not None and cur_dep[c.message.chat.id]['desc'] is not None and cur_dep[c.message.chat.id]['theme'] is not None:
            cur_dep[c.message.chat.id]["active"]=1
            cur_dep[c.message.chat.id]["time"]=datetime.datetime.now().strftime('%H:%M %d.%m.%Y')

            response = requests.post(f'http://{domain}/add_card',json=cur_dep[c.message.chat.id],headers={'Content-Type': 'application/json'})

            usm[c.message.chat.id]=await c.message.edit_text(f'Вы Активировали Dep {cur_dep[c.message.chat.id]["title"]}\n{hi()}',reply_markup=start_kb())            
    else:
        usm[c.message.chat.id]=await c.message.edit_text(f'{hi()}',reply_markup=start_kb())


@dp.callback_query(lambda c: c.data == 'razdacha' and F.chat.type == 'private')
async def razdacha_handler(c: CallbackQuery):
    cur_perm[c.message.chat.id] = False
    if c.message.chat.id in cur_dep:
        usm[c.message.chat.id]=await c.message.edit_text(f'Подтвердилось ли условие Dep {cur_dep[c.message.chat.id]["title"]}\n{cur_dep[c.message.chat.id]["desc"]}',reply_markup=razdach_kb)
    else:
        usm[c.message.chat.id]=await c.message.edit_text(f'{hi()}',reply_markup=start_kb())


@dp.callback_query(lambda c: c.data in ['YES','NO','UNKNOWN'] and F.chat.type == 'private')
async def yesno_handler(c: CallbackQuery):
    cur_perm[c.message.chat.id] = False
    if c.message.chat.id in cur_dep:
        
        response = requests.post(f'http://{domain}/razdacha/{cur_dep[c.message.chat.id]["r"]}/{c.data.lower()}')

        if cur_dep[c.message.chat.id]['r'] in cinfo:
            del cinfo[cur_dep[c.message.chat.id]['r']]
        if cur_dep[c.message.chat.id] in user_info:
            user_info.remove(cur_dep[c.message.chat.id])
        name = cur_dep[c.message.chat.id]["title"]
        del cur_dep[c.message.chat.id]
        usm[c.message.chat.id]=await c.message.edit_text(f'Вы Раздали Очки и Остановили Dep {name}\n{hi()}',reply_markup=start_kb())
    else:
        usm[c.message.chat.id]=await c.message.edit_text(f'{hi()}',reply_markup=start_kb())


@dp.message(F.chat.type == "private")
async def other_message_handler(message: Message):
    if message.chat.id not in cur_perm or cur_perm[message.chat.id] == False:
        await bot.delete_message(message.chat.id, message.message_id)
    else:
        if cur_perm[message.chat.id] == 'title':
            await bot.delete_message(message.chat.id, message.message_id)
            cur_dep[message.chat.id]['title'] = message.text
            usm[message.chat.id] = await bot.edit_message_text(text=f'Dep {cur_dep[message.chat.id]["title"]}',
                chat_id=message.chat.id, message_id=usm[message.chat.id].message_id,reply_markup=menu_kb(message.chat.id))
            cur_perm[message.chat.id] = False
        elif cur_perm[message.chat.id] == 'desc':
            await bot.delete_message(message.chat.id, message.message_id)
            cur_dep[message.chat.id]['desc'] = message.text
            usm[message.chat.id] = await bot.edit_message_text(text=f'Dep {cur_dep[message.chat.id]["title"]}',
                chat_id=message.chat.id, message_id=usm[message.chat.id].message_id,reply_markup=menu_kb(message.chat.id))
            cur_perm[message.chat.id] = False
        elif cur_perm[message.chat.id] == 'period':
            try:
                await bot.delete_message(message.chat.id, message.message_id)
                cur_dep[message.chat.id]['period'] = int(message.text)
                usm[message.chat.id] = await bot.edit_message_text(text=f'Dep {cur_dep[message.chat.id]["title"]}',
                    chat_id=message.chat.id, message_id=usm[message.chat.id].message_id,reply_markup=menu_kb(message.chat.id))
                cur_perm[message.chat.id] = False
            except Exception as ex:
                print(ex)
        else:
            await bot.delete_message(message.chat.id, message.message_id)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())