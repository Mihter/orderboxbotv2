import pandas as pd
import psycopg2 as pg
from sqlalchemy import create_engine

# Подключение к БД
dbname = 'orderboxbotdb'
user = 'postgres'
password = 'sObW}smNk9'
host = 'localhost'
port = '5432'

engine_string = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
engine = create_engine(engine_string)

# Загрузка данных
#ua_df = pd.read_csv('metrics.csv', delimiter=';')
#orders_df = pd.read_csv('orders.csv', delimiter=';')
#surveys_df = pd.read_csv('survey_answers.csv', delimiter=';')

#ua_df.to_sql('user_actions', engine)
#orders_df.to_sql('orders', engine)
#surveys_df.to_sql('survey', engine)

ua_df = pd.read_sql_table('user_actions', engine)
orders_df = pd.read_sql_table('orders', engine)
surveys_df = pd.read_sql_table('survey', engine)

ua_df = ua_df.drop(['timestamp', 'id'], axis=1).drop_duplicates()

start = ua_df[ua_df['action'] == '/start']
want_box = ua_df[ua_df['action'] == 'want_box']
preorder = ua_df[ua_df['action'] == 'preorder']
later_order = ua_df[ua_df['action'] == 'later_order']

start_cnt = len(start)
want_box_cnt = len(want_box)
preorder_cnt = len(preorder)
later_order_cnt = len(later_order)

with open('stats.txt', 'w', encoding='utf-8') as file:
    stats = f'''Всего заказов: {len(orders_df)}
Действия пользователей за все время:

/start - запуск бота
want_box - нажата кнопка \"Хочу коробку\"
preorder - сделан предзаказ, введена дата(-ы), когда нужны коробки
later_order - нажата кнопка \"Закажу позже\"

/start - {start_cnt} чел.
want_box - {want_box_cnt} чел.
preorder - {preorder_cnt} чел.
later_order - {later_order_cnt} чел.

Конверсия из /start в want_box: {round(want_box_cnt / start_cnt * 100, 1)}%
Конверсия из want_box в preorder: {round(preorder_cnt / want_box_cnt * 100, 1)}%
Конверсия из want_box в later_order: {round(later_order_cnt / want_box_cnt * 100, 1)}%

'''
    file.write(stats)

surveys_df['answer'] = surveys_df['answer'].apply(lambda x: x.lower())
surveys_df['obshaga'] = surveys_df['answer'].apply(lambda x: 'да' if x.find('да') != -1 else 'нет')

live_obshaga = surveys_df[surveys_df['obshaga'] == 'да']

with open('stats.txt', 'a', encoding='utf-8') as file:
    file.write(f'Живут в общаге по опросу: {len(live_obshaga)}\n\n')

tg_ids = live_obshaga['tg_id'].values

obshaga_ua = ua_df[ua_df['tg_id'].isin(tg_ids)]
obshaga_want_box = obshaga_ua[obshaga_ua['action'] == 'want_box']
obshaga_preorder = obshaga_ua[obshaga_ua['action'] == 'preorder']
obshaga_later_order = obshaga_ua[obshaga_ua['action'] == 'later_order']

obshaga_want_box_cnt = len(obshaga_want_box)
obshaga_preorder_cnt = len(obshaga_preorder)
obshaga_later_order_cnt = len(obshaga_later_order)

with open('stats.txt', 'a', encoding='utf-8') as file:
    file.write(f'''Из них выполнили действия:
want_box: {obshaga_want_box_cnt} чел.
preorder: {obshaga_preorder_cnt} чел.
later_order: {obshaga_later_order_cnt} чел.

Конверсия из /start в want_box: {round(obshaga_want_box_cnt / len(tg_ids) * 100, 1)}%
Конверсия из want_box в preorder: {round(obshaga_preorder_cnt / obshaga_want_box_cnt * 100, 1)}%
Конверсия из want_box в later_order: {round(obshaga_later_order_cnt / obshaga_want_box_cnt * 100, 1)}%

Все ответы: 

{surveys_df['answer'].value_counts()}''')