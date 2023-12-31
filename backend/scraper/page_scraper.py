import httpx
from selectolax.parser import HTMLParser
import asyncio


async def get_data(client, hotel):
    try:
        resp = await client.get(hotel)
        if resp.status_code == 200:
            page = HTMLParser(resp.text)
            hotel_element = page.css_first("h1#HEADING")
            address_element = None
            if hotel_element:
                address_element = hotel_element.parent.parent.next.child.child.next
            phone_element = page.css_first("div[data-blcontact='PHONE ']")

            if hotel_element is None:
                return None
            return {"name": hotel_element.text() if hotel_element else None,
                    "phone": phone_element.text() if phone_element else None,
                    "address": address_element.text() if address_element else None,
                    "url": hotel}
        else:
            return None
    except httpx.TimeoutException:
        return None


async def scrape_list(list, user_agent, proxies):
    headers = {"User-Agent": user_agent}
    valid_hotel_list = []
    async with httpx.AsyncClient(headers=headers, proxies=proxies, verify=False) as client:
        tasks = []
        for item in list:
            tasks.append(asyncio.create_task(get_data(client, item)))

        results = await asyncio.gather(*tasks, return_exceptions=True)

    for result in results:
        if result is not None and not isinstance(result, Exception):
            valid_hotel_list.append(result)

    return valid_hotel_list
