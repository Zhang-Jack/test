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
from poloniex_apis import public_api
from poloniex_apis.api_models.balances import Balances
from poloniex_apis.api_models.deposit_withdrawal_history import DWHistory
from poloniex_apis.api_models.ticker_price import TickerPrice
from poloniex_apis.api_models.trade_history import TradeHistory
from poloniex_apis.public_api import return_usd_btc
from poloniex_apis.public_api import return_btc_etc
from poloniex_apis.public_api import return_orderbook_usd_etc
from poloniex_apis.chbtc_api_python import chbtc_api

def get_overview():
    balances = Balances(trading_api.return_complete_balances())
    dw_history = DWHistory(trading_api.return_deposits_withdrawals())
    deposits, withdrawals = dw_history.get_dw_history()
    utils.print_dw_history(deposits, withdrawals)
    balance = dw_history.get_btc_balance(public_api.return_ticker())
    current = balances.get_btc_total()

    usd_btc_price = return_usd_btc()
    balance_percentage = float("{:.4}".format(current / balance * 100))
    btc_balance_sum = current - balance
    usd_balance_sum = "{:.2f}".format(btc_balance_sum * usd_btc_price)

    btc_etc_price = 1/return_btc_etc()

    count = 0
    last_etc_price = -1;
    last_btc_price = -1;
    record = open('log.txt','a');
    record.write("----------------------\n");
    record.write(time.ctime()+"\n");

    chbtc_api1 = chbtc_api('1ec4b319-74fb-4751-bc8f-8cdf92a73a50','61e66f7c-536b-4fd8-b157-731501ff587f');
    """chbtc_api1.query_account();"""
    chbtc_etc_market = chbtc_api1.query_market("etc_cny");
    """print chbtc_etc_market;"""
    if chbtc_etc_market == "error":
        chbtc_etc_price = last_etc_price;
    else:
        chbtc_etc_price = chbtc_etc_market["ticker"]["last"];
        last_etc_price = chbtc_etc_price;

    """print chbtc_etc_price;"""

    chbtc_btc_market = chbtc_api1.query_market("btc_cny");
    """print chbtc_btc_market;"""
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
    if (chbtc_btc_etc > 0):
        delta = abs(chbtc_btc_etc - btc_etc_price);
        delta_percent = delta/btc_etc_price*100;
        print str(delta_percent)+"%";
        record.write("delta percent ="+str(delta_percent)+"%\n");
        if delta_percent > 3.0:
            print "here is a arbitrage opportunity!!!!";
            OP_count = OP_count + 1;
            print "we have observed "+str(OP_count)+" times opportunities"
             
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

            ticker_sum = 0
            for trade in current:
                if trade['type'] == 'buy':
                    ticker_sum += float(trade["amount"])  # Total
                    ticker_sum -= float(trade["amount"]) * float(trade["fee"])  # Fee
                else:
                    ticker_sum -= float(trade["amount"])
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



