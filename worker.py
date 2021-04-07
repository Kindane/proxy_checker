import requests
from bs4 import BeautifulSoup
import re
import sqlite3

hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}


db = sqlite3.connect('proxy.db')
cur = db.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS main(ip TEXT, port TEXT, type TEXT, county TEXT)')
db.commit()


def get_page_count(url):
	soup = get_soup(url)
	pagination = soup.find('div', class_='pagination')
	last_page = pagination.find('li', class_='next_array').previous_sibling
	return int(last_page.text)


def get_html(url):
	return requests.get(url, headers=hdr).text

def get_soup(url):
	return BeautifulSoup(get_html(url), 'html.parser')


def add_to_db(ip, port, type_of_connection, country):
	cur.execute('INSERT INTO main VALUES(?,?,?,?)', (ip, port, type_of_connection, country))
	db.commit()


def main(url):
	soup = get_soup(url)
	main_table = soup.find('tbody')
	for tr in main_table.findAll('tr'):
		ip = tr.find('td')
		port = ip.next_sibling.text
		ip = ip.text
		country = tr.find('span', class_='country').text
		city = tr.find('span', class_='city').text
		proxie_type = tr.find('td', text=re.compile(r'SOCKS4|HTTP|HTTPS|SOCKS5')).text #SOCK4 || HTTPS e.t.c

		if 'SOCKS' in proxie_type:
			continue # i don't need SOCK proxies
		if len(port) < 4 or  port == '8080':
			continue # bad proxie
		
		if city:
			print(f'IP: {ip} PORT: {port} TYPE: {proxie_type} PLACE: {country} - {city}\n')
			place = country+ ' - ' +city
			add_to_db(ip, port, proxie_type, place)
		else:
			if country:
				print(f'IP: {ip} PORT: {port} TYPE: {proxie_type} PLACE: {country}\n')
				add_to_db(ip, port, proxie_type, country)
			else:
				print(f'IP: {ip} PORT: {port} TYPE: {proxie_type} PLACE: Unknown\n')
				add_to_db(ip, port, proxie_type, 'Unknown')


if __name__ == "__main__":
	url = 'https://hidemy.name/ru/proxy-list/#list'
	max_count = get_page_count(url)
	main(url)
	final_page = (max_count*64)-64
	for _, page in zip(range(max_count), range(64, final_page, 64)):
		# https://hidemy.name/ru/proxy-list/?start=64#list
		# url += 64
		url = 'https://hidemy.name/ru/proxy-list/?start={}#list'.format(page)
		main(url)
