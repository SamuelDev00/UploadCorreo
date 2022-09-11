import asyncio
from bs4 import BeautifulSoup

import Proxy

import aiohttp
from aiohttp_socks import ProxyConnector
from python_socks import ProxyType

from random import random

from typing import Callable
from io import BufferedReader, FileIO
from pathlib import Path

class ProgressFile(BufferedReader):
    def __init__(self, filename, read_callback):
        f = FileIO(file=filename, mode="r")
        self.__read_callback = read_callback
        super().__init__(raw=f)

        self.length = Path(filename).stat().st_size

    def read(self, size=None):
        calc_sz = size
        if not calc_sz:
            calc_sz = self.length - self.tell()
        self.__read_callback(self.tell(), self.length)
        return super(ProgressFile, self).read(size)

class UclvClient(object):
    def __init__(self, user='', password='', proxy: Proxy=None):
        self.username = user
        self.password = password
        self.session = None
        self.url = 'https://correo.uclv.edu.cu/'
        self.eventloop = None
        self.proxy = proxy
        self.MaxTasks: int = 3
        self.TasksInProgress: int = 0
        self.headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"}
    
    async def construct(self):
        self.eventloop = asyncio.get_event_loop()
        connector = aiohttp.TCPConnector(verify_ssl=False)
        if self.proxy:
            connector = ProxyConnector(
                proxy_type=ProxyType.SOCKS5,
                host=self.proxy.ip,
                port=self.proxy.port,
                rdns=True,
                verify_ssl=False
            )
        self.session = aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True),connector=connector)

    async def LogOut(self):
        await self.session.close()
        self.session = aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True),connector=aiohttp.TCPConnector(verify_ssl=False))

    #loguearse en la página
    async def login(self):
        await self.construct()
        try:
            timeout = aiohttp.ClientTimeout(total=20)
            async with self.session.get(self.url, headers=self.headers, timeout=timeout) as response:
                resp = await response.text()
            soup = BeautifulSoup(resp,'html.parser')
            login_csrf = soup.find("input", attrs={"name": "login_csrf"})["value"]
            payload = {'loginOp': 'login',
                       'login_csrf': login_csrf,
                       'username': self.username,
                       'password': self.password,
                       'zrememberme': 1,
                       'client': 'stantard'}
            async with self.session.post(self.url, data=payload, headers=self.headers, timeout=timeout) as response2:
                resp2 = await response2.text()
            counter = 0
            for i in resp2.splitlines():
                if "ZLoginErrorPanel" in i or (0 < counter <= 3):
                    counter += 1
                    print(i)
            if counter>0:
                print('No pude iniciar sesión')
                return False
            else:
                print('He iniciado sesión')
                return True
        except:
            return False

    #subir el archivo
    async def upload_file(self, path: str, progress_callback: Callable=None):
        await asyncio.sleep(random())
        while self.TasksInProgress >= self.MaxTasks:
            await asyncio.sleep(random() * 4 + 1)
        #@S0muell
        self.TasksInProgress += 1

        try:
            url = self.url+'h/search?st=briefcase'
            timeout = aiohttp.ClientTimeout(total=20)
            async with self.session.get(url, headers=self.headers, timeout=timeout) as response:
                resp = await response.text()
            soup = BeautifulSoup(resp,'html.parser')
            sc = soup.find("a", attrs={"id": "NEW_UPLOAD"})["href"].replace("?si=0&amp;so=0&amp;sc=","").replace("&amp;st=briefcase&amp;action=compose","")
            file = ProgressFile(filename=path, read_callback=progress_callback)
            #crear payload
            data = aiohttp.FormData()
            data.add_field('fileUpload', file)
            data.add_field('actionAttachDone', 'Hecho')
            data.add_field('doBriefcaseAction', '1')
            data.add_field('sendUID', 'Hecho')
            timeout = aiohttp.ClientTimeout(connect=30, total=60 * 60)
            url_post = self.url+f'h/search?si=0&so=0&sc={sc}' #smd
            async with self.session.post(url_post, data=data, headers=self.headers, timeout=timeout) as response2:
                resp2 = await response2.text()
            if Path(path).name in resp2:
                return 'https://correo.uclv.edu.cu/home/'+self.username+'/Briefcase/'+Path(path).name+'?auth=co'
        except Exception as ex:
            print(ex)
        
        self.TasksInProgress -= 1

#client = UclvClient('correo@uclv.cu','contraseña')
#loged = asyncio.run(client.login())
#if loged is True:
    #asyncio.run(client.upload_file('file.txt'))
