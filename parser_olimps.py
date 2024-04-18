from LxmlSoup import LxmlSoup
import requests

# получаем html код сайта
html = requests.get('https://olimpiada.ru/activities?subject%5B6%5D=on&class=11&type=ind&period_date=&period=year').text

soup = LxmlSoup(html)

# получаем список наименований
links = soup.find_all('span', class_='headline')
# получаем список дат
links2 = soup.find_all('span', class_='headline red')

# сопоставляем наименование с датой
result = []
for i in range(len(links)):
    result.append([links[i].text()])
for i in range(len(links)):
    result[i].append(links2[i].text())