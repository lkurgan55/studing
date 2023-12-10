import aiohttp
import random
import asyncio

async def send_request(expression):
    await asyncio.sleep(random.uniform(0.1, 5.1))
    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://localhost:80/calculate', params={'expression': expression}) as resp:
            print(f"{expression} => {await resp.text()}")

async def main():
    await asyncio.gather(
        send_request("1"),
        send_request("2"),
        send_request("3"),
        send_request("4"),
        send_request("5"),
        send_request("6"),
        send_request("7"),
        send_request("8"),
        send_request("9"),
        send_request("10"),
        send_request("11"),
        send_request("12"),
        send_request("13"),
        send_request("14"),
        send_request("15"),
        send_request("16"),
        send_request("17"),
        send_request("18"),
        send_request("19"),
        send_request("20")
)

asyncio.run(main())
