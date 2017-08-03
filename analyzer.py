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
from poloniex_apis.public_api import return_usd_btc
from poloniex_apis.public_api import return_btc_etc
from poloniex_apis.trading_api import sell_etc_btc
from poloniex_apis.trading_api import buy_etc_btc,return_complete_balances
from poloniex_apis.public_api import return_orderbook_usd_etc
from poloniex_apis.chbtc_api_python import chbtc_api, get_chbtc_api_secret,get_chbtc_api_key

ERROR_COUNT = 0;
BTC_TRADING_AMOUNT = 0;
ETC_TRADING_AMOUNT = 0;

def get_overview():
    """balances = Balances(trading_api.return_complete_balances())
    dw_history = DWHistory(trading_api.return_deposits_withdrawals())
    deposits, withdrawals = dw_history.get_dw_history()
    utils.print_dw_history(deposits, withdrawals)
    balance = dw_history.get_btc_balance(public_api.return_ticker())
    current = balances.get_btc_total()

    usd_btc_price = return_usd_btc()
    balance_percentage = float("{:.4}".format(current / balance * 100))
    btc_balance_sum = current - balance
    usd_balance_sum = "{:.2f}".format(btc_balance_sum * usd_btc_price)
    """
    btc_etc_price = 1/return_btc_etc()

    count = 0
    last_etc_price = -1;
    last_btc_price = -1;
    record = open('log.txt','a');
    record.write("----------------------\n");
    record.write(time.ctime()+"\n");

    chbtc_api1 = chbtc_api(get_chbtc_api_key(),  get_chbtc_api_secret());
    """chbtc_api1.query_account();"""
    chbtc_etc_market = chbtc_api1.query_market("etc_cny");
    chbtc_etc_orderBook = chbtc_api1.query_depth("etc_cny");
    print chbtc_etc_market;
    if chbtc_etc_market == "error":
        chbtc_etc_price = last_etc_price;
    else:
        chbtc_etc_price = chbtc_etc_market["ticker"]["last"];
        last_etc_price = chbtc_etc_price;

    orderBook = return_orderbook_usd_etc()
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

    """print chbtc_etc_price;"""

    chbtc_btc_market = chbtc_api1.query_market("btc_cny");
    chbtc_btc_orderBook = chbtc_api1.query_depth("btc_cny");
    print chbtc_btc_market;
    if chbtc_btc_market == "error":
        chbtc_btc_price = last_btc_price;
    else:
        chbtc_btc_price =chbtc_btc_market["ticker"]["last"];
        last_btc_price = chbtc_btc_price;
    """print chbtc_btc_price;"""
    
    record.write("BTC price in chbtc ="+ str(chbtc_btc_price)+"\n");
    record.write("ETC price in chbtc ="+ str(chbtc_etc_price)+"\n");
    record.write("POLONIEX BTC/ETC ="+str(btc_etc_price)+"\n");
    print("POLONIEX BTC/ETC ="+str(btc_etc_price));

    OP_count = 0;
    chbtc_btc_etc = float(chbtc_btc_price)/float(chbtc_etc_price);
    string_chbtc= "CHBTC BTC/ETC ="+str(chbtc_btc_etc);
    record.write(string_chbtc+"\n");
    print string_chbtc;
    if (chbtc_btc_etc > 0) and (btc_etc_price > 0) and (chbtc_btc_price > 0):
        delta = abs(chbtc_btc_etc - btc_etc_price);
        delta_percent = delta/btc_etc_price*100;
        print str(delta_percent)+"%";
        record.write("delta percent ="+str(delta_percent)+"%\n");
        if delta_percent > 2.0:
            print "here is a arbitrage opportunity!!!!";
            OP_count = OP_count + 1;
            print "we have observed "+str(OP_count)+" times opportunities"
            if chbtc_btc_etc > btc_etc_price: 
                """we need to sell out btc and buy etc in chbtc 
                   then sell out etc and buy btc in poloniex """
                try:
                    
                    etc_trading_amount = min(bid_amount, 1.00);
                    btc_trading_amount = etc_trading_amount/chbtc_btc_etc;
                    btc_trading_amount = Decimal(btc_trading_amount).quantize(Decimal('0.000'));
                    chbtc_api1.sell_btc_order(chbtc_btc_price, btc_trading_amount);
                    chbtc_api1.buy_etc_order(chbtc_etc_price, etc_trading_amount);
                    sell_etc_btc(bid_price, etc_trading_amount);
                    record.write("selling {} etc in {} price in poloniex \n".format(etc_trading_amount, bid_price));
                    record.write("selling {} btc in {} price in chbtc \n".format(btc_trading_amount, chbtc_btc_price));
                    record.write("buying {} etc in {} price in chbtc \n".format(etc_trading_amount, chbtc_etc_price));
                except Exception, ex:
                        print 'chbtc cannel_order exception,'
            else:
                """we need to sell out etc and buy btc in chbtc 
                    then sell out btc and buy etc in poloniex """
                try:
                    etc_trading_amount = min(ask_amount, 1.00);
                    btc_trading_amount = etc_trading_amount / chbtc_btc_etc;
                    btc_trading_amount = Decimal(btc_trading_amount).quantize(Decimal('0.000'));
                    chbtc_api1.sell_etc_order(chbtc_etc_price, etc_trading_amount);
                    buy_etc_btc(ask_price, etc_trading_amount);
                    chbtc_api1.buy_btc_order(chbtc_btc_price, btc_trading_amount);
                    record.write("buying {} etc in {} price in poloniex \n".format(etc_trading_amount, ask_price));
                    record.write("buying {} btc in {} price in chbtc \n".format(btc_trading_amount, chbtc_btc_price));
                    record.write("selling {} etc in {} price in chbtc \n".format(etc_trading_amount, chbtc_etc_price));
                except Exception, ex:
                    print 'chbtc cannel_order exception,'
            record.write("!!!Opportunity!!! ="+str(OP_count)+"!!!!\n");
    else:
        count = count + 1;
        print "connection error count ="+str(count);
        record.write("error count ="+str(count)+"!!!!\n");

    """
    etc_buy_orders = chbtc_api1.query_buy_orders("etc_cny");
    print etc_buy_orders;
    etc_sell_orders = chbtc_api1.query_sell_orders("etc_cny");
    print etc_sell_orders;

    btc_buy_orders = chbtc_api1.query_buy_orders("btc_cny");
    print btc_buy_orders;
    btc_sell_orders = chbtc_api1.query_sell_orders("btc_cny");
    print btc_sell_orders;


    orderBook = return_orderbook_usd_etc()
    for bids in orderBook["bids"]:
        print "the {} bid is {}".format(count, bids)
        count = count + 1
    count = 0
    for asks in orderBook["asks"]:
        print "the {} ask is {}".format(count, asks)
        count = count + 1
    

    print "---Earnings/Losses Against Balance--"
    print "{} BTC/${}".format(btc_balance_sum, usd_balance_sum)
    print "BTC_ETC price = {}".format(btc_etc_price)
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
def sellPoloniexETC():
    orderBook = return_orderbook_usd_etc();
    bid_highest_in_sell = orderBook["bids"][0];
    bid_price_in_sell = float(bid_highest_in_sell[0]);
    bid_amount_in_sell = float(bid_highest_in_sell[1]);
    sell_etc_btc(bid_price_in_sell, min(bid_amount_in_sell, 1.00));

def buyPoloniexETC():
    complete_balance= return_complete_balances();
    print "complete_balance etc = {}".format(complete_balance["ETC"]);
    orderBook = return_orderbook_usd_etc();
    asks_lowest_in_function = orderBook["asks"][0];
    ask_price_in_function = float(asks_lowest_in_function[0]);
    ask_amount_in_function = float(asks_lowest_in_function[1]);
    buy_etc_btc(ask_price_in_function, min(ask_amount_in_function, 1.00));

def sellCHBTCETC():
    chbtc_api_trading = chbtc_api(get_chbtc_api_key(), get_chbtc_api_secret());
    chbtc_etc_market = chbtc_api_trading.query_market("etc_cny");
    print chbtc_etc_market;
    last_etc_price = -1;
    if chbtc_etc_market == "error":
        chbtc_etc_price = last_etc_price;
    else:
        chbtc_etc_price =chbtc_etc_market["ticker"]["last"];
        last_etc_price = chbtc_etc_price;
    if chbtc_etc_price > 0:
        """TODO: need to sync amount from different exchanges"""
        chbtc_api_trading.sell_etc_order(str(chbtc_etc_price), str(1.0));

def buyCHBTCETC():
    chbtc_api_trading = chbtc_api(get_chbtc_api_key(), get_chbtc_api_secret());
    chbtc_etc_market = chbtc_api_trading.query_market("etc_cny");
    print chbtc_etc_market;
    last_etc_price = -1;
    if chbtc_etc_market == "error":
        chbtc_etc_price = last_etc_price;
    else:
        chbtc_etc_price =chbtc_etc_market["ticker"]["last"];
        last_etc_price = chbtc_etc_price;
    if chbtc_etc_price > 0:
        """TODO: need to sync amount from different exchanges"""
        chbtc_api_trading.buy_etc_order(str(chbtc_etc_price), str(1.0));

def sellCHBTCBTC():
    chbtc_api_trading = chbtc_api(get_chbtc_api_key(), get_chbtc_api_secret());
    chbtc_btc_market = chbtc_api_trading.query_market("btc_cny");
    print chbtc_btc_market;
    last_btc_price = -1;
    if chbtc_btc_market == "error":
        chbtc_btc_price = last_btc_price;
    else:
        chbtc_btc_price =chbtc_btc_market["ticker"]["last"];
        last_btc_price = chbtc_btc_price;
    if chbtc_btc_price > 0:
        """TODO: need to sync amount from different exchanges"""
        chbtc_api_trading.sell_btc_order(str(chbtc_btc_price), str(0.01));

def buyCHBTCBTC():
    chbtc_api_trading = chbtc_api(get_chbtc_api_key(), get_chbtc_api_secret());
    chbtc_btc_market = chbtc_api_trading.query_market("btc_cny");
    print chbtc_btc_market;
    last_btc_price = -1;
    if chbtc_btc_market == "error":
        chbtc_btc_price = last_btc_price;
    else:
        chbtc_btc_price =chbtc_btc_market["ticker"]["last"];
        last_btc_price = chbtc_btc_price;
    if chbtc_btc_price > 0:
        """TODO: need to sync amount from different exchanges"""
        chbtc_api_trading.buy_btc_order(str(chbtc_btc_price), str(0.01));

def getCHBTCBTCorders():
    chbtc_api_trading = chbtc_api(get_chbtc_api_key(), get_chbtc_api_secret());
    chbtc_btc_market = chbtc_api_trading.query_depth("btc_cny");
    print chbtc_btc_market;

def getCHBTCETCorders():
    chbtc_api_trading = chbtc_api(get_chbtc_api_key(), get_chbtc_api_secret());
    chbtc_etc_market = chbtc_api_trading.query_depth("etc_cny");
    print chbtc_etc_market;

def get_detailed_overview():
    ticker_price = TickerPrice(public_api.return_ticker())
    trade_history = trading_api.return_trade_history()
    print "Warning, if you made non BTC trades, for example, ETH to ETC, some"
    print "of the values may look unusual. Since non BTC trades have not been"
    print "calculated in."
    for ticker in trade_history:
        if ticker.startswith("BTC_"):
            current = list(reversed(trade_history[ticker]))
            btc_sum = 0
            for trade in current:
                if trade['type'] == 'buy':
                    btc_sum += float(trade["total"])
                else:
                    # For some reason, the total for sells do not include the
                    # fee so we include it here.
                    btc_sum -= (float(trade["total"]) * (1 - float(trade["fee"])))
            print "btc_sum = {}".format(btc_sum);
            ticker_sum = 0
            for trade in current:
                if trade['type'] == 'buy':
                    ticker_sum += float(trade["amount"])  # Total
                    ticker_sum -= float(trade["amount"]) * float(trade["fee"])  # Fee
                else:
                    ticker_sum -= float(trade["amount"])                
            print "ticker_sum = {}".format(ticker_sum);

            if ticker_sum > -1:  # Set to 0.000001 to hide 0 balances
                current_btc_sum = float(ticker_price.get_price_for_ticker(ticker)) * ticker_sum
                total_btc = current_btc_sum - btc_sum
                total_usd = float("{:.4}".format(total_btc * ticker_price.get_price_for_ticker("USDT_BTC")))
                print "--------------{}----------------".format(ticker)
                print "You invested {} BTC for {} {}/{} BTC".format(btc_sum, ticker_sum, ticker.split("_")[1],
                                                                    current_btc_sum)
                print "If you sold it all at the current price (assuming enough sell orders)"

                if total_btc < 0:
                    print utils.bcolors.RED,
                else:
                    print utils.bcolors.GREEN,
                print "{} BTC/{} USD".format(total_btc, total_usd)
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
        if currency != "BTC":
            if currency == "USDT":
                total_fees += float(all_prices["USDT_BTC"]['last']) * fees
            else:
                total_fees += float(all_prices["BTC_" + currency]['last']) * fees
        else:
            total_fees += fees
    print "Total fees in BTC={}".format(total_fees)


def get_change_over_time():
    """
    Returns a list of currencies whose volume is over the threshold.
    :return:
    """
    threshold = 1000
    currency_list = []

    volume_data = public_api.return_24_hour_volume()
    for item in volume_data:
        if item.startswith('BTC'):
            if float(volume_data.get(item).get('BTC')) > threshold:
                currency_list.append(item)

    currencies = {}
    for currency_pair in currency_list:
        currencies[currency_pair] = float(volume_data.get(currency_pair).get(u'BTC'))
    sorted_currencies = sorted(currencies.items(), key=operator.itemgetter(1), reverse=True)

    period = 300

    time_segments = [3600, 86400, 172800, 259200, 345600, 604800]

    print "Change over time for BTC traded currencies with volume > 1000 BTC"
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



