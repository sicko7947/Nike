import asyncio,csv,random,time,json,os
from pyppeteer import launch
from classes.utils import Logger, ProxyManager
from classes.devices import Simulator
from queue import Queue
from ast import literal_eval
from retry import retry

logger = Logger()
simulator = Simulator()


global judgequeue
judgequeue = Queue(maxsize=0)

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

def getDevice():
	device_list = []
	for devices in simulator.getDevices():
		device_list.append(devices)

	return random.choice(device_list)

async def block_img_request(req):
	if req.resourceType in ['image', 'media', 'eventsource', 'websocket']:
		await req.abort()
	else:
		await req.continue_()

async def check_status_code(res):
	if 'https://unite.nike.com/login' in res.url:
		if res.status == 401:
			judgequeue.put(True)
			logger.success('[SUCCESS] --> Successfullly Generated 1 Cookie')
		elif res.status == 403:
			judgequeue.put(False)
			logger.error('[ERROR] --> Error Generating Cookies')

async def mouse(page, hasTouch, max_width, max_height):
	[await page.mouse.move(random.randint(0, max_width), random.randint(0,max_height)) for i in range(10)]

async def bring_cookie_back_to_life(page, hasTouch, max_width, max_height):
	logger.status('[STATUS] --> Bringing your cookies back to life!!!')
	if hasTouch:
		[await page.touchscreen.tap(random.randint(0, max_width), random.randint(0,max_height))for i in range(10)]
	else:
		[await page.mouse.move(random.randint(0, max_width), random.randint(0,max_height)) for i in range(10)]
		[await page.mouse.click(random.randint(0, max_width), random.randint(0,max_height)) for i in range(5)]



async def genCookie():
	while True:
		data = genproxy()
		ip_port = data[0]
		username = data[1]
		password = data[2]


		ext_dir = os.getcwd()
		ext_path = ext_dir + '/classes/fpdef'
		browser = await launch(executablePath='C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
							   headless=False,
							   args=[
							   '--proxy-server={}'.format(ip_port), 
							   '--no-sandbox',
							   '--headless',
							   '--log-level=3',
							   '--disable-gpu', 
							   '--disable-application-cache', 
							   '--disable-notifications',
							   '--load-extension={}'.format(ext_path),
							   '--disable-extensions-except={}'.format(ext_path)
							   ])

		page = await browser.newPage()
		await page.waitFor(5000)

		await page.authenticate({
			'username': username,
			'password': password
		});

		await page.setRequestInterception(True)
		page.on('request', block_img_request)
		page.on('response', check_status_code)

		device = getDevice()
		max_width = device['viewport']['width']
		max_height = device['viewport']['height']
		hasTouch = device['viewport']['hasTouch']

		await page.setViewport({"width": device['viewport']['width'], "height": device['viewport']['height'], 
								"deviceScaleFactor": device['viewport']['deviceScaleFactor'], 
								"isMobile": device['viewport']['isMobile'], "hasTouch": hasTouch,
								"isLandscape" : device['viewport']['isLandscape']})
		await page.setUserAgent(device['userAgent'])

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
		await mouse(page,hasTouch,max_width,max_height)
		await mouse(page,hasTouch,max_width,max_height)
		await mouse(page,hasTouch,max_width,max_height)
		await page.mouse.click(random.randint(0, max_width), random.randint(0,max_height))

		email = ''.join(random.sample('zyxwvutsrqponmlkjihgfedcba1234567890', random.randint(1,20))) + '@gmail.com'
		await page.type('input[type="email"]', email);

		await mouse(page,hasTouch,max_width,max_height)
		await page.type('input[type="password"]', str(random.randint(00000000,9999999)));
		await page.click('input[type="button"]')
		await page.waitFor(5000) 

		await mouse(page,hasTouch,max_width,max_height)
		await page.type('input[type="password"]', str(random.randint(00000000,9999999)));
		await page.click('input[type="button"]')
		await page.waitFor(5000) 

		await mouse(page,hasTouch,max_width,max_height)
		# await page.mouse.click(random.randint(0, max_width), random.randint(0,max_height))
		await page.type('input[type="password"]', str(random.randint(00000000,9999999)));
		await mouse(page,hasTouch,max_width,max_height)
		await page.keyboard.press('Enter')
		await page.click('input[type="button"]')
		await page.waitFor(10000)

		result = judgequeue.get()
		if result:
			cookies_list = await page.cookies()

			final_list = []
			for c in cookies_list:
				if c['name'] == '_abck':
					print(c['value'])
					final_list.append(c['value'])


			if final_list:
				output_dir = os.getcwd()
				listdir = os.listdir(output_dir)
				if 'cookies.txt' in listdir:
					curren_list = literal_eval(open('cookies.txt', 'r').read())
						
					for i in final_list:
						curren_list.append(i)

					with open('cookies.txt', "w") as fw:
						fw.write(str(curren_list))
						fw.close()
				else:
					print('[STATUS] --> File is Missing, will create cookies.txt')
					with open('cookies.txt', "w") as fw:  
						fw.write(str(final_list))
						fw.close()

				logger.success('[SUCCESS] --> Successfullly saved a cookie')
			else:
				logger.error('[ERROR] --> Cookie is not valid')

		try:
			await page.close()
			await browser.close()
		except Exception:
			await page.close()
			await browser.close()		
		finally:
			await browser.close()

		logger.status('[STATUS] --> Starting a New Session')
		await asyncio.sleep(random.randint(10,15))
	

tasks = [genCookie() for i in range(10)]
asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))

