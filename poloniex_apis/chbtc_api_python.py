import json, urllib2, hashlib,struct,sha,time,sys
from api_key_secret_util import get_chbtc_api_key, get_chbtc_api_secret

import logging
import logging.handlers
import ConfigParser

class Logger():
    def __init__(self, logname, loglevel, logger):
        # 创建一个logger
        self.logger = logging.getLogger(logger)
        self.logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(logname)
        fh.setLevel(logging.DEBUG)

        # 再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        # 定义handler的输出格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        #formatter = logging.format_dict[int(loglevel)]
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def getlog(self):
        return self.logger

class chbtc_api:
	
    def __init__(self, mykey, mysecret):
        self.mykey    = get_chbtc_api_key();
        self.mysecret = get_chbtc_api_secret();

    def __fill(self, value, lenght, fillByte):
        if len(value) >= lenght:
            return value
        else:
            fillSize = lenght - len(value)
        return value + chr(fillByte) * fillSize

    def __doXOr(self, s, value):
        slist = list(s)
        for index in xrange(len(slist)):
            slist[index] = chr(ord(slist[index]) ^ value)
        return "".join(slist)

    def __hmacSign(self, aValue, aKey):
        keyb   = struct.pack("%ds" % len(aKey), aKey)
        value  = struct.pack("%ds" % len(aValue), aValue)
        k_ipad = self.__doXOr(keyb, 0x36)
        k_opad = self.__doXOr(keyb, 0x5c)
        k_ipad = self.__fill(k_ipad, 64, 54)
        k_opad = self.__fill(k_opad, 64, 92)
        m = hashlib.md5()
        m.update(k_ipad)
        m.update(value)
        dg = m.digest()
        
        m = hashlib.md5()
        m.update(k_opad)
        subStr = dg[0:16]
        m.update(subStr)
        dg = m.hexdigest()
        return dg

    def __digest(self, aValue):
        value  = struct.pack("%ds" % len(aValue), aValue)
        print value
        h = sha.new()
        h.update(value)
        dg = h.hexdigest()
        return dg

    def __api_call(self, path, params = ''):
        try:
            SHA_secret = self.__digest(self.mysecret)
            sign = self.__hmacSign(params, SHA_secret)
            reqTime = (int)(time.time()*1000)
            params+= '&sign=%s&reqTime=%d'%(sign, reqTime)
            url = 'https://trade.chbtc.com/api/' + path + '?' + params
            request = urllib2.Request(url)
            response = urllib2.urlopen(request, timeout=2)
            doc = json.loads(response.read())
            return doc
        except Exception,ex:
            print >>sys.stderr, 'chbtc request ex: ', ex
            return None

    def query_account(self):
        try:
            params = "method=getAccountInfo&accesskey="+self.mykey
            path = 'getAccountInfo'
            
            obj = self.__api_call(path, params)
            print obj
            return obj
        except Exception,ex:
            print >>sys.stderr, 'chbtc query_account exception,',ex
            return None


    def sell_order(self, price, amount):
        try:
            params = "method=order&accesskey=" + self.mykey + "&price=" + price + "&amount=" + amount + "&tradeType=0&currency=eth_cny"
            path = 'order'

            obj = self.__api_call(path, params)
            if obj["code"] != 1000:
                logger.error('sell_order : %s : %s', obj["code"], obj["message"])
                return "error"
            return obj
        except Exception, ex:
            print >> sys.stderr, 'chbtc sell_order exception,', ex
            return "error"

    def buy_order(self, price, amount):
        try:
            params = "method=order&accesskey=" + self.mykey + "&price=" + price + "&amount=" + amount + "&tradeType=1&currency=eth_cny"
            path = 'order'

            obj = self.__api_call(path, params)
            if obj["code"] != 1000:
                logger.error('buy_order : %s : %s', obj["code"], obj["message"])
                return "error"
            return obj
        except Exception, ex:
            print >> sys.stderr, 'chbtc buy_order exception,', ex
            return "error"

    def cancel_order(self, orderId):
        try:
            params = "method=cancelOrder&accesskey=" + self.mykey + "&id=" + orderId + "&currency=eth_cny"
            path = 'cancelOrder'
            obj = self.__api_call(path, params)

            if obj["code"] != 1000:
                logger.error('cannel_order : %s : %s : %s', orderId, obj["code"], obj["message"])
                return "error"
            return obj

        except Exception, ex:
            print >> sys.stderr, 'chbtc cannel_order exception,', ex
            return "error"

    def query_order(self, orderId):
        try:
            params = "method=getOrder&accesskey=" + self.mykey + "&id=" + orderId + "&currency=eth_cny"
            path = 'getOrder'
            obj = self.__api_call(path, params)
            return obj

        except Exception, ex:
            print >> sys.stderr, 'chbtc query_order exception,', ex
            return "error"

    def query_market(self):
        try:
            url = "http://api.chbtc.com/data/v1/ticker?currency=eth_cny"
            request = urllib2.Request(url)
            response = urllib2.urlopen(request, timeout=3)
            obj = json.loads(response.read())
            return obj
        except Exception, ex:
            print >> sys.stderr, 'chbtc query_market exception,', ex
            return "error"

    def query_depth(self):
        try:
            url = "http://api.chbtc.com/data/v1/depth?currency=eth_cny&size=5&merge="
            request = urllib2.Request(url)
            response = urllib2.urlopen(request, timeout=3)
            obj = json.loads(response.read())
            return obj
        except Exception, ex:
            print >> sys.stderr, 'chbtc query_depth exception,', ex
            return "error"


logger = Logger(logname='log.txt', loglevel=1, logger="CHBTC").getlog()

if __name__ == '__main__':
    access_key    = 'accesskey'
    access_secret = 'secretkey'

    api = chbtc_api(access_key, access_secret)

    print api.query_account()
