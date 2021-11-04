import requests
import sqlite3


hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) (комп хуйлы)\
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}
db = sqlite3.connect('proxy.db')
cur = db.cursor()


def del_value_from_db(value):
	cur.execute(f'DELETE FROM main WHERE ip = ?', [value])
	db.commit()


def check_ip(ip):
	proxies = {'http': f'http://{ip}', 'https': f'https://{ip}'}
	try:
		r = requests.get('https://ip-api.io/api/json/', headers=hdr, proxies=proxies)
		print(r.json()['country_name'], end='\t')
		return True
	except Exception as e:
		print(e.__class__.__name__, end='\t')
		return False

if __name__ == '__main__':
	for values in cur.execute('SELECT ip, port, type FROM main').fetchall():
		ip, port, proxy_type = values
		proxy_type = proxy_type.split()[0] # i need only first type
		proxy = f'{ip}:{port}'
		
		if check_ip(proxy):
			print(f'{proxy} работает'.center(35, '*'))
		else:
			del_value_from_db(ip)
			print(f'{proxie} говно переделывай')
