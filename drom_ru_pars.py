import bs4
import requests
import pandas as pd
import time

pd.options.display.width = 0

start_time = time.time()

parse_data = {'make': [], 'model': [], 'year': [], 'engine_capacity': [], 'power': [], 'fuel_type': [],
              'transmission': [], 'drive_mode': [], 'price': [], 'mileage': []}
base_url = 'https://drom.ru/auto/used/all/?distance=500'

for region in ('moscow', 'volgograd', 'voronezh', 'chita', 'irkutsk', 'kemerovo', 'krasnodar', 'krasnoyarsk',
               'kurgan', 'nizhniy-novgorod', 'novosibirsk', 'omsk', 'orenburg', 'perm', 'vladivostok', 'ufa',
               'ulan-ude', 'simferopol', 'sevastopol', 'yakutsk'):
    for page in range(1, 101):
        res = requests.get(base_url[:8] + region + '.' + base_url[8:] + f'page{page}/')
        soup = bs4.BeautifulSoup(res.text, 'html.parser')

        cards = soup.select('body > div:nth-child(3) > div.css-1iexluz.e1m0rp603 > div.css-1f36sr9.e1m0rp604 > '
                            'div.css-0.e1m0rp605 > div.css-1173kvb.eojktn00 > div > div > a')

        for card in cards:
            try:
                full_name = card.select('div.css-l1wt7n.e3f4v4l2 > span')[0].text
                specs = [s.text for s in card.select('div.css-13ocj84.e1icyw250 > div.css-1fe6w6s.e162wx9x0 > span')]
                price = card.select('div.css-1dv8s3l.eyvqki91 > span > span')[0].text

                if len(specs) != 5:
                    pass
                else:
                    parse_data['make'].append(full_name.split()[0])
                    parse_data['model'].append(full_name.split()[1].replace(',', ''))
                    parse_data['year'].append(int(full_name.split()[-1]))

                    if ' л ' not in specs[0] and 'л.с.' in specs[0]:
                        parse_data['engine_capacity'].append(0)
                        parse_data['power'].append(int(specs[0].split()[0]))
                    elif 'л.с.' not in specs[0]:
                        parse_data['engine_capacity'].append(float(specs[0].split()[0]))
                        parse_data['power'].append(0)
                    else:
                        parse_data['engine_capacity'].append(float(specs[0].split()[0]))
                        parse_data['power'].append(int(specs[0].split()[2][1:]))

                    parse_data['fuel_type'].append(specs[1][:-1])
                    parse_data['transmission'].append(specs[2][:-1])
                    parse_data['drive_mode'].append(specs[3])
                    parse_data['price'].append(int(price.replace('\xa0', '')))
                    parse_data['mileage'].append(int(''.join([s for s in specs[4] if s.isdigit()])))
            except IndexError:
                pass


print([(k, len(v)) for k, v in parse_data.items()])

df = pd.DataFrame(parse_data)
df.to_csv('parsed_drom_ru.csv')

print(df.head())
print(df.info())
print("--- %s seconds ---" % (time.time() - start_time))
