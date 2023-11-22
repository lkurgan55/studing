import aiohttp
import asyncio

async def send_request(expression):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://localhost:80/calculate', params={'expression': expression}) as resp:
            print(f"{expression} => {await resp.text()}")

async def main():
    await asyncio.gather(
        send_request("5+5"),
        send_request("5+5-3"),
        send_request("5+5+3"),
        send_request("5+5-2"),
        send_request("5+5%3"),
        send_request("5+5/5"),
        send_request("5+5//5"),
        send_request("5+5-3"),
        send_request("5+11"),
        send_request("(5+5)*8"),
        send_request("5+5-5"),
        send_request("5+5-10")
)


asyncio.run(main())
