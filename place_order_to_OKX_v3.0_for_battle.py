#import okx.Trade as Trade
import okx.MarketData as MarketData
import okx.Funding as Funding
import okx.MarketData as MarketData
import okx.Account as Account
import okx.Account as Account
import okx.Trade as Trade
import okx.PublicData as PublicData
import csv
import ast
import re
import time
import asyncio
from telethon import TelegramClient


api_id = '23796739'
api_hash = 'b04f272bbefc7b1c6249bdcb3fd8f792'
phone_number = '+996550300129'

async def main():
    client = TelegramClient('anon', api_id, api_hash)
    await client.start()
    entity = -4120776820
    await client.send_message(entity, message_tg)
    await client.disconnect()


api_key = "5a07dc3e-8af4-4787-9b30-59fdd196b1ad"
secret_key = "EBDDA65281C66B82411079103008303E"
passphrase = "Lokilol12331!"
leverage = "3"
min_cost_for_order = 120
flag = "1"  # live trading: 0, demo trading: 1

publicDataAPI = PublicData.PublicAPI(flag = flag)

coin_for_check = ""

while True:

    #print(result_for_coin)

    with open(f'messages_from_bot_for_test.csv', newline='') as File:
        test_cache = []
        lines = File.readlines()
        for row_check in lines[-40:]:
            test_cache.append(row_check)
    with open(f'messages_from_bot.csv', newline='') as file_with_info_about_coin:
        reader = csv.reader(file_with_info_about_coin)
        for row in reader:
            for i in range(len(row)):
                res_str = row[i].replace('(', '')
                res_str = res_str.replace(' ', '')
                res_str = res_str.replace(')', '')
                res_str = res_str.replace('[', '')
                res_str = res_str.replace(']', '')
                if '*' in res_str:
                    res_str = res_str.replace('*', ',')
                    my_dict = ast.literal_eval(res_str)
                else:
                    my_dict = ast.literal_eval(res_str)
                for k, v in my_dict.items():
                    if k == "message.id":
                        message_id = my_dict[k]
                    elif k == "message.sender_id":
                        message_sender_id = my_dict[k]
                    elif k == "coin":
                        coin = my_dict[k]
                    elif k == "posSide":
                        posSide_id = my_dict[k]
                    elif k == "input_point":
                        input_point_id = my_dict[k]
                    elif k == "target_point":
                        target_point = my_dict[k]
                    elif k == "stop_lose":
                        stop_lose = my_dict[k]
            check_for_loop = (message_id, message_sender_id, coin, posSide_id, input_point_id, target_point, stop_lose)
            for test_row in test_cache:
                #print(test_row)
                if str(coin) in str(test_row) and str(posSide_id) in str(test_row):
                    take_order = 1
                    break
                else:
                    take_order = 0
            if take_order != 1:
                    result_for_coin = publicDataAPI.get_instruments(instType="SWAP")
                    if posSide_id == "short":
                        side_to_trade = "sell"
                    else:
                        side_to_trade = "buy"
                    inst_ids = [item["instId"] for item in result_for_coin["data"]]
                    for check_coin in inst_ids:
                        if str(coin.upper()) in str(check_coin) and 'USDT' in str(check_coin): # чекаем надичие коинов на бирже
                            check_coin1 = check_coin
                            break
                        else:
                            check_coin1 = None
                    if check_coin1 != None:
                        set_lever = Account.AccountAPI(api_key, secret_key, passphrase, False, flag)

                        # Set leverage for MARGIN instruments under isolated-margin trade mode at pairs level.
                        result_lever = set_lever.set_leverage(
                            instId=check_coin1,
                            lever=leverage,
                            mgnMode="isolated",
                            posSide=posSide_id,
                        )
                        accountAPI = Account.AccountAPI(api_key , secret_key, passphrase, False, flag)
                        result = accountAPI.get_account_balance()
                        # Доступ к первому элементу списка, а затем к деталям
                        details = result['data'][0]['details']
                        # Поиск информации по USDT
                        usdt_info = next(item for item in details if item['ccy'] == 'USDT')
                        # Вывод cashBal и eq для USDT
                        print(f"Cash Balance: {usdt_info['cashBal']}, Equity: {usdt_info['eq']}")
                        for i in result_for_coin["data"]:
                            if i["instId"] == check_coin1:
                                price_low = i["ctVal"]
                        for iu in result_for_coin["data"]:
                            if iu["instId"] == check_coin1:
                                price_for_tpTrigger = iu["tickSz"]
                        # Retrieve mark price
                        result1 = publicDataAPI.get_mark_price(instType="SWAP",)
                        for i in result1["data"]:
                            if i["instId"] == check_coin1:
                                price_market = i["markPx"]
                        if input_point_id != "None":
                            input_cost = (((' '.join(re.findall(r'\'([^\'\']+)\'', input_point_id)))).replace(',', '.')).split()
                        else:
                            input_cost = None
                        min_price_for_order = (float(price_market) * float(price_low))/int(leverage) # это минимальная цена ордера с плечем
                        if float(usdt_info['cashBal']) >= min_cost_for_order and float(usdt_info['cashBal']) >= ((float(min_price_for_order))*2): #проверяю что балан больше минимальной цена которую мы выставили для торгов, и проверял что баланс больше мин цена вхождения Х2
                            if min_price_for_order < (min_cost_for_order/2): # сравнение выше с ценой мин ставки которую ты установил.
                                current_cost_for_order = int((min_cost_for_order/2) / min_price_for_order)
                                if target_point != None:
                                    TP_for_order = target_point.replace("'", '').split(",")
                                else:
                                    TP_for_order = None
                                if posSide_id == "short":
                                    psition_for_tp = "buy"
                                    num_tp_trigger = 1
                                    if input_cost != None:
                                        if float(price_market) < float(input_cost[1]) and float(price_market) > float(input_cost[0]): # уточнить у артера берем линижний предег вдруг тренд разворот
                                            price = (float(input_cost[1]), float(price_market))
                                        #elif float(price_market) > float(input_cost[1]) and float(price_market) < float(input_cost[1]): #ЕСТЬ НАХУЙ НУЖЕН ОРДЕН НА ПЕРЕД НО ЦЕНА НЕ В ДИАЗПОПЗНЕ РАСЕОМНЕТИРОВАТЬ
                                        #    price = (float(input_cost[0]), float(input_cost[1]))
                                        else:
                                            price = "Not_in_range"
                                    else:
                                        price = (None, float(price_market))
                                elif posSide_id == "long":
                                    psition_for_tp = "sell"
                                    num_tp_trigger = 0
                                    if input_cost != None:
                                        if float(price_market) > float(input_cost[0]) and float(price_market) < float(input_cost[1]):  # уточнить у артера берем линижний предег вдруг тренд разворот
                                            price = (float(input_cost[0]), float(input_cost[1]))
                                        else:
                                            #price = (float(input_cost[0]), float(price_market)) раскоментиь когда кончится бычий рынок
                                            price = "Not_in_range"
                                    else:
                                        price = (float(price_market), None)
                                check_point = 0
                                check_for_skip = 0
                                if price != "Not_in_range":
                                    if None not in price:
                                        price = sorted(price)
                                    for price_order in price:
                                        if price_order == float(price[num_tp_trigger]) and price_order != None:
                                            if stop_lose == None:
                                                if posSide_id == "long":
                                                    SL_calculate = float(price_order) - ((float(price_order) * 0.1) / int(leverage))  # вычиляем стоп лос на 10% с нужным пелечем
                                                elif posSide_id == "short":
                                                    SL_calculate = float(price_order) + ((float(price_order) * 0.1) / int(leverage))
                                            else:
                                                SL_calculate = stop_lose
                                            if TP_for_order == None:
                                                TP_for_order = [1]
                                                money_for_algo_SL = (((current_cost_for_order * min_price_for_order) / (
                                                    len(TP_for_order))) / float(price_low))
                                                TP_for_order = None
                                            else:
                                                money_for_algo_SL = ((((current_cost_for_order * min_price_for_order)/(len(TP_for_order))) / float(price_low))/1000)
                                            formatted_number_SL = "{:.20f}".format(money_for_algo_SL)
                                            formatted_number_SL = ((float(formatted_number_SL)*int(leverage))*8)
                                            tradeAPI = Trade.TradeAPI(api_key, secret_key, passphrase, False, flag)
                                            result_order = tradeAPI.place_order(
                                                instId=check_coin1,
                                                tdMode="isolated",
                                                side=side_to_trade,
                                                posSide=posSide_id,
                                                ordType="limit",
                                                slTriggerPx = SL_calculate,
                                                slOrdPx = formatted_number_SL,
                                                px=price_order,
                                                sz=(current_cost_for_order)
                                            )
                                            if result_order["code"] == "0":
                                                print("Successful main order request，order_id = ",result_order["data"][0]["ordId"])
                                                message_tg = (
                                                f"Successful main order request，order_id = {result_order['data'][0]['ordId']} {check_coin1} {side_to_trade} {posSide_id} {SL_calculate} {formatted_number_SL} {price_order}")
                                                loop = asyncio.get_event_loop()
                                                loop.run_until_complete(main())
                                                if TP_for_order != None:
                                                    money_for_algo_TP = ((((current_cost_for_order * min_price_for_order) / (
                                                        len(TP_for_order))) / float(price_low)))*2
                                                    formatted_number = "{:.20f}".format(money_for_algo_TP)
                                                    formatted_number = (float(formatted_number) * int(leverage))
                                                    for TP_for_order_out in TP_for_order:
                                                        if TP_for_order_out == TP_for_order[-1]:
                                                            formatted_number = (float(formatted_number) * 3)
                                                        tradeAPI1 = Trade.TradeAPI(api_key, secret_key, passphrase, False, flag)
                                                        result = tradeAPI1.place_algo_order(
                                                            instId=check_coin1,
                                                            tdMode="isolated",
                                                            side=psition_for_tp,
                                                            posSide=posSide_id,
                                                            ordType="conditional",
                                                            sz="1",  # order amount: 100USDT
                                                            tpTriggerPx=TP_for_order_out,
                                                            tpOrdPx=formatted_number,
                                                        )
                                                        if result["code"] == "0":
                                                            print(f"Successful TP request, {result}")
                                                            message_tg = (f"Successful TP order request，=  {check_coin1} {psition_for_tp} {posSide_id} {TP_for_order_out}")
                                                            loop = asyncio.get_event_loop()
                                                            loop.run_until_complete(main())
                                                        else:
                                                            print(f"Unsuccessful TP request, {result}")
                                                            message_tg = (f"Unsuccessful TP order request，error_code = {result_order} {check_coin1} {psition_for_tp} {posSide_id} {TP_for_order_out}")
                                                            loop = asyncio.get_event_loop()
                                                            loop.run_until_complete(main())
                                                    check_point = 1
                                                    with open(f'messages_from_bot_for_test.csv', 'a', newline='', encoding="utf-8") as csvfile:
                                                        messagewriter = csv.writer(csvfile, delimiter='&', quotechar='|',quoting=csv.QUOTE_MINIMAL)
                                                        messagewriter.writerow([check_for_loop])
                                                else:
                                                    money_for_algo_TP = ((((current_cost_for_order * min_price_for_order) * 0.25) / float(price_low)))
                                                    formatted_number = "{:.20f}".format(money_for_algo_TP)
                                                    formatted_number = (float(formatted_number) * int(leverage))
                                                    if posSide_id == "long":
                                                        TP_for_order = float(
                                                            (((price_order / 100) * 25) / int(leverage)) + price_order)
                                                    elif posSide_id == "short":
                                                        TP_for_order = float(
                                                            (price_order - ((price_order / 100) * 25) / int(leverage)))
                                                    tradeAPI1 = Trade.TradeAPI(api_key, secret_key, passphrase,
                                                                               False, flag)
                                                    result = tradeAPI1.place_algo_order(
                                                        instId=check_coin1,
                                                        tdMode="isolated",
                                                        side=psition_for_tp,
                                                        posSide=posSide_id,
                                                        ordType="conditional",
                                                        sz="1",  # order amount: 100USDT
                                                        tpTriggerPx=TP_for_order,
                                                        tpOrdPx=formatted_number,
                                                    )
                                                    if result["code"] == "0":
                                                        print(f"Successful TP request, {result}")
                                                        message_tg = (
                                                            f"Successful TP order request，=  {check_coin1} {psition_for_tp} {posSide_id} {TP_for_order}")
                                                        loop = asyncio.get_event_loop()
                                                        loop.run_until_complete(main())
                                                    else:
                                                        print(f"Unsuccessful TP request, {result}")
                                                        message_tg = (
                                                            f"Unsuccessful TP order request，error_code = {result_order} {check_coin1} {psition_for_tp} {posSide_id} {TP_for_order}")
                                                        loop = asyncio.get_event_loop()
                                                        loop.run_until_complete(main())
                                                    check_point = 1
                                                    with open(f'messages_from_bot_for_test.csv', 'a', newline='',
                                                              encoding="utf-8") as csvfile:
                                                        messagewriter = csv.writer(csvfile, delimiter='&',
                                                                                   quotechar='|',
                                                                                   quoting=csv.QUOTE_MINIMAL)
                                                        messagewriter.writerow([check_for_loop])
                                            else:
                                                check_for_skip = 1
                                                print("Unsuccessful order request，error_code = ",result_order["data"][0]["sCode"], ", Error_message = ", result_order["data"][0]["sMsg"])
                                                message_tg = (f"Unsuccessful main order request，error_code = {result_order['data'][0]['sCode']} Error_message =  {result_order['data'][0]['sMsg']} {check_coin1} {psition_for_tp} {posSide_id}")
                                                loop = asyncio.get_event_loop()
                                                loop.run_until_complete(main())
                                                check_point = 1
                                                with open(f'messages_from_bot_for_test.csv', 'a', newline='',
                                                          encoding="utf-8") as csvfile:
                                                    messagewriter = csv.writer(csvfile, delimiter='&', quotechar='|',
                                                                               quoting=csv.QUOTE_MINIMAL)
                                                    messagewriter.writerow([check_for_loop])
                                        else:
                                            if check_for_skip != 1 and price_order != None:
                                                tradeAPI = Trade.TradeAPI(api_key, secret_key, passphrase, False, flag)
                                                result_order1 = tradeAPI.place_order(
                                                    instId=check_coin1,
                                                    tdMode="isolated",
                                                    side=side_to_trade,
                                                    posSide=posSide_id,
                                                    ordType="limit",
                                                    px=price_order,
                                                    sz=current_cost_for_order
                                                )
                                                if result_order1["code"] == "0":
                                                    print("Successful order request，order_id = ", result_order1["data"][0]["ordId"],check_coin1,side_to_trade,posSide_id)
                                                    message_tg = (f"Successful order request without SL，order_id = {result_order1['data'][0]['ordId']} {check_coin1} {side_to_trade} {posSide_id}")
                                                    loop = asyncio.get_event_loop()
                                                    loop.run_until_complete(main())
                                                else:
                                                    print("Unsuccessful order request，error_code = ", result_order1["data"][0]["sCode"],", Error_message = ", result_order1["data"][0]["sMsg"])
                                                    message_tg = (f"Unsuccessful order request error_code = {result_order1['data'][0]['sCode']} Error_message = {result_order1['data'][0]['sMsg']} {check_coin1} {side_to_trade} {posSide_id}")
                                                    loop = asyncio.get_event_loop()
                                                    loop.run_until_complete(main())
                                else:
                                    with open(f'messages_from_bot_for_test.csv', 'a', newline='',
                                              encoding="utf-8") as csvfile_found:
                                        messagewriter_found = csv.writer(csvfile_found, delimiter='&', quotechar='|',
                                                                         quoting=csv.QUOTE_MINIMAL)
                                        messagewriter_found.writerow([check_for_loop])
                                    print(f"эта цена не в дизапозоне для шорт")
                                    message_tg = (f"цена входа находится не в диапозоне т.к. текущая цена = {float(price_market)}")
                                    loop = asyncio.get_event_loop()
                                    loop.run_until_complete(main())
                            else:
                                print(f"you_min_price_/3_less_than_min_order_price_for_{check_coin1}, with 3 leverage")
                                message_tg = (f"you_min_price_/3_less_than_min_order_price_for_{check_coin1}, with 3 leverage")
                                with open(f'messages_from_bot_for_test.csv', 'a', newline='',
                                          encoding="utf-8") as csvfile_found:
                                    messagewriter_found = csv.writer(csvfile_found, delimiter='&', quotechar='|',
                                                                     quoting=csv.QUOTE_MINIMAL)
                                    messagewriter_found.writerow([check_for_loop])
                                loop = asyncio.get_event_loop()
                                loop.run_until_complete(main())
                                break
                        else:
                            print("idi nahuy ypu no have money for min deal with 2 input point")  # сделать псал в телегу иди нахуй у тебя нет денег
                            message_tg = (f'idi nahuy you no have money for min deal with 2 input point')
                            loop = asyncio.get_event_loop()
                            loop.run_until_complete(main())
                    else:
                        print("coin_not_found")
                        message_tg = (f'not_found {coin} on FUTURES')
                        loop = asyncio.get_event_loop()
                        loop.run_until_complete(main())

                        with open(f'messages_from_bot_for_test.csv', 'a', newline='',
                                  encoding="utf-8") as csvfile_found:
                            messagewriter_found = csv.writer(csvfile_found, delimiter='&', quotechar='|',
                                                       quoting=csv.QUOTE_MINIMAL)
                            messagewriter_found.writerow([check_for_loop])
            else:
                coin_found_here = 0
                for test_row1 in test_cache:
                    if str(posSide_id) in str(test_row1) and str(coin) in str(test_row1):
                        coin_found_here = 1
                        break
                if coin_found_here == 0 and coin_for_check != coin:
                    print("we_already_take_this_possition")
                    message_tg = (f'we_already_take_this_possition {coin},{posSide_id} on FUTURES')
                    loop = asyncio.get_event_loop()
                    loop.run_until_complete(main())
                    coin_for_check = coin
                    break
    time.sleep(4)