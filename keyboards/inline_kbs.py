from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.db_users import get_user_info


async def main_inline_kb(user_id):
    tg_id, username, is_admin, is_subscriber, vpn_key, label, start_subscribe, end_subscribe, balance, invited_by, trial_used, send_ref = await get_user_info(user_id)

    if not is_subscriber and not trial_used:
        kb_list = [
            [InlineKeyboardButton(text='⚡️Попробовать бесплатно (2 дня)',
                                  callback_data='trial')],
            [InlineKeyboardButton(text="🛒 Купить VPN", callback_data='buy')],
            [InlineKeyboardButton(text="🔥 Ввести промокод", callback_data='promo_step_2')]
        ]
    else:

        kb_list = [
            [InlineKeyboardButton(text="🚀 Продлить VPN" if is_subscriber else "🛒 Купить VPN",
                                  callback_data='buy')],
            [InlineKeyboardButton(text='👤 Профиль', callback_data='profile')]
        ]

    if is_admin:
        kb_list.extend([InlineKeyboardButton(text='🔥 Админка', callback_data='adminka')])
                        # , [InlineKeyboardButton(text='Типа купил', callback_data='fakebuy')],
                        # [InlineKeyboardButton(text='Подписка закончилась', callback_data='end_sub_debug')]))
    return InlineKeyboardMarkup(inline_keyboard=kb_list)


def about_buttons():
    button = [
        [InlineKeyboardButton(text='🆘 Поддержка', url='tg://resolve?domain=danilserge27')],
        [InlineKeyboardButton(text='👤 Профиль', callback_data='profile')],
        [InlineKeyboardButton(text="🛒 Купить VPN", callback_data='buy')],
        [InlineKeyboardButton(text='🏠 Домой', callback_data='get_home')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=button)


def profile_kb():
    inline_kb_profile = [
        [InlineKeyboardButton(text='🔍 В каталог', callback_data='buy')],
        [InlineKeyboardButton(text='👥 Реферальная программа', callback_data='referral_system')],
        [InlineKeyboardButton(text='🏠 На главную', callback_data='get_home')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_profile)


def server_select():
    inline_kb_server = [
        [InlineKeyboardButton(text='🇳🇱 Нидерланды', callback_data='netherlands_server')],
        [InlineKeyboardButton(text='🏠 На главную', callback_data='get_home')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_server)


def select_time_kb():
    inline_kb_buy = [
        [InlineKeyboardButton(text='1 Месяц | 100р', callback_data='one_month')],
        [InlineKeyboardButton(text='🏠 На главную', callback_data='get_home')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_buy)


def select_payment_system(sum_of):
    inline_kb_systems = [
        [InlineKeyboardButton(text='ЮMoney', callback_data=f'yoomoney_{str(sum_of)}')],
        [InlineKeyboardButton(text='🏠 На главную', callback_data='get_home')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_systems)


def accept_or_not(pay_system, sum_of):
    inline_kb_accept = [
        [InlineKeyboardButton(text='✅ Подтвердить', callback_data=f'accept_{str(pay_system)}_{str(sum_of)}')],
        [InlineKeyboardButton(text='❌ Отмена', callback_data='cancel')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_accept)


def admin_actions():
    inline_kb = [
        [InlineKeyboardButton(text='Добавить/Удалить промокод', callback_data='add_del_promo_next_step')],
        [InlineKeyboardButton(text='Добавить сервер (в разработке)', callback_data='add_server')],
        [InlineKeyboardButton(text='Проверить сервера', callback_data='check_server')],
        [InlineKeyboardButton(text='Рассылка сообщения', callback_data='spamming')],
        [InlineKeyboardButton(text='🏠 На главную', callback_data='get_home')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb)


def add_del_promo_kb():
    inline_kb = [
        [InlineKeyboardButton(text='Добавить промокод', callback_data='add_promo')],
        [InlineKeyboardButton(text='Удалить промокод', callback_data='del_promo')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb)


def check_server_kb(list_of_users: list):

    inline_kb = InlineKeyboardMarkup(inline_keyboard=[])

    for user in list_of_users:
        inline_kb.inline_keyboard.append([InlineKeyboardButton(text=f'{user}', callback_data=f'check-user_{user}')])

    inline_kb.inline_keyboard.append([InlineKeyboardButton(text='🏠 На главную', callback_data='get_home')])

    return inline_kb


def pay(link):
    inline_kb = [
        [InlineKeyboardButton(text='Оплатить', url=link)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb)


def apps():
    inline_kb = [
        [InlineKeyboardButton(text='Клиент для iOS', url='https://apps.apple.com/us/app/outline-app/id1356177741')],
        [InlineKeyboardButton(text='Клиент для Android',
                              url='https://play.google.com'
                                  '/store/apps/details?id=org.outline.android.client&pcampaignid=web_share')],
        [InlineKeyboardButton(text='Клиент для MacOS',
                              url='https://apps.apple.com/us/app/outline-secure-internet-access/id1356178125?mt=12')],
        [InlineKeyboardButton(text='Клиент для Windows', url='https://outline-vpn.com/download.php?os=c_windows')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb)


def guide():
    inline_kb = [
        [InlineKeyboardButton(text='Прочитать', url='https://telegra.ph/Nastrojka-VPN-08-03')],
        [InlineKeyboardButton(text='🏠 На главную', callback_data='get_home')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb)


def payed(payment_system, price):
    inline_kb = [
        [InlineKeyboardButton(text='✅ Оплатил(-а)',
                              callback_data=f'confirm-pay_{payment_system}_{price}')],
        [InlineKeyboardButton(text='❌ Передумал(-а) оплачивать', callback_data='cancel_pay')],
        [InlineKeyboardButton(text='🆘 Сообщить о проблеме', url='tg://resolve?domain=danilserge27')],

    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb)


def cancel_fsm_kb():
    inline_kb = [
        [InlineKeyboardButton(text='Отменить ввод и вернуться в меню', callback_data='cancel_FSM')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb)


def get_key_kb(time_subscribe):
    inline_kb = [
        [InlineKeyboardButton(text='Получить ключ', callback_data=f'get-key_{time_subscribe}')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb)

def target_for_spam():
    inline_kb = [
        [InlineKeyboardButton(text='Разослать ВСЕМ ПОЛЬЗОВАТЕЛЯМ С ПОДПИСКОЙ',
                              callback_data='spam_sub')],
        [InlineKeyboardButton(text='Разослать всем', callback_data='spam_all')],
        [InlineKeyboardButton(text='❌ Отменить', callback_data='cancel_FSM')]
    ]

    return InlineKeyboardMarkup(inline_keyboard=inline_kb)

def return_home():
    inline_kb = [
        [InlineKeyboardButton(text='🏠 На главную', callback_data='get_home')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb)

def add_server():
    inline_kb = [
        [InlineKeyboardButton(text='Добавить сервер', callback_data='setup_new_server')],
        [InlineKeyboardButton(text='❌ Отменить', callback_data='cancel_FSM')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb)
#
# def fakebuy_debug():
#     inline_kb = [
#         [InlineKeyboardButton(text='Типа купил', callback_data='fakebuy')]
#     ]
#     return InlineKeyboardMarkup(inline_keyboard=inline_kb)