import asyncio,csv,random,time,ast
from pyppeteer import launch
from discord_webhook import DiscordEmbed, DiscordWebhook
from classes.user_agent import UserAgent
from classes.utils import Logger

logger = Logger()
USER_AGENT = UserAgent()

rf = open('proxy.txt','r')
lines=rf.readlines()
rf.close()

def genproxy():
	global lines
	b = random.sample(lines, 1)
	ip_port = b[0].split(':')[0] + ':' +b[0].split(':')[1]
	username = b[0].split(':')[2]
	password = b[0].split(':')[3].replace("\n","")
	return ip_port,username,password

async def block_img_request(req):
	if req.resourceType in ['image', 'media', 'eventsource', 'websocket']:
		await req.abort()
	else:
		await req.continue_()

async def check_status_code(res):
	if 'https://unite.nike.com/login?appVersion=727&experienceVersion=727&uxid=com.nike.commerce.nikedotcom.web' in res.url:
		if res.status == 403:
			isCookie = False
			logger.error('[ERROR] --> Error Generating Cookies')
		else:
			isCookie = True
			logger.sucess('[SUCCESS] --> Successfullly Generated 1 Cookie')


async def Engine():
	data = genproxy()
	ip_port = data[0]
	username = data[1]
	password = data[2]

	browser = await launch(headless=False,
						   args=['--proxy-server={}'.format(ip_port), 
						   '--no-sandbox',
						   # '--headless',
						   '--log-level=3', 
						   '--disable-gpu', 
						   '--disable-application-cache', 
						   '--disable-notifications'
						   ])

	page = await browser.newPage()

	await page.authenticate({
		'username': username,
		'password': password
	});

	await page.setRequestInterception(True)
	page.on('request', block_img_request)
	page.on('response', check_status_code)

	isMobile = random.choice([True,False])
	if isMobile == True:
		hasTouch = True
	else:
		hasTouch = False
	await page.setViewport({"width": random.randint(300,500), "height": random.randint(400,700), "isMobile": isMobile, "hasTouch": hasTouch})
		
	await page.setUserAgent(random.choice(USER_AGENT))

	await page.evaluate('''() => {
			Object.defineProperty(window,"webdriver",{
				value:undefined
			})
			window.navigator.chrome = {
				runtime: {},
				// etc.
			};
			Object.defineProperties(navigator,{
				webdriver:{
					get: () => false
					}
				})
			}
		''')

	await page.goto('https://www.nike.com/au/login')

	email = ''.join(random.sample('zyxwvutsrqponmlkjihgfedcba1234567890', random.randint(0,20))) + '@gmail.com'
	await page.type('input[type="email"]', email);
	await page.type('input[type="password"]', str(random.randint(00000000,9999999)));
	await page.click('input[type="button"]')
	await page.waitFor(5000) 

	await page.type('input[type="password"]', str(random.randint(00000000,9999999)));
	await page.click('input[type="button"]')
	await page.waitFor(5000) 

	await page.type('input[type="password"]', str(random.randint(00000000,9999999)));
	await page.click('input[type="button"]')
	await page.waitFor(5000)
		
	cookies_list = await page.cookies()
	await browser.close()

	cookiedict = {}
	for c in cookies_list:
		cookiedict[c['name']] = c['value']

	logger.success('[SUCCESS] --> Successfullly saved a cookie')
		
	return cookiedict

# loop = asyncio.set_event_loop(asyncio.new_event_loop())
# task = asyncio.ensure_future(genCookie())
# loop.run_until_complete(asyncio.wait(task))

