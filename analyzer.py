"""
Analyzer for running analysis on given data models :)

Hopefully all the methods in here will be uses for analyzing the data. If that
stops being true and if I were a good developer (it wouldn't have happened in
the first place) I would update this documentation.
"""
import operator

import time
from collections import defaultdict

import poloniex_apis.trading_api as trading_api
import utils
from decimal import Decimal
from poloniex_apis import public_api
from poloniex_apis.api_models.balances import Balances
from poloniex_apis.api_models.deposit_withdrawal_history import DWHistory
from poloniex_apis.api_models.ticker_price import TickerPrice
from poloniex_apis.api_models.trade_history import TradeHistory
from poloniex_apis.public_api import return_usd_bcc
from poloniex_apis.trading_api import sell_usdt_bcc, withdraw
from poloniex_apis.trading_api import buy_usdt_bcc,return_complete_balances,return_deposits_withdrawals
from poloniex_apis.public_api import return_orderbook_usdt_bcc

from poloniex_apis.zb_api_python import zb_api, get_chbtc_api_secret,get_chbtc_api_key, get_zb_bch_address

ERROR_COUNT = 0;
INIT_BCC_AMOUNT = 4.0;
INIT_USDT_AMOUNT = 5000.0;
realtime_bcc_amount = INIT_BCC_AMOUNT;
realtime_usdt_amount = INIT_USDT_AMOUNT;
OP_COUNT =0;
has_paused = False;

def get_zb_balance(currency = 'BCC'):
    zb_api_temp = zb_api(get_chbtc_api_key(),get_chbtc_api_secret());
    account_info = zb_api_temp.query_account();
    for coin in account_info['result']['coins']:
        print "coin info = {}".format(coin);
        if coin['enName'] == currency:
            print "{} balance = {}".format(currency, coin['available']);
            return coin['available'];
    return -1;

def get_overview():
    global OP_COUNT;
    
    global INIT_BCC_AMOUNT;
    global INIT_USDT_AMOUNT;
    global realtime_bcc_amount;
    global realtime_usdt_amount;
    
    """balances = Balances(trading_api.return_complete_balances())
    dw_history = DWHistory(trading_api.return_deposits_withdrawals())
    deposits, withdrawals = dw_history.get_dw_history()
    utils.print_dw_history(deposits, withdrawals)
    balance = dw_history.get_bcc_balance(public_api.return_ticker())
    current = balances.get_bcc_total()

    usd_bcc_price = return_usd_bcc()
    balance_percentage = float("{:.4}".format(current / balance * 100))
    bcc_balance_sum = current - balance
    usd_balance_sum = "{:.2f}".format(bcc_balance_sum * usd_bcc_price)
    """
    if realtime_bcc_amount == INIT_BCC_AMOUNT or realtime_bcc_amount == -1 or realtime_usdt_amount == INIT_USDT_AMOUNT or realtime_usdt_amount == -1:
        realtime_bcc_amount = get_zb_balance('BCC');
        realtime_usdt_amount = get_zb_balance('USDT');
         
    bcc_usdt_price = return_usd_bcc();
    print "bcc usdt price in poloniex ={}".format(bcc_usdt_price);


    count = 0
    last_bcc_price = -1;
    record = open('log.txt','a');
    record.write("----------------------\n");
    record.write(time.ctime()+"\n");

    zb_api1 = zb_api(get_chbtc_api_key(),  get_chbtc_api_secret());
    """zb_api1.query_account();"""
    zb_bcc_market = zb_api1.query_market("bcc_usdt");    
    zb_bcc_orderBook = zb_api1.query_depth("bcc_usdt");
    """print zb_bcc_market;
    print zb_bcc_orderBook;"""
    if zb_bcc_market == "error":
        zb_bcc_price = last_bcc_price;
    else:
        zb_bcc_price = float(zb_bcc_market["ticker"]["last"]);
        last_bcc_price = zb_bcc_price;

    orderBook = return_orderbook_usdt_bcc()
    bid_highest = orderBook["bids"][0];
    bid_price = float(bid_highest[0]);
    bid_amount = float(bid_highest[1]);
    ask_lowest = orderBook["asks"][0];
    ask_price = float(ask_lowest[0]);
    ask_amount = float(ask_lowest[1]);
    print "the highest bid price is {}, amount is {} ".format(bid_price, bid_amount);
    print "the lowest ask price is {}, amount is {}".format(ask_price, ask_amount);
    record.write("the highest bid price is {}, amount is {} \n ".format(bid_price, bid_amount));
    record.write("the lowest ask price is {}, amount is {} \n".format(ask_price, ask_amount));

    """print zb_bcc_price;"""

    
    record.write("BCC price in zb ="+ str(zb_bcc_price)+"\n");
    record.write("POLONIEX BCC/USDT ="+str(bcc_usdt_price)+"\n");
    print("POLONIEX BCC/USDT ="+str(bcc_usdt_price));

    string_zb= "CHBCC BCC/USDT ="+str(zb_bcc_price);
    record.write(string_zb+"\n");
    print string_zb;
    if (bcc_usdt_price > 0) and (zb_bcc_price > 0):
        delta = abs(zb_bcc_price - bcc_usdt_price);
        delta_percent = delta/bcc_usdt_price*100;
        print str(delta_percent)+"%";
        record.write("delta percent ="+str(delta_percent)+"%\n");
        if delta_percent > 1.5:
            print "here is a arbitrage opportunity!!!!";
            OP_COUNT = OP_COUNT + 1;
            print "we have observed "+str(OP_COUNT)+" times opportunities"
            if zb_bcc_price > bcc_usdt_price: 
                """we need to sell out bcc and buy usdt in zb 
                   then sell out usdt and buy bcc in poloniex """
                try:
                    
                    zb_bcc_order_price = float(zb_bcc_orderBook["bids"][0][0]);
                    zb_bcc_order_amount = float(zb_bcc_orderBook["bids"][0][1]);
                    print "zb_bcc_bids_0_price ={}".format(zb_bcc_order_price);
                    """zb_bcc_order_price = float(zb_usdt_orderBook["asks"][9][0]);
                    zb_bcc_order_amount = float(zb_usdt_orderBook["asks"][9][1]);"""
                    double_check_percent = 100*(zb_bcc_order_price-ask_price)/ask_price;
                    print "double check percent ={}".format(double_check_percent);
                    if double_check_percent > 1.0:
                        bcc_trading_amount = min(ask_amount, zb_bcc_order_amount, 1.00);
                        bcc_trading_amount = Decimal(bcc_trading_amount).quantize(Decimal('0.0000'));
                        
                        """
                        zb_api1.sell_bcc_order(zb_bcc_order_price, bcc_trading_amount);
                        buy_usdt_bcc(ask_price, bcc_trading_amount);
                        """
                        print "selling {} bcc in {} price in zb \n".format(bcc_trading_amount, zb_bcc_order_price);
                        print "buying {} bcc in {} price in poloniex \n".format(bcc_trading_amount, ask_price);
                
                        record.write("buying {} bcc in {} price in poloniex \n".format(bcc_trading_amount, ask_price));
                        record.write("selling {} bcc in {} price in zb \n".format(bcc_trading_amount, zb_bcc_order_price));
                        realtime_bcc_amount = realtime_bcc_amount - float(bcc_trading_amount);
                        realtime_usdt_amount = realtime_usdt_amount + float(bcc_trading_amount)*zb_bcc_order_price;
                        print "realtime bcc in zb = {} \n".format(realtime_bcc_amount);
                        print "realtime usdt in zb = {} \n".format(realtime_usdt_amount);
                        if (realtime_bcc_amount < 0.1* INIT_BCC_AMOUNT) or (realtime_ustd_amount < 0.1 * INIT_USDT_AMOUNT):
                            withdraw_between_exchanges(realtime_bcc_amount - INIT_BCC_AMOUNT, realtime_usdt_amount - INIT_USDT_AMOUNT);
        
                    else:
                        print "it is a pity that double check percent is less than 1.0"
                except Exception, ex:
                        print 'zb cannel_order exception,{}'.format(ex);
            else:
                """we need to sell out usdt and buy bcc in zb 
                    then sell out bcc and buy usdt in poloniex """
                try:
                    
                    zb_bcc_order_price = float(zb_bcc_orderBook["asks"][9][0]);
                    zb_bcc_order_amount = float(zb_bcc_orderBook["asks"][9][1]);
                    print "zb_bcc_asks_9_price = {}".format(zb_bcc_order_price);
                    """zb_usdt_order_price = float(zb_usdt_orderBook["bids"][0][0]);
                    zb_usdt_order_amount = float(zb_usdt_orderBook["bids"][0][1]);"""
                    double_check_percent = 100*(bid_price-zb_bcc_order_price)/bid_price;
                    print "double check percent ={}".format(double_check_percent);
                    if double_check_percent > 1.0:
                        bcc_trading_amount = min(bid_amount,  zb_bcc_order_amount, 1.00);
                        bcc_trading_amount = Decimal(bcc_trading_amount).quantize(Decimal('0.0000'));
                        """
                        sell_usdt_bcc(bid_price, bcc_trading_amount);
                        zb_api1.buy_bcc_order(zb_bcc_order_price, bcc_trading_amount);
                        """
                        print "buying {} bcc in {} price in zb \n".format(bcc_trading_amount, zb_bcc_order_price);
                        print "selling {} bcc in {} price in poloniex \n".format(bcc_trading_amount, bid_price);

                        record.write("selling {} bcc in {} price in poloniex \n".format(bcc_trading_amount, bid_price));
                        record.write("buying {} bcc in {} price in zb \n".format(bcc_trading_amount, zb_bcc_order_price));
                        realtime_bcc_amount = realtime_bcc_amount + float(bcc_trading_amount);
                        realtime_usdt_amount = realtime_usdt_amount - float(bcc_trading_amount)*zb_bcc_order_price;
                        print "realtime bcc in zb = {} \n".format(realtime_bcc_amount);
                        print "realtime usdt in zb = {} \n".format(realtime_usdt_amount);
                        if (realtime_bcc_amount < 0.1* INIT_BCC_AMOUNT) or (realtime_ustd_amount < 0.1 * INIT_USDT_AMOUNT):
                            withdraw_between_exchanges(realtime_bcc_amount - INIT_BCC_AMOUNT, realtime_usdt_amount - INIT_USDT_AMOUNT);
                    else:    
                        print "it is a pity that double check percent is less than 1.0"
                except Exception, ex:
                    print 'zb cannel_order exception, {}'.format(ex);
            record.write("!!!Opportunity!!! ="+str(OP_COUNT)+"!!!!\n");
    else:
        count = count + 1;
        print "connection error count ="+str(count);
        record.write("error count ="+str(count)+"!!!!\n");

    """
    usdt_buy_orders = zb_api1.query_buy_orders("usdt_cny");
    print usdt_buy_orders;
    usdt_sell_orders = zb_api1.query_sell_orders("usdt_cny");
    print usdt_sell_orders;

    bcc_buy_orders = zb_api1.query_buy_orders("bcc_cny");
    print bcc_buy_orders;
    bcc_sell_orders = zb_api1.query_sell_orders("bcc_cny");
    print bcc_sell_orders;


    orderBook = return_orderbook_usd_usdt()
    for bids in orderBook["bids"]:
        print "the {} bid is {}".format(count, bids)
        count = count + 1
    count = 0
    for asks in orderBook["asks"]:
        print "the {} ask is {}".format(count, asks)
        count = count + 1
    

    print "---Earnings/Losses Against Balance--"
    print "{} BCC/${}".format(bcc_balance_sum, usd_balance_sum)
    print "BCC_USDT price = {}".format(bcc_usdt_price)
    if balance_percentage < 100:
        print "Stop trading!"
        print "{}%".format(balance_percentage)
    elif balance_percentage < 110:
        print "Still worse than an index."
        print "{}%".format(balance_percentage)
    elif balance_percentage < 150:
        print "Not bad"
        print "{}%".format(balance_percentage)
    elif balance_percentage < 175:
        print "You belong here"
        print "{}%".format(balance_percentage)
    elif balance_percentage < 200:
        print "Like striking crypto-oil"
        print "{}%".format(balance_percentage)
    elif balance_percentage < 250:
        print "On your way to becoming a bitcoin millionaire"
        print "{}%".format(balance_percentage)
    else:
        print "Cryptocurrencies can get heavy, you should send them over to me for safe keeping!"
        print "{}%".format(balance_percentage)
    """
def withdraw_between_exchanges(bcc_amount, usdt_amount):    
    global has_paused;
    has_paused = True;
    if(bcc_amount < 0):
        """
        bcc_amount < 0, needs bcc transfer from poloniex to zb and usdt to poloniex
        """
        print bbc_amount;        
    else:
        """
        bcc_amount > 0, needs bcc transfer from zb to poloniex and usdt to zb
        """
        print bbc_amount;

def withdraw_from_poloniex(currency = 'BCH', amount = '1.0', address = get_zb_bch_address()):
    withdraw(currency, amount, address);
        
def withdraw_from_zb(currency, amount, address):
    withdraw(currency, amount, address);

def sellPoloniexETC():
    orderBook = return_orderbook_usd_usdt();
    bid_highest_in_sell = orderBook["bids"][0];
    bid_price_in_sell = float(bid_highest_in_sell[0]);
    bid_amount_in_sell = float(bid_highest_in_sell[1]);
    sell_usdt_bcc(bid_price_in_sell, min(bid_amount_in_sell, 1.00));

def buyPoloniexETC():
    complete_balance= return_complete_balances();
    print "complete_balance usdt = {}".format(complete_balance["USDT"]);
    orderBook = return_orderbook_usd_usdt();
    asks_lowest_in_function = orderBook["asks"][0];
    ask_price_in_function = float(asks_lowest_in_function[0]);
    ask_amount_in_function = float(asks_lowest_in_function[1]);
    buy_usdt_bcc(ask_price_in_function, min(ask_amount_in_function, 1.00));

def sellCHBTCETC():
    zb_api_trading = zb_api(get_zb_api_key(), get_zb_api_secret());
    zb_usdt_market = zb_api_trading.query_market("usdt_cny");
    print zb_usdt_market;
    last_usdt_price = -1;
    if zb_usdt_market == "error":
        zb_usdt_price = last_usdt_price;
    else:
        zb_usdt_price =zb_usdt_market["ticker"]["last"];
        last_usdt_price = zb_usdt_price;
    if zb_usdt_price > 0:
        """TODO: need to sync amount from different exchanges"""
        zb_api_trading.sell_usdt_order(str(zb_usdt_price), str(1.0));

def buyCHBTCETC():
    zb_api_trading = zb_api(get_zb_api_key(), get_zb_api_secret());
    zb_usdt_market = zb_api_trading.query_market("usdt_cny");
    print zb_usdt_market;
    last_usdt_price = -1;
    if zb_usdt_market == "error":
        zb_usdt_price = last_usdt_price;
    else:
        zb_usdt_price =zb_usdt_market["ticker"]["last"];
        last_usdt_price = zb_usdt_price;
    if zb_usdt_price > 0:
        """TODO: need to sync amount from different exchanges"""
        zb_api_trading.buy_usdt_order(str(zb_usdt_price), str(1.0));

def sellCHBTCBTC():
    zb_api_trading = zb_api(get_zb_api_key(), get_zb_api_secret());
    zb_bcc_market = zb_api_trading.query_market("bcc_cny");
    print zb_bcc_market;
    last_bcc_price = -1;
    if zb_bcc_market == "error":
        zb_bcc_price = last_bcc_price;
    else:
        zb_bcc_price =zb_bcc_market["ticker"]["last"];
        last_bcc_price = zb_bcc_price;
    if zb_bcc_price > 0:
        """TODO: need to sync amount from different exchanges"""
        zb_api_trading.sell_bcc_order(str(zb_bcc_price), str(0.01));

def buyCHBTCBTC():
    zb_api_trading = zb_api(get_zb_api_key(), get_zb_api_secret());
    zb_bcc_market = zb_api_trading.query_market("bcc_cny");
    print zb_bcc_market;
    last_bcc_price = -1;
    if zb_bcc_market == "error":
        zb_bcc_price = last_bcc_price;
    else:
        zb_bcc_price =zb_bcc_market["ticker"]["last"];
        last_bcc_price = zb_bcc_price;
    if zb_bcc_price > 0:
        """TODO: need to sync amount from different exchanges"""
        zb_api_trading.buy_bcc_order(str(zb_bcc_price), str(0.01));

def getCHBTCBTCorders():
    zb_api_trading = zb_api(get_zb_api_key(), get_zb_api_secret());
    zb_bcc_market = zb_api_trading.query_depth("bcc_cny");
    print zb_bcc_market;

def getCHBTCETCorders():
    zb_api_trading = zb_api(get_zb_api_key(), get_zb_api_secret());
    zb_usdt_market = zb_api_trading.query_depth("usdt_cny");
    print zb_usdt_market;

def get_detailed_overview():
    ticker_price = TickerPrice(public_api.return_ticker())
    trade_history = trading_api.return_trade_history()
    print "Warning, if you made non BCC trades, for example, ETH to USDT, some"
    print "of the values may look unusual. Since non BCC trades have not been"
    print "calculated in."
    for ticker in trade_history:
        if ticker.startswith("BCC_"):
            current = list(reversed(trade_history[ticker]))
            bcc_sum = 0
            for trade in current:
                if trade['type'] == 'buy':
                    bcc_sum += float(trade["total"])
                else:
                    # For some reason, the total for sells do not include the
                    # fee so we include it here.
                    bcc_sum -= (float(trade["total"]) * (1 - float(trade["fee"])))
            print "bcc_sum = {}".format(bcc_sum);
            ticker_sum = 0
            for trade in current:
                if trade['type'] == 'buy':
                    ticker_sum += float(trade["amount"])  # Total
                    ticker_sum -= float(trade["amount"]) * float(trade["fee"])  # Fee
                else:
                    ticker_sum -= float(trade["amount"])                
            print "ticker_sum = {}".format(ticker_sum);

            if ticker_sum > -1:  # Set to 0.000001 to hide 0 balances
                current_bcc_sum = float(ticker_price.get_price_for_ticker(ticker)) * ticker_sum
                total_bcc = current_bcc_sum - bcc_sum
                total_usd = float("{:.4}".format(total_bcc * ticker_price.get_price_for_ticker("USDT_BCC")))
                print "--------------{}----------------".format(ticker)
                print "You invested {} BCC for {} {}/{} BCC".format(bcc_sum, ticker_sum, ticker.split("_")[1],
                                                                    current_bcc_sum)
                print "If you sold it all at the current price (assuming enough sell orders)"

                if total_bcc < 0:
                    print utils.bcolors.RED,
                else:
                    print utils.bcolors.GREEN,
                print "{} BCC/{} USD".format(total_bcc, total_usd)
                print utils.bcolors.END_COLOR,

    return current


def calculate_fees():
    # TODO Should this take in the data models or call it itself
    trade_history = TradeHistory(trading_api.return_trade_history())
    all_fees = trade_history.get_all_fees()
    all_prices = public_api.return_ticker()

    fee_dict = defaultdict(float)
    print "--------------All Fees--------------"
    for currency_pair, fees in all_fees.iteritems():
        print "{}={}".format(currency_pair, fees)
        base_currency = currency_pair.split("_")[0]
        fee_dict[base_currency] += fees

    total_fees = 0
    print "-------------Total Fees-------------"
    for currency, fees in fee_dict.iteritems():
        if currency != "BCC":
            if currency == "USDT":
                total_fees += float(all_prices["USDT_BCC"]['last']) * fees
            else:
                total_fees += float(all_prices["BCC_" + currency]['last']) * fees
        else:
            total_fees += fees
    print "Total fees in BCC={}".format(total_fees)

def get_poloniex_withdraw_status():
    result = return_deposits_withdrawals();
    withdraw_result = result['withdrawals'];
    last_result= withdraw_result[len(withdraw_result)-1];
    last_status = last_result['status'];
    if last_status.startswith('COMPLETE') or last_status.startswith('CANCELED'):
        print 'withdraw has been proceed';
        return 2;
    else:
        print 'withdraw is pending';
        return 1;


def get_zb_status():
    zb_api2 = zb_api(get_chbtc_api_key(),  get_chbtc_api_secret()); 
    result = zb_api2.get_zb_withdraw_status('BCC');
    print result;


def get_change_over_time():
    """
    Returns a list of currencies whose volume is over the threshold.
    :return:
    """
    threshold = 1000
    currency_list = []

    volume_data = public_api.return_24_hour_volume()
    for item in volume_data:
        if item.startswith('BCC'):
            if float(volume_data.get(item).get('BCC')) > threshold:
                currency_list.append(item)

    currencies = {}
    for currency_pair in currency_list:
        currencies[currency_pair] = float(volume_data.get(currency_pair).get(u'BCC'))
    sorted_currencies = sorted(currencies.items(), key=operator.itemgetter(1), reverse=True)

    period = 300

    time_segments = [3600, 86400, 172800, 259200, 345600, 604800]

    print "Change over time for BCC traded currencies with volume > 1000 BCC"
    for currency in sorted_currencies:
        now = int(time.time())
        last_week = now - 604800
        history = public_api.return_chart_data(
            period=period,
            currency_pair=currency[0],
            start=last_week,
        )
        time_segment_changes = []
        for segment in time_segments:
            try:
                time_segment_changes.append(_to_percent_change(history[-1]['close']/history[-(segment/period-1)]['close']))
            except KeyError:
                time_segment_changes.append("No data")

        print "Currency: {}, Volume: {}".format(currency[0], currency[1])
        print "  1H: {}, 24H: {}, 2D: {}, 3D: {}, 4D: {}, 1W: {}".format(*time_segment_changes)
        time.sleep(2)


def _to_percent_change(number):
    if not isinstance(number, float):
        number = float(number)
    return "{:.2f}%".format(number * 100 - 100)



