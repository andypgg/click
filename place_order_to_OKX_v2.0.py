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


api_key = "5a07dc3e-8af4-4787-9b30-59fdd196b1ad"
secret_key = "EBDDA65281C66B82411079103008303E"
passphrase = "Lokilol12331!"
leverage = "3"
min_cost_for_order = 120
flag = "1"  # live trading: 0, demo trading: 1

publicDataAPI = PublicData.PublicAPI(flag = flag)

result_for_coin = publicDataAPI.get_instruments(instType = "SWAP")
print(result_for_coin)

with open(f'messages_from_Artur.csv', newline='') as file_with_info_about_coin:
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
        print(message_id, message_sender_id, coin, posSide_id, input_point_id, target_point, stop_lose)
        if posSide_id == "short":
            side_to_trade = "sell"
        else:
            side_to_trade = "buy"
        inst_ids = [item["instId"] for item in result_for_coin["data"]]
        for check_coin in inst_ids:
            if str(coin) in str(check_coin) and 'USDT' in str(check_coin): # чекаем надичие коинов на бирже
                check_coin1 = check_coin
                break
            else:
                check_coin1 = None
        print(check_coin1)
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
                    print(price_for_tpTrigger, "asdadadad")
            # Retrieve mark price
            result1 = publicDataAPI.get_mark_price(instType="SWAP",)
            for i in result1["data"]:
                if i["instId"] == check_coin1:
                    price_market = i["markPx"]
            input_cost = (((' '.join(re.findall(r'\'([^\'\']+)\'', input_point_id)))).replace(',', '.')).split()
            if float(price_market) > float(input_cost[1]):#уточнить у артера берем линижний предег вдруг тренд разворот
                price = (float(input_cost[0]), float(input_cost[1]))
            else:
                price = (float(input_cost[0]), float(price_market))
            min_price_for_order = (float(price_market) * float(price_low))/int(leverage) # это минимальная цена ордера с плечем
            if float(usdt_info['cashBal']) >= min_cost_for_order and float(usdt_info['cashBal']) >= ((float(min_price_for_order))*2): #проверяю что балан больше минимальной цена которую мы выставили для торгов, и проверял что баланс больше мин цена вхождения Х2
                if min_price_for_order < (min_cost_for_order/2): # сравнение выше с ценой мин ставки которую ты установил.
                    current_cost_for_order = int((min_cost_for_order/2) / min_price_for_order)
                    TP_for_order = target_point.replace("'", '').split(",")
                    if posSide_id == "short":
                        num_tp_trigger = 1
                    elif posSide_id == "long":
                        num_tp_trigger = 0
                    for price_order in price:
                        print(price_order)
                        if price_order == float(input_cost[num_tp_trigger]):
                            if stop_lose == None:
                                if posSide_id == "long":
                                    SL_calculate = float(price_order) - ((float(price_order) * 0.1) / int(leverage))  # вычиляем стоп лос на 10% с нужным пелечем
                                elif posSide_id == "short":
                                    SL_calculate = float(price_order) + ((float(price_order) * 0.1) / int(leverage))
                            else:
                                SL_calculate = stop_lose
                            tradeAPI = Trade.TradeAPI(api_key, secret_key, passphrase, False, flag)
                            result_order = tradeAPI.place_order(
                                instId=check_coin1,
                                tdMode="isolated",
                                side=side_to_trade,
                                posSide=posSide_id,
                                ordType="limit",
                                slTriggerPx = SL_calculate,
                                slOrdPx = "-1",
                                px=price_order,
                                sz=(current_cost_for_order+1)
                            )
                            if result_order["code"] == "0":
                                print("Successful order request，order_id = ",result_order["data"][0]["ordId"])
                            else:
                                print("Unsuccessful order request，error_code = ",result_order["data"][0]["sCode"], ", Error_message = ", result_order["data"][0]["sMsg"])
                            money_for_algo_TP = (((current_cost_for_order * min_price_for_order)/(len(TP_for_order))) / int(price_low))
                            formatted_number = "{:.20f}".format(money_for_algo_TP)
                            for TP_for_order_out in TP_for_order:
                                tradeAPI1 = Trade.TradeAPI(api_key, secret_key, passphrase, False, flag)
                                result = tradeAPI1.place_algo_order(
                                    instId=check_coin1,
                                    tdMode="isolated",
                                    side="sell",
                                    posSide="long",
                                    ordType="conditional",
                                    sz="1",               # order amount: 100USDT
                                    tpTriggerPx=TP_for_order_out,
                                    tpOrdPx=formatted_number,
                                )
                                if result["code"] == "0":
                                    print(result)
                                else:
                                    print(result)
                        else:
                            tradeAPI = Trade.TradeAPI(api_key, secret_key, passphrase, False, flag)
                            result_order = tradeAPI.place_order(
                                instId=check_coin1,
                                tdMode="isolated",
                                side=side_to_trade,
                                posSide=posSide_id,
                                ordType="limit",
                                px=price_order,
                                sz=current_cost_for_order
                            )
                            if result_order["code"] == "0":
                                print("Successful order request，order_id = ", result_order["data"][0]["ordId"])
                            else:
                                print("Unsuccessful order request，error_code = ", result_order["data"][0]["sCode"],
                                      ", Error_message = ", result_order["data"][0]["sMsg"])
                else:
                    print(f"you_min_price_/2_less_than_min_order_price_for_{check_coin1}, with 2 leverage")
            else:
                print("idi nahuy ypu no have money for min deal with 2 input point")  # сделать псал в телегу иди нахуй у тебя нет денег
        else:
            print("coin_not_found")




            #print(result_order)