import asyncio
from decouple import config
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


from create_bot import bot
from handlers.start import del_call_kb, del_message_kb, Form
from keyboards.inline_kbs import *
from database.db_users import get_sub_ids, get_all_ids
from database.db_admin import add_promo, del_promo
from outline.main import get_keys
from utils.ssh_utils import execute_outline_server, get_data_from_output

admin_id = config('ADMIN')

admin_router = Router()

class AddServerState(StatesGroup):
    waiting_for_server_data = State()
    store_data_for_execute = State()


@admin_router.callback_query(F.data == 'adminka')
async def add_del_promos(call: CallbackQuery):
    await del_call_kb(call)
    await call.message.answer('Выбирай', reply_markup=admin_actions())

@admin_router.callback_query(F.data == 'add_del_promo_next_step')
async def add_del_promo(call: CallbackQuery, state: FSMContext):
    await del_call_kb(call)
    await call.message.answer('⬇️ Введите промокод и кол-во недель ⬇️\n'
                              'Пример: "TestPromo 31" если хотите добавить промокод на месяц подписки\n'
                              'Пример: "TestPromo" если хотите удалить промокод', reply_markup=cancel_fsm_kb())
    await state.set_state(Form.admin_promokod)

@admin_router.message(F.text, Form.admin_promokod)
async def action_with_promo(message: Message, state: FSMContext):
    await state.update_data(admin_promokod=message.text.split())
    await message.answer('Что делать с этим промокодом?', reply_markup=add_del_promo_kb())
    await del_message_kb(message)

@admin_router.callback_query(F.data, Form.admin_promokod)
async def add_or_del_promo(call: CallbackQuery, state: FSMContext):
    await del_call_kb(call)
    fsm_data = await state.get_data()
    if fsm_data:
        if len(fsm_data['admin_promokod']) == 2:
            promo, time = fsm_data['admin_promokod']
        else:
            promo = fsm_data['admin_promokod'][0]

    if call.data == 'add_promo':
        await add_promo(promo, int(time))
        await call.message.answer(f'Промокод "{promo}" на {time} недель добавлен')
        await state.clear()
        await call.message.answer('Возврат в меню.', reply_markup=await main_inline_kb(call.from_user.id))
    elif call.data == 'del_promo':
        await del_promo(promo)
        await call.message.answer(f'Промокод "{promo}" удален')
        await state.clear()
        await call.message.answer('Возврат в меню.', reply_markup=await main_inline_kb(call.from_user.id))
    else:
        await call.message.answer('Возврат в меню')
        await asyncio.sleep(2)
        await call.message.answer_photo(config('START'),
                                        reply_markup=await main_inline_kb(call.from_user.id))


@admin_router.callback_query(F.data == 'check_server')
async def check_server(call: CallbackQuery):
    vpn_keys = get_keys()
    users = list()
    for keys in vpn_keys:  # Создаём список из айди ключей(а также пользователей) с подпиской
        if keys.name:
            users.append(keys.name)
        else:
            users.append('id=' + keys.key_id)
    print(users)
    await call.message.answer(f'Заполненность сервера: {len(vpn_keys)} пользователей',
                              reply_markup=check_server_kb(users))

@admin_router.callback_query(F.data == 'spamming')
async def get_message_for_spam(call: CallbackQuery, state:FSMContext):
    await call.message.answer('⬇️ Введите текст для рассылки ⬇️', reply_markup=cancel_fsm_kb())
    await state.set_state(Form.spam)


@admin_router.message(F.text, Form.spam)
async def confirm_text_for_spam(message: Message, state: FSMContext):
    await state.update_data(spam=message.text)
    data_text = await state.get_data()

    await message.answer(f'{data_text['spam']}\n'
                         f'\nДанный текст будет разослан',
                         reply_markup=target_for_spam())

@admin_router.callback_query(F.data.startswith('spam_'), Form.spam)
async def spam(call: CallbackQuery, state: FSMContext):
    get_text = await state.get_data()
    text = get_text['spam']
    target = call.data.split('_')[-1]

    if target == 'sub':
        sub_ids = await get_sub_ids()
        for user_id in sub_ids:
            await bot.send_message(chat_id=user_id, text=text)
            await asyncio.sleep(1)
        await del_call_kb(call)
        await call.message.answer('Рассылка завершена',
                                  reply_markup=await main_inline_kb(call.from_user.id))

    elif target == 'all':
        all_ids = await get_all_ids()
        for user_id in all_ids:
            await bot.send_message(chat_id=user_id, text=text)
            await asyncio.sleep(1)
        await del_call_kb(call)
        await call.message.answer('Рассылка завершена',
                                  reply_markup=await main_inline_kb(call.from_user.id))

@admin_router.callback_query(F.data == 'add_server')
async def add_server_func(call: CallbackQuery, state: FSMContext):
    await call.message.answer('Отправьте данные от сервера в формате: ip///port///user///password\n'
                              'Пример: 192.168.19.1///5050///root///uJ1Ps0?a8MN')
    await state.set_state(AddServerState.waiting_for_server_data)

@admin_router.message(AddServerState.waiting_for_server_data)
async def process_server_data(message: Message, state: FSMContext):
    server_data = message.text
    try:
        ip, port, user, password = server_data.split('///')
        await state.update_data(ip=ip, port=port, user=user, password=password)
        await message.answer(f"Данные сервера:\nIP: {ip}\nPort: {port}\nUser: {user}\nPassword: {password}\n"
                             f"\nЕсли данные верны - нажмите 'Добавить сервер'", reply_markup=add_server())
        await state.set_state(AddServerState.store_data_for_execute)
    except ValueError:
        await message.answer('Некорректный формат ввода, попробуйте ещё раз.')

@admin_router.message(AddServerState.store_data_for_execute)
async def execute_server(call: CallbackQuery, state: FSMContext):

    data = await state.get_data()

    ip = data.get('ip')
    port = data.get('port')
    user = data.get('user')
    password = data.get('password')

    try:
        await call.message.answer('Запуск функции установки Outline...')

        output, errors = execute_outline_server(host=ip, port=port, user=user, password=password)

        if errors:
            await call.answer(f'При выполнении произошли следующие ошибки:\n'
                                 f'\n{errors}')
        else:
            await call.answer('Функция отработала без ошибок')

        if output:
            await call.answer('Запуск функции расшифровки полученных данных...')
            try:
                api_url, cert_sha256, management_port, access_key_port = get_data_from_output(output)
                await call.answer('Функция отработала. Полученные данные:\n'
                                     f'\napi_url={api_url}\n'
                                     f'cert_sha256={cert_sha256}\n'
                                     f'management_port={management_port}\n'
                                     f'access_key_port={access_key_port}')

            except Exception as e:
                await call.answer('Произошла ошибка при выполнении функции get_data_from_output:\n'
                                     f'Error: {str(e)}')

    except Exception as e:
        await call.answer()