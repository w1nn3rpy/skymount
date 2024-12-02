from datetime import datetime

from yoomoney import Client, Quickpay, Authorize
from decouple import config


token = config('YOOMONEY_TOKEN')
client = Client(token)
user = client.account_info()


def math_date():
    """
    Генерация числа из года, дня и минут для создания лейбла
    :return:
    """
    data = datetime.date(datetime.now())
    minutes = datetime.time(datetime.now()).minute
    data_for_individual_label = '{}{}{}{}'.format(
        data.year,
        data.month,
        data.day,
        minutes
    )
    return data_for_individual_label


def payment(is_sum: int, is_label: str) -> str | tuple:
    quickpay = Quickpay(
        receiver=config('YOOMONEY_CARD'),
        quickpay_form='shop',
        targets='Subscribe',
        paymentType='SB',
        sum=is_sum,
        label=is_label
    )
    return quickpay.redirected_url, quickpay.label




# for operation in history.operations:
#     print()
#     print("Operation:", operation.operation_id)
#     print("\tStatus     -->", operation.status)
#     print("\tDatetime   -->", operation.datetime)
#     print("\tTitle      -->", operation.title)
#     print("\tPattern id -->", operation.pattern_id)
#     print("\tDirection  -->", operation.direction)
#     print("\tAmount     -->", operation.amount)
#     print("\tLabel      -->", operation.label)
#     print("\tType       -->", operation.type)


def check_payment(is_label: str):
    history = client.operation_history()
    for operation in history.operations:
        if operation.label == is_label and operation.status.lower() == 'success':
            return int(operation.amount)
    return False


def authorize():
    Authorize(
        client_id=input('client_id: '),
        redirect_uri=input('redirect_uri: '),
        client_secret=input('client_secret: '),
        scope=['account-info',
               'operation-history',
               'operation-details',
               'incoming-transfers',
               'payment-p2p',
               'payment-shop'
               ]
    )