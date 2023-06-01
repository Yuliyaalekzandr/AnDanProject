import bs4
import requests
import pandas as pd
import time

pd.options.display.width = 0  # Настройки модуля Пандас

start_time = time.time()  # Задаём начальное время для того, чтобы посмотреть сколько работает алгоритм

parse_data = {'make': [], 'model': [], 'year': [], 'engine_capacity': [], 'power': [], 'fuel_type': [],
              'transmission': [], 'drive_mode': [], 'price': [], 'mileage': []}  # Формируем скелет датасета Пандас
base_url = 'https://drom.ru/auto/used/all/?distance=500'  # Задаём базовую ссылку на сайт, который будем парсить

for region in ('moscow', 'volgograd', 'voronezh', 'chita', 'irkutsk', 'kemerovo', 'krasnodar', 'krasnoyarsk',
               'kurgan', 'nizhniy-novgorod', 'novosibirsk', 'omsk', 'orenburg', 'perm', 'vladivostok', 'ufa',
               'ulan-ude', 'simferopol', 'sevastopol', 'yakutsk'):  # Парсинг будем проводить по этим регионам России
    for page in range(1, 101):  # Возьмём данные с 1 по 100 страницы в каждом регионе, последующие страницы не будут доступны 
        res = requests.get(base_url[:8] + region + '.' + base_url[8:] + f'page{page}/')  # Трансформируем базовую ссылку, чтобы выполнить поиск по региону и странице
        soup = bs4.BeautifulSoup(res.text, 'html.parser')  # Задаём парсер

        cards = soup.select('body > div:nth-child(3) > div.css-1iexluz.e1m0rp603 > div.css-1f36sr9.e1m0rp604 > '
                            'div.css-0.e1m0rp605 > div.css-1173kvb.eojktn00 > div > div > a')  # Парсим карточки автомобилей по css селектору

        for card in cards:  # Цикл для вывода данных из карточки
            try:  # Исключение для карточек, в которых присутствуют пропуски, так как конкретных полей для характеристик машины там нет
                full_name = card.select('div.css-l1wt7n.e3f4v4l2 > span')[0].text  # Достаём полное название автомобиля
                specs = [s.text for s in card.select('div.css-13ocj84.e1icyw250 > div.css-1fe6w6s.e162wx9x0 > span')]  # Список характеристик
                price = card.select('div.css-1dv8s3l.eyvqki91 > span > span')[0].text  # Цену

                if len(specs) != 5:  # Если в характеристиках присутствуют пропуски, то не сохраняем данные в скелет датасета
                    pass
                else:
                    parse_data['make'].append(full_name.split()[0])  # Выделяем из полного названия марку
                    parse_data['model'].append(full_name.split()[1].replace(',', ''))  # Выделяем из полного названия модель
                    parse_data['year'].append(int(full_name.split()[-1]))  # Выделяем из полного названия год производства

                    if ' л ' not in specs[0] and 'л.с.' in specs[0]:  # Делаем обработку отсутствующих значений
                        parse_data['engine_capacity'].append(0)
                        parse_data['power'].append(int(specs[0].split()[0]))
                    elif 'л.с.' not in specs[0]:
                        parse_data['engine_capacity'].append(float(specs[0].split()[0]))
                        parse_data['power'].append(0)
                    else:
                        parse_data['engine_capacity'].append(float(specs[0].split()[0]))
                        parse_data['power'].append(int(specs[0].split()[2][1:]))

                    parse_data['fuel_type'].append(specs[1][:-1])  # Достаём тип топлива из характеристик
                    parse_data['transmission'].append(specs[2][:-1])  # Достаём тип КПП из характеристик
                    parse_data['drive_mode'].append(specs[3][:-1])  # Достаём тип тяги из характеристик
                    parse_data['price'].append(int(price.replace('\xa0', '')))  # Приводим цену к типу int
                    parse_data['mileage'].append(int(''.join([s for s in specs[4] if s.isdigit()])))  # Достаём пробег из характеристик
            except IndexError:
                pass


print([(k, len(v)) for k, v in parse_data.items()])  # Вывод скелета таблицы

df = pd.DataFrame(parse_data)  # Делаем датасет из скелета типа dict
df.to_csv('parsed_drom_ru.csv')  # Выгружаем датасет в csv файл

print(df.head())  # Выводим начало датасета
print(df.info())  # Выводим информацию о датасете
print("--- %s seconds ---" % (time.time() - start_time))  # Выводим количество времени, за которое выполняется программа
