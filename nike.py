import uuid,requests,json,random,time,datetime,threading,ast,asyncio
from discord_webhook import DiscordEmbed, DiscordWebhook
from classes.utils import Logger, ProxyManager
from ast import literal_eval
from retry import retry

logger = Logger()
monitor_delay = 1

country = 'CA'

if country == 'AU':
	currency = 'AUD'
elif country == 'SG':
	currency = 'SGD'
elif country == 'CA':
	currency = 'CAD'
elif country == 'NO':
	currency = 'NOK'
elif country == 'NZ':
	currency = 'NZD'

# taskNum = 5
quantity = '1'

print('\n')
print('Loading Nike - ' + country + '......')
nikeSku = input('Please enter the product Sku: ')
# nikeSku = '554725-092'



api = 'https://api.nike.com/product_feed/threads/v2?filter=marketplace({})&filter=language(en-GB)&filter=channelId(d9a5bc42-4b9c-4976-858a-f159cf99c647)&filter=productInfo.merchProduct.styleColor({})'.format(country,nikeSku)

webhookUrl = 'https://discordapp.com/api/webhooks/12312312/'
cookielist = literal_eval(open('cookies.txt', 'r').read())

#====================================================================================================================================================================================================#
#--------------------------------------------------------------------- Utilis -----------------------------------------------------------------------------------------------------------------------#
#====================================================================================================================================================================================================#

headers = {
		'accept':'application/json; charset=UTF-8, application/json',
		'accept-encoding':'gzip, deflate, br',
		'accept-language':'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
		'appid':'com.nike.commerce.nikedotcom.web',
		'cloud_stack':'buy_domain',
		'content-length':'495',
		'content-type':'application/json; charset=UTF-8',
		'origin':'https://www.nike.com',
		'sec-fetch-mode':'cors',
		'sec-fetch-site':'same-site',
		'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
		'x-b3-spanname':'CiCCart',
		'x-b3-traceid':'5bec7add-b197-4b65-ab21-52b7432ed4a5',
		'x-nike-visitid':'1',
		'x-nike-visitorid':'18949541-b734-4b4e-ae53-459ca7631783'
}


def success_webhook(checkoutUrl,productName,productDescription,size_selected):
	try:
		webhook = DiscordWebhook(url=webhookUrl, content='')
		embed = DiscordEmbed(title='Manual Checkout Needed!', url=checkoutUrl, description=productName + '\n' + productDescription , color=0x00fea9)
		embed.add_embed_field(name='SKU', value=nikeSku)
		embed.add_embed_field(name='Size', value=str(size_selected))
		embed.set_thumbnail(url=str('https://secure-images.nike.com/is/image/DotCom/{}'.format(nikeSku.replace('-','_'))))
		embed.set_footer(text='Sicko AIO | ' + str(datetime.datetime.now()).split(' ')[1], icon_url='https://cdn.discordapp.com/attachments/21313123/12321312/unknown.png')
		webhook.add_embed(embed)
		webhook.execute()
		logger.success('[SUCCESS] --> Successful Checkout!')
	except:
		success_webhook(checkoutUrl,productName,productDescription,size_selected)



def getProxy():
	# proxy = {}
	proxy = ProxyManager().get_proxy()
	return proxy
#====================================================================================================================================================================================================#
#--------------------------------------------------------------------- Main Code ----------------------------------------------------------------------------------------------------------------------#
#====================================================================================================================================================================================================#

class Nike():
	productInfoResponse = requests.get(api,proxies=getProxy(),timeout=(3,8))
	js = json.loads(productInfoResponse.text)
	availableSkuList = js['objects'][0]['productInfo'][0]['skus']  #skus
	productName = js['objects'][0]['productInfo'][0]['productContent']['title']
	productDescription = js['objects'][0]['productInfo'][0]['productContent']['colorDescription']


	def getProductSku(self):
		productSku = self.availableSkuList[0]['productId']
		return productSku

	def getSizes(self):
		sizedict = {}
		for i in self.availableSkuList:
			sizedict[i['nikeSize']] = i['id']

		return sizedict


	@retry(delay=monitor_delay)
	def monitor(self,size_selected, sizeSku):
		
		try:
			stockEndpoint = 'https://api.nike.com/deliver/available_skus/v1/{}?_{}'.format(sizeSku, str(int(time.time())))

			monitorResponse = requests.get(stockEndpoint, headers=headers , proxies=getProxy(),timeout=(3,8))
			monitorResponse.raise_for_status()

			while json.loads(monitorResponse.text)['available'] != True:
				  
				logger.status('[STATUS] --> Waiting for restock - Size{} Retry in {}s'.format(size_selected,monitor_delay))
				time.sleep(monitor_delay)
				monitorResponse = requests.get(stockEndpoint, headers=headers, proxies=getProxy(),timeout=(3,8))

			return True


		except ValueError:
			logger.error('[ERROR] --> Error Getting Stock info')
			raise

		except requests.exceptions.HTTPError as e:
			logger.error('[ERROR] --> [{}]Error Getting Stock info'.format(monitorResponse.status_code))
			raise

		except Exception as e:
			logger.error('[ERROR] --> Connection Error %s' %e)
			raise

		return False

	@retry(tries=100)
	def addToCart(self, productSku, size_selected, sizeSku):
		global country
		global currency

		atc_payload = {
			"country": country,
			"language": "en-GB",
			"channel": "NIKECOM",
			"cartId": str(uuid.uuid1()),
			"currency": currency,
			"paypalClicked": False,
			"items": [
			{
				"id": productSku,
				"skuId": sizeSku,
				"level": "LOW",
				"quantity": quantity,
				"priceInfo": {
					"price": 140,
					"subtotal": 140,
					"discount": 0,
					"valueAddedServices": 0,
					"total": 140,
					"priceSnapshotId": str(uuid.uuid1()),
					"msrp": 140,
					"fullPrice": 140
				}
			}
		]
		}

		try:
			logger.status('[STATUS] --> Adding to cart - Size' + size_selected)

			cookies = random.choice(cookielist)

			logger.status('[STATUS] --> Submitting Checkout')
			checkoutlink = 'https://api.nike.com/buy/partner_cart_preorder/v1/{}'.format(str(uuid.uuid1()))
			checkoutResponse = requests.put(checkoutlink, headers=headers,data=json.dumps(atc_payload), cookies={'_abck': cookies, 'bm_sz' : bm}, proxies=getProxy(),timeout=(3,8))
			# if '~0~' not in checkoutResponse.cookies:
			checkoutResponse.raise_for_status()

			checkouResponse = requests.get(checkoutlink, headers=headers, proxies=getProxy(),timeout=(3,8))
			while 'COMPLETED' not in checkouResponse.text:
				time.sleep(0.3)
				checkouResponse = requests.get(checkoutlink, headers=headers, proxies=getProxy(),timeout=(3,8))

			if 'response' in checkouResponse.text:
				checkouUrl = json.loads(checkouResponse.text)['response']['redirectUrl']
				success_webhook(checkouUrl, self.productName, self.productDescription, size_selected)

					# return False

			elif 'error' in checkouResponse.text or 'Failed' in checkouResponse.text:
				try:
					logger.error('[ERROR] --> ' + json.loads(checkouResponse.text)['error']['errors'][0]['message'])
				except:
					pass

				time.sleep(5)
				isRestock = self.monitor(size_selected, sizeSku)

				while isRestock != True:
					isRestock = self.monitor(size_selected, sizeSku)
				self.addToCart(productSku, size_selected, sizeSku)


		except json.decoder.JSONDecodeError:
			logger.error('[ERROR] --> Error Getting Checkout Url')
			raise

		except requests.exceptions.HTTPError as e:
			logger.error('[ERROR] --> [{}]Error Adding to Cart'.format(checkouResponse.status_code))

			cookielist.remove(cookies)
			# lock.acquire()
			if len(cookielist) < 1:
				with open('cookies.txt', "w") as fw:
					fw.write('[]')
					fw.close()
			else:
				with open('cookies.txt', "w") as fw:
					fw.write(str(cookielist))
					fw.close()
			#lock.release()	
			raise

		except requests.exceptions.Timeout:
			logger.error('[ERROR] --> Timeout Error')
			raise

		except Exception as e:
			if cookielist == []:
				logger.error('[ERROR] --> Opps, you ran out of the cookies')
			else:
				logger.error('[ERROR] --> %s ' &e)
			raise

		finally:
			return False


def main(size_selected):
	if size_selected == 'RA':
		size_selected = random.choice([*sizedict])

	for key, value in sizedict.items():
		if key == size_selected:
			sizeSku = value

	isRestock = nike.monitor(size_selected,sizeSku)
	while isRestock != True:
		isRestock = nike.monitor(size_selected,sizeSku)

	isCheckout = nike.addToCart(productSku, size_selected, sizeSku)
	while isCheckout != True:
		isCheckout = nike.addToCart(productSku, size_selected, sizeSku)


desire_sizes = input('Please enter the size you want to cart: ')
desire_size_list = desire_sizes.split(',')

nike = Nike()
productSku = nike.getProductSku()
sizedict = nike.getSizes()


pool = []
lock = threading.Lock()
for size_selected in desire_size_list:
	thread = threading.Thread(target=main, args=(size_selected,))
	# (threading.Thread(target=main, args=(desire_size_list,))).start()
	pool.append(thread)

for n in pool:
	n.start()