from decouple import config
from aiogram import Bot
from outline_vpn.outline_vpn import OutlineVPN

api_url = config('API_URL')
cert_sha256 = config('CERT_SHA')

client = OutlineVPN(api_url=api_url, cert_sha256=cert_sha256)

botik = Bot(token=config('TOKEN'))
