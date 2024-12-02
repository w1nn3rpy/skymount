import asyncio

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, BotCommand, BotCommandScopeDefault
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.deep_linking import create_start_link, decode_payload

from keyboards.inline_kbs import *
from database.db_users import *
from payment.main import *
from outline.main import *

start_router = Router()

MENU_TEXT = """Добро пожаловать, {username}!\n
SKYMOUNT VPN — это быстрый и безопасный VPN, на протоколе Shadowsocks
В чём мы лучше других сервисов?
Безлимитный трафик
Доступные цены
Нет потерь в скорости интернета
Максимальная конфиденциальность
\nДля начала работы получите доступ\n
Если остались вопросы:
/help – полезная информация и техподдержка"""

async def set_commands():
    commands = [BotCommand(command='start', description='Старт'),
                BotCommand(command='buy', description='Купить VPN'),
                BotCommand(command='help', description='Помощь')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


class LinkMsg:
    msg = None

class Form(StatesGroup):
    promokod = State()
    admin_promokod = State()
    send_payscreen = State()
    spam = State()

async def del_call_kb(call: CallbackQuery, *param: bool):
    """
    Функция удаления прошлого сообщения
    """
    try:
        await bot.delete_message(
            chat_id=call.from_user.id,
            message_id=call.message.message_id
        )
        if param:
            await bot.delete_message(
                chat_id=call.from_user.id,
                message_id=LinkMsg.msg.message_id
            )
            LinkMsg.msg = None

    except Exception as E:
        print(E)

async def del_message_kb(message: Message, *param):
    """
    Функция удаления прошлого сообщения
    2-й необязательный аргумент 'True' = удаление 5-и последних сообщений
    """
    try:
        if param:
            await bot.delete_messages(
                chat_id=message.from_user.id,
                message_ids=[message.message_id - 3, message.message_id - 2,
                             message.message_id - 1, message.message_id, message.message_id + 1]
            )
        else:
            await bot.delete_message(
                chat_id=message.from_user.id,
                message_id=message.message_id
            )

    except Exception as E:
        print(E)

async def confirm_pay(call, amount_days):
    check_old_key = await get_user_info(call.from_user.id, 4)

    try:
        if check_old_key:
            await extension_subscribe(call.from_user.id, amount_days)
            await call.message.answer_photo(config('CONGRATS'), 'Ваша подписка продлена!\n'
                                                                'Спасибо, что пользуетесь нашим сервисом.',
                                            reply_markup=return_home())

        else:
            key = create_new_key(call.from_user.id, call.from_user.username).access_url
            await set_user_vpn_key(call.from_user.id, key)
            await call.message.answer_photo(config('CONGRATS'),
                f'Ваш ключ:\n <pre language="c++">{key}</pre>\n'
                f'\nВыберите свою платформу для скачивания приложения',
                reply_markup=apps())
            await call.message.answer('Инструкция по настройке', reply_markup=guide())

            if int(amount_days) == 2:
                await set_for_trial_subscribe(call.from_user.id)
            else:
                await set_for_subscribe(call.from_user.id, int(amount_days))

    except Exception as e:
        print(str(e))

async def confirm_pay_msg(message, amount_days):

    check_old_key = await get_user_info(message.from_user.id, 4)

    try:
        if check_old_key:
            await extension_subscribe(message.from_user.id, amount_days)
            await message.answer_photo(config('CONGRATS'), 'Ваша подписка продлена!\n'
                                                                'Спасибо, что пользуетесь нашим сервисом.',
                                       reply_markup=return_home())

        else:
            key = create_new_key(message.from_user.id, message.from_user.username).access_url
            await set_user_vpn_key(message.from_user.id, key)
            await message.answer_photo(config('CONGRATS'),
                f'Ваш ключ:\n <pre language="c++">{key}</pre>\n'
                f'\nВыберите свою платформу для скачивания приложения',
                reply_markup=apps())
            await message.answer('Инструкция по настройке', reply_markup=guide())
            if int(amount_days) == 2:
                await set_for_trial_subscribe(message.from_user.id)
            else:
                await set_for_subscribe(message.from_user.id, int(amount_days))

    except Exception as e:
        print(str(e))

@start_router.message(CommandStart())
async def cmd_start(message: Message):

    if not await get_user_info(message.from_user.id):
        if len(message.text.split()) > 1:
            referer = message.text.split()[1]
            referer_id = decode_payload(referer) if referer else None

            if referer:
                if referer_id != message.from_user.id:
                    await new_user(message.from_user.id, message.from_user.username,
                               invited_by_id=int(referer_id))
                else:
                    await message.answer('Вы указали свой ID в качестве пригласившего.\n'
                                         'Ай-ай-ай, нельзя так ☺️')
                    await new_user(message.from_user.id, message.from_user.username)
        else:
            await new_user(message.from_user.id, message.from_user.username)

    else:
        user_id, name, is_admin, is_sub, key, label, start_sub, end_sub, balance, invited_by_id, trial_used, send_ref = await get_user_info(message.from_user.id)
        if name != message.from_user.username:
            await update_username(message.from_user.id, message.from_user.username)

    user_id, name, is_admin, is_sub, key, label, start_sub, end_sub, balance, invited_by_id, trial_used, send_ref = await get_user_info(message.from_user.id)

    if is_sub or trial_used:
        await message.answer_photo(config('START'),
                                   MENU_TEXT.format(username=message.from_user.full_name
                                   if message.from_user.full_name
                                   else message.from_user.username),
                                   reply_markup=await main_inline_kb(message.from_user.id))
    else:
        await message.answer_photo(config('START'),
                                   MENU_TEXT.format(username=message.from_user.full_name
                                   if message.from_user.full_name
                                   else message.from_user.username))
        await asyncio.sleep(1)
        await message.answer_photo(config('PRICE'), reply_markup=await main_inline_kb(message.from_user.id))


@start_router.message(Command('help'))
async def about(message: Message):
    await del_message_kb(message, True)
    await message.answer(
        'У нас Вы можете быстро купить качественный VPN.\n'
        'После оплаты Вам будет предоставлен ключ и инструкция\n'
        'Настройка занимает 1 минуту, всё очень просто!\n'
        'Наши сервера находятся в разных уголках мира, имеют низкий пинг и высокую скорость!\n'
        'А самое главное - наш VPN дешевый и доступен каждому!',
        reply_markup=about_buttons())

@start_router.callback_query(F.data == 'buy')
@start_router.message(Command('buy'))
async def cmd_buy(event: Message|CallbackQuery):
    if isinstance(event, Message):
        await del_message_kb(event, True)
        await event.answer(
            'Выберите сервер', reply_markup=server_select())
    else:
        await del_call_kb(event)
        await event.message.answer(
            'Выберите сервер', reply_markup=server_select())


@start_router.callback_query(F.data == 'profile')
async def profile(call: CallbackQuery):
    await del_call_kb(call)
    user_id, name, is_admin, is_sub, key, label, start_sub, end_sub, balance, referer, trial_used, send_ref = await get_user_info(call.from_user.id)
    if name is not None:
        name = '@' + name
    if not is_sub:
        key = 'Нет ключа'
        await call.message.answer_photo(
            config('PROFILE'),
            '👤 Профиль\n'
            f'├ <b>ID</b>: {user_id}\n'
            f'├ <b>Никнейм</b>: {name}\n'
            f'├ <b>Реферальный баланс</b>: {balance}р.\n'
            f'├ <b>Подписка</b>: ❌\n'
            f'└ <b>Ключ</b>: {key}',
            reply_markup=profile_kb())
    else:
        await call.message.answer_photo(
            config('PROFILE'),
            '👤 Профиль\n'
            f'├ <b>ИД</b>: {call.from_user.id}\n'
            f'├ <b>Никнейм</b>: {name}\n'
            f'├ <b>Реферальный баланс</b>: {balance}р.\n'
            f'├ <b>Подписка</b>: ✅\n'
            f'├ <b>Начало подписки</b>: {start_sub}\n'
            f'├ <b>Окончание подписки</b>: {end_sub}\n'
            f'└ <b>Ключ</b>:\n{key}',
            reply_markup=profile_kb())

@start_router.callback_query(F.data == 'referral_system')
async def referral_system(call: CallbackQuery):
    await del_call_kb(call)
    referral_link = await create_start_link(bot, str(call.from_user.id), encode=True)
    await call.message.answer('Приглашай друзей по своей ссылке и получай 25 рублей '
                              'на свой реферальный баланс с каждого, '
                              'кто оплатит подписку 💰\n'
                              '\nПригласи 4 друга и получи целый месяц подписки <b>БЕСПЛАТНО!</b>\n'
                              f'\nВаша реферальная ссылка:\n <pre language="c++">{referral_link}</pre>\n',
                              reply_markup=return_home())


@start_router.callback_query(F.data == 'get_home')
async def to_homepage_callback(call: CallbackQuery):
    await del_call_kb(call)
    await call.message.answer_photo(config('START'),
                                    MENU_TEXT.format(username=call.from_user.full_name
                                    if call.from_user.full_name
                                    else call.from_user.username),
                                    reply_markup=await main_inline_kb(call.from_user.id))


@start_router.callback_query(F.data == 'trial')
async def get_trial(call: CallbackQuery):
    await del_call_kb(call)
    await call.message.answer('Мы отличаемся тем, что даём бесплатно опробовать наш сервис '
                              'в течение двух дней!\n'
                              'Жми кнопку и наслаждайся свободным интернетом!', reply_markup=get_key_kb(2))


@start_router.callback_query(F.data == 'netherlands_server')
async def buy(call: CallbackQuery):
    await del_call_kb(call)
    await call.message.answer_photo(config('PRICE'),
        'Выберите срок подписки', reply_markup=select_time_kb())


@start_router.callback_query(F.data == 'one_month')
async def price(call: CallbackQuery):
    await del_call_kb(call)
    await call.message.answer(
        f'<b>Стоимость подписки</b>: 100р.\n'
        '\n<b>Выберите способ оплаты</b>',
        reply_markup=select_payment_system(100)
    )


@start_router.callback_query(F.data.in_({'yoomoney_100', 'sbp_100', 'card-transfer_100'}))
async def any_system_pay(call: CallbackQuery):
    price_dict = {'100': '1 месяц'}

    types_dict = {'yoomoney': 'ЮMoney (возможна комиссия)',
                  'sbp': 'СБП (Комиссия 0%)'}

    pay_system = call.data.split('_')[0]
    amount = call.data.split('_')[-1]
    await del_call_kb(call)

    await call.message.answer(f'<b>💳 Способ оплаты</b>: {types_dict.get(pay_system)}\n'
                              f'\n<b>🕓 Длительность подписки</b>: {price_dict.get(amount)}\n'
                              f'\n<b>💵 Стоимость</b>: {amount} рублей',
                              reply_markup=accept_or_not(pay_system, amount))


@start_router.callback_query(F.data.in_({'accept_yoomoney_100', 'cancel'}))
async def result_yoomoney_pay(call: CallbackQuery):
    result = call.data.split('_')
    payment_system = result[1]
    price = result[-1]
    await del_call_kb(call)
    if result[0] == 'accept':
        if payment_system == 'yoomoney':
            link, label = payment(int(price), str(call.from_user.id) + math_date())
            print(f'Создан лейбл: {label}')
            await add_label(call.from_user.id, label)
            LinkMsg.msg = await call.message.answer(
                f'Внимание!\nБанк может взымать комиссию!\n'
                f'Ваша ссылка на оплату подписки:', reply_markup=pay(link))
            await call.message.answer(
                'После оплаты нажмите на соответствующую кнопку\n',
                reply_markup=payed('yoomoney', price),
                callback_data=price)

    else:
        await call.message.answer('Оплата отменена ❌.\nВозврат в меню.')
        await asyncio.sleep(2)
        await call.message.answer_photo(config('START'),
                                        MENU_TEXT.format(username=call.from_user.full_name
                                        if call.from_user.full_name
                                        else call.from_user.username),
                                        reply_markup=await main_inline_kb(call.from_user.id))


@start_router.callback_query(lambda c: c.data.startswith('confirm-pay_yoomoney_'))
async def check_payment_yoomoney(call: CallbackQuery):
    await del_call_kb(call)
    payment_label = await get_user_info(call.from_user.id, 5)
    result = check_payment(payment_label)
    if result is not False:
        amount = {97: 31}  # Кол-во дней исходя из суммы оплаты
        time_on = amount[result]
        referrer = await get_user_info(call.from_user.id, 9)
        if referrer:
            check_to_already_get_referral_pay_by_this_user = await get_user_info(call.from_user.id, 11)
            if not check_to_already_get_referral_pay_by_this_user:
                result = await add_balance_for_refer(referrer, call.from_user.id)
                if result:
                    await bot.send_message(referrer, 'Пользователь оплатил подписку по вашей ссылке!\n'
                                             'На ваш счёт начислено 25р.\n'
                                             '\nСпасибо, что пользуетесь нашим сервисом!')
        await confirm_pay(call=call, amount_days=time_on)
    else:
        await call.message.answer(
            'Оплата не поступала. Попробуйте через несколько минут, либо свяжитесь с поддержкой.',
            reply_markup=payed('yoomoney', 0))


@start_router.callback_query(lambda c: c.data.startswith('get-key_'))
async def check_is_confirmed(call: CallbackQuery):
    time_subscribe = call.data.split('_')[-1]
    await bot.edit_message_reply_markup(chat_id=call.from_user.id,
                                        message_id=call.message.message_id)
    await confirm_pay(call=call, amount_days=time_subscribe)


@start_router.callback_query(F.data == 'cancel_pay')
async def cancel_pay(call: CallbackQuery):
    await del_call_kb(call, True)
    await del_label(call.from_user.id)
    await call.message.answer(
        'Оплата отменена ❌.\nВозврат в меню.')
    await asyncio.sleep(3)
    await call.message.answer_photo(config('START'),
                                    MENU_TEXT.format(username=call.from_user.full_name
                                    if call.from_user.full_name
                                    else call.from_user.username),
                                    reply_markup=await main_inline_kb(call.from_user.id))


@start_router.callback_query(F.data == 'promo_step_2')
async def promik(call: CallbackQuery, state: FSMContext):
    await del_call_kb(call)
    await call.message.answer(
        '⬇️ Введите промокод ⬇️', reply_markup=cancel_fsm_kb())
    await state.set_state(Form.promokod)


@start_router.message(F.text, Form.promokod)
async def check_promo(message: Message, state: FSMContext):
    await state.update_data(promokod=message.text)
    LinkMsg.msg = (await message.answer('Промокод проверяется... ⏳'))
    data_promo = await state.get_data()
    promo = data_promo['promokod']
    promo_info = await pop_promo(promo)
    await del_message_kb(message)
    if promo_info is not False:
        await del_message_kb(message)
        promo_time = promo_info[1]
        await message.answer(f'Промокод {promo} активирован! 🔥\n'
                             f'Вам предоставлен доступ на {promo_time} недель.\n'
                             'Ожидайте ключ и инструкцию')
        await state.clear()
        await confirm_pay_msg(message, promo_time)
    else:
        await del_message_kb(message, True)
        await message.answer('Такого промокода не существует')
        await message.answer('⬇️ Введите промокод ⬇️', reply_markup=cancel_fsm_kb())
        await state.set_state(Form.promokod)


@start_router.callback_query(F.data == 'cancel_FSM')
async def cancel_fsm(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await del_call_kb(call)
    await del_message_kb(call.message, True)
    await call.message.answer('Возврат в меню')
    await asyncio.sleep(2)
    await call.message.answer_photo(config('START'),
                                    MENU_TEXT.format(username=call.from_user.full_name
                                    if call.from_user.full_name
                                    else call.from_user.username),
                                    reply_markup=await main_inline_kb(call.from_user.id))


@start_router.message(F.text)
async def nothing(message: Message):
    await del_message_kb(message, True)
    await message.answer('Error 404')
    await message.answer_photo(config('START'),
                               MENU_TEXT.format(username=message.from_user.full_name
                               if message.from_user.full_name
                               else message.from_user.username),
                               reply_markup=await main_inline_kb(message.from_user.id))

@start_router.message(F.photo)
async def get_photo_id(message: Message):
    photo = max(message.photo, key=lambda x: x.height)
    file_id = photo.file_id
    await message.answer(f'{file_id}')
