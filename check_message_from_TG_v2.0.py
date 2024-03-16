import time
from telethon import TelegramClient, events
import csv
import re
import ast
from datetime import datetime

api_id = '23796739'
api_hash = 'b04f272bbefc7b1c6249bdcb3fd8f792'
phone_number = '+996550300129'

client = TelegramClient('phone', api_id, api_hash, system_version='4.16.30-vxCUSTOM')
tg_channel = {"bot": -4120776820}
check_number = ''
while True:
    async def main():
        global check_number
        await client.start(phone_number)
        print("Client Created")
        for channel in tg_channel:
            async for i in (client.iter_messages(tg_channel[channel], limit=1)):
                if i.id != check_number:
                    srt_file = []
                    with open(f'messages_from_{channel}.csv', newline='') as File:
                        reader = csv.reader(File)
                        for row in reader:
                                res_str = row[0].replace('(', '')
                                res_str = res_str.replace('[', '')
                                my_dict = ast.literal_eval(res_str)
                                srt_file.append(my_dict['message.id']) #разобраться добавить описание
                    with open(f'messages_from_{channel}.csv', 'a', newline='', encoding="utf-8") as csvfile:
                        messagewriter = csv.writer(csvfile, delimiter='&', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                        print('save_to_', channel)
                        async for message in client.iter_messages(tg_channel[channel], limit=20):
                            if message.id not in srt_file:
                                coin_find = re.findall('#(\w+)\s', message.text or "") #  изменить на none
                                if type(coin_find) == list:
                                    if coin_find != []:
                                        for find_coin in coin_find:
                                            find_coin_1 = find_coin.replace('_', '')
                                            if find_coin_1 != []:
                                                coin = find_coin_1
                                            else:
                                                coin = None
                                    else:
                                        coin = None
                                else:
                                    coin = coin_find.group(1) if coin_find else None
                                if message.text != None: #поднять выше пере дпроверкой токена, зачем он так делко в коде.
                                    #posSide = "short" if "short" in message.text or "шорт" in message.text or "Short" in message.text else "long" if "лонг" in message.text or "long" in message.text or "Long" in message.text else None
                                    message_text_lower = (message.text).lower()
                                    if "short" in message_text_lower or "шорт" in message_text_lower:
                                        posSide = "short"
                                    elif "long" in message_text_lower or "лонг" in message_text_lower:
                                        posSide = "long"
                                    else:
                                        posSide = None
                                    input_find = re.search(r'твх.+-.+', message.text or "")
                                    input_point = re.findall(r"\d+.\d+|\d+", input_find[0]) if input_find else None
                                    input_point = str(input_point).replace(',', '*') #заменить на json
                                    target_find = re.search(r'цел\w.*($|\n)', message.text or "", flags=re.MULTILINE)
                                    target_point = None # изменить, поставить None выше
                                    if target_find:
                                        pattern = re.compile(r'цел[иь]?\s([\d\s\.$-]+)', re.IGNORECASE)
                                        matches = pattern.findall(target_find[0])
                                        target_point = [re.sub(r'\s*-\s*', ', ', match.strip()).replace('$', '') for match in matches]
                                        target_point = str(target_point).replace(',', '*')
                                    #stop_lose_pattern = r"стоп[^\d]*лосс?[^\d]+([\d\.]+)"
                                    stop_lose_pattern = r"стоп[^\d]*лосс?[^\d]+([\d\.]+)"
                                    stop_lose_matches = re.findall(stop_lose_pattern, message.text or "", re.IGNORECASE)
                                    target_stop_lose = ", ".join(stop_lose_matches) if stop_lose_matches else None
                                    if coin != None and input_point != None and posSide != None and target_point != None and str(input_point) != "[]" and str(target_point) != "[]": # убрать все наны, передать код что бы выходил по нану для каждого метода
                                        data = (
                                            {'message.id': message.id},
                                            {'message.sender_id': message.sender_id},
                                            {'coin': coin},
                                            {'posSide': posSide},
                                            {'input_point': input_point},
                                            {'target_point': target_point},
                                            {'stop_lose': target_stop_lose}
                                        )
                                        messagewriter.writerow([data])
                check_number = i.id
    with client:
        client.loop.run_until_complete(main())
    time.sleep(2)