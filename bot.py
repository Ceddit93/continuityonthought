#Or	iginally Written December 2017

#Setting API Keys
from binance.client import Client
client = Client("Public Key to be inserted here", "Secret Key to be inserted here")

import time

import math

from pymarketcap import Pymarketcap
cmc = Pymarketcap()

#Import of pymarketcap has issues upon startup at times, thus the repeated loop of trying to innitiate it is required until it succesfuly initiates

while True:
    try:
        binance = cmc.exchange('binance')
    except:
        pass
    else:
        break

#--------------------------------------
from binance.enums import *

#=======================================================
#Constant Variables
#-----------------
TRX_uptrgtfitprct = 20.0
TRX_lowtrgtfitprct = 19.75
IOTA_uptrgtfitprct = 17.0
IOTA_lowtrgtfitprct = 16.75
XRP_uptrgtfitprct = 15.0
XRP_lowtrgtfitprct = 14.50
BNB_uptrgtfitprct = 13.0
BNB_lowtrgtfitprct = 12.50
ADA_uptrgtfitprct = 11.0
ADA_lowtrgtfitprct = 10.50
LTC_uptrgtfitprct = 10.0
LTC_lowtrgtfitprct = 9.50
XLM_uptrgtfitprct = 9.0
XLM_lowtrgtfitprct = 8.00
SALT_uptrgtfitprct = 4.0
SALT_lowtrgtfitprct = 3.25
SUB_uptrgtfitprct = 4.0
SUB_lowtrgtfitprct = 3.25

#The above variables are the range within which we wish to trade each coin expressed as a percentage of our total assets
#======================================================

#Investment model
#if perctrx > uptargetperctrx
#		if candlestick condition to sell or hold
#if perctrx < lowtargetperctrx
#		if candlestick condition to buy or hold

#===================================================
#order = client.order_market_buy(
#    symbol='TickerBTC',
#    quantity=()

#order = client.order_market_sell(
#    symbol='TickerBTC',
#    quantity=()
#===================================================
#Master Code
#-----------

#ticker = 'TRX-BTC'
#ind = [x for x in range(len(binance)) if binance[x]['market'] == ticker][0]
#price = binance[ind]['price_usd']
#========================================
#Functions
#----------------------------------------
#Returns candlestick data from the web - this is used later to make buy/sell decisions
def colour(oursymbol):
    candles = client.get_klines(symbol = oursymbol, interval=KLINE_INTERVAL_30MINUTE)

    close = float(candles[-1][4])
    _open = float(candles[-1][1])

    return float(((close - _open)/_open)*100)

#===================================================
#Redistribute Function

#This function redistributes our assets amongst each coin such that we can stay within the inteded percentage range for each coin

def redistributeFunc(ourCoin):
    if ourCoin == 'TRX':
        trgtfitprct = TRX_uptrgtfitprct
        coinSymbol = 'TRXBTC'

    elif ourCoin == 'IOTA':
        trgtfitprct = IOTA_uptrgtfitprct
        coinSymbol = 'IOTABTC'

    elif ourCoin == 'XRP':
        trgtfitprct = XRP_lowtrgtfitprct
        coinSymbol = 'XRPBTC'

    elif ourCoin == 'BNB':
        trgtfitprct = BNB_lowtrgtfitprct
        coinSymbol = 'BNBBTC'

    elif ourCoin == 'ADA':
        trgtfitprct = ADA_lowtrgtfitprct
        coinSymbol = 'ADABTC'

    elif ourCoin == 'LTC':
        trgtfitprct = LTC_lowtrgtfitprct
        coinSymbol = 'LTCBTC'

    elif ourCoin == 'XLM':
        trgtfitprct = XLM_lowtrgtfitprct
        coinSymbol = 'XLMBTC'

    elif ourCoin == 'SALT':
        trgtfitprct = SALT_uptrgtfitprct
        coinSymbol = 'SALTBTC'

    elif ourCoin == 'SUB':
        trgtfitprct = SUB_uptrgtfitprct
        coinSymbol = 'SUBBTC'

    btcbalance = client.get_asset_balance(asset='BTC')
    qbtc = float(btcbalance['free'])

    redist = float((qbtc*0.5)*(trgtfitprct/100))

    stepSizefctr = client.get_symbol_info(coinSymbol)['filters'][1]['stepSize']
    lotSizefctr = int(round(math.log10(float(stepSizefctr)), 0))*int(-1)
    minQuant = float(client.get_symbol_info(coinSymbol)['filters'][1]['minQty'])
    maxQuant = float(client.get_symbol_info(coinSymbol)['filters'][1]['maxQty'])

    if minQuant < redist < maxQuant:
        client.order_market_buy(symbol = coinSymbol, quantity = round(redist, lotSizefctr))
        print('Redistributed BTC to ' + coinSymbol + ', bought ' + str(redist))
    else:
        print('Redistribution to ' + coinSymbol + 'did not meet conditions; tried to buy' + str(redist))


#=======================================================
#qrestoredown is quantity needed to rest to lowtrgtfitprct
#(lowtrgtfitprct/100)vAssets = newvalue_ticker
#newvalue_ticker/pticker = new quantity
#sell ticker at market with quantity(current asset balance - new quantity)


#qrestoreup is quantity needed to rest to uptrgtfitprct

def oursymbolDIR(our_symbol):
    return [x for x in range(len(client.get_all_tickers())) if client.get_all_tickers()[x]['symbol'] == our_symbol][0]

#Finds the dictionary within which the BNBBTC price is stored
#=======================================================
#Tether Function Code

#This is a failsafe function which converts the majority of our assets into USD_Teather when the entire market takes a downturn. It also buys back our traded coins when the market stabilizes again

def colourFunc(our_symbol):
    candles_coin = client.get_klines(symbol = our_symbol, interval=KLINE_INTERVAL_4HOUR)
    coin_close = float(candles_coin[-1][4])
    coin_open = float(candles_coin[-1][1])
    return float((coin_close - coin_open)*100/coin_open)

def colourPreFunc(our_symbol):
    candles_coin = client.get_klines(symbol = our_symbol, interval=KLINE_INTERVAL_4HOUR)
    coin_closepre = float(candles_coin[-2][4])
    coin_openpre = float(candles_coin[-2][1])
    return float((coin_closepre - coin_openpre)*100/coin_openpre)


def tetherFunc():
    avg_clr = (colourFunc('TRXBTC') + colourFunc('IOTABTC') + colourFunc('BNBBTC') + colourFunc('ADABTC') + colourFunc('LTCBTC') + colourFunc('XLMBTC') + colourFunc('SALTBTC') + colourFunc('SUBBTC'))/9
    print('AvgColour is ' + str(avg_clr))

    avgclrpre = (colourPreFunc('TRXBTC') + colourPreFunc('IOTABTC') + colourPreFunc('BNBBTC') + colourPreFunc('ADABTC') + colourPreFunc('LTCBTC') + colourPreFunc('XLMBTC') + colourPreFunc('SALTBTC') + colourPreFunc('SUBBTC'))/9
    print('Avg Pre Colour is ' + str(avgclrpre))

    btcbalance = client.get_asset_balance(asset='BTC')
    qbtc = float(btcbalance['free'])

    Qtether = float(((math.sqrt(math.fabs(avgclrpre)))/100)*qbtc)

    magprechange = math.fabs(avgclrpre)

    if magprechange > 100:
        q_mkt = qbtc
    elif magprechange < 100:
        q_mkt = Qtether

    stepSizefctr = client.get_symbol_info('BTCUSDT')['filters'][1]['stepSize']
    lotSizefctr = int(round(math.log10(float(stepSizefctr)), 0))*int(-1)
    minQuant = float(client.get_symbol_info('BTCUSDT')['filters'][1]['minQty'])
    maxQuant = float(client.get_symbol_info('BTCUSDT')['filters'][1]['maxQty'])

    magchange = math.fabs(avg_clr)

    if magchange >= 10:
        if avg_clr > 0 and minQuant < q_mkt < maxQuant:
            client.order_market_sell(symbol = 'BTCUSDT', quantity = round(q_mkt, lotSizefctr))
            print('Sold BTCUSDT')

        elif avg_clr < 0 and minQuant < q_mkt < maxQuant:
            client.order_market_buy(symbol = 'BTCUSDT', quantity = round(q_mkt, lotSizefctr))
            print('Bought BTCUSDT')
#=======================================================
def execution(coin):

#This function actually does the buying and selling of coins and adjusts how much to buy or sell depending on the worth of our total assets

    if coin == 'TRX':
        lowtrgtfitprct = TRX_lowtrgtfitprct
        uptrgtfitprct = TRX_uptrgtfitprct
        pcoin = ptrx
        qcoin = qtrx
        perccoin = perctrx
        oursymbol = 'TRXBTC'
        symbolDIR = trxDIR

    elif coin == 'IOTA':
        lowtrgtfitprct = IOTA_lowtrgtfitprct
        uptrgtfitprct = IOTA_uptrgtfitprct
        pcoin = piota
        qcoin = qiota
        perccoin = perciota
        oursymbol = 'IOTABTC'
        symbolDIR = iotaDIR

    elif coin == 'XRP':
        lowtrgtfitprct = XRP_lowtrgtfitprct
        uptrgtfitprct = XRP_uptrgtfitprct
        pcoin = pxrp
        qcoin = qxrp
        perccoin = percxrp
        oursymbol = 'XRPBTC'
        symbolDIR = xrpDIR

    elif coin == 'BNB':
        lowtrgtfitprct = BNB_lowtrgtfitprct
        uptrgtfitprct = BNB_uptrgtfitprct
        pcoin = pbnb
        qcoin = qbnb
        perccoin = percbnb
        oursymbol = 'BNBBTC'
        symbolDIR = bnbDIR

    elif coin == 'ADA':
        lowtrgtfitprct = ADA_lowtrgtfitprct
        uptrgtfitprct = ADA_uptrgtfitprct
        pcoin = pada
        qcoin = qada
        perccoin = percada
        oursymbol = 'ADABTC'
        symbolDIR = adaDIR

    elif coin == 'LTC':
        lowtrgtfitprct = LTC_lowtrgtfitprct
        uptrgtfitprct = LTC_uptrgtfitprct
        pcoin = pltc
        qcoin = qltc
        perccoin = percltc
        oursymbol = 'LTCBTC'
        symbolDIR = ltcDIR

    elif coin == 'XLM':
        lowtrgtfitprct = XLM_lowtrgtfitprct
        uptrgtfitprct = XLM_uptrgtfitprct
        pcoin = pxlm
        qcoin = qxlm
        perccoin = percxlm
        oursymbol = 'XLMBTC'
        symbolDIR = xlmDIR

    elif coin == 'SALT':
        lowtrgtfitprct = SALT_lowtrgtfitprct
        uptrgtfitprct = SALT_uptrgtfitprct
        pcoin = psalt
        qcoin = qsalt
        perccoin = percsalt
        oursymbol = 'SALTBTC'
        symbolDIR = saltDIR

    elif coin == 'SUB':
        lowtrgtfitprct = SUB_lowtrgtfitprct
        uptrgtfitprct = SUB_uptrgtfitprct
        pcoin = psub
        qcoin = qsub
        perccoin = percsub
        oursymbol = 'SUBBTC'
        symbolDIR = subDIR

    stepSizefctr = client.get_symbol_info(oursymbol)['filters'][1]['stepSize']
    lotSizefctr = int(round(math.log10(float(stepSizefctr)), 0))*int(-1)
    minQuant = float(client.get_symbol_info(oursymbol)['filters'][1]['minQty'])
    maxQuant = float(client.get_symbol_info(oursymbol)['filters'][1]['maxQty'])
    coinValBTC = float(client.get_all_tickers()[symbolDIR]['price'])
    btcbalance = client.get_asset_balance(asset='BTC')
    qbtc = float(btcbalance['free'])


    if perccoin > uptrgtfitprct:
        newvalue = (((float(lowtrgtfitprct))/100)*vAssets)
        newquantity = (float(newvalue))/(float(pcoin))
        qrestoredown = round(float(qcoin) - float(newquantity), lotSizefctr)

        if colour(oursymbol) < 0.0 and minQuant < qrestoredown < maxQuant and math.fabs(colour(oursymbol)) >= 1.11 and pcoin*qrestoredown >= 5.0:
            client.order_market_sell(symbol = oursymbol, quantity = qrestoredown)
            return 'sold ' + oursymbol + ', ' + str(qrestoredown)
        else:
            return 'restoredown is ' + str(qrestoredown)

    elif perccoin < lowtrgtfitprct:
        newvalue = (((float(uptrgtfitprct))/100)*vAssets)
        newquantity = (float(newvalue))/(float(pcoin))
        qrestoreup = round(float(newquantity) - float(qcoin), lotSizefctr)
        qValBTC = qrestoreup*coinValBTC

        if colour(oursymbol) > 0.0 and minQuant < qrestoreup < maxQuant and qValBTC <= qbtc and math.fabs(colour(oursymbol)) >= 1.11 and pcoin*qrestoreup >= 5.0:
            client.order_market_buy(symbol = oursymbol, quantity = qrestoreup)
            return 'bought ' + oursymbol + ', ' + str(qrestoreup)
        else:
            return 'restoreup is ' + str(qrestoreup)
#----------------------------------------------
#MAIN FUNCTION

#This is the main function and is actually what is running our bot 

while True:
    trxDIR = oursymbolDIR('TRXBTC')
    iotaDIR = oursymbolDIR('IOTABTC')
    xrpDIR = oursymbolDIR('XRPBTC')
    bnbDIR = oursymbolDIR('BNBBTC')
    adaDIR = oursymbolDIR('ADABTC')
    ltcDIR = oursymbolDIR('LTCBTC')
    xlmDIR = oursymbolDIR('XLMBTC')
    saltDIR = oursymbolDIR('SALTBTC')
    subDIR = oursymbolDIR('SUBBTC')

    count = 0
    t_end = time.time() + 60 * 60 * 24
    while time.time() < t_end:
        #---------------------------------------
        try:
            binance = cmc.exchange('binance')
              #test
            #btc
              #price

            pbtc = 15000

                #Quantity
            btcbalance = client.get_asset_balance(asset='BTC')
            qbtc = float(btcbalance['free'])

              #Total Value
            vbtc = pbtc*qbtc

            #trx
              #price
            trx = [x for x in range(len(binance)) if binance[x]['market'] == 'TRX-BTC'][0]
            ptrx = float(binance[trx]['price_usd'])

              #Quantity
            trxbalance = client.get_asset_balance(asset='TRX')
            qtrx = float(trxbalance['free'])

              #Total Value
            vtrx = ptrx*qtrx

            #iota
              #price
            iota = [x for x in range(len(binance)) if binance[x]['market'] == 'IOTA-BTC'][0]
            piota = float(binance[iota]['price_usd'])

              #Quantity
            iotabalance = client.get_asset_balance(asset='IOTA')
            qiota = float(iotabalance['free'])

              #Total Value
            viota = piota*qiota

            #xrp
              #price
            xrp = [x for x in range(len(binance)) if binance[x]['market'] == 'XRP-BTC'][0]
            pxrp = float(binance[xrp]['price_usd'])

              #Quantity
            xrpbalance = client.get_asset_balance(asset='XRP')
            qxrp = float(xrpbalance['free'])

              #Total Value
            vxrp = pxrp*qxrp

            #bnb
              #price
            bnb = [x for x in range(len(binance)) if binance[x]['market'] == 'BNB-BTC'][0]
            pbnb = float(binance[bnb]['price_usd'])

              #Quantity
            bnbbalance = client.get_asset_balance(asset='BNB')
            qbnb = float(bnbbalance['free'])

              #Total Value
            vbnb = pbnb*qbnb

            #ada
              #price
            ada = [x for x in range(len(binance)) if binance[x]['market'] == 'ADA-BTC'][0]
            pada = float(binance[ada]['price_usd'])

              #Quantity
            adabalance = client.get_asset_balance(asset='ADA')
            qada = float(adabalance['free'])

              #Total Value
            vada = pada*qada

            #ltc
              #price
            ltc = [x for x in range(len(binance)) if binance[x]['market'] == 'LTC-BTC'][0]
            pltc = float(binance[ltc]['price_usd'])

              #Quantity
            ltcbalance = client.get_asset_balance(asset='LTC')
            qltc = float(ltcbalance['free'])

              #Total Value
            vltc = pltc*qltc

            #xlm
              #price
            xlm = [x for x in range(len(binance)) if binance[x]['market'] == 'XLM-BTC'][0]
            pxlm = float(binance[xlm]['price_usd'])

              #Quantity
            xlmbalance = client.get_asset_balance(asset='XLM')
            qxlm = float(xlmbalance['free'])

              #Total Value
            vxlm = pxlm*qxlm

            #salt
              #price
            salt = [x for x in range(len(binance)) if binance[x]['market'] == 'SALT-BTC'][0]
            psalt = float(binance[salt]['price_usd'])

              #Quantity
            saltbalance = client.get_asset_balance(asset='SALT')
            qsalt = float(saltbalance['free'])

              #Total Value
            vsalt = psalt*qsalt

            #sub
              #price
            sub = [x for x in range(len(binance)) if binance[x]['market'] == 'SUB-BTC'][0]
            psub = float(binance[sub]['price_usd'])

              #Quantity
            subbalance = client.get_asset_balance(asset='SUB')
            qsub = float(subbalance['free'])

              #Total Value
            vsub = psub*qsub

            #-------------------------------------------------------
            #Total Assets
            vAssets = vtrx + viota + vxrp + vbnb + vada + vltc + vxlm + vsalt + vsub
            print(vAssets + vbtc)

            #percentages
            perctrx = vtrx/vAssets*100
            perciota = viota/vAssets*100
            percxrp = vxrp/vAssets*100
            percbnb = vbnb/vAssets*100
            percada = vada/vAssets*100
            percltc = vltc/vAssets*100
            percxlm = vxlm/vAssets*100
            percsalt = vsalt/vAssets*100
            percsub = vsub/vAssets*100
            #percbtc = vbtc/vAssets*100
            print(perctrx, perciota, percxrp, percbnb, percada, percltc, percxlm, percsalt, percsub)

            #-------------------------------------------------------


            #=======================================================

            #=======================================================
            #Bot Code
            tetherFunc()

            print(execution('TRX'))
            print(execution('IOTA'))
            print(execution('XRP'))
            print(execution('BNB'))
            print(execution('ADA'))
            print(execution('LTC'))
            print(execution('XLM'))
            print(execution('SALT'))
            print(execution('SUB'))
        except:
            pass
        else:
            pass
        print(count)
        count += 1
    redistributeFunc('TRX')
    redistributeFunc('IOTA')
    redistributeFunc('XRP')
    redistributeFunc('BNB')
    redistributeFunc('ADA')
    redistributeFunc('LTC')
    redistributeFunc('XLM')
    redistributeFunc('SALT')
    redistributeFunc('SUB')
// Copyright 2012 Google Inc. All rights reserved.

(function(w, g) {
    w[g] = w[g] || {};
    w[g].e = function(s) {
        return eval(s);
    }
    ;
}
)(window, 'google_tag_manager');

(function() {

    var data = {
        "resource": {
            "version": "81",

            "macros": [{
                "function": "__e"
            }, {
                "function": "__e"
            }, {
                "function": "__u",
                "vtp_component": "HOST",
                "vtp_enableMultiQueryKeys": false,
                "vtp_enableIgnoreEmptyQueryParam": false
            }, {
                "function": "__v",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": false,
                "vtp_name": "eventCategory"
            }, {
                "function": "__jsm",
                "vtp_javascript": ["template", "(function(){var b=document.URL,e=\"csrftoken\",d=b.split(\"?\");if(1\u003Cd.length\u0026\u0026-1\u003Cd[1].indexOf(e)){var a=d[1];b={};a=a.split(\"\\x26\");for(var c=0;c\u003Ca.length;c++)a[c]=a[c].split(\"\\x3d\"),b[a[c][0]]=a[c][1];delete b[e];return e=d[0]+\"?\"+JSON.stringify(b).replace(\/[\"\\{\\}]\/g,\"\").replace(\/:\/g,\"\\x3d\").replace(\/,\/g,\"\\x26\")}return b})();"]
            }, {
                "function": "__cvt_32196322_685",
                "vtp_type": "page_load_info",
                "vtp_key": "userid"
            }, {
                "function": "__v",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": false,
                "vtp_name": "elementid"
            }, {
                "function": "__cvt_32196322_685",
                "vtp_type": "page_load_info",
                "vtp_key": "bncuuid"
            }, {
                "function": "__cvt_32196322_685",
                "vtp_type": "page_load_info",
                "vtp_key": "pageName"
            }, {
                "function": "__v",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": false,
                "vtp_name": "layout"
            }, {
                "function": "__cid"
            }, {
                "function": "__u",
                "vtp_component": "QUERY",
                "vtp_queryKey": "ref",
                "vtp_enableMultiQueryKeys": false,
                "vtp_enableIgnoreEmptyQueryParam": false
            }, {
                "function": "__v",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": false,
                "vtp_name": "dlv_customTID"
            }, {
                "function": "__cvt_32196322_683"
            }, {
                "function": "__cvt_32196322_685",
                "vtp_type": "cookie",
                "vtp_key": "clientidUA"
            }, {
                "function": "__gas",
                "vtp_cookieDomain": "auto",
                "vtp_doubleClick": false,
                "vtp_setTrackerName": false,
                "vtp_useDebugVersion": false,
                "vtp_fieldsToSet": ["list", ["map", "fieldName", "location", "value", ["macro", 4]], ["map", "fieldName", "userId", "value", ["macro", 5]], ["map", "fieldName", "anonymizeIp", "value", "true"]],
                "vtp_useHashAutoLink": false,
                "vtp_decorateFormsAutoLink": false,
                "vtp_enableLinkId": false,
                "vtp_dimension": ["list", ["map", "index", "2", "dimension", ["macro", 6]], ["map", "index", "3", "dimension", ["macro", 7]], ["map", "index", "4", "dimension", ["macro", 5]], ["map", "index", "5", "dimension", ["macro", 8]], ["map", "index", "7", "dimension", ["macro", 9]], ["map", "index", "20", "dimension", ["macro", 10]], ["map", "index", "29", "dimension", ["macro", 11]], ["map", "index", "24", "dimension", ["macro", 12]], ["map", "index", "30", "dimension", ["macro", 13]], ["map", "index", "21", "dimension", ["macro", 14]]],
                "vtp_enableEcommerce": false,
                "vtp_trackingId": "UA-162512367-1",
                "vtp_enableRecaptchaOption": false,
                "vtp_enableUaRlsa": false,
                "vtp_enableUseInternalVersion": false,
                "vtp_enableGA4Schema": true
            }, {
                "function": "__v",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": false,
                "vtp_name": "eventAction"
            }, {
                "function": "__v",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": false,
                "vtp_name": "eventLabel"
            }, {
                "function": "__v",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": false,
                "vtp_name": "eventCategory"
            }, {
                "function": "__v",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": false,
                "vtp_name": "language"
            }, {
                "function": "__v",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": false,
                "vtp_name": "cryptoid"
            }, {
                "function": "__v",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": false,
                "vtp_name": "fiatid"
            }, {
                "function": "__v",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": false,
                "vtp_name": "paymentmethodid"
            }, {
                "function": "__v",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": false,
                "vtp_name": "railid"
            }, {
                "function": "__v",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": false,
                "vtp_name": "cardid"
            }, {
                "function": "__v",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": false,
                "vtp_name": "error"
            }, {
                "function": "__v",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": false,
                "vtp_name": "elementid"
            }, {
                "function": "__v",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": false,
                "vtp_name": "KYC_dlvar_kycLevel"
            }, {
                "function": "__v",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": false,
                "vtp_name": "KYC_dlvar_kycCountry"
            }, {
                "function": "__v",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": false,
                "vtp_name": "country"
            }, {
                "function": "__jsm",
                "vtp_javascript": ["template", "(function(){return ", ["escape", ["macro", 28], 8, 16], "?", ["escape", ["macro", 28], 8, 16], ":", ["escape", ["macro", 29], 8, 16], "})();"]
            }, {
                "function": "__v",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": false,
                "vtp_name": "flow"
            }, {
                "function": "__v",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": false,
                "vtp_name": "layout"
            }, {
                "function": "__c",
                "vtp_value": "UA-162512367-1"
            }, {
                "function": "__gas",
                "vtp_cookieDomain": "auto",
                "vtp_doubleClick": false,
                "vtp_setTrackerName": false,
                "vtp_useDebugVersion": false,
                "vtp_fieldsToSet": ["list", ["map", "fieldName", "userId", "value", ["macro", 5]], ["map", "fieldName", "anonymizeIp", "value", "true"]],
                "vtp_useHashAutoLink": false,
                "vtp_decorateFormsAutoLink": false,
                "vtp_enableLinkId": false,
                "vtp_dimension": ["list", ["map", "index", "6", "dimension", ["macro", 19]], ["map", "index", "10", "dimension", ["macro", 20]], ["map", "index", "11", "dimension", ["macro", 21]], ["map", "index", "12", "dimension", ["macro", 22]], ["map", "index", "13", "dimension", ["macro", 23]], ["map", "index", "15", "dimension", ["macro", 24]], ["map", "index", "19", "dimension", ["macro", 25]], ["map", "index", "2", "dimension", ["macro", 26]], ["map", "index", "3", "dimension", ["macro", 7]], ["map", "index", "5", "dimension", ["macro", 8]], ["map", "index", "4", "dimension", ["macro", 5]], ["map", "index", "20", "dimension", ["macro", 10]], ["map", "index", "18", "dimension", ["macro", 27]], ["map", "index", "16", "dimension", ["macro", 30]], ["map", "index", "17", "dimension", ["macro", 31]], ["map", "index", "7", "dimension", ["macro", 32]], ["map", "index", "29", "dimension", ["macro", 11]], ["map", "index", "24", "dimension", ["macro", 12]], ["map", "index", "30", "dimension", ["macro", 13]], ["map", "index", "21", "dimension", ["macro", 14]]],
                "vtp_enableEcommerce": false,
                "vtp_trackingId": ["macro", 33],
                "vtp_enableRecaptchaOption": false,
                "vtp_enableUaRlsa": false,
                "vtp_enableUseInternalVersion": false,
                "vtp_enableGA4Schema": true
            }, {
                "function": "__v",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": false,
                "vtp_name": "eventAction"
            }, {
                "function": "__v",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": false,
                "vtp_name": "eventLabel"
            }, {
                "function": "__u",
                "vtp_component": "PATH",
                "vtp_enableMultiQueryKeys": false,
                "vtp_enableIgnoreEmptyQueryParam": false
            }, {
                "function": "__v",
                "vtp_name": "gtm.triggers",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": true,
                "vtp_defaultValue": ""
            }, {
                "function": "__j",
                "vtp_name": "document.title"
            }, {
                "function": "__v",
                "vtp_name": "gtm.scrollThreshold",
                "vtp_dataLayerVersion": 1
            }, {
                "function": "__gas",
                "vtp_cookieDomain": "auto",
                "vtp_doubleClick": false,
                "vtp_setTrackerName": false,
                "vtp_useDebugVersion": false,
                "vtp_fieldsToSet": ["list", ["map", "fieldName", "userId", "value", ["macro", 5]], ["map", "fieldName", "anonymizeIp", "value", "true"]],
                "vtp_useHashAutoLink": false,
                "vtp_decorateFormsAutoLink": false,
                "vtp_enableLinkId": false,
                "vtp_dimension": ["list", ["map", "index", "3", "dimension", ["macro", 7]], ["map", "index", "4", "dimension", ["macro", 5]], ["map", "index", "5", "dimension", ["macro", 8]], ["map", "index", "20", "dimension", ["macro", 10]], ["map", "index", "29", "dimension", ["macro", 11]], ["map", "index", "24", "dimension", ["macro", 12]], ["map", "index", "30", "dimension", ["macro", 13]], ["map", "index", "21", "dimension", ["macro", 14]]],
                "vtp_enableEcommerce": false,
                "vtp_trackingId": "UA-162512367-1",
                "vtp_enableRecaptchaOption": false,
                "vtp_enableUaRlsa": false,
                "vtp_enableUseInternalVersion": false,
                "vtp_enableGA4Schema": true
            }, {
                "function": "__gas",
                "vtp_useDebugVersion": false,
                "vtp_useHashAutoLink": false,
                "vtp_decorateFormsAutoLink": false,
                "vtp_cookieDomain": "auto",
                "vtp_useEcommerceDataLayer": true,
                "vtp_doubleClick": false,
                "vtp_setTrackerName": false,
                "vtp_fieldsToSet": ["list", ["map", "fieldName", "userId", "value", ["macro", 5]], ["map", "fieldName", "anonymizeIp", "value", "true"]],
                "vtp_useGA4SchemaForEcommerce": false,
                "vtp_enableLinkId": false,
                "vtp_dimension": ["list", ["map", "index", "2", "dimension", ["macro", 26]], ["map", "index", "3", "dimension", ["macro", 7]], ["map", "index", "5", "dimension", ["macro", 8]], ["map", "index", "4", "dimension", ["macro", 5]], ["map", "index", "20", "dimension", ["macro", 10]], ["map", "index", "29", "dimension", ["macro", 11]], ["map", "index", "24", "dimension", ["macro", 12]], ["map", "index", "30", "dimension", ["macro", 13]], ["map", "index", "21", "dimension", ["macro", 14]]],
                "vtp_enableEcommerce": true,
                "vtp_trackingId": ["macro", 33],
                "vtp_enableRecaptchaOption": false,
                "vtp_enableUaRlsa": false,
                "vtp_enableUseInternalVersion": false,
                "vtp_ecommerceIsEnabled": true,
                "vtp_enableGA4Schema": true
            }, {
                "function": "__v",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": false,
                "vtp_name": "ecommerce.purchase.actionField.revenue"
            }, {
                "function": "__u",
                "vtp_enableMultiQueryKeys": false,
                "vtp_enableIgnoreEmptyQueryParam": false
            }, {
                "function": "__v",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": false,
                "vtp_name": "page_load_info.userId"
            }, {
                "function": "__v",
                "convert_null_to": "0.00",
                "convert_undefined_to": "0.00",
                "convert_true_to": "0.00",
                "convert_false_to": "0.00",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": true,
                "vtp_defaultValue": "0.00",
                "vtp_name": "conversionValue"
            }, {
                "function": "__c",
                "vtp_value": "2401726993442574"
            }, {
                "function": "__c",
                "vtp_value": "G-3WP50LGEEC"
            }, {
                "function": "__cvt_32196322_685",
                "vtp_type": "cookie",
                "vtp_key": "clientid"
            }, {
                "function": "__c",
                "vtp_value": "transaction_id"
            }, {
                "function": "__v",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": false,
                "vtp_name": "ecommerce"
            }, {
                "function": "__jsm",
                "vtp_javascript": ["template", "(function(){var a=", ["escape", ["macro", 51], 8, 16], ",c={};if(a.constructor===Object\u0026\u0026a.click.constructor===Object\u0026\u0026a.click.actionField.constructor===Object\u0026\u0026a.click.products.constructor===Array){c=a.click.actionField;a=a.click.products;var d=[];a.forEach(function(b){d.push({item_id:b.id,item_name:b.name,item_brand:b.brand,item_category:b.category,item_variant:b.variant,price:b.price,location_id:b.position})});c={item_list_name:c.list,items:d}}return c})();"]
            }, {
                "function": "__jsm",
                "vtp_javascript": ["template", "(function(){return ", ["escape", ["macro", 52], 8, 16], ".item_list_name})();"]
            }, {
                "function": "__jsm",
                "vtp_javascript": ["template", "(function(){return ", ["escape", ["macro", 52], 8, 16], ".items})();"]
            }, {
                "function": "__u",
                "vtp_component": "URL",
                "vtp_enableMultiQueryKeys": false,
                "vtp_enableIgnoreEmptyQueryParam": false
            }, {
                "function": "__cvt_32196322_701",
                "vtp_key": "ad_storage"
            }, {
                "function": "__cvt_32196322_701",
                "vtp_key": "ad_user_data"
            }, {
                "function": "__cvt_32196322_701",
                "vtp_key": "personalization_storage"
            }, {
                "function": "__cvt_32196322_701",
                "vtp_key": "analytics_storage"
            }, {
                "function": "__cvt_32196322_701",
                "vtp_key": "ad_personalization"
            }, {
                "function": "__c",
                "vtp_value": "G-MEG0BSW76K"
            }, {
                "function": "__gas",
                "vtp_cookieDomain": "auto",
                "vtp_doubleClick": false,
                "vtp_setTrackerName": false,
                "vtp_useDebugVersion": false,
                "vtp_fieldsToSet": ["list", ["map", "fieldName", "userId", "value", ["macro", 5]], ["map", "fieldName", "anonymizeIp", "value", "true"]],
                "vtp_useHashAutoLink": false,
                "vtp_decorateFormsAutoLink": false,
                "vtp_enableLinkId": false,
                "vtp_dimension": ["list", ["map", "index", "1", "dimension", ["macro", 7]], ["map", "index", "3", "dimension", ["macro", 5]], ["map", "index", "7", "dimension", ["macro", 8]], ["map", "index", "17", "dimension", ["macro", 10]], ["map", "index", "4", "dimension", ["macro", 11]], ["map", "index", "2", "dimension", ["macro", 14]]],
                "vtp_enableEcommerce": false,
                "vtp_trackingId": "UA-123190985-1",
                "vtp_enableRecaptchaOption": false,
                "vtp_enableUaRlsa": false,
                "vtp_enableUseInternalVersion": false,
                "vtp_enableGA4Schema": true
            }, {
                "function": "__cvt_32196322_685",
                "vtp_type": "page_load_info",
                "vtp_key": "author"
            }, {
                "function": "__cvt_32196322_685",
                "vtp_type": "page_load_info",
                "vtp_key": "pagename"
            }, {
                "function": "__cvt_32196322_685",
                "vtp_type": "page_load_info",
                "vtp_key": "topic"
            }, {
                "function": "__d",
                "vtp_elementId": "gtm-trueMetrics",
                "vtp_attributeName": "data-nonce",
                "vtp_selectorType": "ID"
            }, {
                "function": "__v",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": false,
                "vtp_name": "productClick_info"
            }, {
                "function": "__v",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": false,
                "vtp_name": "type"
            }, {
                "function": "__v",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": false,
                "vtp_name": "isAttempted"
            }, {
                "function": "__v",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": false,
                "vtp_name": "side"
            }, {
                "function": "__v",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": false,
                "vtp_name": "uniqueID"
            }, {
                "function": "__v",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": false,
                "vtp_name": "page_load_info"
            }, {
                "function": "__v",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": false,
                "vtp_name": "page_load_info"
            }, {
                "function": "__v",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": false,
                "vtp_name": "fn_earn_coinType"
            }, {
                "function": "__v",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": false,
                "vtp_name": "en_savings_coinType"
            }, {
                "function": "__v",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": false,
                "vtp_name": "fn_liquid_poolType"
            }, {
                "function": "__v",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": false,
                "vtp_name": "fn_earn_historyTab"
            }, {
                "function": "__v",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": false,
                "vtp_name": "productClick_info"
            }, {
                "function": "__jsm",
                "vtp_javascript": ["template", "(function(){return ", ["escape", ["macro", 78], 8, 16], ".eventCategory})();"]
            }, {
                "function": "__jsm",
                "vtp_javascript": ["template", "(function(){return ", ["escape", ["macro", 78], 8, 16], ".eventAction})();"]
            }, {
                "function": "__jsm",
                "vtp_javascript": ["template", "(function(){return ", ["escape", ["macro", 78], 8, 16], ".eventLabel})();"]
            }, {
                "function": "__k",
                "vtp_decodeCookie": false,
                "vtp_name": "_ga"
            }, {
                "function": "__c",
                "vtp_value": "447029915788678"
            }, {
                "function": "__v",
                "vtp_dataLayerVersion": 2,
                "vtp_setDefaultValue": false,
                "vtp_name": "dlv_shaOid"
            }, {
                "function": "__f",
                "vtp_component": "URL"
            }, {
                "function": "__v",
                "vtp_name": "gtm.elementClasses",
                "vtp_dataLayerVersion": 1
            }, {
                "function": "__v",
                "vtp_name": "gtm.elementId",
                "vtp_dataLayerVersion": 1
            }, {
                "function": "__v",
                "vtp_name": "gtm.elementClasses",
                "vtp_dataLayerVersion": 1
            }, {
                "function": "__v",
                "vtp_name": "gtm.elementId",
                "vtp_dataLayerVersion": 1
            }, {
                "function": "__v",
                "vtp_name": "gtm.scrollUnits",
                "vtp_dataLayerVersion": 1
            }, {
                "function": "__v",
                "vtp_name": "gtm.scrollDirection",
                "vtp_dataLayerVersion": 1
            }],
            "tags": [{
                "function": "__ua",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_nonInteraction": false,
                "vtp_overrideGaSettings": true,
                "vtp_eventCategory": "web conversion",
                "vtp_trackType": "TRACK_EVENT",
                "vtp_eventAction": "email confirmation",
                "vtp_eventLabel": "registration",
                "vtp_trackingId": "UA-162512367-1",
                "vtp_enableRecaptchaOption": false,
                "vtp_enableUaRlsa": false,
                "vtp_enableUseInternalVersion": false,
                "vtp_enableFirebaseCampaignData": true,
                "vtp_trackTypeIsEvent": true,
                "vtp_enableGA4Schema": true,
                "tag_id": 49
            }, {
                "function": "__ua",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_nonInteraction": false,
                "vtp_overrideGaSettings": false,
                "vtp_eventCategory": ["macro", 3],
                "vtp_trackType": "TRACK_EVENT",
                "vtp_gaSettings": ["macro", 15],
                "vtp_eventAction": ["macro", 16],
                "vtp_eventLabel": ["macro", 17],
                "vtp_enableRecaptchaOption": false,
                "vtp_enableUaRlsa": false,
                "vtp_enableUseInternalVersion": false,
                "vtp_enableFirebaseCampaignData": true,
                "vtp_trackTypeIsEvent": true,
                "vtp_enableGA4Schema": true,
                "tag_id": 84
            }, {
                "function": "__ua",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_nonInteraction": false,
                "vtp_overrideGaSettings": false,
                "vtp_eventCategory": ["macro", 18],
                "vtp_trackType": "TRACK_EVENT",
                "vtp_gaSettings": ["macro", 34],
                "vtp_eventAction": ["macro", 35],
                "vtp_eventLabel": ["macro", 36],
                "vtp_enableRecaptchaOption": false,
                "vtp_enableUaRlsa": false,
                "vtp_enableUseInternalVersion": false,
                "vtp_enableFirebaseCampaignData": true,
                "vtp_trackTypeIsEvent": true,
                "vtp_enableGA4Schema": true,
                "tag_id": 115
            }, {
                "function": "__ua",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_nonInteraction": false,
                "vtp_overrideGaSettings": false,
                "vtp_eventCategory": ["macro", 18],
                "vtp_trackType": "TRACK_EVENT",
                "vtp_gaSettings": ["macro", 34],
                "vtp_eventAction": ["macro", 35],
                "vtp_eventLabel": ["macro", 36],
                "vtp_enableRecaptchaOption": false,
                "vtp_enableUaRlsa": false,
                "vtp_enableUseInternalVersion": false,
                "vtp_enableFirebaseCampaignData": true,
                "vtp_trackTypeIsEvent": true,
                "vtp_enableGA4Schema": true,
                "tag_id": 149
            }, {
                "function": "__paused",
                "vtp_originalTagType": "ua",
                "tag_id": 151
            }, {
                "function": "__ua",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_nonInteraction": false,
                "vtp_overrideGaSettings": false,
                "vtp_eventCategory": "fb_card",
                "vtp_trackType": "TRACK_EVENT",
                "vtp_gaSettings": ["macro", 34],
                "vtp_eventAction": "popup_view",
                "vtp_eventLabel": "fb_card::add_new_card_confirm_view",
                "vtp_enableRecaptchaOption": false,
                "vtp_enableUaRlsa": false,
                "vtp_enableUseInternalVersion": false,
                "vtp_enableFirebaseCampaignData": true,
                "vtp_trackTypeIsEvent": true,
                "vtp_enableGA4Schema": true,
                "tag_id": 163
            }, {
                "function": "__ua",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_nonInteraction": false,
                "vtp_overrideGaSettings": false,
                "vtp_eventCategory": "fb_card",
                "vtp_trackType": "TRACK_EVENT",
                "vtp_gaSettings": ["macro", 34],
                "vtp_eventAction": "popup_view",
                "vtp_eventLabel": "fb_card::change_card_view",
                "vtp_enableRecaptchaOption": false,
                "vtp_enableUaRlsa": false,
                "vtp_enableUseInternalVersion": false,
                "vtp_enableFirebaseCampaignData": true,
                "vtp_trackTypeIsEvent": true,
                "vtp_enableGA4Schema": true,
                "tag_id": 165
            }, {
                "function": "__ua",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_nonInteraction": false,
                "vtp_overrideGaSettings": false,
                "vtp_eventCategory": "fb_multiple",
                "vtp_trackType": "TRACK_EVENT",
                "vtp_gaSettings": ["macro", 34],
                "vtp_eventAction": "popup_view",
                "vtp_eventLabel": "fb_multiple::add_new_card_confirm_view",
                "vtp_enableRecaptchaOption": false,
                "vtp_enableUaRlsa": false,
                "vtp_enableUseInternalVersion": false,
                "vtp_enableFirebaseCampaignData": true,
                "vtp_trackTypeIsEvent": true,
                "vtp_enableGA4Schema": true,
                "tag_id": 172
            }, {
                "function": "__paused",
                "vtp_originalTagType": "html",
                "tag_id": 193
            }, {
                "function": "__paused",
                "vtp_originalTagType": "ua",
                "tag_id": 202
            }, {
                "function": "__ua",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_nonInteraction": false,
                "vtp_overrideGaSettings": false,
                "vtp_eventCategory": "sp_announce",
                "vtp_trackType": "TRACK_EVENT",
                "vtp_gaSettings": ["macro", 15],
                "vtp_eventAction": "scroll",
                "vtp_eventLabel": ["template", "sp_announce::article_", ["macro", 39], "_", ["macro", 40], "%"],
                "vtp_enableRecaptchaOption": false,
                "vtp_enableUaRlsa": false,
                "vtp_enableUseInternalVersion": false,
                "vtp_enableFirebaseCampaignData": true,
                "vtp_trackTypeIsEvent": true,
                "vtp_enableGA4Schema": true,
                "tag_id": 228
            }, {
                "function": "__ua",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_nonInteraction": false,
                "vtp_overrideGaSettings": false,
                "vtp_eventCategory": "sp_faq",
                "vtp_trackType": "TRACK_EVENT",
                "vtp_gaSettings": ["macro", 15],
                "vtp_eventAction": "scroll",
                "vtp_eventLabel": ["template", "sp_faq::article_", ["macro", 39], "_", ["macro", 40], "%"],
                "vtp_enableRecaptchaOption": false,
                "vtp_enableUaRlsa": false,
                "vtp_enableUseInternalVersion": false,
                "vtp_enableFirebaseCampaignData": true,
                "vtp_trackTypeIsEvent": true,
                "vtp_enableGA4Schema": true,
                "tag_id": 232
            }, {
                "function": "__ua",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_nonInteraction": false,
                "vtp_overrideGaSettings": false,
                "vtp_eventCategory": ["macro", 18],
                "vtp_trackType": "TRACK_EVENT",
                "vtp_gaSettings": ["macro", 34],
                "vtp_eventAction": ["macro", 35],
                "vtp_eventLabel": ["macro", 36],
                "vtp_enableRecaptchaOption": false,
                "vtp_enableUaRlsa": false,
                "vtp_enableUseInternalVersion": false,
                "vtp_enableFirebaseCampaignData": true,
                "vtp_trackTypeIsEvent": true,
                "vtp_enableGA4Schema": true,
                "tag_id": 294
            }, {
                "function": "__paused",
                "vtp_originalTagType": "html",
                "tag_id": 299
            }, {
                "function": "__ua",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_nonInteraction": false,
                "vtp_overrideGaSettings": false,
                "vtp_eventCategory": "fb_card",
                "vtp_trackType": "TRACK_EVENT",
                "vtp_gaSettings": ["macro", 34],
                "vtp_eventAction": "popup_view",
                "vtp_eventLabel": "fb_card::add_new_card_view",
                "vtp_enableRecaptchaOption": false,
                "vtp_enableUaRlsa": false,
                "vtp_enableUseInternalVersion": false,
                "vtp_enableFirebaseCampaignData": true,
                "vtp_trackTypeIsEvent": true,
                "vtp_enableGA4Schema": true,
                "tag_id": 316
            }, {
                "function": "__paused",
                "vtp_originalTagType": "html",
                "tag_id": 320
            }, {
                "function": "__ua",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_load": true,
                "vtp_overrideGaSettings": false,
                "vtp_trackType": "TRACK_PAGEVIEW",
                "vtp_gaSettings": ["macro", 41],
                "vtp_enableRecaptchaOption": false,
                "vtp_enableUaRlsa": false,
                "vtp_enableUseInternalVersion": false,
                "vtp_enableFirebaseCampaignData": true,
                "vtp_enableGA4Schema": true,
                "tag_id": 337
            }, {
                "function": "__ua",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_nonInteraction": false,
                "vtp_overrideGaSettings": false,
                "vtp_eventCategory": ["macro", 18],
                "vtp_trackType": "TRACK_EVENT",
                "vtp_gaSettings": ["macro", 42],
                "vtp_eventAction": ["macro", 35],
                "vtp_eventLabel": ["macro", 36],
                "vtp_enableRecaptchaOption": false,
                "vtp_enableUaRlsa": false,
                "vtp_enableUseInternalVersion": false,
                "vtp_enableFirebaseCampaignData": true,
                "vtp_trackTypeIsEvent": true,
                "vtp_enableGA4Schema": true,
                "tag_id": 342
            }, {
                "function": "__cvt_32196322_349",
                "metadata": ["map"],
                "once_per_event": true,
                "vtp_wait_for_update": "500",
                "vtp_sendDataLayer": false,
                "vtp_regions": "all",
                "vtp_command": "default",
                "vtp_functionality_storage": "granted",
                "vtp_url_passthrough": false,
                "vtp_ad_storage": "denied",
                "vtp_ads_data_redaction": false,
                "vtp_ad_user_data": "denied",
                "vtp_security_storage": "granted",
                "vtp_personalization_storage": "denied",
                "vtp_analytics_storage": "denied",
                "vtp_ad_personalization": "denied",
                "tag_id": 350
            }, {
                "function": "__ua",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_nonInteraction": false,
                "vtp_overrideGaSettings": false,
                "vtp_eventCategory": ["macro", 18],
                "vtp_trackType": "TRACK_EVENT",
                "vtp_gaSettings": ["macro", 34],
                "vtp_eventAction": ["macro", 35],
                "vtp_eventLabel": ["macro", 36],
                "vtp_enableRecaptchaOption": false,
                "vtp_enableUaRlsa": false,
                "vtp_enableUseInternalVersion": false,
                "vtp_enableFirebaseCampaignData": true,
                "vtp_trackTypeIsEvent": true,
                "vtp_enableGA4Schema": true,
                "tag_id": 360
            }, {
                "function": "__ua",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_nonInteraction": false,
                "vtp_overrideGaSettings": false,
                "vtp_eventCategory": ["macro", 18],
                "vtp_trackType": "TRACK_EVENT",
                "vtp_gaSettings": ["macro", 42],
                "vtp_eventAction": ["macro", 35],
                "vtp_eventLabel": ["macro", 36],
                "vtp_enableRecaptchaOption": false,
                "vtp_enableUaRlsa": false,
                "vtp_enableUseInternalVersion": false,
                "vtp_enableFirebaseCampaignData": true,
                "vtp_trackTypeIsEvent": true,
                "vtp_enableGA4Schema": true,
                "tag_id": 367
            }, {
                "function": "__ua",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_nonInteraction": false,
                "vtp_overrideGaSettings": false,
                "vtp_eventCategory": ["macro", 18],
                "vtp_trackType": "TRACK_EVENT",
                "vtp_gaSettings": ["macro", 34],
                "vtp_eventAction": ["macro", 35],
                "vtp_eventLabel": ["macro", 36],
                "vtp_enableRecaptchaOption": false,
                "vtp_enableUaRlsa": false,
                "vtp_enableUseInternalVersion": false,
                "vtp_enableFirebaseCampaignData": true,
                "vtp_trackTypeIsEvent": true,
                "vtp_enableGA4Schema": true,
                "tag_id": 386
            }, {
                "function": "__gclidw",
                "metadata": ["map"],
                "consent": ["list", "personalization_storage"],
                "once_per_event": true,
                "vtp_enableCrossDomain": false,
                "vtp_enableUrlPassthrough": false,
                "vtp_enableCookieOverrides": false,
                "tag_id": 397
            }, {
                "function": "__awct",
                "metadata": ["map"],
                "consent": ["list", "personalization_storage"],
                "once_per_event": true,
                "vtp_enableNewCustomerReporting": false,
                "vtp_enableConversionLinker": true,
                "vtp_orderId": ["macro", 13],
                "vtp_enableProductReporting": false,
                "vtp_conversionValue": ["macro", 43],
                "vtp_enableEnhancedConversion": false,
                "vtp_conversionCookiePrefix": "_gcl",
                "vtp_enableShippingData": false,
                "vtp_conversionId": "373946534",
                "vtp_currencyCode": "USD",
                "vtp_conversionLabel": "kw4hCJzUtZkDEKbxp7IB",
                "vtp_rdp": false,
                "vtp_url": ["macro", 44],
                "vtp_enableProductReportingCheckbox": true,
                "vtp_enableNewCustomerReportingCheckbox": true,
                "vtp_enableEnhancedConversionsCheckbox": false,
                "vtp_enableRdpCheckbox": true,
                "vtp_enableTransportUrl": false,
                "vtp_enableCustomParams": false,
                "tag_id": 398
            }, {
                "function": "__awct",
                "metadata": ["map"],
                "consent": ["list", "personalization_storage"],
                "once_per_event": true,
                "vtp_enableNewCustomerReporting": false,
                "vtp_enableConversionLinker": true,
                "vtp_enableProductReporting": false,
                "vtp_enableEnhancedConversion": false,
                "vtp_conversionCookiePrefix": "_gcl",
                "vtp_enableShippingData": false,
                "vtp_conversionId": "373946534",
                "vtp_conversionLabel": "aMToCNiz7JkDEKbxp7IB",
                "vtp_rdp": false,
                "vtp_url": ["macro", 44],
                "vtp_enableProductReportingCheckbox": true,
                "vtp_enableNewCustomerReportingCheckbox": true,
                "vtp_enableEnhancedConversionsCheckbox": false,
                "vtp_enableRdpCheckbox": true,
                "vtp_enableTransportUrl": false,
                "vtp_enableCustomParams": false,
                "tag_id": 399
            }, {
                "function": "__sp",
                "metadata": ["map"],
                "consent": ["list", "personalization_storage"],
                "once_per_event": true,
                "vtp_enableConversionLinker": true,
                "vtp_enableDynamicRemarketing": false,
                "vtp_conversionCookiePrefix": "_gcl",
                "vtp_conversionId": "373946534",
                "vtp_customParamsFormat": "NONE",
                "vtp_rdp": false,
                "vtp_enableOgtRmktParams": true,
                "vtp_enableUserId": true,
                "vtp_url": ["macro", 44],
                "vtp_enableRdpCheckbox": true,
                "vtp_enableConversionLinkingSettings": true,
                "tag_id": 401
            }, {
                "function": "__fls",
                "metadata": ["map"],
                "consent": ["list", "personalization_storage"],
                "once_per_event": true,
                "vtp_customVariable": ["list", ["map", "key", "u1", "value", ["macro", 45]], ["map", "key", "u2", "value", ["macro", 3]], ["map", "key", "u3", "value", ["macro", 16]]],
                "vtp_revenue": ["macro", 46],
                "vtp_enableConversionLinker": true,
                "vtp_countingMethod": "TRANSACTIONS",
                "vtp_enhancedUserData": false,
                "vtp_orderId": ["macro", 12],
                "vtp_enableProductReporting": false,
                "vtp_groupTag": "allwe0",
                "vtp_useImageTag": true,
                "vtp_activityTag": "alltr0",
                "vtp_conversionCookiePrefix": "_gcl",
                "vtp_advertiserId": "11776143",
                "vtp_useImageTagIsTrue": true,
                "vtp_countingMethodIsTransactions": true,
                "vtp_url": ["macro", 44],
                "vtp_enableGoogleAttributionOptions": false,
                "vtp_showConversionLinkingControls": true,
                "vtp_enableMatchIdVariable": true,
                "tag_id": 414
            }, {
                "function": "__awct",
                "metadata": ["map"],
                "consent": ["list", "personalization_storage"],
                "once_per_event": true,
                "vtp_enableNewCustomerReporting": false,
                "vtp_enableConversionLinker": true,
                "vtp_enableProductReporting": false,
                "vtp_enableEnhancedConversion": false,
                "vtp_conversionCookiePrefix": "_gcl",
                "vtp_enableShippingData": false,
                "vtp_conversionId": "10924664731",
                "vtp_conversionLabel": "zBHoCJbAlcIDEJvPpNko",
                "vtp_rdp": false,
                "vtp_url": ["macro", 44],
                "vtp_enableProductReportingCheckbox": true,
                "vtp_enableNewCustomerReportingCheckbox": true,
                "vtp_enableEnhancedConversionsCheckbox": false,
                "vtp_enableRdpCheckbox": true,
                "vtp_enableTransportUrl": false,
                "vtp_enableCustomParams": false,
                "tag_id": 440
            }, {
                "function": "__ua",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_nonInteraction": false,
                "vtp_overrideGaSettings": false,
                "vtp_eventCategory": ["macro", 18],
                "vtp_trackType": "TRACK_EVENT",
                "vtp_gaSettings": ["macro", 34],
                "vtp_eventAction": ["macro", 35],
                "vtp_eventLabel": ["macro", 36],
                "vtp_enableRecaptchaOption": false,
                "vtp_enableUaRlsa": false,
                "vtp_enableUseInternalVersion": false,
                "vtp_enableFirebaseCampaignData": true,
                "vtp_trackTypeIsEvent": true,
                "vtp_enableGA4Schema": true,
                "tag_id": 447
            }, {
                "function": "__cvt_32196322_451",
                "metadata": ["map"],
                "consent": ["list", "personalization_storage"],
                "once_per_event": true,
                "vtp_disablePushState": false,
                "vtp_pixelId": ["macro", 47],
                "vtp_objectPropertyList": ["list", ["map", "name", "category", "value", ["macro", 3]], ["map", "name", "action", "value", ["macro", 16]], ["map", "name", "label", "value", ["macro", 17]]],
                "vtp_disableAutoConfig": false,
                "vtp_enhancedEcommerce": false,
                "vtp_dpoLDU": false,
                "vtp_eventName": "custom",
                "vtp_objectPropertiesFromVariable": false,
                "vtp_customEventName": "Application_Form_Success",
                "vtp_consent": true,
                "vtp_advancedMatching": false,
                "tag_id": 452
            }, {
                "function": "__paused",
                "vtp_originalTagType": "cvt_32196322_451",
                "tag_id": 481
            }, {
                "function": "__paused",
                "vtp_originalTagType": "cvt_32196322_451",
                "tag_id": 482
            }, {
                "function": "__paused",
                "vtp_originalTagType": "cvt_32196322_451",
                "tag_id": 483
            }, {
                "function": "__paused",
                "vtp_originalTagType": "cvt_32196322_451",
                "tag_id": 484
            }, {
                "function": "__paused",
                "vtp_originalTagType": "cvt_32196322_451",
                "tag_id": 485
            }, {
                "function": "__paused",
                "vtp_originalTagType": "cvt_32196322_451",
                "tag_id": 486
            }, {
                "function": "__paused",
                "vtp_originalTagType": "cvt_32196322_451",
                "tag_id": 487
            }, {
                "function": "__paused",
                "vtp_originalTagType": "cvt_32196322_451",
                "tag_id": 488
            }, {
                "function": "__paused",
                "vtp_originalTagType": "cvt_32196322_451",
                "tag_id": 489
            }, {
                "function": "__paused",
                "vtp_originalTagType": "cvt_32196322_451",
                "tag_id": 490
            }, {
                "function": "__paused",
                "vtp_originalTagType": "cvt_32196322_451",
                "tag_id": 491
            }, {
                "function": "__paused",
                "vtp_originalTagType": "cvt_32196322_451",
                "tag_id": 492
            }, {
                "function": "__googtag",
                "metadata": ["map"],
                "setup_tags": ["list", ["tag", 155, 0]],
                "once_per_load": true,
                "vtp_tagId": ["macro", 48],
                "vtp_userProperties": ["list", ["map", "name", "userID", "value", ["macro", 5]], ["map", "name", "clientID", "value", ["macro", 49]], ["map", "name", "bncuuID", "value", ["macro", 7]], ["map", "name", "ref", "value", ["macro", 11]]],
                "vtp_configSettingsTable": ["list", ["map", "parameter", "user_id", "parameterValue", ["macro", 5]], ["map", "parameter", "elementID", "parameterValue", ["macro", 26]], ["map", "parameter", "pageName", "parameterValue", ["macro", 8]], ["map", "parameter", "language", "parameterValue", ["macro", 19]], ["map", "parameter", "layout", "parameterValue", ["macro", 32]], ["map", "parameter", "cryptoID", "parameterValue", ["macro", 20]], ["map", "parameter", "fiatID", "parameterValue", ["macro", 21]], ["map", "parameter", "payentmethodID", "parameterValue", ["macro", 22]], ["map", "parameter", "railID", "parameterValue", ["macro", 23]], ["map", "parameter", "cardID", "parameterValue", ["macro", 24]], ["map", "parameter", "kycLevel", "parameterValue", ["macro", 27]], ["map", "parameter", "kycCountry", "parameterValue", ["macro", 30]], ["map", "parameter", "flow", "parameterValue", ["macro", 31]], ["map", "parameter", "error", "parameterValue", ["macro", 25]], ["map", "parameter", "containerID", "parameterValue", ["macro", 10]], ["map", "parameter", "country", "parameterValue", ["macro", 30]], ["map", "parameter", ["macro", 50], "parameterValue", ["macro", 12]], ["map", "parameter", "send_page_view", "parameterValue", "true"]],
                "tag_id": 496
            }, {
                "function": "__gaawe",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_sendEcommerceData": false,
                "vtp_eventSettingsTable": ["list", ["map", "parameter", "eventCategory", "parameterValue", ["macro", 3]], ["map", "parameter", "eventLabel", "parameterValue", ["macro", 17]], ["map", "parameter", "elementID", "parameterValue", ["macro", 26]], ["map", "parameter", ["macro", 50], "parameterValue", ["macro", 12]]],
                "vtp_eventName": ["macro", 16],
                "vtp_measurementIdOverride": ["macro", 48],
                "vtp_enableUserProperties": true,
                "vtp_enableMoreSettingsOption": true,
                "vtp_enableEuid": true,
                "vtp_migratedToV2": true,
                "vtp_demoV2": false,
                "tag_id": 498
            }, {
                "function": "__gaawe",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_sendEcommerceData": false,
                "vtp_eventSettingsTable": ["list", ["map", "parameter", "eventCategory", "parameterValue", ["macro", 3]], ["map", "parameter", "eventLabel", "parameterValue", ["macro", 17]], ["map", "parameter", "elementID", "parameterValue", ["macro", 26]], ["map", "parameter", "country", "parameterValue", ["macro", 30]], ["map", "parameter", "layout", "parameterValue", ["macro", 32]], ["map", "parameter", "cryptoID", "parameterValue", ["macro", 20]], ["map", "parameter", "fiatID", "parameterValue", ["macro", 21]], ["map", "parameter", "payentmethodID", "parameterValue", ["macro", 22]], ["map", "parameter", "railID", "parameterValue", ["macro", 23]], ["map", "parameter", "cardID", "parameterValue", ["macro", 24]], ["map", "parameter", ["macro", 50], "parameterValue", ["macro", 12]]],
                "vtp_eventName": ["macro", 16],
                "vtp_measurementIdOverride": ["macro", 48],
                "vtp_enableUserProperties": true,
                "vtp_enableMoreSettingsOption": true,
                "vtp_enableEuid": true,
                "vtp_migratedToV2": true,
                "vtp_demoV2": false,
                "tag_id": 499
            }, {
                "function": "__gaawe",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_sendEcommerceData": false,
                "vtp_eventSettingsTable": ["list", ["map", "parameter", "eventCategory", "parameterValue", "fb_card"], ["map", "parameter", "eventLabel", "parameterValue", "fb_card::add_new_card_confirm_view"], ["map", "parameter", "elementID", "parameterValue", ["macro", 26]], ["map", "parameter", "cardID", "parameterValue", ["macro", 24]]],
                "vtp_eventName": "popup_view",
                "vtp_measurementIdOverride": ["macro", 48],
                "vtp_enableUserProperties": true,
                "vtp_enableMoreSettingsOption": true,
                "vtp_enableEuid": true,
                "vtp_migratedToV2": true,
                "vtp_demoV2": false,
                "tag_id": 500
            }, {
                "function": "__gaawe",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_sendEcommerceData": false,
                "vtp_eventSettingsTable": ["list", ["map", "parameter", "eventCategory", "parameterValue", "fb_card"], ["map", "parameter", "eventLabel", "parameterValue", "fb_card::add_new_card_view"], ["map", "parameter", "elementID", "parameterValue", ["macro", 26]], ["map", "parameter", "cardID", "parameterValue", ["macro", 24]]],
                "vtp_eventName": "popup_view",
                "vtp_measurementIdOverride": ["macro", 48],
                "vtp_enableUserProperties": true,
                "vtp_enableMoreSettingsOption": true,
                "vtp_enableEuid": true,
                "vtp_migratedToV2": true,
                "vtp_demoV2": false,
                "tag_id": 501
            }, {
                "function": "__gaawe",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_sendEcommerceData": false,
                "vtp_eventSettingsTable": ["list", ["map", "parameter", "eventCategory", "parameterValue", "fb_card"], ["map", "parameter", "eventLabel", "parameterValue", "fb_card::change_card_view"], ["map", "parameter", "elementID", "parameterValue", ["macro", 26]], ["map", "parameter", "cardID", "parameterValue", ["macro", 24]]],
                "vtp_eventName": "popup_view",
                "vtp_measurementIdOverride": ["macro", 48],
                "vtp_enableUserProperties": true,
                "vtp_enableMoreSettingsOption": true,
                "vtp_enableEuid": true,
                "vtp_migratedToV2": true,
                "vtp_demoV2": false,
                "tag_id": 502
            }, {
                "function": "__gaawe",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_sendEcommerceData": false,
                "vtp_eventSettingsTable": ["list", ["map", "parameter", "eventCategory", "parameterValue", "fb_multiple"], ["map", "parameter", "eventLabel", "parameterValue", "fb_multiple::add_new_card_confirm_view"], ["map", "parameter", "elementID", "parameterValue", ["macro", 26]], ["map", "parameter", "cardID", "parameterValue", ["macro", 24]]],
                "vtp_eventName": "popup_view",
                "vtp_measurementIdOverride": ["macro", 48],
                "vtp_enableUserProperties": true,
                "vtp_enableMoreSettingsOption": true,
                "vtp_enableEuid": true,
                "vtp_migratedToV2": true,
                "vtp_demoV2": false,
                "tag_id": 503
            }, {
                "function": "__gaawe",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_sendEcommerceData": false,
                "vtp_eventSettingsTable": ["list", ["map", "parameter", "eventCategory", "parameterValue", ["macro", 3]], ["map", "parameter", "eventLabel", "parameterValue", ["macro", 17]], ["map", "parameter", "elementID", "parameterValue", ["macro", 26]], ["map", "parameter", "country", "parameterValue", ["macro", 30]], ["map", "parameter", "cryptoID", "parameterValue", ["macro", 20]], ["map", "parameter", "fiatID", "parameterValue", ["macro", 21]], ["map", "parameter", "payentmethodID", "parameterValue", ["macro", 22]], ["map", "parameter", "cardID", "parameterValue", ["macro", 24]], ["map", "parameter", ["macro", 50], "parameterValue", ["macro", 12]]],
                "vtp_eventName": ["macro", 16],
                "vtp_measurementIdOverride": ["macro", 48],
                "vtp_enableUserProperties": true,
                "vtp_enableMoreSettingsOption": true,
                "vtp_enableEuid": true,
                "vtp_migratedToV2": true,
                "vtp_demoV2": false,
                "tag_id": 504
            }, {
                "function": "__gaawe",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_sendEcommerceData": false,
                "vtp_eventSettingsTable": ["list", ["map", "parameter", "eventCategory", "parameterValue", ["macro", 3]], ["map", "parameter", "eventLabel", "parameterValue", ["macro", 17]], ["map", "parameter", "elementID", "parameterValue", ["macro", 26]], ["map", "parameter", "kycLevel", "parameterValue", ["macro", 27]], ["map", "parameter", "kycCountry", "parameterValue", ["macro", 30]], ["map", "parameter", "country", "parameterValue", ["macro", 30]]],
                "vtp_eventName": ["macro", 16],
                "vtp_measurementIdOverride": ["macro", 48],
                "vtp_enableUserProperties": true,
                "vtp_enableMoreSettingsOption": true,
                "vtp_enableEuid": true,
                "vtp_migratedToV2": true,
                "vtp_demoV2": false,
                "tag_id": 505
            }, {
                "function": "__gaawe",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_sendEcommerceData": false,
                "vtp_eventSettingsTable": ["list", ["map", "parameter", "eventCategory", "parameterValue", ["macro", 3]], ["map", "parameter", "eventLabel", "parameterValue", ["macro", 17]], ["map", "parameter", "elementID", "parameterValue", ["macro", 26]]],
                "vtp_eventName": ["macro", 16],
                "vtp_measurementIdOverride": ["macro", 48],
                "vtp_enableUserProperties": true,
                "vtp_enableMoreSettingsOption": true,
                "vtp_enableEuid": true,
                "vtp_migratedToV2": true,
                "vtp_demoV2": false,
                "tag_id": 506
            }, {
                "function": "__gaawe",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_sendEcommerceData": false,
                "vtp_eventSettingsTable": ["list", ["map", "parameter", "eventCategory", "parameterValue", ["macro", 3]], ["map", "parameter", "eventLabel", "parameterValue", ["macro", 17]], ["map", "parameter", "elementID", "parameterValue", ["macro", 26]]],
                "vtp_eventName": ["macro", 16],
                "vtp_measurementIdOverride": ["macro", 48],
                "vtp_enableUserProperties": true,
                "vtp_enableMoreSettingsOption": true,
                "vtp_enableEuid": true,
                "vtp_migratedToV2": true,
                "vtp_demoV2": false,
                "tag_id": 507
            }, {
                "function": "__gaawe",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_sendEcommerceData": false,
                "vtp_eventSettingsTable": ["list", ["map", "parameter", "eventCategory", "parameterValue", ["macro", 3]], ["map", "parameter", "eventLabel", "parameterValue", ["macro", 17]], ["map", "parameter", "elementID", "parameterValue", ["macro", 26]]],
                "vtp_eventName": ["macro", 16],
                "vtp_measurementIdOverride": ["macro", 48],
                "vtp_enableUserProperties": true,
                "vtp_enableMoreSettingsOption": true,
                "vtp_enableEuid": true,
                "vtp_migratedToV2": true,
                "vtp_demoV2": false,
                "tag_id": 508
            }, {
                "function": "__gaawe",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_sendEcommerceData": false,
                "vtp_eventSettingsTable": ["list", ["map", "parameter", "eventCategory", "parameterValue", "sp_announce"], ["map", "parameter", "eventLabel", "parameterValue", ["template", "sp_announce::article_", ["macro", 39], "_", ["macro", 40], "%"]], ["map", "parameter", "elementID", "parameterValue", ["macro", 26]]],
                "vtp_eventName": "scroll",
                "vtp_measurementIdOverride": ["macro", 48],
                "vtp_enableUserProperties": true,
                "vtp_enableMoreSettingsOption": true,
                "vtp_enableEuid": true,
                "vtp_migratedToV2": true,
                "vtp_demoV2": false,
                "tag_id": 509
            }, {
                "function": "__gaawe",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_sendEcommerceData": false,
                "vtp_eventSettingsTable": ["list", ["map", "parameter", "eventCategory", "parameterValue", "sp_faq"], ["map", "parameter", "eventLabel", "parameterValue", ["template", "sp_faq::article_", ["macro", 39], "_", ["macro", 40], "%"]], ["map", "parameter", "elementID", "parameterValue", ["macro", 26]]],
                "vtp_eventName": "scroll",
                "vtp_measurementIdOverride": ["macro", 48],
                "vtp_enableUserProperties": true,
                "vtp_enableMoreSettingsOption": true,
                "vtp_enableEuid": true,
                "vtp_migratedToV2": true,
                "vtp_demoV2": false,
                "tag_id": 510
            }, {
                "function": "__cvt_32196322_451",
                "metadata": ["map"],
                "consent": ["list", "personalization_storage"],
                "once_per_event": true,
                "vtp_disablePushState": false,
                "vtp_pixelId": ["macro", 47],
                "vtp_objectPropertyList": ["list", ["map", "name", "category", "value", ["macro", 3]], ["map", "name", "action", "value", ["macro", 16]], ["map", "name", "label", "value", ["macro", 17]]],
                "vtp_disableAutoConfig": false,
                "vtp_enhancedEcommerce": false,
                "vtp_dpoLDU": false,
                "vtp_eventName": "custom",
                "vtp_objectPropertiesFromVariable": false,
                "vtp_customEventName": "Form_Submission_Click_Submit",
                "vtp_consent": true,
                "vtp_advancedMatching": false,
                "tag_id": 511
            }, {
                "function": "__gaawe",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_sendEcommerceData": true,
                "vtp_getEcommerceDataFrom": "dataLayer",
                "vtp_eventSettingsTable": ["list", ["map", "parameter", "eventCategory", "parameterValue", ["macro", 18]], ["map", "parameter", "eventLabel", "parameterValue", ["macro", 36]], ["map", "parameter", "eventAction", "parameterValue", ["macro", 35]], ["map", "parameter", ["macro", 50], "parameterValue", ["macro", 12]]],
                "vtp_eventName": "purchase",
                "vtp_measurementIdOverride": ["macro", 48],
                "vtp_enableUserProperties": true,
                "vtp_enableMoreSettingsOption": true,
                "vtp_enableEuid": true,
                "vtp_migratedToV2": true,
                "vtp_demoV2": false,
                "tag_id": 513
            }, {
                "function": "__gaawe",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_sendEcommerceData": false,
                "vtp_eventSettingsTable": ["list", ["map", "parameter", "item_list_name", "parameterValue", ["macro", 53]], ["map", "parameter", "items", "parameterValue", ["macro", 54]], ["map", "parameter", "eventCategory", "parameterValue", ["macro", 18]], ["map", "parameter", "eventLabel", "parameterValue", ["macro", 36]], ["map", "parameter", "eventAction", "parameterValue", ["macro", 35]], ["map", "parameter", ["macro", 50], "parameterValue", ["macro", 12]]],
                "vtp_eventName": "select_item",
                "vtp_measurementIdOverride": ["macro", 48],
                "vtp_enableUserProperties": true,
                "vtp_enableMoreSettingsOption": true,
                "vtp_enableEuid": true,
                "vtp_migratedToV2": true,
                "vtp_demoV2": false,
                "tag_id": 516
            }, {
                "function": "__gaawe",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_eventSettingsTable": ["list", ["map", "parameter", "eventCategory", "parameterValue", "web conversion"], ["map", "parameter", "eventLabel", "parameterValue", "registration"]],
                "vtp_eventName": "email confirmation",
                "vtp_measurementIdOverride": ["macro", 48],
                "vtp_enableUserProperties": true,
                "vtp_enableMoreSettingsOption": true,
                "vtp_enableEuid": true,
                "vtp_migratedToV2": true,
                "vtp_demoV2": false,
                "tag_id": 519
            }, {
                "function": "__ua",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_nonInteraction": false,
                "vtp_overrideGaSettings": false,
                "vtp_eventCategory": ["macro", 18],
                "vtp_trackType": "TRACK_EVENT",
                "vtp_gaSettings": ["macro", 34],
                "vtp_eventAction": ["macro", 35],
                "vtp_eventLabel": ["macro", 36],
                "vtp_enableRecaptchaOption": false,
                "vtp_enableUaRlsa": false,
                "vtp_enableUseInternalVersion": false,
                "vtp_enableFirebaseCampaignData": true,
                "vtp_trackTypeIsEvent": true,
                "vtp_enableGA4Schema": true,
                "tag_id": 546
            }, {
                "function": "__gaawe",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_sendEcommerceData": false,
                "vtp_eventSettingsTable": ["list", ["map", "parameter", "eventCategory", "parameterValue", ["macro", 3]], ["map", "parameter", "eventLabel", "parameterValue", ["macro", 17]], ["map", "parameter", "elementID", "parameterValue", ["macro", 26]], ["map", "parameter", "country", "parameterValue", ["macro", 30]], ["map", "parameter", ["macro", 50], "parameterValue", ["macro", 12]]],
                "vtp_eventName": ["macro", 16],
                "vtp_measurementIdOverride": ["macro", 48],
                "vtp_enableUserProperties": true,
                "vtp_enableMoreSettingsOption": true,
                "vtp_enableEuid": true,
                "vtp_migratedToV2": true,
                "vtp_demoV2": false,
                "tag_id": 547
            }, {
                "function": "__cvt_32196322_451",
                "metadata": ["map"],
                "consent": ["list", "personalization_storage"],
                "once_per_event": true,
                "vtp_disablePushState": false,
                "vtp_pixelId": ["macro", 47],
                "vtp_objectPropertyList": ["list", ["map", "name", "category", "value", ["macro", 3]], ["map", "name", "action", "value", ["macro", 16]], ["map", "name", "label", "value", ["macro", 17]]],
                "vtp_disableAutoConfig": false,
                "vtp_enhancedEcommerce": false,
                "vtp_dpoLDU": false,
                "vtp_eventName": "custom",
                "vtp_objectPropertiesFromVariable": false,
                "vtp_customEventName": "Landing_page_Get_started_click",
                "vtp_consent": true,
                "vtp_advancedMatching": false,
                "tag_id": 553
            }, {
                "function": "__cvt_32196322_451",
                "metadata": ["map"],
                "consent": ["list", "personalization_storage"],
                "once_per_event": true,
                "vtp_disablePushState": false,
                "vtp_pixelId": ["macro", 47],
                "vtp_objectPropertyList": ["list", ["map", "name", "category", "value", ["macro", 3]], ["map", "name", "action", "value", ["macro", 16]], ["map", "name", "label", "value", ["macro", 17]]],
                "vtp_disableAutoConfig": false,
                "vtp_enhancedEcommerce": false,
                "vtp_dpoLDU": false,
                "vtp_eventName": "custom",
                "vtp_objectPropertiesFromVariable": false,
                "vtp_customEventName": "Complete_Card_order",
                "vtp_consent": true,
                "vtp_advancedMatching": false,
                "tag_id": 554
            }, {
                "function": "__paused",
                "vtp_originalTagType": "opt",
                "tag_id": 557
            }, {
                "function": "__paused",
                "vtp_originalTagType": "opt",
                "tag_id": 576
            }, {
                "function": "__paused",
                "vtp_originalTagType": "opt",
                "tag_id": 588
            }, {
                "function": "__cvt_32196322_451",
                "metadata": ["map"],
                "consent": ["list", "personalization_storage"],
                "once_per_event": true,
                "vtp_disablePushState": false,
                "vtp_pixelId": ["macro", 47],
                "vtp_objectPropertyList": ["list", ["map", "name", "category", "value", ["macro", 3]], ["map", "name", "action", "value", ["macro", 16]], ["map", "name", "label", "value", ["macro", 17]]],
                "vtp_disableAutoConfig": false,
                "vtp_enhancedEcommerce": false,
                "vtp_dpoLDU": false,
                "vtp_eventName": "custom",
                "vtp_objectPropertiesFromVariable": false,
                "vtp_customEventName": "Card_order_shipping_info_order_click",
                "vtp_consent": true,
                "vtp_advancedMatching": false,
                "tag_id": 598
            }, {
                "function": "__cvt_32196322_451",
                "metadata": ["map"],
                "consent": ["list", "personalization_storage"],
                "once_per_event": true,
                "vtp_disablePushState": false,
                "vtp_pixelId": ["macro", 47],
                "vtp_objectPropertyList": ["list", ["map", "name", "category", "value", ["macro", 3]], ["map", "name", "action", "value", ["macro", 16]], ["map", "name", "label", "value", ["macro", 17]]],
                "vtp_disableAutoConfig": false,
                "vtp_enhancedEcommerce": false,
                "vtp_dpoLDU": false,
                "vtp_eventName": "custom",
                "vtp_objectPropertiesFromVariable": false,
                "vtp_customEventName": "binance_card_get_started_click",
                "vtp_consent": true,
                "vtp_advancedMatching": false,
                "tag_id": 600
            }, {
                "function": "__cvt_32196322_451",
                "metadata": ["map"],
                "consent": ["list", "personalization_storage"],
                "once_per_event": true,
                "vtp_disablePushState": false,
                "vtp_pixelId": ["macro", 47],
                "vtp_objectPropertyList": ["list", ["map", "name", "category", "value", ["macro", 3]], ["map", "name", "action", "value", ["macro", 16]], ["map", "name", "label", "value", ["macro", 17]]],
                "vtp_disableAutoConfig": false,
                "vtp_enhancedEcommerce": false,
                "vtp_dpoLDU": false,
                "vtp_eventName": "custom",
                "vtp_objectPropertiesFromVariable": false,
                "vtp_customEventName": "Card_order_VC_ready_popup_view",
                "vtp_consent": true,
                "vtp_advancedMatching": false,
                "tag_id": 602
            }, {
                "function": "__baut",
                "metadata": ["map"],
                "consent": ["list", "personalization_storage"],
                "once_per_event": true,
                "vtp_c_navTimingApi": false,
                "vtp_tagId": "137033855",
                "vtp_c_storeConvTrackCookies": true,
                "vtp_uetqName": "uetq",
                "vtp_c_disableAutoPageView": false,
                "vtp_c_removeQueryFromUrls": false,
                "vtp_eventType": "PAGE_LOAD",
                "tag_id": 615
            }, {
                "function": "__baut",
                "metadata": ["map"],
                "consent": ["list", "personalization_storage"],
                "once_per_load": true,
                "vtp_p_currency": "USD",
                "vtp_eventCategory": "add_to_cart",
                "vtp_uetqName": "uetq",
                "vtp_customEventAction": "add_to_cart",
                "vtp_eventType": "CUSTOM",
                "tag_id": 616
            }, {
                "function": "__ua",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_nonInteraction": false,
                "vtp_overrideGaSettings": false,
                "vtp_eventCategory": ["macro", 18],
                "vtp_trackType": "TRACK_EVENT",
                "vtp_gaSettings": ["macro", 34],
                "vtp_eventAction": ["macro", 35],
                "vtp_eventLabel": ["macro", 36],
                "vtp_enableRecaptchaOption": false,
                "vtp_enableUaRlsa": false,
                "vtp_enableUseInternalVersion": false,
                "vtp_enableFirebaseCampaignData": true,
                "vtp_trackTypeIsEvent": true,
                "vtp_enableGA4Schema": true,
                "tag_id": 618
            }, {
                "function": "__gaawe",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_sendEcommerceData": false,
                "vtp_eventSettingsTable": ["list", ["map", "parameter", "eventCategory", "parameterValue", ["macro", 18]], ["map", "parameter", "eventLabel", "parameterValue", ["macro", 36]], ["map", "parameter", "elementID", "parameterValue", ["macro", 26]], ["map", "parameter", ["macro", 50], "parameterValue", ["macro", 12]]],
                "vtp_eventName": ["macro", 35],
                "vtp_measurementIdOverride": ["macro", 48],
                "vtp_enableUserProperties": true,
                "vtp_enableMoreSettingsOption": true,
                "vtp_enableEuid": true,
                "vtp_migratedToV2": true,
                "vtp_demoV2": false,
                "tag_id": 619
            }, {
                "function": "__ua",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_nonInteraction": false,
                "vtp_overrideGaSettings": false,
                "vtp_eventCategory": ["macro", 18],
                "vtp_trackType": "TRACK_EVENT",
                "vtp_gaSettings": ["macro", 34],
                "vtp_eventAction": ["macro", 35],
                "vtp_eventLabel": ["macro", 36],
                "vtp_enableRecaptchaOption": false,
                "vtp_enableUaRlsa": false,
                "vtp_enableUseInternalVersion": false,
                "vtp_enableFirebaseCampaignData": true,
                "vtp_trackTypeIsEvent": true,
                "vtp_enableGA4Schema": true,
                "tag_id": 622
            }, {
                "function": "__gaawe",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_sendEcommerceData": false,
                "vtp_eventSettingsTable": ["list", ["map", "parameter", "eventCategory", "parameterValue", ["macro", 18]], ["map", "parameter", "eventLabel", "parameterValue", ["macro", 36]], ["map", "parameter", "elementID", "parameterValue", ["macro", 26]], ["map", "parameter", ["macro", 50], "parameterValue", ["macro", 12]]],
                "vtp_eventName": ["macro", 35],
                "vtp_measurementIdOverride": ["macro", 48],
                "vtp_enableUserProperties": true,
                "vtp_enableMoreSettingsOption": true,
                "vtp_enableEuid": true,
                "vtp_migratedToV2": true,
                "vtp_demoV2": false,
                "tag_id": 623
            }, {
                "function": "__ua",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_nonInteraction": false,
                "vtp_overrideGaSettings": false,
                "vtp_eventCategory": ["macro", 18],
                "vtp_trackType": "TRACK_EVENT",
                "vtp_gaSettings": ["macro", 42],
                "vtp_eventAction": ["macro", 35],
                "vtp_eventLabel": ["macro", 36],
                "vtp_enableRecaptchaOption": false,
                "vtp_enableUaRlsa": false,
                "vtp_enableUseInternalVersion": false,
                "vtp_enableFirebaseCampaignData": true,
                "vtp_trackTypeIsEvent": true,
                "vtp_enableGA4Schema": true,
                "tag_id": 626
            }, {
                "function": "__ua",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_nonInteraction": false,
                "vtp_overrideGaSettings": false,
                "vtp_eventCategory": ["macro", 18],
                "vtp_trackType": "TRACK_EVENT",
                "vtp_gaSettings": ["macro", 42],
                "vtp_eventAction": ["macro", 35],
                "vtp_eventLabel": ["macro", 36],
                "vtp_enableRecaptchaOption": false,
                "vtp_enableUaRlsa": false,
                "vtp_enableUseInternalVersion": false,
                "vtp_enableFirebaseCampaignData": true,
                "vtp_trackTypeIsEvent": true,
                "vtp_enableGA4Schema": true,
                "tag_id": 627
            }, {
                "function": "__gaawe",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_sendEcommerceData": true,
                "vtp_getEcommerceDataFrom": "dataLayer",
                "vtp_eventSettingsTable": ["list", ["map", "parameter", "eventCategory", "parameterValue", ["macro", 18]], ["map", "parameter", "eventLabel", "parameterValue", ["macro", 36]], ["map", "parameter", "elementID", "parameterValue", ["macro", 26]], ["map", "parameter", "eventAction", "parameterValue", ["macro", 35]]],
                "vtp_eventName": "view_promotion",
                "vtp_measurementIdOverride": ["macro", 48],
                "vtp_enableUserProperties": true,
                "vtp_enableMoreSettingsOption": true,
                "vtp_enableEuid": true,
                "vtp_migratedToV2": true,
                "vtp_demoV2": false,
                "tag_id": 628
            }, {
                "function": "__gaawe",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_sendEcommerceData": true,
                "vtp_getEcommerceDataFrom": "dataLayer",
                "vtp_eventSettingsTable": ["list", ["map", "parameter", "eventCategory", "parameterValue", ["macro", 18]], ["map", "parameter", "eventLabel", "parameterValue", ["macro", 36]], ["map", "parameter", "elementID", "parameterValue", ["macro", 26]], ["map", "parameter", "eventAction", "parameterValue", ["macro", 35]]],
                "vtp_eventName": "select_promotion",
                "vtp_measurementIdOverride": ["macro", 48],
                "vtp_enableUserProperties": true,
                "vtp_enableMoreSettingsOption": true,
                "vtp_enableEuid": true,
                "vtp_migratedToV2": true,
                "vtp_demoV2": false,
                "tag_id": 629
            }, {
                "function": "__cvt_32196322_349",
                "metadata": ["map"],
                "once_per_event": true,
                "vtp_ad_storage": ["macro", 56],
                "vtp_ads_data_redaction": false,
                "vtp_sendDataLayer": true,
                "vtp_ad_user_data": ["macro", 57],
                "vtp_security_storage": "granted",
                "vtp_command": "update",
                "vtp_functionality_storage": "granted",
                "vtp_personalization_storage": ["macro", 58],
                "vtp_url_passthrough": false,
                "vtp_analytics_storage": ["macro", 59],
                "vtp_ad_personalization": ["macro", 60],
                "tag_id": 646
            }, {
                "function": "__googtag",
                "metadata": ["map"],
                "once_per_load": true,
                "vtp_tagId": ["macro", 61],
                "vtp_userProperties": ["list", ["map", "name", "userID", "value", ["macro", 5]], ["map", "name", "clientID", "value", ["macro", 49]], ["map", "name", "bncuuID", "value", ["macro", 7]], ["map", "name", "ref", "value", ["macro", 11]]],
                "vtp_configSettingsTable": ["list", ["map", "parameter", "user_id", "parameterValue", ["macro", 5]], ["map", "parameter", "elementID", "parameterValue", ["macro", 26]], ["map", "parameter", "pageName", "parameterValue", ["macro", 8]], ["map", "parameter", "language", "parameterValue", ["macro", 19]], ["map", "parameter", "layout", "parameterValue", ["macro", 32]], ["map", "parameter", "cryptoID", "parameterValue", ["macro", 20]], ["map", "parameter", "fiatID", "parameterValue", ["macro", 21]], ["map", "parameter", "payentmethodID", "parameterValue", ["macro", 22]], ["map", "parameter", "railID", "parameterValue", ["macro", 23]], ["map", "parameter", "cardID", "parameterValue", ["macro", 24]], ["map", "parameter", "kycLevel", "parameterValue", ["macro", 27]], ["map", "parameter", "kycCountry", "parameterValue", ["macro", 30]], ["map", "parameter", "flow", "parameterValue", ["macro", 31]], ["map", "parameter", "error", "parameterValue", ["macro", 25]], ["map", "parameter", "containerID", "parameterValue", ["macro", 10]], ["map", "parameter", "country", "parameterValue", ["macro", 30]], ["map", "parameter", "send_page_view", "parameterValue", "true"]],
                "tag_id": 654
            }, {
                "function": "__ua",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_load": true,
                "vtp_overrideGaSettings": false,
                "vtp_trackType": "TRACK_PAGEVIEW",
                "vtp_gaSettings": ["macro", 62],
                "vtp_enableRecaptchaOption": false,
                "vtp_enableUaRlsa": false,
                "vtp_enableUseInternalVersion": false,
                "vtp_enableFirebaseCampaignData": true,
                "vtp_enableGA4Schema": true,
                "tag_id": 659
            }, {
                "function": "__ua",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_load": true,
                "vtp_overrideGaSettings": false,
                "vtp_trackType": "TRACK_PAGEVIEW",
                "vtp_gaSettings": ["macro", 41],
                "vtp_enableRecaptchaOption": false,
                "vtp_enableUaRlsa": false,
                "vtp_enableUseInternalVersion": false,
                "vtp_enableFirebaseCampaignData": true,
                "vtp_enableGA4Schema": true,
                "tag_id": 662
            }, {
                "function": "__ua",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_load": true,
                "vtp_overrideGaSettings": false,
                "vtp_trackType": "TRACK_PAGEVIEW",
                "vtp_gaSettings": ["macro", 62],
                "vtp_enableRecaptchaOption": false,
                "vtp_enableUaRlsa": false,
                "vtp_enableUseInternalVersion": false,
                "vtp_enableFirebaseCampaignData": true,
                "vtp_enableGA4Schema": true,
                "tag_id": 664
            }, {
                "function": "__ua",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_nonInteraction": false,
                "vtp_overrideGaSettings": false,
                "vtp_eventCategory": ["macro", 3],
                "vtp_trackType": "TRACK_EVENT",
                "vtp_gaSettings": ["macro", 15],
                "vtp_eventAction": ["macro", 16],
                "vtp_eventLabel": ["macro", 17],
                "vtp_enableRecaptchaOption": false,
                "vtp_enableUaRlsa": false,
                "vtp_enableUseInternalVersion": false,
                "vtp_enableFirebaseCampaignData": true,
                "vtp_trackTypeIsEvent": true,
                "vtp_enableGA4Schema": true,
                "tag_id": 672
            }, {
                "function": "__gaawe",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_sendEcommerceData": false,
                "vtp_eventSettingsTable": ["list", ["map", "parameter", "eventCategory", "parameterValue", ["macro", 3]], ["map", "parameter", "eventLabel", "parameterValue", ["macro", 17]], ["map", "parameter", "elementID", "parameterValue", ["macro", 26]], ["map", "parameter", "country", "parameterValue", ["macro", 30]], ["map", "parameter", "layout", "parameterValue", ["macro", 32]], ["map", "parameter", "cryptoID", "parameterValue", ["macro", 20]], ["map", "parameter", "fiatID", "parameterValue", ["macro", 21]], ["map", "parameter", "payentmethodID", "parameterValue", ["macro", 22]], ["map", "parameter", "railID", "parameterValue", ["macro", 23]], ["map", "parameter", "cardID", "parameterValue", ["macro", 24]], ["map", "parameter", ["macro", 50], "parameterValue", ["macro", 12]]],
                "vtp_eventName": ["macro", 16],
                "vtp_measurementIdOverride": ["macro", 48],
                "vtp_enableUserProperties": true,
                "vtp_enableMoreSettingsOption": true,
                "vtp_enableEuid": true,
                "vtp_migratedToV2": true,
                "vtp_demoV2": false,
                "tag_id": 673
            }, {
                "function": "__cvt_32196322_678",
                "metadata": ["map"],
                "once_per_event": true,
                "vtp_orderId": ["macro", 13],
                "vtp_label": ["macro", 36],
                "tag_id": 684
            }, {
                "function": "__gaawe",
                "metadata": ["map"],
                "once_per_event": true,
                "vtp_sendEcommerceData": false,
                "vtp_enhancedUserId": false,
                "vtp_eventSettingsTable": ["list", ["map", "parameter", "eventCategory", "parameterValue", "feed_post_profile"], ["map", "parameter", "author", "parameterValue", ["macro", 63]], ["map", "parameter", "pageName", "parameterValue", ["macro", 64]], ["map", "parameter", "topic", "parameterValue", ["macro", 65]]],
                "vtp_userProperties": ["list", ["map", "name", "bncuuID", "value", ["macro", 7]], ["map", "name", "userID", "value", ["macro", 5]]],
                "vtp_eventName": "measure_event",
                "vtp_measurementIdOverride": ["macro", 48],
                "vtp_enableUserProperties": true,
                "vtp_enableMoreSettingsOption": true,
                "vtp_enableEuid": true,
                "vtp_migratedToV2": true,
                "vtp_demoV2": false,
                "tag_id": 695
            }, {
                "function": "__cl",
                "tag_id": 696
            }, {
                "function": "__cl",
                "tag_id": 697
            }, {
                "function": "__cl",
                "tag_id": 698
            }, {
                "function": "__cl",
                "tag_id": 699
            }, {
                "function": "__cl",
                "tag_id": 700
            }, {
                "function": "__cl",
                "tag_id": 701
            }, {
                "function": "__cl",
                "tag_id": 702
            }, {
                "function": "__cl",
                "tag_id": 703
            }, {
                "function": "__sdl",
                "vtp_verticalThresholdUnits": "PERCENT",
                "vtp_verticalThresholdsPercent": "10,25,50,75,90",
                "vtp_verticalThresholdOn": true,
                "vtp_triggerStartOption": "WINDOW_LOAD",
                "vtp_horizontalThresholdOn": false,
                "vtp_uniqueTriggerId": "32196322_226",
                "vtp_enableTriggerStartOption": true,
                "tag_id": 704
            }, {
                "function": "__sdl",
                "vtp_verticalThresholdUnits": "PERCENT",
                "vtp_verticalThresholdsPercent": "10,25,50,75,90",
                "vtp_verticalThresholdOn": true,
                "vtp_triggerStartOption": "WINDOW_LOAD",
                "vtp_horizontalThresholdOn": false,
                "vtp_uniqueTriggerId": "32196322_231",
                "vtp_enableTriggerStartOption": true,
                "tag_id": 705
            }, {
                "function": "__hl",
                "tag_id": 706
            }, {
                "function": "__hl",
                "tag_id": 707
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\"\u003Evar flag1=!0,flag2=!0;document.body.addEventListener(\"DOMSubtreeModified\",gatest);\nfunction gatest(){flag1\u0026\u0026document.getElementById(\"header_register\")\u0026\u0026(document.getElementById(\"header_register\").addEventListener(\"click\",function(){dataLayer.push({eventCategory:\"registration\",eventAction:\"click\",eventLabel:\"registration::start\",elementid:\"header_register\",event:\"click\"})}),flag1=!1);flag2\u0026\u0026document.getElementById(\"header_login\")\u0026\u0026(document.getElementById(\"header_login\").addEventListener(\"click\",function(){dataLayer.push({eventCategory:\"login\",eventAction:\"click\",eventLabel:\"login::start\",\nelementid:\"header_login\",event:\"click\"})}),flag2=!1)};\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": true,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "vtp_usePostscribe": true,
                "tag_id": 86
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\"\u003Evar flag7=!0,flag8=!0;document.body.addEventListener(\"DOMSubtreeModified\",gatest);function gatest(){flag7\u0026\u0026document.getElementById(\"click_login_submit\")\u0026\u0026(document.getElementById(\"click_login_submit\").addEventListener(\"click\",function(){var a=document.getElementsByClassName(\"active\")[0].textContent;dataLayer.push({eventCategory:\"login\",eventAction:\"submit\",eventLabel:\"login::\"+a,elementid:\"click_login_submit\",event:\"click\"})}),flag7=!1)};\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": true,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "vtp_usePostscribe": true,
                "tag_id": 88
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\"\u003Evar flag9=!0;document.body.addEventListener(\"DOMSubtreeModified\",gatest);function gatest(){flag9\u0026\u0026document.getElementById(\"click-registration-submit\")\u0026\u0026(document.getElementById(\"click-registration-submit\").addEventListener(\"click\",function(){var a=document.getElementsByClassName(\"active\")[0].textContent;dataLayer.push({eventCategory:\"registration\",eventAction:\"click\",eventLabel:\"registration::\"+a,elementid:\"click-registration-submit\",event:\"click\"})}),flag9=!1)};\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": true,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "vtp_usePostscribe": true,
                "tag_id": 89
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\"\u003Evar flag10=!0,flag11=!0;document.body.addEventListener(\"DOMSubtreeModified\",gatest);function gatest(){flag10\u0026\u0026document.getElementById(\"click-voice-Verification-voice\")\u0026\u0026(document.getElementById(\"click-voice-Verification-voice\").addEventListener(\"click\",function(){dataLayer.push({eventCategory:\"registration\",eventAction:\"click\",eventLabel:\"registration::email_resend\",elementid:\"click-voice-Verification-voicev\",event:\"click\"})}),flag10=!1)};\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": true,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "vtp_usePostscribe": true,
                "tag_id": 96
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\" type=\"text\/gtmscript\"\u003Edocument.querySelector(\"body\").addEventListener(\"click\",function(a){(a.target.id.match(\/^market_sector_favorite_.*\/)||a.target.id.match(\/^market_filter_Zone_.*\/)||a.target.id.match(\/^market_filter_spot_.*\/)||a.target.id.match(\/^market_filter_futures_.*\/))\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"mk_market sector\",eventAction:\"click\",eventLabel:\"market::sector_\"+a.target.innerHTML,elementid:a.target.id});a.target.id.match(\/^market_3rd_filter.*\/)\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"mk_marketfilter\",\neventAction:\"click\",eventLabel:\"market::filter_\"+a.target.innerHTML,elementid:a.target.id});\"market_sector_overview\"==a.target.id\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"mk_marketsoverview\",eventAction:\"click\",eventLabel:\"market::markets_overview\",elementid:\"market_sector_overview\"});\"market_sector_moves\"==a.target.id\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"mk_marketsoverview\",eventAction:\"click\",eventLabel:\"market::markets_overview\",elementid:\"market_sector_moves\"});\"market_filter_ranking_quoteVolume|number|desc\"==\na.target.id\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"mo_24hrankings\",eventAction:\"click\",eventLabel:\"mo_24h_rankings::volume\",elementid:\"market_filter_ranking_quoteVolume|number|desc\"});\"market_filter_ranking_difference|number|desc\"==a.target.id\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"mo_24hrankings\",eventAction:\"click\",eventLabel:\"mo_24h_rankings::gainers\",elementid:\"market_filter_ranking_difference|number|desc\"});\"market_filter_ranking_difference|number|asc\"==a.target.id\u0026\u0026dataLayer.push({event:\"click\",\neventCategory:\"mo_24hrankings\",eventAction:\"click\",eventLabel:\"mo_24h_rankings::losers\",elementid:\"market_filter_ranking_difference|number|asc\"});\"market_overview_topmovers_arrow\"==a.target.id\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"mo_topmovers\",eventAction:\"click\",eventLabel:\"mo_top_movers::view_more\",elementid:\"market_overview_topmovers_arrow\"});\"market_filter_derivativestop_perpetual\"==a.target.id\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"mo_topderivatives\",eventAction:\"click\",eventLabel:\"mo_top_derivatives::coin\",\nelementid:\"market_filter_derivativestop_perpetual\"});\"market_filter_derivativestop_quarterly\"==a.target.id\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"mo_topderivatives\",eventAction:\"click\",eventLabel:\"mo_topderivatives_usdt\",elementid:\"market_filter_derivativestop_quarterly\"});\"market_filter_derivativestop_etf\"==a.target.id\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"mo_topderivatives\",eventAction:\"click\",eventLabel:\"mo_topderivatives_etf\",elementid:\"market_filter_derivativestop_etf\"})});\ntry{document.getElementById(\"markets_main_search\").addEventListener(\"change\",function(){dataLayer.push({event:\"click\",eventCategory:\"mk_searchbar\",eventAction:\"click\",eventLabel:\"market::search_\"+document.getElementById(\"markets_main_search\").value,elementid:\"markets_main_search\"})})}catch(a){};\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": false,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "tag_id": 137
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\" type=\"text\/gtmscript\"\u003Etry{document.getElementById(\"topcta_mainbtn_buynow\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"hp_buycrypto\",eventAction:\"click\",eventLabel:\"homepage::buy_now\",elementid:\"topcta_mainbtn_buynow\"})}),document.getElementById(\"newtopcta_mainbtn_buynow\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"hp_buycrypto\",eventAction:\"click\",eventLabel:\"homepage::buy_now\",elementid:\"newtopcta_mainbtn_buynow\"})})}catch(a){}\ntry{document.getElementById(\"announcement_template_item\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"hp_announcement\",eventAction:\"click\",eventLabel:\"homepage::announcement_\"+this.getAttribute(\"data-title\"),elementid:\"announcement_template_item\"})}),document.getElementById(\"announcement_template_more\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"hp_announcement\",eventAction:\"click\",eventLabel:\"homepage::view_more_announcement\",\nelementid:\"announcement_template_more\"})}),document.getElementById(\"top_crypto_view_more\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"hp_markets\",eventAction:\"click\",eventLabel:\"homepage::view_more_markets\",elementid:\"top_crypto_view_more\"})}),document.getElementById(\"banner_activity_item\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"hp_activity\",eventAction:\"click\",eventLabel:\"homepage::activity\"+this.getAttribute(\"alt\"),\nelementid:\"banner_activity_item\"})}),document.getElementById(\"download_mobile_app_store\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"hp_download\",eventAction:\"click\",eventLabel:\"homepage::mobile_\"+this.lastChild.innerHTML,elementid:this.id})}),document.getElementById(\"download_mobile_android_apk\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"hp_download\",eventAction:\"click\",eventLabel:\"homepage::mobile_\"+this.lastChild.innerHTML,\nelementid:this.id})}),document.getElementById(\"download_mobile_google_play\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"hp_download\",eventAction:\"click\",eventLabel:\"homepage::mobile_\"+this.lastChild.innerHTML,elementid:this.id})}),document.getElementById(\"download_desktop_mac\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"hp_download\",eventAction:\"click\",eventLabel:\"homepage::desktop_\"+this.lastChild.innerHTML,elementid:this.id})}),\ndocument.getElementById(\"download_desktop_windows\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"hp_download\",eventAction:\"click\",eventLabel:\"homepage::desktop_\"+this.lastChild.innerHTML,elementid:this.id})}),document.getElementById(\"download_desktop_linux\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"hp_download\",eventAction:\"click\",eventLabel:\"homepage::desktop_\"+this.lastChild.innerHTML,elementid:this.id})}),document.getElementById(\"download_api\").addEventListener(\"click\",\nfunction(){dataLayer.push({event:\"click\",eventCategory:\"hp_download\",eventAction:\"click\",eventLabel:\"homepage::api\",elementid:\"download_api\"})}),document.getElementById(\"download_view_more\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"hp_download\",eventAction:\"click\",eventLabel:\"homepage::view_more_downloads\",elementid:\"download_view_more\"})}),document.querySelector(\"body\").addEventListener(\"click\",function(a){if(a.target.id.match(\/^horizontal_card_panel_.*\/)){var b=\na.target.id,c=b.lastIndexOf(\"_\");b=b.substring(c+1,b.length);dataLayer.push({event:\"click\",eventCategory:\"hp_contactus\",eventAction:\"click\",eventLabel:\"homepage::contact_\"+b,elementid:a.target.id})}}),document.getElementById(\"buttom_cta_trade_now\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"hp_trade\",eventAction:\"click\",eventLabel:\"homepage::trade_now\",elementid:\"buttom_cta_trade_now\"})})}catch(a){};\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": false,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "tag_id": 138
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\"\u003Edocument.querySelector(\"body\").addEventListener(\"click\",function(a){if(a.target.id.match(\/^fiatlngdialog_ba-languageRegion.*\/)||a.target.parentNode.id.match(\/^fiatlngdialog_ba-languageRegion.*\/)){if(a.target.id.match(\/^fiatlngdialog_ba-languageRegion.*\/))var b=a.target.firstChild.innerHTML.indexOf(\"(\"),c=a.target;else b=a.target.parentNode.firstChild.innerHTML.indexOf(\"(\"),c=a.target.parentNode;if(0\u003Cb){var d=c.firstChild.innerHTML.substring(0,b);c.firstChild.innerHTML.substring(b+1,c.firstChild.innerHTML.length-\n1)}else d=c.firstChild.innerHTML;dataLayer.push({event:\"language_region\",eventCategory:\"lr_language\",eventAction:\"click\",eventLabel:\"language::\"+d,elementid:c.id})}if(a.target.id.match(\/^fiatlngdialog_ba-Currency.*\/)||a.target.parentNode.id.match(\/^fiatlngdialog_ba-Currency.*\/))a.target.id.match(\/^fiatlngdialog_ba-Currency.*\/)?(b=a.target.firstChild.innerHTML,a=a.target.id):(b=a.target.parentNode.firstChild.innerHTML,a=a.target.parentNode.id),dataLayer.push({event:\"currency\",eventCategory:\"cr_currency\",\neventAction:\"click\",eventLabel:\"currency::\"+b,elementid:a})});\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": true,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "vtp_usePostscribe": true,
                "tag_id": 139
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\"\u003Evar gaGet_kycType=function(c){var e=\"basic\";\/intermediate\/i.test(c)?e=\"intermediate\":\/pro\/i.test(c)?e=\"advanced_pro\":\/advanced\/i.test(c)\u0026\u0026(e=\"advanced\");return e};\n(function(){var c=\"ac_kyc\",e=\"popup click\",f={},g=[\"kyc_bv\",\"'kyc_iv\",\"kyc_av\",\"kyc_apv\"],h=document.getElementsByTagName(\"body\")[0];window.navigator\u0026\u0026window.navigator.language\u0026\u0026dataLayer.push({language:window.navigator.language});0\u003Cdocument.querySelectorAll(\"#verification_center_page_exposure input.bn-sdd-input\").length\u0026\u0026document.querySelectorAll(\"#verification_center_page_exposure input.bn-sdd-input\")[0].value\u0026\u0026dataLayer.push({KYC_dlvar_kycCountry:document.querySelectorAll(\"#verification_center_page_exposure input.bn-sdd-input\")[0].value});\nvar k=[{eid:\"popup_click_binance_popup_click_kyc_verification_center_page_basic_popup_continue\",el:\"kyc_bv::basic_verification_continue\"},{eid:\"popup_click_binance_popup_click_kyc_verification_center_page_basic_popup_confirm\",el:\"kyc_bv::basic_verification_confirm\"},{eid:\"popup_click_binance_popup_click_kyc_verification_center_page_intermediate_popup_begin\",el:\"kyc_iv::intermediate_verification_begin\"},{eid:\"popup_click_binance_popup_click_kyc_verification_center_page_intermediate_popup_upload_id_continue\",\nel:\"kyc_iv::intermediate_verification_id_continue\"},{eid:\"popup_click_binance_popup_click_kyc_verification_center_page_intermediate_popup_upload_photo_continue\",el:\"kyc_iv::intermediate_verification_photo_continue\"},{eid:\"popup_click_binance_popup_click_kyc_verification_center_page_intermediate_popup_video_continue\",el:\"kyc_iv::intermediate_verification_video_continue\"},{eid:\"popup_click_binance_popup_click_kyc_verification_center_page_intermediate_popup_video_switch_qr_code\",el:\"kyc_iv::intermediate_verification_video_qr_code\"},\n{eid:\"popup_click_binance_popup_click_kyc_verification_center_page_advanced_popup_continue\",el:\"kyc_av::advanced_verification_residential_continue\"},{eid:\"popup_click_binance_popup_click_kyc_verification_center_page_advanced_popup_confirm\",el:\"kyc_av::advanced_verification_upload_continue\"},{eid:\"popup_click_binance_popup_click_kyc_verification_center_page_advanced_pro_popup_continue\",el:\"kyc_apv::advanced_pro_verification_continue\"},{eid:\"popup_click_binance_popup_click_kyc_verification_center_page_advanced_pro_popup_confirm\",\nel:\"kyc_apv::advanced_pro_verification_confirm\"}],l=[{eid:\"popup_view_binance_screen_kyc_verification_center_page_account_verified_popup_view\",el:\"kyc_vc::$kyclevel_verified\"},{eid:\"popup_view_binance_screen_kyc_verification_center_page_under_repopup_view_popup_continue\",el:\"kyc_vc::$kyclevel_under_review\"}];try{document.querySelectorAll(\".click_binance_click_kyc_verification_center_page_verify\").forEach(function(d){d.addEventListener(\"click\",function(){var b=0,a=gaGet_kycType(d.parentNode.firstChild.innerText);\ndataLayer.push({eventCategory:c,eventAction:\"click\",eventLabel:\"kyc_vc::$kyclevel_verify_now\".replace(\"$kyclevel\",a),KYC_dlvar_kycLevel:a,elementId:\"click_binance_click_kyc_verification_center_page_verify\",event:\"GA_TM_cme_KYC\"});dataLayer.push({eventCategory:c,eventAction:\"popup_view\",eventLabel:\"$vName::$kyclevel_verify_now\".replace(\"$vName\",g[b]).replace(\"$kyclevel\",a),KYC_dlvar_kycLevel:a,elementId:\"popup_view_binance_screen_kyc_verification_center_page_$vName_popup_view\".replace(\"$vName\",g[b]),\nevent:\"GA_TM_cme_KYC\"})})});h.addEventListener(\"click\",function(d){var b=d.target.className;50\u003Cb.length\u0026\u0026k.forEach(function(a){console.log(new RegExp(a.eid));(new RegExp(a.eid)).test(b)\u0026\u0026dataLayer.push({eventCategory:c,eventAction:e,eventLabel:a.el,elementId:a.eid,event:\"GA_TM_cme_KYC\"})})});var m=function(){l.forEach(function(d){var b=d.eid;if(0\u003Cdocument.getElementsByClassName(b).length\u0026\u0026!f[b]){var a=gaGet_kycType(document.getElementsByClassName(b)[0].firstChild.innerText);dataLayer.push({eventCategory:c,\neventAction:\"popup_view\",eventLabel:d.el.replace(\"$kyclevel\",a),KYC_dlvar_kycLevel:a,elementId:b,event:\"GA_TM_cme_KYC\"});f[b]=!0}})},n=new MutationObserver(m);n.observe(h,{childList:!0,subtree:!0})}catch(d){}})();\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": true,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "vtp_usePostscribe": true,
                "tag_id": 147
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\"\u003E(function(){var d={},e=document.getElementsByTagName(\"body\")[0],f=[{eid:\"binance_click_fiat_buy_with_card_select_payment_page_add_new_card_confirmation_popup_confirm\",ec:\"fb_card\",ea:\"popup_click\",el:\"fb_card::add_new_card_confirm_add\"},{eid:\"binance_click_fiat_buy_with_card_select_payment_page_change_card_popup_add_new_card\",ec:\"fb_card\",ea:\"popup_click\",el:\"fb_card::change_card_add_new_card\"},{eid:\"binance_click_fiat_multiple_buy_select_payment_page_add_new_card_confirmation_popup_confirm\",ec:\"fb_multiple\",\nea:\"popup_click\",el:\"fb_multiple::add_new_card_confirm_add\"},{eid:\"binance_click_fiat_multiple_buy_select_payment_page_change_card_popup_confirm\",ec:\"fb_multiple\",ea:\"popup_click\",el:\"fb_multiple::change_card_confirm\"},{eid:\"binance_click_fiat_multiple_buy_select_payment_page_change_card_popup_add_new_card\",ec:\"fb_multiple\",ea:\"popup_click\",el:\"fb_multiple::change_card_add_new_card\"},{eid:\"binance_click_fiat_deposit_enter_amount_page_add_new_card_confirmation_popup_confirm\",ec:\"fiat_deposit\",ea:\"click\",\nel:\"fiat_deposit::add_new_card_confirm_add\"},{eid:\"binance_click_fiat_deposit_enter_amount_page_change_card_popup_add_new_card\",ec:\"fiat_deposit\",ea:\"popup_click\",el:\"fiat_deposit::change_card_add_new_card\"},{eid:\"binance_click_fiat_sell_select_payment_page_confirm\",ec:\"fs_multiple\",ea:\"popup_click\",el:\"fs_multiple::confirmation_confirm\"},{eid:\"binance_click_fiat_sell_select_payment_page_refresh\",ec:\"fs_multiple\",ea:\"popup_click\",el:\"fs_multiple::confirmation_refresh\"},{eid:\"binance_click_fiat_withdraw_detail_page_confirm\",\nec:\"fiat_withdraw\",ea:\"click\",el:\"fiat_withdraw::withdraw_confirmation_confirm\"}],g=[{eid:\"binance_screen_fiat_multiple_buy_select_payment_page_add_new_card_popup_view\",ec:\"fb_multiple\",ea:\"popup_view\",el:\"fb_multiple::add_new_card_view\"},{eid:\"binance_screen_fiat_multiple_buy_select_payment_page_change_card_popup_view\",ec:\"fb_multiple\",ea:\"popup_view\",el:\"fb_multiple::change_card_view\"},{eid:\"binance_screen_fiat_deposit_enter_amount_page_add_new_card_popup_view\",ec:\"fiat_deposit\",ea:\"popup_view\",\nel:\"fiat_deposit::add_new_card_view\"},{eid:\"binance_screen_fiat_deposit_enter_amount_page_add_new_card_confirmation_popup_view\",ec:\"fiat_deposit\",ea:\"popup_view\",el:\"fiat_deposit::add_new_card_confirm_view\"},{eid:\"binance_screen_fiat_deposit_enter_amount_page_change_card_popup_view\",ec:\"fiat_deposit\",ea:\"popup_view\",el:\"fiat_deposit::change_card_view\"}];try{e.addEventListener(\"click\",function(a){var b=a.target.id;40\u003Cb.length\u0026\u0026f.forEach(function(c){(new RegExp(c.eid)).test(b)\u0026\u0026dataLayer.push({eventCategory:c.ec,\neventAction:c.ea,eventLabel:c.el,elementId:c.eid,event:\"GA_TM_cme_FIAT\"})})});var h=function(){g.forEach(function(a){var b=a.eid;document.getElementById(b)\u0026\u0026!d[b]\u0026\u0026(dataLayer.push({eventCategory:a.ec,eventAction:a.ea,eventLabel:a.el,elementId:b,event:\"GA_TM_cme_FIAT\"}),d[b]=!0)})},k=new MutationObserver(h);k.observe(e,{childList:!0,subtree:!0})}catch(a){}})();\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": true,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "vtp_usePostscribe": true,
                "tag_id": 170
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\" type=\"text\/gtmscript\"\u003Efunction getParentTag(a,b){return\"BODY\"!==a.parentElement.nodeName?(b.push(a.parentElement.id),getParentTag(a.parentElement,b)):b}\ndocument.querySelector(\"body\").addEventListener(\"click\",function(a){\"walletOverview_top_deposit\"==a.target.id\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"wl_overview\",eventAction:\"click\",eventLabel:\"wallet::overview_deposit\",elementid:\"walletOverview_top_deposit\"});-1!=getParentTag(a.target,[]).indexOf(\"walletOverview_deposit_crypto\")\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"wl_overview\",eventAction:\"click\",eventLabel:\"wl_overview::deposit_Crypto Deposit\",elementid:\"walletOverview_deposit_crypto\"});\n-1!=getParentTag(a.target,[]).indexOf(\"walletOverview_deposit_fiat\")\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"wl_overview\",eventAction:\"click\",eventLabel:\"wl_overview::deposit_fiat\",elementid:\"walletOverview_deposit_fiat\"});-1!=getParentTag(a.target,[]).indexOf(\"walletOverview_deposit_fiat\")\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"wl_overview\",eventAction:\"click\",eventLabel:\"wl_overview::deposit_fiat\",elementid:\"walletOverview_deposit_fiat\"});-1!=getParentTag(a.target,[]).indexOf(\"walletOverview_deposit_card\")\u0026\u0026\ndataLayer.push({event:\"click\",eventCategory:\"wl_overview\",eventAction:\"click\",eventLabel:\"wl_overview::deposit_card\",elementid:\"walletOverview_deposit_card\"});-1!=getParentTag(a.target,[]).indexOf(\"walletOverview_deposit_p2p\")\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"wl_overview\",eventAction:\"click\",eventLabel:\"wl_overview::deposit_p2p\",elementid:\"walletOverview_deposit_p2p\"});\"walletOverview_top_withdrawal\"==a.target.id\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"wl_overview\",eventAction:\"click\",\neventLabel:\"wallet::overview_withdraw\",elementid:\"walletOverview_top_withdrawal\"});\"walletOverview_top_transfer\"==a.target.id\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"wl_overview\",eventAction:\"click\",eventLabel:\"wl_overview::transfer\",elementid:\"walletOverview_top_transfer\"});\"walletOverview_transaction_history_aLink\"==a.target.id\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"wl_overview\",eventAction:\"click\",eventLabel:\"wl_overview::transaction_history\",elementid:\"walletOverview_transaction_history_aLink\"})});\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": false,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "tag_id": 176
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\" type=\"text\/gtmscript\"\u003Efunction getParentTag(a,b){return\"BODY\"!==a.parentElement.nodeName?(b.push(a.parentElement.id),getParentTag(a.parentElement,b)):b}\ndocument.querySelector(\"body\").addEventListener(\"click\",function(a){-1!=getParentTag(a.target,[]).indexOf(\"spotAccount_top_deposit\")\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"wl_faitandspot\",eventAction:\"click\",eventLabel:\"wl_fiat_spot::deposit\",elementid:\"spotAccount_top_deposit\"});-1!=getParentTag(a.target,[]).indexOf(\"spotAccount_top_withdrawal\")\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"wl_faitandspot\",eventAction:\"click\",eventLabel:\"wl_fiat_spot::withdraw\",elementid:\"spotAccount_top_withdrawal\"});\n-1!=getParentTag(a.target,[]).indexOf(\"spotAccount_top_transfer\")\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"wl_faitandspot\",eventAction:\"click\",eventLabel:\"wl_fiat_spot::trasfer\",elementid:\"spotAccount_top_transfer\"});-1!=getParentTag(a.target,[]).indexOf(\"spotAccount_top_wallet_direct\")\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"wl_faitandspot\",eventAction:\"click\",eventLabel:\"wl_fiat_spot::wallet_direct\",elementid:\"spotAccount_top_wallet_direct\"});\"spotAccount_deposit_and_withdraw_history\"==\na.target.id\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"wl_faitandspot\",eventAction:\"click\",eventLabel:\"wl_fiat_spot::deposit_withdraw_history\",elementid:\"spotAccount_deposit_and_withdraw_history\"});\"spotAccount_account_pnl_analysis\"==a.target.id\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"wl_faitandspot\",eventAction:\"click\",eventLabel:\"wl_fiat_spot::pnl\",elementid:\"spotAccount_account_pnl_analysis\"});\"spotAccount_assets_list_search\"==a.target.id\u0026\u0026(document.getElementById(\"spotAccount_assets_list_search\").onchange=\nfunction(){dataLayer.push({event:\"click\",eventCategory:\"wl_faitandspot\",eventAction:\"input\",eventLabel:\"wl_fiat_spot::search_\"+document.getElementById(\"spotAccount_assets_list_search\").value,elementid:\"spotAccount_assets_list_search\"})});\"spotAccount_convert_bnb\"==a.target.id\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"wl_faitandspot\",eventAction:\"click\",eventLabel:\"wl_fiat_spot::convert_to_bnb\",elementid:\"spotAccount_convert_bnb\"})});\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": false,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "tag_id": 177
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\" type=\"text\/gtmscript\"\u003Edocument.querySelector(\"body\").addEventListener(\"click\",function(a){\"spotAccount_top_deposit\"==a.target.id\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"wl_cryptodeposit\",eventAction:\"click\",eventLabel:\"wl_fiat_spot::deposit_crypto_mot_arrived\",elementid:\"crypto_deposit_not_arrived\"})});\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": false,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "tag_id": 178
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\" type=\"text\/gtmscript\"\u003Edocument.querySelector(\"body\").addEventListener(\"click\",function(a){\"crypto_withdraw_address_management\"==a.target.id\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"wl_cryptowithdrawal\",eventAction:\"click\",eventLabel:\"wl_fiat_spot::withdraw_crypto_addr\",elementid:\"crypto_withdraw_address_management\"});\"crypto_withdraw_confitm_btn\"==a.target.id\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"wl_cryptowithdrawal\",eventAction:\"click\",eventLabel:\"wl_fiat_spot::withdraw_crypto_continue\",elementid:\"crypto_withdraw_confitm_btn\"});\n\"crypto_withdraw_complete_btn\"==a.target.id\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"wl_cryptowithdrawal\",eventAction:\"click\",eventLabel:\"wl_fiat_spot::withdraw_crypto_complete\",elementid:\"crypto_withdraw_complete_btn\"})});\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": false,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "tag_id": 179
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\" type=\"text\/gtmscript\"\u003Efunction getParentTag(c,d){return\"BODY\"!==c.parentElement.nodeName?(d.push(c.parentElement.id),getParentTag(c.parentElement,d)):d}var flag_crypto_deposit_not_arrived=!0,flag_deposit_not_arrived=!0,flag_withdraw_not_arrive=!0,flag_reset_crypto=!0,flag_reset_fiat=!0,flag_reset_transfer=!0,flag_type_deposit=!0,flag_type_fiat=!0,flag_coinCryp=!0,flag_coinTran=!0,flag_coinDist=!0,flag_from=!0,flag_to=!0,flag_asset=!0,flag_account=!0,flag_status=!0,tab=document.getElementsByClassName(\"active\")[0].innerHTML;\ndocument.querySelector(\"body\").addEventListener(\"click\",function(c){\"transaction_history_generate_all_statements\"==c.target.id\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"wl_transactionhistory\",eventAction:\"click\",eventLabel:\"wallet::transactionhistory_allstatements\",elementid:\"transaction_history_generate_all_statements\"});-1!=getParentTag(c.target,[]).indexOf(\"tab-crypto\")\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"wl_transactionhistory\",eventAction:\"click\",eventLabel:\"wl_transaction_history::Crypto\",\nelementid:\"tab-crypto\"});-1!=getParentTag(c.target,[]).indexOf(\"tab-fiat\")\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"wl_transactionhistory\",eventAction:\"click\",eventLabel:\"wl_transaction_history::Fiat\",elementid:\"tab-fiat\"});-1!=getParentTag(c.target,[]).indexOf(\"tab-transfer\")\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"wl_transactionhistory\",eventAction:\"click\",eventLabel:\"wl_transaction_history::Transfer\",elementid:\"tab-transfer\"});-1!=getParentTag(c.target,[]).indexOf(\"tab-distribution\")\u0026\u0026\ndataLayer.push({event:\"click\",eventCategory:\"wl_transactionhistory\",eventAction:\"click\",eventLabel:\"wl_transaction_history::Distribution\",elementid:\"tab-distribution\"});-1!=getParentTag(c.target,[]).indexOf(\"tab-bnbconvert\")\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"wl_transactionhistory\",eventAction:\"click\",eventLabel:\"wl_transaction_history::BNB Convert\",elementid:\"tab-bnbconvert\"});try{flag_crypto_deposit_not_arrived\u0026\u0026(document.getElementById(\"deposit_not_arrive_fiat\").addEventListener(\"click\",\nfunction(){dataLayer.push({event:\"click\",eventCategory:\"wl_transactionhistory\",eventAction:\"click\",eventLabel:\"wl_transaction_history::deposit_not_arrived\",elementid:\"deposit_not_arrive\"})}),flag_crypto_deposit_not_arrived=!1)}catch(b){}try{flag_deposit_not_arrived\u0026\u0026(document.getElementById(\"transaction_history_deposit_not_arrive_fiat\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"wl_transactionhistory\",eventAction:\"click\",eventLabel:\"wl_transaction_history::deposit_not_arrived\",\nelementid:\"transaction_history_deposit_not_arrive_fiat\"})}),flag_deposit_not_arrived=!1)}catch(b){}try{flag_withdraw_not_arrive\u0026\u0026(document.getElementById(\"transaction_history_withdraw_not_arrive\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"wl_transactionhistory\",eventAction:\"click\",eventLabel:\"wl_transaction_history::withdrawal_not_arrived\",elementid:\"transaction_history_withdraw_not_arrive\"})}),flag_withdraw_not_arrive=!1)}catch(b){}try{flag_reset_crypto\u0026\u0026(document.getElementById(\"transaction_history_reset_crypto\").addEventListener(\"click\",\nfunction(){dataLayer.push({event:\"click\",eventCategory:\"wl_transactionhistory\",eventAction:\"click\",eventLabel:\"wl_transaction_history::Crypto_reset\",elementid:\"transaction_history_reset_crypto\"})}),flag_reset_crypto=!1)}catch(b){}try{flag_reset_fiat\u0026\u0026(document.getElementById(\"transaction_history_reset_fiat\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"wl_transactionhistory\",eventAction:\"click\",eventLabel:\"wl_transaction_history::Fiat_reset\",elementid:\"transaction_history_reset_fiat\"})}),\nflag_reset_fiat=!1)}catch(b){}try{flag_reset_transfer\u0026\u0026(document.getElementById(\"transaction_history_reset_transfer\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"wl_transactionhistory\",eventAction:\"click\",eventLabel:\"wl_transaction_history::Transfer_reset\",elementid:\"transaction_history_reset_transfer\"})}),flag_reset_transfer=!1)}catch(b){}try{var d=document.getElementById(\"transaction_history_type\"),e=d.getElementsByTagName(\"li\");tab=document.getElementsByClassName(\"active\")[0].innerHTML;\nif(flag_type_deposit){for(var a=0;a\u003Ce.length;a++)e[a].onclick=function(){dataLayer.push({event:\"click\",eventCategory:\"wl_transactionhistory\",eventAction:\"click\",eventLabel:\"wl_transaction_history::\"+tab+\"_type_\"+this.getAttribute(\"id\"),elementid:this.getAttribute(\"id\")})};flag_type_deposit=!1}}catch(b){}try{var r=document.getElementById(\"transaction_history_type_fiat\"),f=r.getElementsByTagName(\"li\");tab=document.getElementsByClassName(\"active\")[0].innerHTML;if(flag_type_fiat){for(a=0;a\u003Cf.length;a++)f[a].onclick=\nfunction(){dataLayer.push({event:\"click\",eventCategory:\"wl_transactionhistory\",eventAction:\"click\",eventLabel:\"wl_transaction_history::\"+tab+\"_type_\"+this.getAttribute(\"id\"),elementid:this.getAttribute(\"id\")})};flag_type_fiat=!1}}catch(b){}try{var t=document.getElementById(\"transaction_history_coin_crypto\"),g=t.getElementsByTagName(\"li\");tab=document.getElementsByClassName(\"active\")[0].innerHTML;if(flag_coinCryp){for(a=0;a\u003Cg.length;a++)g[a].onclick=function(){dataLayer.push({event:\"click\",eventCategory:\"wl_transactionhistory\",\neventAction:\"click\",eventLabel:\"wl_transaction_history::\"+tab+\"_coin_\"+this.getAttribute(\"title\"),elementid:this.getAttribute(\"id\")})};flag_coinCryp=!1}}catch(b){}try{var u=document.getElementById(\"transaction_history_coin_transfer\"),h=u.getElementsByTagName(\"li\");tab=document.getElementsByClassName(\"active\")[0].innerHTML;if(flag_coinTran){for(a=0;a\u003Ch.length;a++)h[a].onclick=function(){dataLayer.push({event:\"click\",eventCategory:\"wl_transactionhistory\",eventAction:\"click\",eventLabel:\"wl_transaction_history::\"+\ntab+\"_coin_\"+this.getAttribute(\"title\"),elementid:this.getAttribute(\"id\")})};flag_coinTran=!1}}catch(b){}try{var v=document.getElementById(\"transaction_history_coin_distribution\"),k=v.getElementsByTagName(\"li\");tab=document.getElementsByClassName(\"active\")[0].innerHTML;if(flag_coinDist){for(a=0;a\u003Ck.length;a++)k[a].onclick=function(){dataLayer.push({event:\"click\",eventCategory:\"wl_transactionhistory\",eventAction:\"click\",eventLabel:\"wl_transaction_history::\"+tab+\"_coin_\"+this.getAttribute(\"title\"),\nelementid:this.getAttribute(\"id\")})};flag_coinDist=!1}}catch(b){}try{var w=document.getElementById(\"transaction_history_from\"),l=w.getElementsByTagName(\"li\");tab=document.getElementsByClassName(\"active\")[0].innerHTML;if(flag_from){for(a=0;a\u003Cl.length;a++)l[a].onclick=function(){dataLayer.push({event:\"click\",eventCategory:\"wl_transactionhistory\",eventAction:\"click\",eventLabel:\"wl_transaction_history::\"+tab+\"_from_\"+this.getAttribute(\"title\"),elementid:this.getAttribute(\"id\")})};flag_from=!1}}catch(b){}try{var x=\ndocument.getElementById(\"transaction_history_to\"),m=x.getElementsByTagName(\"li\");tab=document.getElementsByClassName(\"active\")[0].innerHTML;if(flag_to){for(a=0;a\u003Cm.length;a++)m[a].onclick=function(){dataLayer.push({event:\"click\",eventCategory:\"wl_transactionhistory\",eventAction:\"click\",eventLabel:\"wl_transaction_history::\"+tab+\"_to_\"+this.getAttribute(\"title\"),elementid:this.getAttribute(\"id\")})};flag_to=!1}}catch(b){}try{var y=document.getElementById(\"transaction_history_account\"),n=y.getElementsByTagName(\"li\");\ntab=document.getElementsByClassName(\"active\")[0].innerHTML;if(flag_account){for(a=0;a\u003Cn.length;a++)n[a].onclick=function(){dataLayer.push({event:\"click\",eventCategory:\"wl_transactionhistory\",eventAction:\"click\",eventLabel:\"wl_transaction_history::\"+tab+\"_account_\"+this.getAttribute(\"title\"),elementid:this.getAttribute(\"id\")})};flag_account=!1}}catch(b){}try{var z=document.getElementById(\"transaction_history_asset\"),p=z.getElementsByTagName(\"li\");tab=document.getElementsByClassName(\"active\")[0].innerHTML;\nif(flag_asset){for(a=0;a\u003Cp.length;a++)p[a].onclick=function(){dataLayer.push({event:\"click\",eventCategory:\"wl_transactionhistory\",eventAction:\"click\",eventLabel:\"wl_transaction_history::\"+tab+\"_asset_\"+this.getAttribute(\"title\"),elementid:this.getAttribute(\"id\")})};flag_asset=!1}}catch(b){}try{var A=document.getElementById(\"transaction_history_status\"),q=A.getElementsByTagName(\"li\");tab=document.getElementsByClassName(\"active\")[0].innerHTML;if(flag_status){for(a=0;a\u003Cq.length;a++)q[a].onclick=function(){dataLayer.push({event:\"click\",\neventCategory:\"wl_transactionhistory\",eventAction:\"click\",eventLabel:\"wl_transaction_history::\"+tab+\"_status_\"+this.getAttribute(\"title\"),elementid:this.getAttribute(\"id\")})};flag_status=!1}}catch(b){}});\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": false,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "tag_id": 188
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\" type=\"text\/gtmscript\"\u003Efor(var j=0;;j++)if(document.getElementById(\"blogList2-carousel-\"+j))document.getElementById(\"blogList2-carousel-\"+j).addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"bl_carousel\",eventAction:\"click\",eventLabel:\"bl_carousel::\"+this.firstChild.lastChild.firstChild.getAttribute(\"title\")+\"_\"+this.parentNode.parentNode.getAttribute(\"data-index\"),elementid:this.id})});else break;\nfor(j=0;;j++)if(document.getElementById(\"blogList2-category-\"+j))document.getElementById(\"blogList2-category-\"+j).addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"bl_category\",eventAction:\"click\",eventLabel:\"bl_categ::view_\"+this.childNodes[0].innerHTML,elementid:this.id})});else break;function getParentNode(a,b){if(\"BODY\"==a.nodeName)return a;for(a=a.parentNode;a.nodeName!=b\u0026\u0026\"BODY\"!=a.nodeName;)a=a.parentNode;if(a.nodeName==b)return a}\ndocument.querySelector(\"body\").addEventListener(\"click\",function(a){if((a=getParentNode(a.target,\"A\"))\u0026\u0026a.id.match(\/^blogList2-content-.*\/)){var b=document.getElementsByClassName(\"active\")[0].innerText;dataLayer.push({event:\"click\",eventCategory:\"bl_content\",eventAction:\"click\",eventLabel:\"bl_cont:\"+b+\"_\"+a.getElementsByTagName(\"h2\")[0].getAttribute(\"title\")+\"_\"+a.id.substr(a.id.lastIndexOf(\"-\")+1,a.id.length),elementid:a.id})}});\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": false,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "tag_id": 196
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\" type=\"text\/gtmscript\"\u003Edocument.getElementById(\"settings-orderConfirmation-limitOrder\").addEventListener(\"click\",function(){var a=0==this.getAttribute(\"aria-checked\")?\"on\":\"off\";dataLayer.push({event:\"click\",eventCategory:\"ac_preferences\",eventAction:\"click\",eventLabel:\"ac_pref::limit_\"+a,elementid:\"settings-orderConfirmation-limitOrder\"})});\ndocument.getElementById(\"settings-orderConfirmation-marketOrder\").addEventListener(\"click\",function(){var a=0==this.getAttribute(\"aria-checked\")?\"on\":\"off\";dataLayer.push({event:\"click\",eventCategory:\"ac_preferences\",eventAction:\"click\",eventLabel:\"ac_pref::market_\"+a,elementid:\"settings-orderConfirmation-marketOrder\"})});\ndocument.getElementById(\"settings-orderConfirmation-stopLossOrder\").addEventListener(\"click\",function(){var a=0==this.getAttribute(\"aria-checked\")?\"on\":\"off\";dataLayer.push({event:\"click\",eventCategory:\"ac_preferences\",eventAction:\"click\",eventLabel:\"ac_pref::stop_limit_\"+a,elementid:\"settings-orderConfirmation-stopLossOrder\"})});\nfor(var lng=document.getElementById(\"settings-notification-lng\").getElementsByTagName(\"li\"),i=0;i\u003Clng.length;i++)lng[i].onclick=function(){dataLayer.push({event:\"click\",eventCategory:\"ac_preferences\",eventAction:\"click\",eventLabel:\"ac_pref::notif_lang_\"+this.getAttribute(\"title\"),elementid:this.getAttribute(\"id\")})};\ndocument.getElementById(\"settings-email-push\").addEventListener(\"click\",function(){var a=0==this.getAttribute(\"aria-checked\")?\"on\":\"off\";dataLayer.push({event:\"click\",eventCategory:\"ac_preferences\",eventAction:\"click\",eventLabel:\"ac_pref::promotion_\"+a,elementid:\"settings-email-push\"})});\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": false,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "tag_id": 212
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\" type=\"text\/gtmscript\"\u003Edocument.getElementById(\"security2fa_yubikey_btn_setup\")\u0026\u0026document.getElementById(\"security2fa_yubikey_btn_setup\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"ac_2fa\",eventAction:\"click\",eventLabel:\"ac_2fa::key_setup\",elementid:\"security2fa_yubikey_btn_setup\"})});\ndocument.getElementById(\"security2fa_googleauth_btn_enable\")\u0026\u0026document.getElementById(\"security2fa_googleauth_btn_enable\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"ac_2fa\",eventAction:\"click \",eventLabel:\"ac_2fa::google_enable\",elementid:\"security2fa_googleauth_btn_enable\"})});\ndocument.getElementById(\"security2fa_googleauth_btn_remove\")\u0026\u0026document.getElementById(\"security2fa_googleauth_btn_remove\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"ac_2fa\",eventAction:\"click \",eventLabel:\"ac_2fa::google_disable\",elementid:\"security2fa_googleauth_btn_remove\"})});\ndocument.getElementById(\"security2fa_sms_btn_enable\")\u0026\u0026document.getElementById(\"security2fa_sms_btn_enable\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"ac_2fa\",eventAction:\"click \",eventLabel:\"ac_2fa::sms_on\",elementid:\"security2fa_sms_btn_enable\"})});\ndocument.getElementById(\"security2fa_sms_btn_change\")\u0026\u0026document.getElementById(\"security2fa_sms_btn_change\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"ac_2fa\",eventAction:\"click \",eventLabel:\"ac_2fa::sms_change\",elementid:\"security2fa_sms_btn_change\"})});\ndocument.getElementById(\"security2fa_sms_btn_remove\")\u0026\u0026document.getElementById(\"security2fa_sms_btn_remove\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"ac_2fa\",eventAction:\"click \",eventLabel:\"ac_2fa::sms_remove\",elementid:\"security2fa_sms_btn_remove\"})});\ndocument.getElementById(\"security2fa_email_btn_enable\")\u0026\u0026document.getElementById(\"security2fa_email_btn_enable\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"ac_2fa\",eventAction:\"click \",eventLabel:\"ac_2fa::email_on\",elementid:\"security2fa_email_btn_enable\"})});\ndocument.getElementById(\"security2fa_email_btn_change\")\u0026\u0026document.getElementById(\"security2fa_email_btn_change\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"ac_2fa\",eventAction:\"click \",eventLabel:\"ac_2fa::email_change\",elementid:\"security2fa_email_btn_change\"})});\ndocument.getElementById(\"security2fa_email_btn_remove\")\u0026\u0026document.getElementById(\"security2fa_email_btn_remove\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"ac_2fa\",eventAction:\"click \",eventLabel:\"ac_2fa::email_remove\",elementid:\"security2fa_email_btn_remove\"})});\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": false,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "tag_id": 215
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\" type=\"text\/gtmscript\"\u003Edocument.getElementById(\"inmail_tab_all\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"nt_view_all\",eventAction:\"click\",eventLabel:\"notification::view_all\",elementid:\"inmail_tab_all\"})});document.getElementById(\"inmail_btn_mark_all_read\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"nt_read_all\",eventAction:\"click\",eventLabel:\"notification::read_all\",elementid:\"inmail_btn_mark_all_read\"})});\ndocument.getElementById(\"inmail_btn_clear_all\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"nt_read_all\",eventAction:\"click\",eventLabel:\"notification::clear_all\",elementid:\"inmail_btn_clear_all\"})});document.getElementById(\"inmail_btn_settings\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"nt_setting\",eventAction:\"click\",eventLabel:\"notification::settings\",elementid:\"inmail_btn_settings\"})});\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": false,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "tag_id": 219
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\" type=\"text\/gtmscript\"\u003Edocument.getElementById(\"homepage-download-appStore\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"dl_mobile\",eventAction:\"click\",eventLabel:\"download::mobile_App Store\",elementid:\"homepage-download-appStore\"})});document.getElementById(\"homepage-download-googlePlay\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"dl_mobile\",eventAction:\"click\",eventLabel:\"download::mobile_Google Play\",elementid:\"homepage-download-googlePlay\"})});\ndocument.getElementById(\"homepage-download-macos\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"dl_desktop\",eventAction:\"click\",eventLabel:\"download::desktop_macOs\",elementid:\"homepage-download-macos\"})});document.getElementById(\"homepage-download-windows\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"dl_desktop\",eventAction:\"click\",eventLabel:\"download::desktop_Windows\",elementid:\"homepage-download-windows\"})});\ndocument.getElementById(\"homepage-download-Linux-deb\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"dl_desktop\",eventAction:\"click\",eventLabel:\"download::desktop_Linux deb\",elementid:\"homepage-download-Linux-deb\"})});document.getElementById(\"homepage-download-Linux-rpm\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"dl_desktop\",eventAction:\"click\",eventLabel:\"download::desktop_Linux rpm\",elementid:\"homepage-download-Linux-rpm\"})});\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": false,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "tag_id": 221
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\" type=\"text\/gtmscript\"\u003Edocument.getElementById(\"Community-a-BinanceExchange\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"cm_officials\",eventAction:\"click\",eventLabel:\"cm_officials::exchange_English\",elementid:\"Community-a-BinanceExchange\"})});document.getElementById(\"Community-a-BinanceExchangeChinese\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"cm_officials\",eventAction:\"click\",eventLabel:\"cm_officials::exchange_Chinese\",elementid:\"Community-a-BinanceExchangeChinese\"})});\ndocument.getElementById(\"Community-a-BinanceExchangeAnnouncements\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"cm_officials\",eventAction:\"click\",eventLabel:\"cm_officials::exchange_Announcements\",elementid:\"Community-a-BinanceExchangeAnnouncements\"})});\ndocument.getElementById(\"Community-a-BinanceExchangeNFT\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"cm_officials\",eventAction:\"click\",eventLabel:\"cm_officials::exchange_NFT\",elementid:\"Community-a-BinanceExchangeNFT\"})});document.getElementById(\"Community-a-AcademyAnnouncements\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"cm_officials\",eventAction:\"click\",eventLabel:\"cm_officials::academy_Announcements\",elementid:\"Community-a-AcademyAnnouncements\"})});\ndocument.getElementById(\"Community-a-DiscussionTow\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"cm_officials\",eventAction:\"click\",eventLabel:\"cm_officials::academy_Discussion\",elementid:\"Community-a-DiscussionTow\"})});document.getElementById(\"Community-a-InfoEn\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"cm_officials\",eventAction:\"click\",eventLabel:\"cm_officials::info_English\",elementid:\"Community-a-InfoEn\"})});\ndocument.getElementById(\"Community-a-InfoResearch\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"cm_officials\",eventAction:\"click\",eventLabel:\"cm_officials::info_Research Announcements\",elementid:\"Community-a-InfoResearch\"})});for(var multilingual=[],i=1;48\u003E=i;i++)multilingual.push(\"Community-a-Exchange_\"+i);\nfor(item in multilingual)document.getElementById(multilingual[item]).addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"cm_multilingual\",eventAction:\"click\",eventLabel:\"cm_multilingual::exchange_\"+this.previousSibling.innerHTML,elementid:this.id})});\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": false,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "tag_id": 224
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\"\u003Efor(var related=[],i=0;;i++)if(document.getElementById(\"supportDetail-relatedLink-\"+i))related.push(\"supportDetail-relatedLink-\"+i);else break;for(item in related)document.getElementById(related[item]).addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"sp_faq\",eventAction:\"click\",eventLabel:\"sp_faq::article_\"+document.title+\"_related_\"+this.innerHTML,elementid:this.id})});\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": true,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "vtp_usePostscribe": true,
                "tag_id": 234
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\"\u003Edocument.getElementById(\"support-search-input\").addEventListener(\"change\",function(){dataLayer.push({event:\"input\",eventCategory:\"sp_search\",eventAction:\"input\",eventLabel:\"sp_faq::search_\"+this.value,elementid:\"support-search-input\"})});document.getElementById(\"support-search-button\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"sp_search\",eventAction:\"click\",eventLabel:\"sp_faq::search_result\",elementid:\"support-search-button\"})});\ndocument.getElementById(\"support-selfService-resetPassword\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"sp_selfservice\",eventAction:\"click\",eventLabel:\"sp_self_service::view_Reset Password\",elementid:\"support-selfService-resetPassword\"})});\ndocument.getElementById(\"support-selfService-unlockAccount\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"sp_selfservice\",eventAction:\"click\",eventLabel:\"sp_self_service::view_Unlock Account\",elementid:\"support-selfService-unlockAccount\"})});\ndocument.getElementById(\"support-selfService-resetPhoneSecurityVerification\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"sp_selfservice\",eventAction:\"click\",eventLabel:\"sp_self_service::view_Reset Phone Security Verification\",elementid:\"support-selfService-resetPhoneSecurityVerification\"})});\ndocument.getElementById(\"support-selfService-changeEmailAddress\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"sp_selfservice\",eventAction:\"click\",eventLabel:\"sp_self_service::view_Change Email Address\",elementid:\"support-selfService-changeEmailAddress\"})});\ndocument.getElementById(\"support-selfService-resetGoogleAuthenticator\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"sp_selfservice\",eventAction:\"click\",eventLabel:\"sp_self_service::view_Reset Google Authenticator\",elementid:\"support-selfService-resetGoogleAuthenticator\"})});\ndocument.getElementById(\"support-selfService-depositNotCreditAssetRecovery\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"sp_selfservice\",eventAction:\"click\",eventLabel:\"sp_self_service::view_Deposit Not Credit Asset Recovery\",elementid:\"support-selfService-depositNotCreditAssetRecovery\"})});\ndocument.getElementById(\"support-selfService-depositTagMemoRecovery\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"sp_selfservice\",eventAction:\"click\",eventLabel:\"sp_self_service::view_Deposit Missing or Wrong Tag\/memo Asset Recovery\",elementid:\"support-selfService-depositTagMemoRecovery\"})});\nfor(var j=0;5\u003Ej;j++)document.getElementById(\"support-latest-\"+j).addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"sp_latest_articles\",eventAction:\"click\",eventLabel:\"sp_la::article_\"+this.firstChild.innerHTML,elementid:this.id})}),document.getElementById(\"support-top-\"+j).addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"sp_top_articles\",eventAction:\"click\",eventLabel:\"sp_ta::article_\"+this.firstChild.innerHTML,elementid:this.id})});\nfor(var faq=[],i=0;;i++)if(document.getElementById(\"support-faq-\"+i))faq.push(\"support-faq-\"+i);else break;for(item in faq)document.getElementById(faq[item]).addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"sp_faq\",eventAction:\"click\",eventLabel:\"sp_faq::module\"+this.lastChild.innerHTML,elementid:this.id})});var Announce=[];for(i=0;;i++)if(document.getElementById(\"support-announcement-\"+i))faq.push(\"support-announcement-\"+i);else break;\nfor(item in Announce)document.getElementById(Announce[item]).addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"sp_announcement\",eventAction:\"click\",eventLabel:\"sp_announcement::module\"+this.lastChild.innerHTML,elementid:this.id})});\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": true,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "vtp_usePostscribe": true,
                "tag_id": 235
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\"\u003Edocument.querySelector(\"body\").addEventListener(\"click\",function(a){a.target.id.match(\/^supportSearch-list-.*\/)\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"sp_search\",eventAction:\"click\",eventLabel:\"sp_faq::search_result_view_\"+a.target.innerHTML.replace('\\x3cspan style\\x3d\"color:#F0B90B\"\\x3e',\"\").replace(\"\\x3c\/span\\x3e\",\"\"),elementid:a.target.id})});\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": true,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "vtp_usePostscribe": true,
                "tag_id": 245
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\"\u003Efor(var faq=[],article=[],i=0;;i++)if(document.getElementById(\"module-\"+i))faq.push(\"module-\"+i);else break;for(item in faq)document.getElementById(faq[item]).addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"sp_faq\",eventAction:\"click\",eventLabel:\"sp_faq::module\"+this.innerHTML,elementid:this.id})});\ndocument.querySelector(\"body\").addEventListener(\"click\",function(a){a.target.id.match(\/^link-.*\/)\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"sp_faq\",eventAction:\"click\",eventLabel:\"sp_faq::article_\"+a.target.innerHTML,elementid:a.target})});\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": true,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "vtp_usePostscribe": true,
                "tag_id": 247
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\"\u003Edocument.querySelector(\"body\").addEventListener(\"click\",function(a){a.target.id.match(\/^module-.*\/)\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"sp_announce\",eventAction:\"click\",eventLabel:\"sp_announce::module_\"+a.target.firstChild.innerHTML,elementid:a.target.id});a.target.id.match(\/^link-.*\/)\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"sp_announce\",eventAction:\"click\",eventLabel:\"sp_announce::article_\"+a.target.innerHTML,elementid:a.target})});\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": true,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "vtp_usePostscribe": true,
                "tag_id": 249
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\"\u003E(function(){var b=", ["escape", ["macro", 51], 8, 16], ",a=", ["escape", ["macro", 67], 8, 16], ";b\u0026\u0026b.click?(dataLayer.push({ecommerce:null}),dataLayer.push({ecommerce:b,event:\"GA_TM_cme_productClick\"})):a\u0026\u0026(dataLayer.push({ecommerce:null}),dataLayer.push({ecommerce:a.ecommerce,eventCategory:a.eventCategory,eventAction:a.eventAction,eventLabel:a.eventLabel,elementid:a.elementid,event:\"GA_TM_cme_productClick\"}))})();\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": true,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "vtp_usePostscribe": true,
                "tag_id": 253
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\"\u003Efor(var related=[],i=0;;i++)if(document.getElementById(\"supportDetail-relatedLink-\"+i))related.push(\"supportDetail-relatedLink-\"+i);else break;for(item in related)document.getElementById(related[item]).addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"sp_announce\",eventAction:\"click\",eventLabel:\"sp_announce::article_\"+document.title+\"_related_\"+this.innerHTML,elementid:this.id})});\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": true,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "vtp_usePostscribe": true,
                "tag_id": 259
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\"\u003Efunction getParentTag(a,b){return\"BODY\"!==a.parentElement.nodeName?(b.push(a.parentElement.id),getParentTag(a.parentElement,b)):b}if(document.querySelector(\"#C2Cfiatfilter_searhbox_fiat\"))for(var coin=document.getElementById(\"C2Cfiatfilter_searhbox_fiat\").getElementsByTagName(\"li\"),i=0;i\u003Ccoin.length;i++)coin[i].onclick=function(){dataLayer.push({event:\"click\",eventCategory:\"p2p_orders\",eventAction:\"click\",eventLabel:\"p2p_orders::filter_coin_\"+this.id,elementid:this.id})};\nif(document.querySelector(\"#C2Cpaymentfilter_searchbox_payment\")){var type=document.getElementById(\"C2Cpaymentfilter_searchbox_payment\").getElementsByTagName(\"li\");for(i=0;i\u003Ctype.length;i++)type[i].onclick=function(){dataLayer.push({event:\"click\",eventCategory:\"p2p_orders\",eventAction:\"click\",eventLabel:\"p2p_orders::filter_type_\"+this.id,elementid:this.id})}}\ndocument.querySelector(\"body\").addEventListener(\"click\",function(a){-1!=getParentTag(a.target,[]).indexOf(\"C2CofferList_btn_VIDEO\")\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"p2p_videotutorial\",eventAction:\"click\",eventLabel:\"p2p::video_tutorial\",elementid:\"C2CofferList_btn_VIDEO\"});-1!=getParentTag(a.target,[]).indexOf(\"C2CofferList_btn_order\")\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"p2p_orders\",eventAction:\"click\",eventLabel:\"p2p_orders::view\",elementid:\"C2CofferList_btn_order\"});-1!=getParentTag(a.target,\n[]).indexOf(\"C2CofferList_dropdown_payments\")\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"p2p_paymentsettings\",eventAction:\"click\",eventLabel:\"p2p_more::payment_settings\",elementid:\"C2CofferList_dropdown_payments\"});-1!=getParentTag(a.target,[]).indexOf(\"C2CofferList_dropdown_postads\")\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"p2p_ads\",eventAction:\"click\",eventLabel:\"p2p_more::post_new_ads\",elementid:\"C2CofferList_dropdown_postads\"});-1!=getParentTag(a.target,[]).indexOf(\"C2CofferList_dropdown_becomeMerchant\")\u0026\u0026\ndataLayer.push({event:\"click\",eventCategory:\"p2p_ads\",eventAction:\"click\",eventLabel:\"p2p_more::become_merchant\",elementid:\"C2CofferList_dropdown_becomeMerchant\"});-1!=getParentTag(a.target,[]).indexOf(\"C2CofferList_dropdown_FAQ\")\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"p2p_faqs\",eventAction:\"click\",eventLabel:\"p2p_more::faqs\",elementid:\"C2CofferList_dropdown_FAQ\"});\"C2C_p2pMyAdsList_filter_btn_reset\"==a.target.id\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"p2p_ads\",eventAction:\"click\",eventLabel:\"p2p_my_ads::reset\",\nelementid:\"C2C_p2pMyAdsList_filter_btn_reset\"})});\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": true,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "vtp_usePostscribe": true,
                "tag_id": 264
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\"\u003Evar flag_coin=!0,flag_type=!0,flag_status=!0;\ndocument.querySelector(\"body\").addEventListener(\"click\",function(){if(flag_coin\u0026\u0026document.getElementById(\"c2c-order-list-coin-filter\")){var a=document.getElementById(\"c2c-order-list-coin-filter\").parentNode,b=a.getElementsByTagName(\"li\");for(a=0;a\u003Cb.length;a++)b[a].onclick=function(){dataLayer.push({event:\"click\",eventCategory:\"po_allorders\",eventAction:\"click\",eventLabel:\"od_p2p::coin_\"+this.id,elementid:this.id})};flag_coin=!1}if(flag_type\u0026\u0026document.getElementById(\"c2c-order-list-type-filter\")){a=document.getElementById(\"c2c-order-list-type-filter\").parentNode;\nb=a.getElementsByTagName(\"li\");for(a=0;a\u003Cb.length;a++)b[a].onclick=function(){dataLayer.push({event:\"click\",eventCategory:\"po_allorders\",eventAction:\"click\",eventLabel:\"od_p2p::order_type_\"+this.id,elementid:this.id})};flag_type=!1}if(flag_status\u0026\u0026document.getElementById(\"c2c-order-list-status-filter\")){a=document.getElementById(\"c2c-order-list-status-filter\").parentNode;b=a.getElementsByTagName(\"li\");for(a=0;a\u003Cb.length;a++)b[a].onclick=function(){dataLayer.push({event:\"click\",eventCategory:\"po_allorders\",\neventAction:\"click\",eventLabel:\"od_p2p::status_\"+this.innerHTML,elementid:this.id})};flag_status=!1}});\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": true,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "vtp_usePostscribe": true,
                "tag_id": 268
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\"\u003Etry{var fu_switch=document.querySelector(\"[data-testid\\x3dfo_openorder_pageSwitch]\");fu_switch.firstChild.onclick=function(){dataLayer.push({event:\"click\",eventCategory:\"fo_openorder\",eventAction:\"click\",eventLabel:\"od_futures::openorder_\"+this.innerHTML,elementid:\"fo_openorder_pageSwitch\"})};fu_switch.lastChild.onclick=function(){dataLayer.push({event:\"click\",eventCategory:\"fo_openorder\",eventAction:\"click\",eventLabel:\"od_futures::openorder_\"+this.innerHTML,elementid:\"fo_openorder_pageSwitch\"})};\nvar flag_type=!0,flag_sym=!0,flag_side=!0,flag_reset=!0,flag_cancel=!0;document.querySelector(\"body\").addEventListener(\"click\",function(){if(flag_type\u0026\u0026document.querySelector(\"[data-testid\\x3dfo_openorder_orderType]\")){var a=document.querySelector(\"[data-testid\\x3dfo_openorder_orderType]\"),b=a.querySelectorAll(\"li\");for(a=0;a\u003Cb.length;a++)b[a].onclick=function(){dataLayer.push({event:\"click\",eventCategory:\"fo_openorder\",eventAction:\"click\",eventLabel:\"od_futures::openorder_filter_\"+this.id,elementid:this.id})};\nflag_type=!1}if(flag_sym\u0026\u0026document.querySelector(\"[data-testid\\x3dfo_openorder_symbol]\")){a=document.querySelector(\"[data-testid\\x3dfo_openorder_symbol]\");b=a.querySelectorAll(\"li\");for(a=0;a\u003Cb.length;a++)b[a].onclick=function(){dataLayer.push({event:\"click\",eventCategory:\"fo_openorder\",eventAction:\"click\",eventLabel:\"od_futures::openorder_symbol_\"+this.id,elementid:this.id})};flag_sym=!1}if(flag_side\u0026\u0026document.querySelector(\"[data-testid\\x3dfo_openorder_side]\")){a=document.querySelector(\"[data-testid\\x3dfo_openorder_side]\");\nb=a.querySelectorAll(\"li\");for(a=0;a\u003Cb.length;a++)b[a].onclick=function(){dataLayer.push({event:\"click\",eventCategory:\"fo_openorder\",eventAction:\"click\",eventLabel:\"od_futures::openorder_side_\"+this.id,elementid:this.id})};flag_side=!1}flag_reset\u0026\u0026document.querySelector(\"[data-testid\\x3dfo_openorder_reset]\")\u0026\u0026(document.querySelector(\"[data-testid\\x3dfo_openorder_reset]\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"fo_openorder\",eventAction:\"click\",eventLabel:\"od_futures::openorder_reset\",\nelementid:\"fo_openorder_reset\"})}),flag_reset=!1);flag_cancel\u0026\u0026document.querySelector(\"[data-testid\\x3dfo_openorder_cancelAll]\")\u0026\u0026(document.querySelector(\"[data-testid\\x3dfo_openorder_cancelAll]\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"fo_openorder\",eventAction:\"click\",eventLabel:\"od_futures::openorder_cancel_all_orders\",elementid:\"fo_openorder_cancelAll\"})}),flag_cancel=!1)})}catch(a){};\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": true,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "vtp_usePostscribe": true,
                "tag_id": 270
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\" type=\"text\/gtmscript\"\u003Etry{var fu_switch=document.querySelector(\"[data-testid\\x3dfo_tradehistory_pageSwitch]\");fu_switch.firstChild.onclick=function(){dataLayer.push({event:\"click\",eventCategory:\"fo_tradehistory\",eventAction:\"click\",eventLabel:\"od_futures::tradehistory_\"+this.innerHTML,elementid:\"fo_tradehistory_pageSwitch\"})};fu_switch.lastChild.onclick=function(){dataLayer.push({event:\"click\",eventCategory:\"fo_tradehistory\",eventAction:\"click\",eventLabel:\"od_futures::tradehistory_\"+this.innerHTML,elementid:\"fo_tradehistory_pageSwitch\"})};\ndocument.querySelector(\"[data-testid\\x3dfo_tradehistory_reset]\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"fo_tradehistory\",eventAction:\"click\",eventLabel:\"od_futures::tradehistory_reset\",elementid:\"fo_tradehistory_reset\"})})}catch(a){};\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": false,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "tag_id": 272
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\"\u003Etry{var fu_switch=document.querySelector(\"[data-testid\\x3dfo_orderhistory_pageSwitch]\");fu_switch.firstChild.onclick=function(){dataLayer.push({event:\"click\",eventCategory:\"fo_orderhistory\",eventAction:\"click\",eventLabel:\"od_futures::orderhistory_\"+this.innerHTML,elementid:\"fo_orderhistory_pageSwitch\"})};fu_switch.lastChild.onclick=function(){dataLayer.push({event:\"click\",eventCategory:\"fo_orderhistory\",eventAction:\"click\",eventLabel:\"od_futures::orderhistory_\"+this.innerHTML,elementid:\"fo_orderhistory_pageSwitch\"})};\ndocument.querySelector(\"[data-testid\\x3dfo_orderhistory_reset]\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"fo_orderhistory\",eventAction:\"click\",eventLabel:\"od_futures::orderhistory_reset\",elementid:\"fo_orderhistory_reset\"})})}catch(a){};\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": true,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "vtp_usePostscribe": true,
                "tag_id": 273
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\" type=\"text\/gtmscript\"\u003Etry{var fu_switch=document.querySelector(\"[data-testid\\x3dfo_transactionhistory_pageSwitch]\");fu_switch.firstChild.onclick=function(){dataLayer.push({event:\"click\",eventCategory:\"fo_transactionhistory\",eventAction:\"click\",eventLabel:\"od_futures::transactionhistory_\"+this.innerHTML,elementid:\"fo_transactionhistory_pageSwitch\"})};fu_switch.lastChild.onclick=function(){dataLayer.push({event:\"click\",eventCategory:\"fo_transactionhistory\",eventAction:\"click\",eventLabel:\"od_futures::transactionhistory_\"+\nthis.innerHTML,elementid:\"fo_transactionhistory_pageSwitch\"})};document.querySelector(\"[data-testid\\x3dfo_transactionhistory_reset]\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"fo_transactionhistory\",eventAction:\"click\",eventLabel:\"od_futures::transactionhistory_reset\",elementid:\"fo_transactionhistory_reset\"})})}catch(a){};\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": false,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "tag_id": 275
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\" type=\"text\/gtmscript\"\u003Etry{document.querySelector(\"[data-testid\\x3dfo_borrowhistory_reset]\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"fo_borrowhistory\",eventAction:\"click\",eventLabel:\"od_futures::borrowhistory_reset\",elementid:\"fo_borrowhistory_reset\"})}),document.querySelector(\"[data-testid\\x3dfo_borrowhistory_search]\").addEventListener(\"click\",function(){var a=document.getElementsByClassName(\"rc-picker-input\")[0].firstChild.value+\"-\"+document.getElementsByClassName(\"rc-picker-input\")[1].firstChild.value;\ndataLayer.push({event:\"click\",eventCategory:\"fo_borrowhistory\",eventAction:\"click\",eventLabel:\"od_futures::borrowhistory_search_\"+a,elementid:\"fo_borrowhistory_search\"})})}catch(a){};\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": false,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "tag_id": 278
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\" type=\"text\/gtmscript\"\u003Etry{document.querySelector(\"[data-testid\\x3dfo_repaymenthistory_reset]\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"fo_repaymenthistory\",eventAction:\"click\",eventLabel:\"od_futures::repaymenthistory_reset\",elementid:\"fo_repaymenthistory_reset\"})}),document.querySelector(\"[data-testid\\x3dfo_repaymenthistory_search]\").addEventListener(\"click\",function(){var a=document.getElementsByClassName(\"rc-picker-input\")[0].firstChild.value+\"-\"+document.getElementsByClassName(\"rc-picker-input\")[1].firstChild.value;\ndataLayer.push({event:\"click\",eventCategory:\"fo_repaymenthistory\",eventAction:\"click\",eventLabel:\"od_futures::repaymenthistory_search_\"+a,elementid:\"fo_repaymenthistory_search\"})})}catch(a){};\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": false,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "tag_id": 280
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\" type=\"text\/gtmscript\"\u003Etry{document.querySelector(\"[data-testid\\x3dfo_adjusthistory_reset]\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"fo_adjusthistory\",eventAction:\"click\",eventLabel:\"od_futures::adjusthistory_reset\",elementid:\"fo_adjusthistory_reset\"})})}catch(a){};\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": false,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "tag_id": 282
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\" type=\"text\/gtmscript\"\u003Etry{document.querySelector(\"[data-testid\\x3dfo_liquidationhistory_reset]\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"fo_liquidationhistory\",eventAction:\"click\",eventLabel:\"od_futures::liquidationhistory_reset\",elementid:\"fo_liquidationhistory_reset\"})})}catch(a){};\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": false,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "tag_id": 284
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\" type=\"text\/gtmscript\"\u003Etry{document.querySelector(\"[data-testid\\x3dfo_interesthistory_reset]\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"fo_interesthistory\",eventAction:\"click\",eventLabel:\"od_futures::interesthistory_reset\",elementid:\"fo_interesthistory_reset\"})}),document.querySelector(\"[data-testid\\x3dfo_interesthistory_search]\").addEventListener(\"click\",function(){var a=document.getElementsByClassName(\"rc-picker-input\")[0].firstChild.value+\"-\"+document.getElementsByClassName(\"rc-picker-input\")[1].firstChild.value;\ndataLayer.push({event:\"click\",eventCategory:\"fo_interesthistory\",eventAction:\"click\",eventLabel:\"od_futures::interesthistory_search_\"+a,elementid:\"fo_interesthistory_search\"})})}catch(a){};\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": false,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "tag_id": 285
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\" type=\"text\/gtmscript\"\u003Edocument.querySelector(\".item\").onclick=function(){dataLayer.push({event:\"click\",eventCategory:\"bch_historytab\",eventAction:\"click\",eventLabel:\"od_bc::history_\"+this.innerHTML,elementid:\"\"})};\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": false,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "tag_id": 288
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\" type=\"text\/gtmscript\"\u003Edocument.querySelector(\"id^\\x3dtab-\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"eh_earn\",eventAction:\"click\",eventLabel:\"od_eh::view_\"+this.firstChild.innerHTML,elementid:this.id})});var tab=\"undefined\"!=document.querySelector(\".active\")?document.querySelector(\".active\").innerHTML:\"\";document.querySelector(\"mainuc-reset\").onclick=function(){dataLayer.push({event:\"click\",eventCategory:\"eh_earn\",eventAction:\"click\",eventLabel:\"od_eh::\"+tab+\"_reset\",elementid:\"mainuc-reset\"})};\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": false,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "tag_id": 290
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\"\u003Edocument.querySelector(\"[data-testid\\x3dopenOrderCancelAll]\")\u0026\u0026document.querySelector(\"[data-testid\\x3dopenOrderCancelAll]\").addEventListener(\"click\",function(){var a=location.href,b=a.lastIndexOf(\"\\x3d\");a=a.substring(b+1,a.length);dataLayer.push({event:\"click\",eventCategory:\"td_spotnmargin\",eventAction:\"click\",eventLabel:\"td_spot_margin::cancel_all_open_orders\",layout:a,elementid:\"openOrderCancelAll\"})});\ndocument.querySelector(\"[data-testid\\x3dHideLowBalanceAsset]\")\u0026\u0026document.querySelector(\"[data-testid\\x3dHideLowBalanceAsset]\").addEventListener(\"click\",function(){var a=location.href,b=a.lastIndexOf(\"\\x3d\");a=a.substring(b+1,a.length);dataLayer.push({event:\"click\",eventCategory:\"td_spotnmargin\",eventAction:\"tick\",eventLabel:\"td_spot_margin::hide_low_balance_assets\",layout:a,elementid:\"HideLowBalanceAsset\"})});\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": true,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "vtp_usePostscribe": true,
                "tag_id": 296
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\"\u003Efunction ga_trackFn_fnLoan(c,a){dataLayer.push({eventCategory:\"fn_loan\",eventAction:\"click\",eventLabel:c,elementid:a,event:\"GA_TM_cme_MARGIN\"})}\n(function(){var c=document.getElementsByTagName(\"body\")[0];c.addEventListener(\"click\",function(a){var b=a.target.id;a=a.target.parentNode.id;\"tab-BORROW\"==a?ga_trackFn_fnLoan(\"fn_cloans::view_Borrow\",\"tab-BORROW\"):\"tab-ONGOING_ORDERS\"==a?ga_trackFn_fnLoan(\"fn_cloans::view_OngingOrders\",\"tab-ONGOING_ORDERS\"):\"tab-ASSET_OVERVIEW\"==a\u0026\u0026ga_trackFn_fnLoan(\"fn_cloans::view_AssetOverview\",\"tab-ASSET_OVERVIEW\");\"start-borrow-now\"==b?ga_trackFn_fnLoan(\"fn_cloans::start_borrow_now\",\"start-borrow-now\"):\"borrow-confirm\"==\nb?ga_trackFn_fnLoan(\"fn_cloans::borrow_confirm\",\"borrow-confirm\"):\"tab-loanable-assets\"==b?ga_trackFn_fnLoan(\"fn_cloans::data_tab-loanable-assets\",\"tab-loanable-assets\"):\"tab-collateral-assets\"==b?ga_trackFn_fnLoan(\"fn_cloans::data_tab-collateral-assets\",\"tab-collateral-assets\"):\"tab-borrow-limit\"==b?ga_trackFn_fnLoan(\"fn_cloans::data_tab-borrow-limit\",\"tab-borrow-limit\"):\"tab-priceindex\"==b\u0026\u0026ga_trackFn_fnLoan(\"fn_cloans::data_tab-priceindex\",\"tab-priceindex\")})})();\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": true,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "vtp_usePostscribe": true,
                "tag_id": 301
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\"\u003Efunction ga_trackFn_wlMg(c,b){dataLayer.push({eventCategory:\"wl_margin\",eventAction:\"click\",eventLabel:c,elementid:b,event:\"GA_TM_cme_MARGIN\"})}\n(function(){var c=document.getElementsByTagName(\"body\")[0];c.addEventListener(\"click\",function(b){var a=b.target.id;b=b.target.parentNode.id;\"tab-cross\"==a?ga_trackFn_wlMg(\"wl_margin::view_Cross\",\"tab-cross\"):\"tab-isolated\"==a?ga_trackFn_wlMg(\"wl_margin::view_Isolated\",\"tab-isolated\"):\"TODAY\"==a?ga_trackFn_wlMg(\"wl_margin::view_TODAY\",\"TODAY\"):\"SEVEN_DAYS\"==a?ga_trackFn_wlMg(\"wl_margin::view_SEVEN_DAYS\",\"SEVEN_DAYS\"):\"THIRTY_DAYS\"==a?ga_trackFn_wlMg(\"wl_margin::view_THIRTY_DAYS\",\"THIRTY_DAYS\"):\"ALL\"==\na?ga_trackFn_wlMg(\"wl_margin::view_ALL\",\"ALL\"):\"convert-BNB\"==a?ga_trackFn_wlMg(\"wl_margin::convert_to_bnb\",\"convert-BNB\"):\"borrow-history\"==a?ga_trackFn_wlMg(\"wl_margin::borrowing_history\",\"borrow-history\"):\"cross-positions-transfer\"==a?ga_trackFn_wlMg(\"wl_margin::action_cross-positions-transfer\",\"cross-positions-transfer\"):\"cross-positions-borrowrepay\"==a?ga_trackFn_wlMg(\"wl_margin::action_cross-positions-borrowrepay\",\"cross-positions-borrowrepay\"):\"cross-positions-trade\"==a?ga_trackFn_wlMg(\"wl_margin::action_cross-positions-trade\",\n\"cross-positions-trade\"):\"cross-funds-trade\"==a?ga_trackFn_wlMg(\"wl_margin::action_cross-funds-trade\",\"cross-funds-trade\"):\"cross-funds-transfer\"==a?ga_trackFn_wlMg(\"wl_margin::action_cross-funds-transfer\",\"cross-funds-transfer\"):\"cross-funds-borrowrepay\"==a?ga_trackFn_wlMg(\"wl_margin::action_cross-funds-borrowrepay\",\"cross-funds-borrowrepay\"):\"isolated-funds-trade\"==a?ga_trackFn_wlMg(\"wl_margin::action_isolated-funds-trade\",\"isolated-funds-trade\"):\"isolated-funds-transfer\"==a?ga_trackFn_wlMg(\"wl_margin::action_isolated-funds-transfer\",\n\"isolated-funds-transfer\"):\"isolated-funds-borrowrepay\"==a?ga_trackFn_wlMg(\"wl_margin::action_isolated-funds-borrowrepay\",\"isolated-funds-borrowrepay\"):\"isolated-positions-trade\"==a?ga_trackFn_wlMg(\"wl_margin::action_isolated-positions-trade\",\"isolated-positions-trade\"):\"isolated-positions-transfer\"==a?ga_trackFn_wlMg(\"wl_margin::action_isolated-positions-transfer\",\"isolated-positions-transfer\"):\"isolated-positions-borrowrepay\"==a\u0026\u0026ga_trackFn_wlMg(\"wl_margin::action_isolated-positions-borrowrepay\",\n\"isolated-positions-borrowrepay\");\"borrow\"==b?ga_trackFn_wlMg(\"wl_margin::borrow\",\"borrow\"):\"repay\"==b?ga_trackFn_wlMg(\"wl_margin::repay\",\"repay\"):\"Transfer\"==b?ga_trackFn_wlMg(\"wl_margin::trasfer\",\"Transfer\"):\"history-jump\"==b?ga_trackFn_wlMg(\"wl_margin::margin_history\",\"history-jump\"):\"tab-FUNDS\"==b?ga_trackFn_wlMg(\"wl_margin::view_FUNDSy\",\"tab-FUNDS\"):\"tab-POSITIONS\"==b\u0026\u0026ga_trackFn_wlMg(\"wl_margin::view_POSITIONS\",\"tab-POSITIONS\");try{document.querySelector(\".BTC-benchmark\")\u0026\u0026document.querySelector(\".BTC-benchmark\").children[0].children[1].children[0].addEventListener(\"click\",\nfunction(){ga_trackFn_wlMg(\"wl_margin::view_BTC-benchmark\",\"BTC-benchmark\")}),document.querySelector(\".USDT-benchmark\")\u0026\u0026document.querySelector(\".USDT-benchmark\").children[0].children[1].children[0].addEventListener(\"click\",function(){ga_trackFn_wlMg(\"wl_margin::view_USDT-benchmark\",\"USDT-benchmark\")})}catch(d){}})})();\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": true,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "vtp_usePostscribe": true,
                "tag_id": 305
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\"\u003E(function(){var n=document.getElementsByTagName(\"body\")[0];n.addEventListener(\"click\",function(b){var d=document.location.pathname,a=\"null\",e=b.target.id,m=b.target.parentNode.id;\/openorder\/.test(d)?a=\"openorder\":\/tradeorder\/.test(d)?a=\"order\":\/usertrade\/.test(d)?a=\"trade\":\/capitalflow\/.test(d)?a=\"capitalflow\":\/fee-return-history\/.test(d)?a=\"feesreturn\":\/borrow\/.test(d)?a=\"borrowing\":\/repayment\/.test(d)?a=\"repayment\":\/transfer\/.test(d)?a=\"transfers\":\/interest\/.test(d)?a=\"interest\":\/margin-call\/.test(d)?\na=\"margincall\":\/liquidation-order\/.test(d)?a=\"liquidationOrder\":\/liquidation\/.test(d)\u0026\u0026(a=\"liquidation\");\"tab-cross\"==e?dataLayer.push({eventCategory:\"mo_\"+a,eventAction:\"click\",eventLabel:\"od_margin::\"+a+\"_Cross\",elementid:\"tab-cross\",event:\"GA_TM_cme_MARGIN\"}):\"tab-isolated\"==e\u0026\u0026dataLayer.push({eventCategory:\"mo_\"+a,eventAction:\"click\",eventLabel:\"od_margin::\"+a+\"_Isolated\",elementid:\"tab-isolated\",event:\"GA_TM_cme_MARGIN\"});d=[\"MARGIN-reset\",\"ISOLATED_MARGIN-reset\",\"iso-reset\",\"cross-reset\"];d.some(function(g,\nr){if(e==g)return dataLayer.push({eventCategory:\"mo_\"+a,eventAction:\"click\",eventLabel:\"od_margin::\"+a+\"_reset\",elementId:g,event:\"GA_TM_cme_MARGIN\"}),!0});try{if(\"order\"==a||\"trade\"==a)if(\"MARGIN-search\"==e){var c=b.target.parentNode.parentNode.children[0].querySelector(\"input.bnc-input\").value,p=b.target.parentNode.parentNode.children[1].querySelectorAll(\"input.bn-sdd-input\")[0].value,q=b.target.parentNode.parentNode.children[1].querySelectorAll(\"input.bn-sdd-input\")[1].value,h=b.target.parentNode.parentNode.children[2].querySelector(\"input.bn-sdd-input\").value;\ndataLayer.push({eventCategory:\"mo_\"+a,eventAction:\"click\",eventLabel:\"od_margin::\"+a+\"_search_\"+c+\"_\"+p+\"-\"+q+\"_\"+h,elementId:\"MARGIN-search\",event:\"GA_TM_cme_MARGIN\"})}else if(\"ISOLATED_MARGIN-search\"==e){c=b.target.parentNode.parentNode.children[0].querySelector(\"input.bnc-input\").value;var k=b.target.parentNode.parentNode.children[1].querySelectorAll(\"input.bn-sdd-input\")[0].value;h=b.target.parentNode.parentNode.children[2].querySelector(\"input.bn-sdd-input\").value;dataLayer.push({eventCategory:\"mo_\"+\na,eventAction:\"click\",eventLabel:\"od_margin::\"+a+\"_search_\"+c+\"_\"+k+\"_\"+h,elementId:\"ISOLATED_MARGIN-search\",event:\"GA_TM_cme_MARGIN\"})}if(\"feesreturn\"==a\u0026\u0026\"iso-search\"==e){c=b.target.parentNode.parentNode.children[0].querySelector(\"input.bnc-input\").value;k=b.target.parentNode.parentNode.children[1].querySelector(\"div.bn-sdd-value\").innerText;var f=b.target.parentNode.parentNode.children[2].querySelector(\"input.bn-sdd-input\").value;dataLayer.push({eventCategory:\"mo_\"+a,eventAction:\"click\",eventLabel:\"od_margin::\"+\na+\"_search_\"+c+\"_\"+k+\"_\"+f,elementId:\"iso-search\",event:\"GA_TM_cme_MARGIN\"})}if(\"borrowing\"==a||\"repayment\"==a||\"interest\"==a)\"cross-search\"==e?(c=b.target.parentNode.parentNode.children[1].querySelector(\"input.bnc-input\").value,f=b.target.parentNode.parentNode.children[2].querySelector(\"input.bn-sdd-input\").value,dataLayer.push({eventCategory:\"mo_\"+a,eventAction:\"click\",eventLabel:\"od_margin::\"+a+\"_search_\"+c+\"_\"+f,elementId:\"cross-search\",event:\"GA_TM_cme_MARGIN\"})):\"iso-search\"==e\u0026\u0026(c=b.target.parentNode.parentNode.children[1].querySelector(\"input.bnc-input\").value,\nf=b.target.parentNode.parentNode.children[3].querySelector(\"input.bn-sdd-input\").value,dataLayer.push({eventCategory:\"mo_\"+a,eventAction:\"click\",eventLabel:\"od_margin::\"+a+\"_search_\"+c+\"_\"+f,elementId:\"iso-search\",event:\"GA_TM_cme_MARGIN\"}));if(\"transfers\"==a)if(\"cross-search\"==e){c=b.target.parentNode.parentNode.children[1].querySelector(\"input.bnc-input\").value;f=b.target.parentNode.parentNode.children[2].querySelector(\"input.bn-sdd-input\").value;var l=b.target.parentNode.parentNode.children[3].querySelector(\"input.bn-sdd-input\").value;\ndataLayer.push({eventCategory:\"mo_\"+a,eventAction:\"click\",eventLabel:\"od_margin::\"+a+\"_search_\"+c+\"_\"+f+\"_\"+l,elementId:\"cross-search\",event:\"GA_TM_cme_MARGIN\"})}else\"iso-search\"==e\u0026\u0026(c=b.target.parentNode.parentNode.children[1].querySelector(\"input.bnc-input\").value,f=b.target.parentNode.parentNode.children[3].querySelector(\"input.bn-sdd-input\").value,l=b.target.parentNode.parentNode.children[4].querySelector(\"input.bn-sdd-input\").value,dataLayer.push({eventCategory:\"mo_\"+a,eventAction:\"click\",eventLabel:\"od_margin::\"+\na+\"_search_\"+c+\"_\"+f+\"_\"+l,elementId:\"iso-search\",event:\"GA_TM_cme_MARGIN\"}));if(\"margincall\"==a||\"liquidationOrder\"==a||\"liquidation\"==a)\"cross-search\"==e?(c=b.target.parentNode.parentNode.children[0].querySelector(\"input.bnc-input\").value,dataLayer.push({eventCategory:\"mo_\"+a,eventAction:\"click\",eventLabel:\"od_margin::\"+a+\"_search_\"+c,elementId:\"cross-search\",event:\"GA_TM_cme_MARGIN\"})):\"iso-search\"==e\u0026\u0026(c=b.target.parentNode.parentNode.children[0].querySelector(\"input.bnc-input\").value,dataLayer.push({eventCategory:\"mo_\"+\na,eventAction:\"click\",eventLabel:\"od_margin::\"+a+\"_search_\"+c,elementId:\"iso-search\",event:\"GA_TM_cme_MARGIN\"}))}catch(g){}if(\"borrowing\"==a||\"repayment\"==a||\"transfers\"==a||\"interest\"==a)\"Radio-a-r1\"==m?dataLayer.push({eventCategory:\"mo_\"+a,eventAction:\"click\",eventLabel:\"od_margin::\"+a+\"_Within 6 months\",elementId:\"Radio-a-r1\",event:\"GA_TM_cme_MARGIN\"}):\"Radio-a-r2\"==m\u0026\u0026dataLayer.push({eventCategory:\"mo_\"+a,eventAction:\"click\",eventLabel:\"od_margin::\"+a+\"_Beyond 6 months\",elementId:\"Radio-a-r2\",\nevent:\"GA_TM_cme_MARGIN\"})})})();\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": true,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "vtp_usePostscribe": true,
                "tag_id": 306
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\"\u003E(function(){var k=document.getElementsByTagName(\"body\")[0];k.addEventListener(\"click\",function(a){var g=a.target.id,l=document.location.pathname,b=\"null\",m=[\"orders\",\"repayment\",\"ltv\",\"liquidation\",\"loan\"];[\"order\",\"repay\",\"LTV\",\"liquidation\",\"history\"].some(function(h,n){if((new RegExp(h)).test(l))return b=m[n],!0});a.target.parentNode.parentNode\u0026\u0026a.target.parentNode.parentNode.id\u0026\u0026dataLayer.push({eventCategory:\"lh_loanorders\",eventAction:\"click\",eventLabel:\"od_cloan::loan_orders\",elementid:\"sidebar-loan-order\",\nevent:\"GA_TM_cme_MARGIN\"});\"loan-reset\"==g\u0026\u0026dataLayer.push({eventCategory:\"lh_\"+b,eventAction:\"click\",eventLabel:\"od_loan::\"+b+\"_reset\",elementId:\"loan-reset\",event:\"GA_TM_cme_MARGIN\"});try{if(\"loan-search\"==g)if(\"loanorders\"==b||\"liquidation\"==b||\"loan\"==b){var c=a.target.parentNode.parentNode.children[0].querySelector(\"input\").value,d=a.target.parentNode.parentNode.children[1].querySelector(\"input\").value,e=a.target.parentNode.parentNode.children[2].children[0].lastChild.value,f=a.target.parentNode.parentNode.children[3].children[0].lastChild.value,\np=a.target.parentNode.parentNode.children[4].children[0].lastChild.value;dataLayer.push({eventCategory:\"lh_\"+b,eventAction:\"click\",eventLabel:\"od_loan::\"+b+\"_search_\"+c+\"_\"+d+\"_\"+e+\"_\"+f+\"_\"+p,elementId:\"loan-search\",event:\"GA_TM_cme_MARGIN\"})}else\"repayment\"==b?(c=a.target.parentNode.parentNode.children[0].querySelector(\"input\").value,d=a.target.parentNode.parentNode.children[1].querySelector(\"input\").value,e=a.target.parentNode.parentNode.children[2].children[0].lastChild.value,dataLayer.push({eventCategory:\"lh_\"+\nb,eventAction:\"click\",eventLabel:\"od_loan::\"+b+\"_search_\"+c+\"_\"+d+\"_\"+e,elementId:\"loan-search\",event:\"GA_TM_cme_MARGIN\"})):\"ltv\"==b\u0026\u0026(c=a.target.parentNode.parentNode.children[0].querySelector(\"input\").value,d=a.target.parentNode.parentNode.children[1].querySelector(\"input\").value,e=a.target.parentNode.parentNode.children[2].children[0].lastChild.value,f=a.target.parentNode.parentNode.children[3].children[0].lastChild.value,dataLayer.push({eventCategory:\"lh_\"+b,eventAction:\"click\",eventLabel:\"od_loan::\"+\nb+\"_search_\"+c+\"_\"+d+\"_\"+e+\"_\"+f,elementId:\"loan-search\",event:\"GA_TM_cme_MARGIN\"}))}catch(h){}})})();\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": true,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "vtp_usePostscribe": true,
                "tag_id": 309
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\" type=\"text\/gtmscript\"\u003Efunction getParentTag(a,b){return\"BODY\"!==a.parentElement.nodeName?(b.push(a.parentElement.getAttribute(\"data-testid\")),getParentTag(a.parentElement,b)):b}\ndocument.querySelector(\"body\").addEventListener(\"click\",function(a){-1!=getParentTag(a.target,[]).indexOf(\"One-wayMode\")\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"td_futures\",eventAction:\"click\",eventLabel:\"td_futures::position_mode_One-wayMode\",elementid:\"One-wayMode\"});-1!=getParentTag(a.target,[]).indexOf(\"HedgeMode\")\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"td_futures\",eventAction:\"click\",eventLabel:\"td_futures::position_mode_HedgeMode\",elementid:\"HedgeMode\"});-1!=getParentTag(a.target,\n[]).indexOf(\"cross\")\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"td_futures\",eventAction:\"click\",eventLabel:\"td_futures::margin_type_cross\",elementid:\"cross\"});-1!=getParentTag(a.target,[]).indexOf(\"isolated\")\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"td_futures\",eventAction:\"click\",eventLabel:\"td_futures::margin_type_cross\",elementid:\"isolated\"})});\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": false,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "tag_id": 322
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\" type=\"text\/gtmscript\"\u003Etry{var fu_switch=document.querySelector(\"[data-testid\\x3dwl_futuresPageSwitch]\");fu_switch.firstChild.onclick=function(){dataLayer.push({event:\"click\",eventCategory:\"wl_futures\",eventAction:\"click\",eventLabel:\"wl_futures::view_\"+this.innerHTML,elementid:\"wl_futuresPageSwitch\"})};fu_switch.lastChild.onclick=function(){dataLayer.push({event:\"click\",eventCategory:\"wl_futures\",eventAction:\"click\",eventLabel:\"wl_futures::view_\"+this.innerHTML,elementid:\"wl_futuresPageSwitch\"})};document.querySelector(\"[data-testid\\x3dwl_futuresConvert]\").addEventListener(\"click\",\nfunction(){dataLayer.push({event:\"click\",eventCategory:\"wl_futures\",eventAction:\"click\",eventLabel:\"wl_futures::convert\",elementid:\"Convert\"})});document.querySelector(\"[data-testid\\x3dwl_futuresBuyCrypto]\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"wl_futures\",eventAction:\"click\",eventLabel:\"wl_futures::buy_crypto\",elementid:\"wl_futuresBuyCrypto\"})});document.querySelector(\"[data-testid\\x3dwl_futuresTransfer]\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",\neventCategory:\"wl_futures\",eventAction:\"click\",eventLabel:\"wl_futures::transfer\",elementid:\"wl_futuresTransfer\"})});document.querySelector(\"[data-testid\\x3dwl_futuresTransHistory]\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"wl_futures\",eventAction:\"click\",eventLabel:\"wl_futures::transaction_history\",elementid:\"wl_futuresTransHistory\"})});document.querySelector(\"[data-testid\\x3dwl_futuresClickMoreRates]\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",\neventCategory:\"wl_futures\",eventAction:\"click\",eventLabel:\"wl_futures::click_more_info\",elementid:\"wl_futuresClickMoreRates\"})});document.querySelector(\"[data-testid\\x3dwl_futuresStartBorrowing]\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"wl_futures\",eventAction:\"click\",eventLabel:\"wl_futures::start_borrwing\",elementid:\"wl_futuresStartBorrowing\"})});document.querySelector(\"[data-testid\\x3dwl_futuresViewListType]\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",\neventCategory:\"wl_futures\",eventAction:\"click\",eventLabel:\"wl_futures::view_\"+this.firstChild.innerHTML,elementid:\"wl_futuresViewListType\"})})}catch(a){}\ndocument.querySelector(\"body\").addEventListener(\"click\",function(a){\"wl_futures_actionGoToTrade\"==a.target.id\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"wl_futures\",eventAction:\"click\",eventLabel:\"wl_futures::action_Trade\",elementid:\"wl_futures_actionGoToTrade\"});\"wl_futures_actionTransfer\"==a.target.id\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"wl_futures\",eventAction:\"click\",eventLabel:\"wl_futures::action_Transfer\",elementid:\"wl_futures_actionTransfer\"});\"wl_futures_actionBorrow\"==a.target.id\u0026\u0026\ndataLayer.push({event:\"click\",eventCategory:\"wl_futures\",eventAction:\"click\",eventLabel:\"wl_futures::action_Borrow\",elementid:\"wl_futures_actionBorrow\"});\"wl_futures_actionRepay\"==a.target.id\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"wl_futures\",eventAction:\"click\",eventLabel:\"wl_futures::action_Repay\",elementid:\"wl_futures_actionRepay\"});\"wl_futures_actionAdjustLTV\"==a.target.id\u0026\u0026dataLayer.push({event:\"click\",eventCategory:\"wl_futures\",eventAction:\"click\",eventLabel:\"wl_futures::action_AdjustLTV\",\nelementid:\"wl_futures_actionAdjustLTV\"})});\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": false,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "tag_id": 324
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\"\u003Etry{for(var date=document.querySelector(\"[data-testid\\x3dwl_futurespnl_date]\"),i=0;3\u003Ei;i++)date.getElementsByTagName(\"button\")[i].addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"wl_futurespnl\",eventAction:\"click\",eventLabel:\"wl_futures::pnl_\"+this.innerHTML,elementid:\"wl_futurespnl_date\"})})}catch(a){}\ntry{for(var j=0;;j++)if(date.getElementsByTagName(\"li\")[j])date.getElementsByTagName(\"li\")[j].addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"wl_futurespnl\",eventAction:\"click\",eventLabel:\"wl_futures::pnl_\"+this.title,elementid:\"wl_futurespnl_date\"})});else break}catch(a){}\ntry{var page=document.querySelector(\"[data-testid\\x3dwl_futurespnl_preNextPage]\");page.querySelector(\"[aria-label^\\x3dPrevious]\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"wl_futurespnl\",eventAction:\"click\",eventLabel:\"wl_futures::pnl_prepage\",elementid:\"wl_futurespnl_preNextPage\"})});page.querySelector(\"[aria-label^\\x3dNext]\").addEventListener(\"click\",function(){dataLayer.push({event:\"click\",eventCategory:\"wl_futurespnl\",eventAction:\"click\",eventLabel:\"wl_futures::pnl_nextpage\",\nelementid:\"wl_futurespnl_preNextPage\"})})}catch(a){};\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": true,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "vtp_usePostscribe": true,
                "tag_id": 326
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\" type=\"text\/gtmscript\"\u003Etry{document.querySelector(\"[data-testid\\x3dfuturesStrategyTutorial]\").addEventListener(\"click\",function(a){dataLayer.push({event:\"click\",eventCategory:\"sg_tutorial\",eventAction:\"click\",eventLabel:\"sg_tutorial::click_to_see_grid_trading\",elementid:\"futuresStrategyTutorial\"})})}catch(a){};\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": false,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "tag_id": 328
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\"\u003E(function(){var a=", ["escape", ["macro", 51], 8, 16], ";try{var d=ga.getAll()[0].get(\"clientId\")}catch(b){d=Math.round(+new Date\/1E3);try{var g=new Uint32Array(1);var e=crypto.getRandomValues(g)[0]}catch(h){e=Math.round(2147483647*Math.random())}d=[e,d].join(\".\")}e=[d,Date.now()].join(\".\");if(a instanceof Object\u0026\u0026a.purchase\u0026\u0026a.purchase instanceof Object){a.currencyCode=\"USD\";if(a.purchase.actionField){var c=a.purchase.actionField;var f=c.id;c.id||(c.id=e);c.revenue||(c.revenue=1);a.purchase.products\u0026\u0026a.purchase.products instanceof\nArray\u0026\u0026a.purchase.products.forEach(function(b){b instanceof Object\u0026\u0026(b.price||(b.price=1),b.quantity||(b.quantity=1),b.orderId\u0026\u0026(f=c.id=b.orderId))})}window.dataLayer=window.dataLayer||[];window.dataLayer.push({ecommerce:null});window.dataLayer.push({event:\"purchaseWithTi\",dlv_customTID:f,ecommerce:a})}})();\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": true,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "vtp_usePostscribe": true,
                "tag_id": 347
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\"\u003E(function(){var h=document.getElementsByTagName(\"body\")[0],k=[{eid:\"tab-favorite\",txt:\"Favorites\"},{eid:\"tab-spot\",txt:\"Spot Markets\"},{eid:\"tab-futures\",txt:\"Futures Markets\"},{eid:\"tab-newListing\",txt:\"New listing\"},{eid:\"tab-coinInfo\",txt:\"All Cryptos\"},{eid:\"tab-overview\",txt:\"Markets Overview\"},{eid:\"tab-moves\",txt:\"Top Movers\"}],c={},g=function(){if(document.getElementById(\"market_sector_Spot\")){document.getElementById(\"market_overview_topmovers_enter\")||(c.market_overview_topmovers_enter=!1,\nc[\"24h_ranking_enter\"]=!1,c.derivatives_top_enter=!1,c.market_filter_ranking=!1,c.market_filter_derivativestop=!1);document.querySelector(\"#tab-favorite\")\u0026\u0026!c.mk_selection\u0026\u0026(k.forEach(function(a){document.querySelectorAll(\"#\"+a.eid).forEach(function(e){e.addEventListener(\"click\",function(){dataLayer.push({eventCategory:\"mk_selection\",eventAction:\"click\",eventLabel:\"market::select_\"+a.txt,elementId:a.eid,event:\"GA_TM_cme_Markets\"});c.market_filter_spot=!1;c.market_filter_futures=!1;c.market_filter_coinInfo=\n!1;c.mk_favourites=!1;c.mk_data_history=!1})})}),c.mk_selection=!0);if(document.querySelector(\"#market_filter_spot\")\u0026\u0026!c.market_filter_spot){var d=\"market_filter_spot\";document.querySelector(\"#\"+d).addEventListener(\"click\",function(a){a=a.target;for(var e=a.outerText,b=a.id;\"body\"!=a.tagName\u0026\u0026\"__APP\"!==b\u0026\u0026b!==d\u0026\u0026!\/^tab-\/.test(b);)a=a.parentNode,b=a.id;\/^tab-\/.test(b)\u0026\u0026dataLayer.push({eventCategory:\"mk_sector\",eventAction:\"click\",eventLabel:\"market::sector_\"+e,elementId:b,event:\"GA_TM_cme_Markets\"})});\nc.market_filter_spot=!0}document.querySelector(\"#market_filter_futures\")\u0026\u0026!c.market_filter_futures\u0026\u0026(d=\"market_filter_futures\",document.querySelector(\"#\"+d).addEventListener(\"click\",function(a){a=a.target;for(var e=a.outerText,b=a.id;\"body\"!=a.tagName\u0026\u0026\"__APP\"!==b\u0026\u0026b!==d\u0026\u0026!\/^tab-\/.test(b);)a=a.parentNode,b=a.id;\/^tab-\/.test(b)\u0026\u0026dataLayer.push({eventCategory:\"mk_sector\",eventAction:\"click\",eventLabel:\"market::sector_\"+e,elementId:b,event:\"GA_TM_cme_Markets\"})}),c.market_filter_futures=!0);document.querySelector(\"#market_filter_coinInfo\")\u0026\u0026\n!c.market_filter_coinInfo\u0026\u0026(d=\"market_filter_coinInfo\",document.querySelector(\"#\"+d).addEventListener(\"click\",function(a){a=a.target;for(var e=a.outerText,b=a.id;\"body\"!=a.tagName\u0026\u0026\"__APP\"!==b\u0026\u0026b!==d\u0026\u0026!\/^tab-\/.test(b);)a=a.parentNode,b=a.id;\/^tab-\/.test(b)\u0026\u0026dataLayer.push({eventCategory:\"mk_sector\",eventAction:\"click\",eventLabel:\"market::sector_\"+e,elementId:b,event:\"GA_TM_cme_Markets\"})}),c.market_filter_coinInfo=!0);0\u003Cdocument.querySelectorAll(\"#market_trade_list_item a\").length\u0026\u0026!c.mk_data_history\u0026\u0026\ndocument.querySelectorAll(\"#market_trade_list_item a\").forEach(function(a){a.addEventListener(\"click\",function(e){(e=e.target.className.match(\/click_markets_futures_history\\w*\\b\/))\u0026\u0026dataLayer.push({eventCategory:\"mk_data_history\",eventAction:\"click\",eventLabel:\"market::data_history\"+e[0].replace(\"click_markets_futures_history\",\"\"),elementId:e[0],event:\"GA_TM_cme_Markets\"})});c.mk_data_history=!0});0\u003Cdocument.querySelectorAll(\"#market_trade_list_item svg\").length\u0026\u0026!c.mk_favourites\u0026\u0026document.querySelectorAll(\"#market_trade_list_item svg\").forEach(function(a){a.addEventListener(\"click\",\nfunction(){var e=a.id;\/favourit\/.test(e)\u0026\u0026dataLayer.push({eventCategory:\"mk_favourites\",eventAction:\"click\",eventLabel:\"market::favourites_\"+e.replace(\"_favourit\",\"\"),elementId:e,event:\"GA_TM_cme_Markets\"})});c.mk_favourites=!0});var f=[\"market_overview_topmovers_enter\",\"24h_ranking_enter\",\"derivatives_top_enter\"];document.getElementById(f[0])\u0026\u0026!c[f[0]]\u0026\u0026(d=f[0],document.getElementById(d).addEventListener(\"click\",function(){dataLayer.push({eventCategory:\"mo_categ\",eventAction:\"click\",eventLabel:\"market_overview::select_\"+\nd.replace(\"market_overview_\",\"\").replace(\"_enter\",\"\"),elementId:d,event:\"GA_TM_cme_Markets\"})}),c[f[0]]=!0);document.getElementById(f[1])\u0026\u0026!c[f[1]]\u0026\u0026(d=f[1],document.getElementById(d).addEventListener(\"click\",function(){dataLayer.push({eventCategory:\"mo_categ\",eventAction:\"click\",eventLabel:\"market_overview::select_\"+d.replace(\"market_overview_\",\"\").replace(\"_enter\",\"\"),elementId:d,event:\"GA_TM_cme_Markets\"})}),c[f[1]]=!0);document.getElementById(f[2])\u0026\u0026!c[f[2]]\u0026\u0026(d=f[2],document.getElementById(d).addEventListener(\"click\",\nfunction(){dataLayer.push({eventCategory:\"mo_categ\",eventAction:\"click\",eventLabel:\"market_overview::select_\"+d.replace(\"market_overview_\",\"\").replace(\"_enter\",\"\"),elementId:d,event:\"GA_TM_cme_Markets\"})}),c[f[2]]=!0);document.querySelector(\"#market_filter_ranking\")\u0026\u0026!c.market_filter_ranking\u0026\u0026(d=\"market_filter_ranking\",document.querySelector(\"#\"+d).addEventListener(\"click\",function(a){a=a.target;for(var e=a.outerText,b=a.id;\"body\"!=a.tagName\u0026\u0026\"__APP\"!==b\u0026\u0026b!==d\u0026\u0026!\/^tab-\/.test(b);)a=a.parentNode,b=\na.id;\/^tab-\/.test(b)\u0026\u0026dataLayer.push({eventCategory:\"mo_24h_rankings\",eventAction:\"click\",eventLabel:\"market_overview::24h_rankings_\"+e,elementId:b,event:\"GA_TM_cme_Markets\"})}),c.market_filter_ranking=!0);document.querySelector(\"#market_filter_derivativestop\")\u0026\u0026!c.market_filter_derivativestop\u0026\u0026(d=\"market_filter_derivativestop\",document.querySelector(\"#\"+d).addEventListener(\"click\",function(a){a=a.target;for(var e=a.outerText,b=a.id;\"body\"!=a.tagName\u0026\u0026\"__APP\"!==b\u0026\u0026b!==d\u0026\u0026!\/^tab-\/.test(b);)a=a.parentNode,\nb=a.id;\/^tab-\/.test(b)\u0026\u0026dataLayer.push({eventCategory:\"mo_top_derivatives\",eventAction:\"click\",eventLabel:\"market_overview::top_derivatives_\"+e,elementId:b,event:\"GA_TM_cme_Markets\"})}),c.market_filter_derivativestop=!0)}};g=new MutationObserver(g);g.observe(h,{childList:!0,subtree:!0})})();\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": true,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "vtp_usePostscribe": true,
                "tag_id": 357
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "analytics_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cscript nonce=\"", ["escape", ["macro", 66], 4], "\" type=\"text\/gtmscript\"\u003E(function(){var b={},c=[{eid:\"type-market\",txt:\"Market\"},{eid:\"type-limit\",txt:\"Limit\"}];c.forEach(function(a){document.querySelectorAll(\"#\"+a.eid).forEach(function(e){e.addEventListener(\"click\",function(){dataLayer.push({eventCategory:\"convert_otc\",eventAction:\"click\",eventLabel:\"convert_otc::type_\"+a.txt,elementId:a.eid,event:\"GA_TM_cme_convert_otc\"});b.convert_otc_TimeRange=!1})})});document.querySelector(\".tab .order\")\u0026\u0026document.querySelector(\".tab .order\").addEventListener(\"click\",function(a){dataLayer.push({eventCategory:\"convert_otc\",\neventAction:\"click\",eventLabel:\"convert_otc::view_convert_orders\",elementId:\"order\",event:\"GA_TM_cme_convert_otc\"})});var d=function(){document.querySelector(\".period-select\")\u0026\u0026!b.convert_otc_TimeRange\u0026\u0026(b.convert_otc_TimeRange=!0,document.querySelector(\".period-select\").addEventListener(\"click\",function(a){a=a.target;dataLayer.push({eventCategory:\"convert_otc\",eventAction:\"click\",eventLabel:\"convert_otc::limit_\"+a.outerText+\"_view\",elementId:\"period-item::\"+a.outerText,event:\"GA_TM_cme_convert_otc\"})}))};\nc=document.getElementsByTagName(\"body\")[0];d=new MutationObserver(d);d.observe(c,{childList:!0,subtree:!0})})();\u003C\/script\u003E"],
                "vtp_supportDocumentWrite": false,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "tag_id": 385
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "personalization_storage"],
                "once_per_event": true,
                "vtp_html": ["template", "\u003Cimg src=\"\/\/pixel.mathtag.com\/event\/img?mt_id=1578955\u0026amp;mt_adid=251559\u0026amp;mt_exem=\u0026amp;mt_excl=\u0026amp;v1=", ["escape", ["macro", 43], 12], "\u0026amp;v2=\u0026amp;v3=\u0026amp;s1=\u0026amp;s2=", ["escape", ["macro", 12], 12], "\u0026amp;s3=\" width=\"1\" height=\"1\"\u003E\n"],
                "vtp_supportDocumentWrite": false,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "tag_id": 433
            }, {
                "function": "__html",
                "metadata": ["map"],
                "consent": ["list", "personalization_storage"],
                "once_per_event": true,
                "vtp_html": "\u003Cimg src=\"\/\/pixel.mathtag.com\/event\/img?mt_id=1618746\u0026amp;mt_adid=251559\u0026amp;mt_exem=\u0026amp;mt_excl=\u0026amp;v1=\u0026amp;v2=\u0026amp;v3=\u0026amp;s1=\u0026amp;s2=\u0026amp;s3=\" width=\"1\" height=\"1\"\u003E\n",
                "vtp_supportDocumentWrite": false,
                "vtp_enableIframeMode": false,
                "vtp_enableEditJsMacroBehavior": false,
                "tag_id": 587
            }, {
                "function": "__paused",
                "vtp_originalTagType": "opt",
                "tag_id": 533
            }],
            "predicates": [{
                "function": "_eq",
                "arg0": ["macro", 0],
                "arg1": "Registration"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "Registration"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "go to homepage"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "go to welcome page"
            }, {
                "function": "_re",
                "arg0": ["macro", 2],
                "arg1": "c2c.binance.com|p2p.binance.com|www.binance.com|www.binance.me|accounts.binance.com"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "click"
            }, {
                "function": "_re",
                "arg0": ["macro", 2],
                "arg1": "www.binance.com|www.binance.me"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "language_region"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "currency"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "input"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "received account confirm"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "buy_crypto_card"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "buy_crypto_common"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "buy_crypto_multiple"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "buy_crypto_result"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "buy_crypto_wallet"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "deposit_fiat"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "sell_crypto_multiple"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "top_navig_bc"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "withdraw_fiat"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "GA_TM_cme_FIAT"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "GA_TM_cme_KYC"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "kyc_verification_interface"
            }, {
                "function": "_eq",
                "arg0": ["macro", 36],
                "arg1": "fb_card::add_new_card_next"
            }, {
                "function": "_eq",
                "arg0": ["macro", 36],
                "arg1": "fb_card::change_card"
            }, {
                "function": "_eq",
                "arg0": ["macro", 36],
                "arg1": "fb_multiple::add_new_card_next"
            }, {
                "function": "_cn",
                "arg0": ["macro", 37],
                "arg1": "\/saving\/history\/"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "page loading"
            }, {
                "function": "_cn",
                "arg0": ["macro", 37],
                "arg1": "\/account\/saving"
            }, {
                "function": "_cn",
                "arg0": ["macro", 37],
                "arg1": "\/swap\/pool"
            }, {
                "function": "_cn",
                "arg0": ["macro", 37],
                "arg1": "\/eth2"
            }, {
                "function": "_cn",
                "arg0": ["macro", 37],
                "arg1": "\/pos"
            }, {
                "function": "_cn",
                "arg0": ["macro", 37],
                "arg1": "\/bnbmining"
            }, {
                "function": "_cn",
                "arg0": ["macro", 37],
                "arg1": "\/savings"
            }, {
                "function": "_cn",
                "arg0": ["macro", 37],
                "arg1": "\/earn"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "GA_TM_cme_EARN"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "GA_TM_cme_LiquidSwap"
            }, {
                "function": "_re",
                "arg0": ["macro", 37],
                "arg1": "[0-9a-zA-Z]{32}$"
            }, {
                "function": "_cn",
                "arg0": ["macro", 37],
                "arg1": "\/support\/announcement\/"
            }, {
                "function": "_re",
                "arg0": ["macro", 2],
                "arg1": "www.binance.me|www.binance.com"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "gtm.scrollDepth"
            }, {
                "function": "_re",
                "arg0": ["macro", 38],
                "arg1": "(^$|((^|,)32196322_226($|,)))"
            }, {
                "function": "_re",
                "arg0": ["macro", 37],
                "arg1": "[0-9]{12}$"
            }, {
                "function": "_cn",
                "arg0": ["macro", 37],
                "arg1": "\/support\/faq\/"
            }, {
                "function": "_re",
                "arg0": ["macro", 38],
                "arg1": "(^$|((^|,)32196322_231($|,)))"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "GA_TM_cme_MARGIN"
            }, {
                "function": "_cn",
                "arg0": ["macro", 37],
                "arg1": "\/my\/orders\/exchange\/"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "gtm.dom"
            }, {
                "function": "_cn",
                "arg0": ["macro", 37],
                "arg1": "\/leveraged-tokens\/tokens\/allTokens"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "gtm_consent_update"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "purchaseWithTi"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "gtm.init_consent"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "GA_TM_cme_Markets"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "market_column"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "market_detail"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "market_edit"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "GA_TM_cme_productClick"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "GA_TM_cme_convert_otc"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "gtm.js"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "dle_ads_purchase"
            }, {
                "function": "_eq",
                "arg0": ["macro", 16],
                "arg1": "first_trade"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "purchase"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "trade"
            }, {
                "function": "_eq",
                "arg0": ["macro", 2],
                "arg1": "merchant.binance.com"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "channel_partner"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "contact_sales"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "direct_merchant"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "get_started"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "trial"
            }, {
                "function": "_eq",
                "arg0": ["macro", 17],
                "arg1": "application:form:channel:partner"
            }, {
                "function": "_eq",
                "arg0": ["macro", 16],
                "arg1": "submit:success"
            }, {
                "function": "_eq",
                "arg0": ["macro", 17],
                "arg1": "contact:sales:form:success:pop:up"
            }, {
                "function": "_eq",
                "arg0": ["macro", 17],
                "arg1": "application:form:direct:merchant"
            }, {
                "function": "_eq",
                "arg0": ["macro", 16],
                "arg1": "click:submit"
            }, {
                "function": "_eq",
                "arg0": ["macro", 17],
                "arg1": "get started:landing:channelpartner"
            }, {
                "function": "_eq",
                "arg0": ["macro", 16],
                "arg1": "click:button"
            }, {
                "function": "_eq",
                "arg0": ["macro", 17],
                "arg1": "get started:onboardingsolution:channelpartner"
            }, {
                "function": "_eq",
                "arg0": ["macro", 17],
                "arg1": "get started:landing:directmerchant"
            }, {
                "function": "_eq",
                "arg0": ["macro", 17],
                "arg1": "get started:onboardingsolution:directmerchant"
            }, {
                "function": "_eq",
                "arg0": ["macro", 17],
                "arg1": "get started:header"
            }, {
                "function": "_eq",
                "arg0": ["macro", 17],
                "arg1": "start trial:landing"
            }, {
                "function": "_eq",
                "arg0": ["macro", 16],
                "arg1": "click:banner"
            }, {
                "function": "_eq",
                "arg0": ["macro", 17],
                "arg1": "start trial:onboarding"
            }, {
                "function": "_eq",
                "arg0": ["macro", 17],
                "arg1": "view:page:trial:get:started:mmp"
            }, {
                "function": "_eq",
                "arg0": ["macro", 16],
                "arg1": "view:page"
            }, {
                "function": "_eq",
                "arg0": ["macro", 17],
                "arg1": "get started:landing:submerchant"
            }, {
                "function": "_eq",
                "arg0": ["macro", 17],
                "arg1": "get started:onboardingsolution:submerchant"
            }, {
                "function": "_eq",
                "arg0": ["macro", 17],
                "arg1": "contact:sales:form"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "activate_card"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "apply_card"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "card_dashboard"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "card_fees"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "card_level_cashback"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "currency_conversion"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "order_card"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "refugee_card"
            }, {
                "function": "_eq",
                "arg0": ["macro", 3],
                "arg1": "global_card"
            }, {
                "function": "_eq",
                "arg0": ["macro", 16],
                "arg1": "click"
            }, {
                "function": "_eq",
                "arg0": ["macro", 16],
                "arg1": "popup_view"
            }, {
                "function": "_re",
                "arg0": ["macro", 55],
                "arg1": "binance\\.(com|me)\\\/en-in\\\/?$",
                "ignore_case": true
            }, {
                "function": "_eq",
                "arg0": ["macro", 26],
                "arg1": "Card_order_shipping_info_order_click"
            }, {
                "function": "_eq",
                "arg0": ["macro", 26],
                "arg1": "binance_card_get_started_click"
            }, {
                "function": "_eq",
                "arg0": ["macro", 26],
                "arg1": "Card_order_VC_ready_popup_view"
            }, {
                "function": "_eq",
                "arg0": ["macro", 3],
                "arg1": "cryptoBox_shareCampaign"
            }, {
                "function": "_re",
                "arg0": ["macro", 1],
                "arg1": "^(share|faq|send_cryptoBox|claim_crypto|search_crypto|choose_crypto|create_box|box_created_success|box_created_failed|share_copyLink|share_download|share_share|open_box|share_rewards)$"
            }, {
                "function": "_sw",
                "arg0": ["macro", 3],
                "arg1": "pay_"
            }, {
                "function": "_re",
                "arg0": ["macro", 1],
                "arg1": "^(pay_send|pay_receive|pay_links|pay_copy_id|pay_faqs|pay_txn|pay_setting|pay_common_payees|pay_send_to|pay_faq|pay_amount|pay_confirm|pay_success|pay_fail|pay_qrcode|pay_select_currency|pay_filter|pay_action|pay_my_subscription|pay_live|pay_subscribe|pay_share|pay_play_now|pay_FIL|pay_support|registration_entrance)$"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "view_promotion"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "select_promotion"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "OneTrustGroupsUpdated"
            }, {
                "function": "_sw",
                "arg0": ["macro", 2],
                "arg1": "academy."
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "gtm.historyChange"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "share"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "rating_submit"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "calculate_prediction"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "buy_coin"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "register"
            }, {
                "function": "_re",
                "arg0": ["macro", 37],
                "arg1": "^\\\/[a-zA-Z\\-]+\\\/feed\\\/(post|profile)\\\/",
                "ignore_case": true
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "gtm.load"
            }, {
                "function": "_cn",
                "arg0": ["macro", 55],
                "arg1": "login"
            }, {
                "function": "_eq",
                "arg0": ["macro", 2],
                "arg1": "accounts.binance.com"
            }, {
                "function": "_cn",
                "arg0": ["macro", 55],
                "arg1": "register"
            }, {
                "function": "_cn",
                "arg0": ["macro", 37],
                "arg1": "verification-new-register"
            }, {
                "function": "_cn",
                "arg0": ["macro", 37],
                "arg1": "markets"
            }, {
                "function": "_cn",
                "arg0": ["macro", 37],
                "arg1": "my\/settings\/profile"
            }, {
                "function": "_re",
                "arg0": ["macro", 37],
                "arg1": "^\/[a-z]{2}(-[A-Z]{2})?\/fiat(\/.*)?$"
            }, {
                "function": "_re",
                "arg0": ["macro", 37],
                "arg1": "^\/[a-zA-Z-]+\/my\/wallet\/exchange\/(withdrawal|deposit)\/(fiat|fiat-deposit|fiat-withdrawal)(\/.*)?$"
            }, {
                "function": "_re",
                "arg0": ["macro", 37],
                "arg1": "^\/[a-zA-Z-]+\/my\/wallet\/exchange\/(identity-verified|buysell-history|receipt-detail)(\/.*)?$"
            }, {
                "function": "_re",
                "arg0": ["macro", 37],
                "arg1": "\/[a-zA-Z-]+\/my\/wallet\/account\/main\/(deposit|withdrawal)\/(fiat|fiat-deposit|fiat-withdrawal)(\/.*)?$"
            }, {
                "function": "_re",
                "arg0": ["macro", 37],
                "arg1": "^\/[a-z]{2}(-[a-zA-Z]{2})?\/(busd|buy-sell-crypto|connect)(\/.*)?$"
            }, {
                "function": "_ew",
                "arg0": ["macro", 37],
                "arg1": "\/my\/wallet\/account\/overview"
            }, {
                "function": "_ew",
                "arg0": ["macro", 37],
                "arg1": "\/my\/wallet\/account\/main"
            }, {
                "function": "_ew",
                "arg0": ["macro", 37],
                "arg1": "my\/wallet\/account\/main\/deposit\/crypto"
            }, {
                "function": "_cn",
                "arg0": ["macro", 37],
                "arg1": "\/withdrawal\/crypto"
            }, {
                "function": "_cn",
                "arg0": ["macro", 37],
                "arg1": "\/wallet\/history"
            }, {
                "function": "_ew",
                "arg0": ["macro", 37],
                "arg1": "\/blog"
            }, {
                "function": "_ew",
                "arg0": ["macro", 37],
                "arg1": "\/my\/settings\/preference"
            }, {
                "function": "_ew",
                "arg0": ["macro", 37],
                "arg1": "\/my\/security"
            }, {
                "function": "_ew",
                "arg0": ["macro", 37],
                "arg1": "\/inmail"
            }, {
                "function": "_ew",
                "arg0": ["macro", 37],
                "arg1": "\/download"
            }, {
                "function": "_ew",
                "arg0": ["macro", 37],
                "arg1": "\/community"
            }, {
                "function": "_ew",
                "arg0": ["macro", 37],
                "arg1": "\/support"
            }, {
                "function": "_ew",
                "arg0": ["macro", 37],
                "arg1": "\/support\/search"
            }, {
                "function": "_cn",
                "arg0": ["macro", 37],
                "arg1": "\/support\/faq"
            }, {
                "function": "_cn",
                "arg0": ["macro", 8],
                "arg1": "\/support\/announcement"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "productClick"
            }, {
                "function": "_re",
                "arg0": ["macro", 37],
                "arg1": "[0-9a-z]{32}$"
            }, {
                "function": "_eq",
                "arg0": ["macro", 2],
                "arg1": "p2p.binance.com"
            }, {
                "function": "_eq",
                "arg0": ["macro", 2],
                "arg1": "c2c.binance.com"
            }, {
                "function": "_cn",
                "arg0": ["macro", 37],
                "arg1": "\/fiatOrder"
            }, {
                "function": "_cn",
                "arg0": ["macro", 37],
                "arg1": "\/my\/orders\/futures\/openorder"
            }, {
                "function": "_eq",
                "arg0": ["macro", 2],
                "arg1": "www.binance.com"
            }, {
                "function": "_cn",
                "arg0": ["macro", 37],
                "arg1": "\/my\/orders\/futures\/tradehistory"
            }, {
                "function": "_cn",
                "arg0": ["macro", 37],
                "arg1": "\/my\/orders\/futures\/orderhistory"
            }, {
                "function": "_cn",
                "arg0": ["macro", 37],
                "arg1": "\/my\/orders\/futures\/transactionhistory"
            }, {
                "function": "_cn",
                "arg0": ["macro", 37],
                "arg1": "\/my\/orders\/futures\/borrowhistory"
            }, {
                "function": "_cn",
                "arg0": ["macro", 37],
                "arg1": "\/my\/orders\/futures\/repaymenthistory"
            }, {
                "function": "_cn",
                "arg0": ["macro", 37],
                "arg1": "\/my\/orders\/futures\/adjusthistory"
            }, {
                "function": "_cn",
                "arg0": ["macro", 37],
                "arg1": "\/my\/orders\/futures\/liquidationhistory"
            }, {
                "function": "_cn",
                "arg0": ["macro", 37],
                "arg1": "\/my\/orders\/futures\/interesthistory"
            }, {
                "function": "_cn",
                "arg0": ["macro", 37],
                "arg1": "\/my\/wallet\/exchange\/buysell-history"
            }, {
                "function": "_cn",
                "arg0": ["macro", 37],
                "arg1": "\/my\/saving\/history\/"
            }, {
                "function": "_cn",
                "arg0": ["macro", 55],
                "arg1": "\/trade\/"
            }, {
                "function": "_cn",
                "arg0": ["macro", 55],
                "arg1": "layout=basic"
            }, {
                "function": "_cn",
                "arg0": ["macro", 55],
                "arg1": "layout=pro"
            }, {
                "function": "_re",
                "arg0": ["macro", 37],
                "arg1": "^\/[a-z]{2}(-[A-Z]{2})?\/loan(\/.*)?$"
            }, {
                "function": "_re",
                "arg0": ["macro", 37],
                "arg1": "^\/[a-z]{2}(-[A-Z]{2})?\/my\/wallet\/account\/margin(\/.*)?$"
            }, {
                "function": "_re",
                "arg0": ["macro", 37],
                "arg1": "^\/[a-z]{2}(-[A-Z]{2})?\/my\/orders\/margin(\/.*)?$"
            }, {
                "function": "_re",
                "arg0": ["macro", 37],
                "arg1": "^\/[a-z]{2}(-[A-Z]{2})?\/my\/loan(\/.*)?$"
            }, {
                "function": "_cn",
                "arg0": ["macro", 37],
                "arg1": "\/futures\/"
            }, {
                "function": "_cn",
                "arg0": ["macro", 37],
                "arg1": "\/my\/wallet\/account\/futures"
            }, {
                "function": "_cn",
                "arg0": ["macro", 37],
                "arg1": "\/my\/wallet\/futures\/balance\/analysis"
            }, {
                "function": "_cn",
                "arg0": ["macro", 37],
                "arg1": "\/futures\/strategy\/grid"
            }, {
                "function": "_re",
                "arg0": ["macro", 37],
                "arg1": "^\/[a-z]{2}(-[A-Z]{2})?\/markets(\/.*)?$",
                "ignore_case": true
            }, {
                "function": "_cn",
                "arg0": ["macro", 37],
                "arg1": "\/convert"
            }, {
                "function": "_re",
                "arg0": ["macro", 16],
                "arg1": "^binance_register_.*verifiy_view"
            }, {
                "function": "_eq",
                "arg0": ["macro", 3],
                "arg1": "pageview"
            }, {
                "function": "_eq",
                "arg0": ["macro", 1],
                "arg1": "Registration (New)"
            }],
            "rules": [[["if", 0, 1], ["add", 0, 59, 154]], [["if", 2], ["add", 1, 44]], [["if", 3], ["add", 1, 44]], [["if", 4, 5], ["add", 1, 44]], [["if", 6, 7], ["add", 1, 44]], [["if", 6, 8], ["add", 1, 44]], [["if", 6, 9], ["add", 1, 44]], [["if", 10], ["add", 1, 44]], [["if", 11], ["add", 2, 49]], [["if", 12], ["add", 2, 49]], [["if", 13], ["add", 2, 49]], [["if", 14], ["add", 2, 49]], [["if", 15], ["add", 2, 49]], [["if", 16], ["add", 2, 49]], [["if", 17], ["add", 2, 49]], [["if", 18], ["add", 2, 49]], [["if", 19], ["add", 2, 49]], [["if", 20], ["add", 2, 49]], [["if", 21], ["add", 3, 50]], [["if", 22], ["add", 3, 50]], [["if", 5], ["add", 4]], [["if", 11, 23], ["add", 5, 45]], [["if", 11, 24], ["add", 6, 14, 46, 47]], [["if", 13, 25], ["add", 7, 48]], [["if", 26, 27], ["add", 8]], [["if", 27, 28], ["add", 8]], [["if", 27, 29], ["add", 8]], [["if", 27, 30], ["add", 8]], [["if", 27, 31], ["add", 8]], [["if", 27, 32], ["add", 8]], [["if", 27, 33], ["add", 8]], [["if", 27, 34], ["add", 8]], [["if", 35], ["add", 9]], [["if", 36], ["add", 9]], [["if", 37, 38, 39, 40, 41], ["add", 10, 54]], [["if", 39, 40, 42, 43, 44], ["add", 11, 55]], [["if", 45], ["add", 12, 51]], [["if", 6, 46, 47], ["add", 13]], [["if", 47, 48], ["add", 15]], [["if", 49], ["add", 16, 42]], [["if", 50], ["add", 17, 26, 57, 153, 71]], [["if", 51], ["add", 18, 64, 66]], [["if", 52], ["add", 19, 52]], [["if", 53], ["add", 19, 52]], [["if", 54], ["add", 19, 52]], [["if", 55], ["add", 19, 52]], [["if", 56], ["add", 20, 58]], [["if", 57], ["add", 21, 43]], [["if", 58], ["add", 22, 25, 70, 89, 90, 91, 92, 93, 94, 95, 96, 99, 100]], [["if", 59], ["add", 23]], [["if", 60, 61], ["add", 24, 27]], [["if", 62], ["add", 26, 71, 153]], [["if", 63, 64], ["add", 28, 53]], [["if", 63, 65], ["add", 28, 53]], [["if", 63, 66], ["add", 28, 53]], [["if", 63, 67], ["add", 28, 53]], [["if", 63, 68], ["add", 28, 53]], [["if", 64, 69, 70], ["add", 29]], [["if", 65, 70, 71], ["add", 29]], [["if", 66, 70, 72], ["add", 29]], [["if", 64, 69, 73], ["add", 30, 56]], [["if", 67, 74, 75], ["add", 31]], [["if", 67, 75, 76], ["add", 32]], [["if", 66, 72, 73], ["add", 33, 56]], [["if", 67, 75, 77], ["add", 34]], [["if", 67, 75, 78], ["add", 35]], [["if", 67, 75, 79], ["add", 36]], [["if", 68, 80, 81], ["add", 37]], [["if", 68, 81, 82], ["add", 38]], [["if", 68, 83, 84], ["add", 39]], [["if", 67, 75, 85], ["add", 40]], [["if", 67, 75, 86], ["add", 41]], [["if", 65, 73, 87], ["add", 56]], [["if", 88], ["add", 60, 61]], [["if", 89], ["add", 60, 61]], [["if", 90], ["add", 60, 61]], [["if", 91], ["add", 60, 61]], [["if", 92], ["add", 60, 61]], [["if", 93], ["add", 60, 61]], [["if", 67], ["unless", 63], ["add", 60, 61]], [["if", 94], ["add", 60, 61]], [["if", 95], ["add", 60, 61]], [["if", 67, 96, 97], ["add", 62]], [["if", 94, 96, 98], ["add", 63]], [["if", 51, 99], ["add", 65]], [["if", 94, 100], ["add", 67]], [["if", 67, 101], ["add", 68]], [["if", 94, 102], ["add", 69]], [["if", 103, 104], ["add", 72, 73]], [["if", 105, 106], ["add", 74, 75]], [["if", 105, 107], ["add", 76, 78]], [["if", 105, 108], ["add", 77, 79]], [["if", 109], ["add", 80]], [["if", 49, 110], ["add", 81, 82]], [["if", 111], ["add", 83]], [["if", 110, 111], ["add", 84]], [["if", 112], ["add", 85, 86]], [["if", 113], ["add", 85, 86]], [["if", 114], ["add", 85, 86]], [["if", 115], ["add", 85, 86]], [["if", 116], ["add", 85, 86]], [["if", 61], ["add", 87, 150]], [["if", 117, 118], ["add", 88]], [["if", 118], ["add", 97, 98]], [["if", 39, 47], ["add", 101, 106, 107]], [["if", 47, 119, 120], ["add", 102]], [["if", 47, 120, 121], ["add", 103, 154]], [["if", 47, 120, 122], ["add", 104, 154]], [["if", 39, 47, 123], ["add", 105]], [["if", 27, 124], ["add", 108]], [["if", 27, 125], ["add", 109]], [["if", 27, 126], ["add", 109]], [["if", 27, 127], ["add", 109]], [["if", 27, 128], ["add", 109]], [["if", 27, 129], ["add", 109]], [["if", 39, 47, 130], ["add", 110]], [["if", 39, 47, 131], ["add", 111]], [["if", 39, 47, 132], ["add", 112]], [["if", 39, 47, 133], ["add", 113]], [["if", 39, 47, 134], ["add", 114]], [["if", 39, 47, 135], ["add", 115]], [["if", 39, 47, 136], ["add", 116]], [["if", 6, 47, 137], ["add", 117]], [["if", 39, 47, 138], ["add", 118]], [["if", 39, 47, 139], ["add", 119]], [["if", 39, 47, 140], ["add", 120]], [["if", 39, 42, 43, 47], ["add", 121]], [["if", 39, 47, 141], ["add", 122]], [["if", 39, 47, 142], ["add", 123]], [["if", 39, 47, 143], ["add", 124]], [["if", 39, 47, 144], ["add", 125]], [["if", 6, 145], ["add", 126]], [["if", 38, 39, 47, 146], ["add", 127]], [["if", 47, 147], ["add", 128]], [["if", 47, 148, 149], ["add", 129]], [["if", 47, 150, 151], ["add", 130]], [["if", 47, 151, 152], ["add", 131]], [["if", 47, 151, 153], ["add", 132]], [["if", 47, 151, 154], ["add", 133]], [["if", 47, 151, 155], ["add", 134]], [["if", 47, 151, 156], ["add", 135]], [["if", 47, 151, 157], ["add", 136]], [["if", 47, 151, 158], ["add", 137]], [["if", 47, 151, 159], ["add", 138]], [["if", 58, 151, 160], ["add", 139]], [["if", 47, 151, 161], ["add", 140]], [["if", 6, 47, 162, 163], ["add", 141]], [["if", 6, 47, 162, 164], ["add", 141]], [["if", 27, 165], ["add", 142]], [["if", 27, 166], ["add", 143]], [["if", 27, 167], ["add", 144]], [["if", 27, 168], ["add", 145]], [["if", 47, 169], ["add", 146]], [["if", 47, 170], ["add", 147]], [["if", 47, 171], ["add", 148]], [["if", 47, 172], ["add", 149]], [["if", 27, 173], ["add", 151]], [["if", 47, 174], ["add", 152]], [["if", 175, 176, 177], ["add", 154]]]
        },
        "runtime": [[50, "__cvt_32196322_349", [46, "a"], [52, "b", [13, [41, "$0"], [3, "$0", ["require", "createQueue"]], ["$0", "dataLayer"]]], [52, "c", ["require", "gtagSet"]], [52, "d", ["require", "logToConsole"]], [52, "e", ["require", "makeNumber"]], [52, "f", ["require", "makeTableMap"]], [52, "g", ["require", "setDefaultConsentState"]], [52, "h", ["require", "updateConsentState"]], [52, "i", [39, [20, [17, [15, "a"], "command"], "default"], [15, "g"], [15, "h"]]], [52, "j", [8, "ad_storage", [17, [15, "a"], "ad_storage"], "analytics_storage", [17, [15, "a"], "analytics_storage"], "ad_user_data", [17, [15, "a"], "ad_user_data"], "ad_personalization", [17, [15, "a"], "ad_personalization"], "personalization_storage", [17, [15, "a"], "personalization_storage"], "functionality_storage", [17, [15, "a"], "functionality_storage"], "security_storage", [17, [15, "a"], "security_storage"]]], [22, [1, [20, [17, [15, "a"], "command"], "default"], [18, ["e", [17, [15, "a"], "wait_for_update"]], 0]], [46, [43, [15, "j"], "wait_for_update", ["e", [17, [15, "a"], "wait_for_update"]]]]], [22, [1, [20, [17, [15, "a"], "command"], "default"], [21, [17, [15, "a"], "regions"], "all"]], [46, [43, [15, "j"], "region", [2, [2, [17, [15, "a"], "regions"], "split", [7, ","]], "map", [7, [51, "", [7, "k"], [36, [2, [15, "k"], "trim", [7]]]]]]]]], ["c", [8, "url_passthrough", [30, [17, [15, "a"], "url_passthrough"], false], "ads_data_redaction", [30, [17, [15, "a"], "ads_data_redaction"], false]]], ["i", [15, "j"]], [22, [17, [15, "a"], "sendDataLayer"], [46, [43, [15, "j"], "event", [0, "gtm_consent_", [17, [15, "a"], "command"]]], ["b", [15, "j"]]]], [2, [15, "a"], "gtmOnSuccess", [7]]], [50, "__cvt_32196322_451", [46, "a"], [52, "b", ["require", "createQueue"]], [52, "c", ["require", "callInWindow"]], [52, "d", ["require", "aliasInWindow"]], [52, "e", ["require", "copyFromWindow"]], [52, "f", ["require", "setInWindow"]], [52, "g", ["require", "injectScript"]], [52, "h", ["require", "makeTableMap"]], [52, "i", ["require", "makeNumber"]], [52, "j", ["require", "getType"]], [52, "k", ["require", "copyFromDataLayer"]], [52, "l", ["require", "Math"]], [52, "m", ["require", "logToConsole"]], [52, "n", [30, ["e", "_fbq_gtm_ids"], [7]]], [52, "o", [17, [15, "a"], "pixelId"]], [52, "p", [7, "AddPaymentInfo", "AddToCart", "AddToWishlist", "CompleteRegistration", "Contact", "CustomizeProduct", "Donate", "FindLocation", "InitiateCheckout", "Lead", "PageView", "Purchase", "Schedule", "Search", "StartTrial", "SubmitApplication", "Subscribe", "ViewContent"]], [52, "q", ["k", "ecommerce", 1]], [52, "r", [51, "", [7, "bg"], ["m", [15, "bg"]], [2, [15, "a"], "gtmOnFailure", [7]]]], [52, "s", [51, "", [7, "bg", "bh"], [55, "bi", [15, "bh"], [46, [22, [2, [15, "bh"], "hasOwnProperty", [7, [15, "bi"]]], [46, [43, [15, "bg"], [15, "bi"], [16, [15, "bh"], [15, "bi"]]]]]]], [36, [15, "bg"]]]], [52, "t", [51, "", [7, "bg"], [36, [8, "id", [17, [15, "bg"], "id"], "quantity", [17, [15, "bg"], "quantity"]]]]], [41, "u", "v", "w"], [22, [17, [15, "a"], "enhancedEcommerce"], [46, [22, [28, [15, "q"]], [46, [36, ["r", "Facebook Pixel: No valid \"ecommerce\" object found in dataLayer"]]]], [22, [17, [15, "q"], "detail"], [46, [3, "u", "ViewContent"], [3, "v", "detail"]], [46, [22, [17, [15, "q"], "add"], [46, [3, "u", "AddToCart"], [3, "v", "add"]], [46, [22, [17, [15, "q"], "checkout"], [46, [3, "u", "InitiateCheckout"], [3, "v", "checkout"]], [46, [22, [17, [15, "q"], "purchase"], [46, [3, "u", "Purchase"], [3, "v", "purchase"]], [46, [36, ["r", "Facebook Pixel: Most recently pushed \"ecommerce\" object must be one of types \"detail\", \"add\", \"checkout\" or \"purchase\"."]]]]]]]]]], [22, [30, [28, [17, [16, [15, "q"], [15, "v"]], "products"]], [21, ["j", [17, [16, [15, "q"], [15, "v"]], "products"]], "array"]], [46, [36, ["r", "Facebook pixel: Most recently pushed \"ecommerce\" object did not have a valid \"products\" array."]]]], [3, "w", [8, "content_type", "product", "contents", [2, [17, [16, [15, "q"], [15, "v"]], "products"], "map", [7, [15, "t"]]], "value", [2, [17, [16, [15, "q"], [15, "v"]], "products"], "reduce", [7, [51, "", [7, "bg", "bh"], [52, "bi", [10, [2, [15, "l"], "round", [7, [26, [26, ["i", [30, [17, [15, "bh"], "price"], 0]], [30, [17, [15, "bh"], "quantity"], 1]], 100]]], 100]], [36, [0, [15, "bg"], [15, "bi"]]]], 0]], "currency", [30, [17, [15, "q"], "currencyCode"], "USD"]]], [22, [18, [2, [7, "InitiateCheckout", "Purchase"], "indexOf", [7, [15, "u"]]], [27, 1]], [46, [43, [15, "w"], "num_items", [2, [17, [16, [15, "q"], [15, "v"]], "products"], "reduce", [7, [51, "", [7, "bg", "bh"], [36, [0, [15, "bg"], ["i", [30, [17, [15, "bh"], "quantity"], 1]]]]], 0]]]]]]], [52, "x", [39, [1, [17, [15, "a"], "advancedMatchingList"], [17, [17, [15, "a"], "advancedMatchingList"], "length"]], ["h", [17, [15, "a"], "advancedMatchingList"], "name", "value"], [8]]], [52, "y", [39, [1, [17, [15, "a"], "objectPropertyList"], [17, [17, [15, "a"], "objectPropertyList"], "length"]], ["h", [17, [15, "a"], "objectPropertyList"], "name", "value"], [8]]], [52, "z", [39, [20, ["j", [17, [15, "a"], "objectPropertiesFromVariable"]], "object"], [17, [15, "a"], "objectPropertiesFromVariable"], [8]]], [52, "ba", ["s", [15, "z"], [15, "y"]]], [52, "bb", ["s", [30, [15, "w"], [8]], [15, "ba"]]], [3, "u", [30, [15, "u"], [39, [20, [17, [15, "a"], "eventName"], "custom"], [17, [15, "a"], "customEventName"], [39, [20, [17, [15, "a"], "eventName"], "variable"], [17, [15, "a"], "variableEventName"], [17, [15, "a"], "standardEventName"]]]]], [52, "bc", [39, [20, [2, [15, "p"], "indexOf", [7, [15, "u"]]], [27, 1]], "trackSingleCustom", "trackSingle"]], [52, "bd", [39, [20, [17, [15, "a"], "consent"], false], "revoke", "grant"]], [52, "be", [51, "", [7], [41, "bg"], [3, "bg", ["e", "fbq"]], [22, [15, "bg"], [46, [36, [15, "bg"]]]], ["f", "fbq", [51, "", [7], [52, "bh", ["e", "fbq.callMethod.apply"]], [22, [15, "bh"], [46, ["c", "fbq.callMethod.apply", [45], [15, "arguments"]]], [46, ["c", "fbq.queue.push", [15, "arguments"]]]]]], ["d", "_fbq", "fbq"], ["b", "fbq.queue"], [36, ["e", "fbq"]]]], [52, "bf", ["be"]], ["bf", "consent", [15, "bd"]], [22, [17, [15, "a"], "dpoLDU"], [46, ["bf", "dataProcessingOptions", [7, "LDU"], ["i", [17, [15, "a"], "dpoCountry"]], ["i", [17, [15, "a"], "dpoState"]]]]], [2, [2, [15, "o"], "split", [7, ","]], "forEach", [7, [51, "", [7, "bg"], [22, [20, [2, [15, "n"], "indexOf", [7, [15, "bg"]]], [27, 1]], [46, [22, [17, [15, "a"], "disableAutoConfig"], [46, ["bf", "set", "autoConfig", false, [15, "bg"]]]], [22, [17, [15, "a"], "disablePushState"], [46, ["f", "fbq.disablePushState", true]]], ["bf", "init", [15, "bg"], [15, "x"]], ["bf", "set", "agent", "tmSimo-GTM-WebTemplate", [15, "bg"]], [2, [15, "n"], "push", [7, [15, "bg"]]], ["f", "_fbq_gtm_ids", [15, "n"], true]]], [22, [17, [15, "a"], "eventId"], [46, ["bf", [15, "bc"], [15, "bg"], [15, "u"], [15, "bb"], [8, "eventID", [17, [15, "a"], "eventId"]]]], [46, ["bf", [15, "bc"], [15, "bg"], [15, "u"], [15, "bb"]]]]]]], ["g", "https://connect.facebook.net/en_US/fbevents.js", [17, [15, "a"], "gtmOnSuccess"], [17, [15, "a"], "gtmOnFailure"], "fbPixel"]], [50, "__cvt_32196322_678", [46, "a"], [52, "b", ["require", "logToConsole"]], [52, "c", ["require", "createQueue"]], [52, "d", ["c", "dataLayer"]], [52, "e", ["require", "sha256"]], [52, "f", ["require", "getType"]], ["b", "data =", [15, "a"]], [22, [1, [20, ["f", [17, [15, "a"], "orderId"]], "string"], [20, ["f", [17, [15, "a"], "label"]], "string"]], [46, [53, [52, "g", [0, [17, [15, "a"], "orderId"], [17, [15, "a"], "label"]]], ["e", [15, "g"], [51, "", [7, "h"], ["d", [8, "event", "dle_ads_purchase", "dlv_shaOid", [15, "h"]]], [2, [15, "a"], "gtmOnSuccess", [7]]], [17, [15, "a"], "gtmOnFailure"], [8, "outputEncoding", "hex"]]]], [46, ["d", [8, "event", "dle_ads_purchase"]], [2, [15, "a"], "gtmOnFailure", [7]]]]], [50, "__cvt_32196322_683", [46, "a"], [52, "b", ["require", "copyFromDataLayer"]], [52, "c", ["b", "ecommerce"]], [36, [17, [16, [17, [17, [15, "c"], "purchase"], "products"], 0], "orderId"]]], [50, "__cvt_32196322_685", [46, "a"], [41, "b"], [52, "c", [17, [15, "a"], "type"]], [52, "d", [17, [15, "a"], "key"]], [22, [12, [15, "c"], "cookie"], [46, [53, [52, "e", ["require", "getCookieValues"]], [52, "f", ["e", "_ga"]], [22, [12, [15, "d"], "clientid"], [46, [3, "b", [39, [18, [17, [15, "f"], "length"], 0], [0, [2, [2, [2, [16, [15, "f"], 0], "split", [7, "."]], "slice", [7, [27, 2]]], "join", [7, "."]], "."], [44]]]], [46, [22, [12, [15, "d"], "clientidUA"], [46, [3, "b", [39, [18, [17, [15, "f"], "length"], 0], [2, [2, [2, [16, [15, "f"], 0], "split", [7, "."]], "slice", [7, [27, 2]]], "join", [7, "."]], [44]]]]]]]]], [46, [22, [12, [15, "c"], "page_load_info"], [46, [53, [52, "e", ["require", "copyFromDataLayer"]], [52, "f", ["require", "getType"]], [52, "g", ["e", "page_load_info"]], [52, "h", ["require", "makeString"]], [52, "i", [51, "", [7, "j"], [3, "j", ["h", [15, "j"]]], [36, [39, [30, [30, [20, [15, "j"], ""], [20, [15, "j"], "null"]], [20, [15, "j"], "undefined"]], [44], [15, "j"]]]]], [22, [12, ["f", [15, "g"]], "object"], [46, [38, [15, "d"], [46, "bncuuid", "userid", "author", "pagename", "pageName", "topic"], [46, [5, [46, [3, "b", ["i", [30, [17, [15, "g"], "bncuuid"], [17, [15, "g"], "bncUUID"]]]], [4]]], [5, [46, [3, "b", ["i", [30, [17, [15, "g"], "userid"], [17, [15, "g"], "userId"]]]], [4]]], [5, [46, [3, "b", [17, [15, "g"], "author"]], [4]]], [5, [46, [3, "b", [17, [15, "g"], "pagename"]], [4]]], [5, [46, [3, "b", [17, [15, "g"], "pageName"]], [4]]], [5, [46, [3, "b", [17, [15, "g"], "topic"]], [4]]], [9, [46, [3, "b", [44]]]]]]]]]]]]], [36, [15, "b"]]], [50, "__cvt_32196322_701", [46, "a"], [41, "d", "e", "f", "g", "h"], [52, "b", ["require", "getCookieValues"]], [52, "c", ["b", "OptanonConsent"]], [22, [18, [17, [15, "c"], "length"], 0], [46, [3, "e", [17, [15, "a"], "key"]], [3, "f", [16, [15, "c"], 0]], [3, "g", [29, [2, [15, "f"], "indexOf", [7, "C0002:1"]], [27, 1]]], [3, "h", [29, [2, [15, "f"], "indexOf", [7, "C0004:1"]], [27, 1]]], [22, [30, [12, [15, "e"], "analytics_storage"], [12, [15, "e"], "ad_storage"]], [46, [3, "d", [1, [15, "g"], [15, "h"]]]], [46, [22, [30, [30, [12, [15, "e"], "ad_user_data"], [12, [15, "e"], "ad_personalization"]], [12, [15, "e"], "personalization_storage"]], [46, [3, "d", [15, "h"]]]]]]]], [36, [39, [15, "d"], "granted", "denied"]]], [50, "__baut", [46, "a"], [52, "b", ["require", "injectScript"]], [52, "c", ["require", "callInWindow"]], [52, "d", ["require", "makeTableMap"]], [38, [17, [15, "a"], "eventType"], [46, "PAGE_LOAD", "VARIABLE_REVENUE", "CUSTOM"], [46, [5, [46, [43, [15, "a"], "eventType", "pageView"], [4]]], [5, [46, [43, [15, "a"], "eventType", "variableRevenue"], [4]]], [5, [46, [43, [15, "a"], "eventType", "custom"]]]]], [22, [17, [15, "a"], "eventCategory"], [46, [43, [15, "a"], "p_event_category", [17, [15, "a"], "eventCategory"]]]], [22, [17, [15, "a"], "eventLabel"], [46, [43, [15, "a"], "p_event_label", [17, [15, "a"], "eventLabel"]]]], [22, [17, [15, "a"], "eventValue"], [46, [43, [15, "a"], "p_event_value", [17, [15, "a"], "eventValue"]]]], [22, [17, [15, "a"], "goalValue"], [46, [43, [15, "a"], "p_revenue_value", [17, [15, "a"], "goalValue"]]]], [52, "e", [51, "", [7], [52, "i", [39, [30, [20, [17, [15, "a"], "eventType"], "pageView"], [28, [17, [15, "a"], "customParamTable"]]], [8], ["d", [17, [15, "a"], "customParamTable"], "customParamName", "customParamValue"]]], [52, "j", [8, "pageViewSpa", [7, "page_path", "page_title"], "variableRevenue", [7, "currency", "revenue_value"], "custom", [7, "event_category", "event_label", "event_value", "currency", "revenue_value"], "ecommerce", [7, "ecomm_prodid", "ecomm_pagetype", "ecomm_totalvalue", "ecomm_category"], "hotel", [7, "currency", "hct_base_price", "hct_booking_xref", "hct_checkin_date", "hct_checkout_date", "hct_length_of_stay", "hct_partner_hotel_id", "hct_total_price", "hct_pagetype"], "travel", [7, "travel_destid", "travel_originid", "travel_pagetype", "travel_startdate", "travel_enddate", "travel_totalvalue"], "enhancedConversion", [7, "em", "ph"]]], [65, "k", [30, [16, [15, "j"], [17, [15, "a"], "eventType"]], [7]], [46, [43, [15, "i"], [15, "k"], [30, [16, [15, "i"], [15, "k"]], [16, [15, "a"], [0, "p_", [15, "k"]]]]]]], [43, [15, "i"], "tpp", "1"], [36, [15, "i"]]]], [52, "f", [51, "", [7], [52, "i", [39, [28, [17, [15, "a"], "customConfigTable"]], [8], ["d", [17, [15, "a"], "customConfigTable"], "customConfigName", "customConfigValue"]]], [54, "k", [15, "i"], [46, [22, [20, [16, [15, "i"], [15, "k"]], "true"], [46, [43, [15, "i"], [15, "k"], true]], [46, [22, [20, [16, [15, "i"], [15, "k"]], "false"], [46, [43, [15, "i"], [15, "k"], false]]]]]]], [52, "j", [7, "navTimingApi", "enableAutoSpaTracking", "storeConvTrackCookies", "removeQueryFromUrls", "disableAutoPageView"]], [65, "k", [15, "j"], [46, [43, [15, "i"], [15, "k"], [30, [16, [15, "i"], [15, "k"]], [16, [15, "a"], [0, "c_", [15, "k"]]]]]]], [22, [20, [17, [15, "a"], "c_enhancedConversion"], true], [46, [43, [15, "i"], "pagePid", [8, "em", [17, [15, "a"], "p_em"], "ph", [17, [15, "a"], "p_ph"]]]]], [43, [15, "i"], "ti", [17, [15, "a"], "tagId"]], [43, [15, "i"], "tm", "gtm002"], [36, [15, "i"]]]], [52, "g", [51, "", [7], [22, [20, [17, [15, "a"], "eventType"], "pageView"], [46, [53, [52, "i", ["f"]], ["c", "UET_init", [17, [15, "a"], "uetqName"], [15, "i"]], ["c", "UET_push", [17, [15, "a"], "uetqName"], "pageLoad"]]], [46, [53, [52, "i", ["e"]], [22, [20, [17, [15, "a"], "eventType"], "pageViewSpa"], [46, ["c", "UET_push", [17, [15, "a"], "uetqName"], "event", "page_view", [15, "i"]]], [46, [22, [20, [17, [15, "a"], "eventType"], "enhancedConversion"], [46, ["c", "UET_push", [17, [15, "a"], "uetqName"], "set", [8, "pid", [15, "i"]]]], [46, [53, [52, "j", [30, [30, [17, [15, "a"], "customEventAction"], [17, [15, "a"], "eventAction"]], ""]], ["c", "UET_push", [17, [15, "a"], "uetqName"], "event", [15, "j"], [15, "i"]]]]]]]]]], [2, [15, "a"], "gtmOnSuccess", [7]]]], [52, "h", "https://bat.bing.com/bat.js"], ["b", [15, "h"], [15, "g"], [17, [15, "a"], "gtmOnFailure"], [15, "h"]]], [50, "__cid", [46, "a"], [36, [17, [13, [41, "$0"], [3, "$0", ["require", "getContainerVersion"]], ["$0"]], "containerId"]]], [50, "__e", [46, "a"], [36, [13, [41, "$0"], [3, "$0", ["require", "internal.getEventData"]], ["$0", "event"]]]], [50, "__googtag", [46, "a"], [50, "l", [46, "u", "v"], [66, "w", [2, [15, "b"], "keys", [7, [15, "v"]]], [46, [43, [15, "u"], [15, "w"], [16, [15, "v"], [15, "w"]]]]]], [50, "m", [46], [36, [7, [17, [17, [15, "d"], "SCHEMA"], "EP_SERVER_CONTAINER_URL"], [17, [17, [15, "d"], "SCHEMA"], "EP_TRANSPORT_URL"]]]], [50, "n", [46, "u"], [52, "v", ["m"]], [65, "w", [15, "v"], [46, [53, [52, "x", [16, [15, "u"], [15, "w"]]], [22, [15, "x"], [46, [36, [15, "x"]]]]]]], [36, [44]]], [52, "b", ["require", "Object"]], [52, "c", ["require", "createArgumentsQueue"]], [52, "d", [15, "__module_gtag"]], [52, "e", ["require", "internal.gtagConfig"]], [52, "f", ["require", "getType"]], [52, "g", ["require", "internal.loadGoogleTag"]], [52, "h", ["require", "logToConsole"]], [52, "i", ["require", "makeNumber"]], [52, "j", ["require", "makeString"]], [52, "k", ["require", "makeTableMap"]], [52, "o", [30, [17, [15, "a"], "tagId"], ""]], [22, [30, [21, ["f", [15, "o"]], "string"], [24, [2, [15, "o"], "indexOf", [7, "-"]], 0]], [46, ["h", [0, "Invalid Measurement ID for the GA4 Configuration tag: ", [15, "o"]]], [2, [15, "a"], "gtmOnFailure", [7]], [36]]], [52, "p", [30, [17, [15, "a"], "configSettingsVariable"], [8]]], [52, "q", [30, ["k", [30, [17, [15, "a"], "configSettingsTable"], [7]], "parameter", "parameterValue"], [8]]], ["l", [15, "p"], [15, "q"]], [52, "r", [30, [17, [15, "a"], "eventSettingsVariable"], [8]]], [52, "s", [30, ["k", [30, [17, [15, "a"], "eventSettingsTable"], [7]], "parameter", "parameterValue"], [8]]], ["l", [15, "r"], [15, "s"]], [52, "t", [15, "p"]], ["l", [15, "t"], [15, "r"]], [22, [30, [2, [15, "t"], "hasOwnProperty", [7, [17, [17, [15, "d"], "SCHEMA"], "EP_USER_PROPERTIES"]]], [17, [15, "a"], "userProperties"]], [46, [53, [52, "u", [30, [16, [15, "t"], [17, [17, [15, "d"], "SCHEMA"], "EP_USER_PROPERTIES"]], [8]]], ["l", [15, "u"], [30, ["k", [30, [17, [15, "a"], "userProperties"], [7]], "name", "value"], [8]]], [43, [15, "t"], [17, [17, [15, "d"], "SCHEMA"], "EP_USER_PROPERTIES"], [15, "u"]]]]], [2, [15, "d"], "convertParameters", [7, [15, "t"], [17, [15, "d"], "GOLD_BOOLEAN_FIELDS"], [51, "", [7, "u"], [36, [39, [20, "false", [2, ["j", [15, "u"]], "toLowerCase", [7]]], false, [28, [28, [15, "u"]]]]]]]], [2, [15, "d"], "convertParameters", [7, [15, "t"], [17, [15, "d"], "GOLD_NUMERIC_FIELDS"], [51, "", [7, "u"], [36, ["i", [15, "u"]]]]]], ["g", [15, "o"], [8, "firstPartyUrl", ["n", [15, "t"]]]], ["e", [15, "o"], [15, "t"], [8, "noTargetGroup", true]], [2, [15, "a"], "gtmOnSuccess", [7]]], [50, "__paused", [46, "a"], [2, [15, "a"], "gtmOnFailure", [7]]], [52, "__module_gtag", [13, [41, "$0"], [3, "$0", [51, "", [7], [50, "a", [46], [50, "f", [46, "g", "h", "i"], [65, "j", [15, "h"], [46, [22, [2, [15, "g"], "hasOwnProperty", [7, [15, "j"]]], [46, [43, [15, "g"], [15, "j"], ["i", [16, [15, "g"], [15, "j"]]]]]]]]], [52, "b", ["require", "Object"]], [52, "c", [2, [15, "b"], "freeze", [7, [8, "EP_FIRST_PARTY_COLLECTION", "first_party_collection", "EP_SERVER_CONTAINER_URL", "server_container_url", "EP_TRANSPORT_URL", "transport_url", "EP_USER_PROPERTIES", "user_properties"]]]], [52, "d", [2, [15, "b"], "freeze", [7, [7, "allow_ad_personalization_signals", "allow_google_signals", "cookie_update", "ignore_referrer", "update", "first_party_collection", "send_page_view"]]]], [52, "e", [2, [15, "b"], "freeze", [7, [7, "cookie_expires", "event_timeout", "session_duration", "session_engaged_time", "engagement_time_msec"]]]], [36, [8, "SCHEMA", [15, "c"], "GOLD_BOOLEAN_FIELDS", [15, "d"], "GOLD_NUMERIC_FIELDS", [15, "e"], "convertParameters", [15, "f"]]]], [36, ["a"]]]], ["$0"]]]
        ],
        "entities": {
            "__cid": {
                "2": true,
                "4": true,
                "3": true
            },
            "__e": {
                "2": true,
                "4": true
            },
            "__googtag": {
                "1": 10
            }

        },
        "blob": {
            "1": "81"
        },
        "permissions": {
            "__cvt_32196322_349": {
                "logging": {
                    "environments": "debug"
                },
                "access_globals": {
                    "keys": [{
                        "key": "dataLayer",
                        "read": true,
                        "write": true,
                        "execute": false
                    }]
                },
                "access_consent": {
                    "consentTypes": [{
                        "consentType": "ad_storage",
                        "read": true,
                        "write": true
                    }, {
                        "consentType": "analytics_storage",
                        "read": true,
                        "write": true
                    }, {
                        "consentType": "personalization_storage",
                        "read": true,
                        "write": true
                    }, {
                        "consentType": "functionality_storage",
                        "read": true,
                        "write": true
                    }, {
                        "consentType": "security_storage",
                        "read": true,
                        "write": true
                    }, {
                        "consentType": "ad_user_data",
                        "read": true,
                        "write": true
                    }, {
                        "consentType": "ad_personalization",
                        "read": true,
                        "write": true
                    }]
                },
                "write_data_layer": {
                    "keyPatterns": ["url_passthrough", "ads_data_redaction"]
                }
            },
            "__cvt_32196322_451": {
                "access_globals": {
                    "keys": [{
                        "key": "fbq",
                        "read": true,
                        "write": true,
                        "execute": false
                    }, {
                        "key": "_fbq_gtm",
                        "read": true,
                        "write": true,
                        "execute": false
                    }, {
                        "key": "_fbq",
                        "read": false,
                        "write": true,
                        "execute": false
                    }, {
                        "key": "_fbq_gtm_ids",
                        "read": true,
                        "write": true,
                        "execute": false
                    }, {
                        "key": "fbq.callMethod.apply",
                        "read": true,
                        "write": false,
                        "execute": true
                    }, {
                        "key": "fbq.queue.push",
                        "read": false,
                        "write": false,
                        "execute": true
                    }, {
                        "key": "fbq.queue",
                        "read": true,
                        "write": true,
                        "execute": false
                    }, {
                        "key": "fbq.disablePushState",
                        "read": true,
                        "write": true,
                        "execute": false
                    }]
                },
                "inject_script": {
                    "urls": ["https:\/\/connect.facebook.net\/en_US\/fbevents.js"]
                },
                "logging": {
                    "environments": "debug"
                },
                "read_data_layer": {
                    "keyPatterns": ["ecommerce"]
                }
            },
            "__cvt_32196322_678": {
                "access_globals": {
                    "keys": [{
                        "key": "dataLayer",
                        "read": true,
                        "write": true,
                        "execute": false
                    }]
                },
                "logging": {
                    "environments": "debug"
                }
            },
            "__cvt_32196322_683": {
                "read_data_layer": {
                    "allowedKeys": "specific",
                    "keyPatterns": ["ecommerce"]
                }
            },
            "__cvt_32196322_685": {
                "read_data_layer": {
                    "allowedKeys": "specific",
                    "keyPatterns": ["page_load_info"]
                },
                "get_cookies": {
                    "cookieAccess": "specific",
                    "cookieNames": ["_ga"]
                }
            },
            "__cvt_32196322_701": {
                "get_cookies": {
                    "cookieAccess": "specific",
                    "cookieNames": ["OptanonConsent"]
                }
            },
            "__baut": {
                "inject_script": {
                    "urls": ["https:\/\/bat.bing.com\/bat.js"]
                },
                "access_globals": {
                    "keys": [{
                        "key": "UET_push",
                        "read": false,
                        "write": false,
                        "execute": true
                    }, {
                        "key": "UET_init",
                        "read": false,
                        "write": false,
                        "execute": true
                    }]
                }
            },
            "__cid": {
                "read_container_data": {}
            },
            "__e": {
                "read_event_data": {
                    "eventDataAccess": "specific",
                    "keyPatterns": ["event"]
                }
            },
            "__googtag": {
                "logging": {
                    "environments": "debug"
                },
                "access_globals": {
                    "keys": [{
                        "key": "gtag",
                        "read": true,
                        "write": true,
                        "execute": true
                    }, {
                        "key": "dataLayer",
                        "read": true,
                        "write": true,
                        "execute": false
                    }]
                },
                "configure_google_tags": {
                    "allowedTagIds": "any"
                },
                "load_google_tags": {
                    "allowedTagIds": "any",
                    "allowFirstPartyUrls": true,
                    "allowedFirstPartyUrls": "any"
                }
            },
            "__paused": {}

        }
        ,
        "sandboxed_scripts": ["__cvt_32196322_349", "__cvt_32196322_451", "__cvt_32196322_678", "__cvt_32196322_683", "__cvt_32196322_685", "__cvt_32196322_701"
        ]
        ,
        "security_groups": {
            "google": ["__cid", "__e", "__googtag"
            ],
            "nonGoogleScripts": ["__baut"
            ]

        }

    };

    try {
        (function() {
            /*

 Copyright The Closure Library Authors.
 SPDX-License-Identifier: Apache-2.0
*/
            var C = this || self
              , D = function(n, v) {
                var w = n.split(".")
                  , q = C;
                w[0]in q || "undefined" == typeof q.execScript || q.execScript("var " + w[0]);
                for (var t; w.length && (t = w.shift()); )
                    w.length || void 0 === v ? q = q[t] && q[t] !== Object.prototype[t] ? q[t] : q[t] = {} : q[t] = v
            };
            /*
 Copyright (c) 2014 Derek Brans, MIT license https://github.com/krux/postscribe/blob/master/LICENSE. Portions derived from simplehtmlparser, which is licensed under the Apache License, Version 2.0 */
            var E, F = function() {};
            (function() {
                function n(h, m) {
                    h = h || "";
                    m = m || {};
                    for (var y in v)
                        v.hasOwnProperty(y) && (m.N && (m["fix_" + y] = !0),
                        m.G = m.G || m["fix_" + y]);
                    var z = {
                        comment: /^\x3c!--/,
                        endTag: /^<\//,
                        atomicTag: /^<\s*(script|style|noscript|iframe|textarea)[\s\/>]/i,
                        startTag: /^</,
                        chars: /^[^<]/
                    }
                      , e = {
                        comment: function() {
                            var a = h.indexOf("--\x3e");
                            if (0 <= a)
                                return {
                                    content: h.substr(4, a),
                                    length: a + 3
                                }
                        },
                        endTag: function() {
                            var a = h.match(q);
                            if (a)
                                return {
                                    tagName: a[1],
                                    length: a[0].length
                                }
                        },
                        atomicTag: function() {
                            var a = e.startTag();
                            if (a) {
                                var b = h.slice(a.length);
                                if (b.match(new RegExp("</\\s*" + a.tagName + "\\s*>","i"))) {
                                    var c = b.match(new RegExp("([\\s\\S]*?)</\\s*" + a.tagName + "\\s*>","i"));
                                    if (c)
                                        return {
                                            tagName: a.tagName,
                                            g: a.g,
                                            content: c[1],
                                            length: c[0].length + a.length
                                        }
                                }
                            }
                        },
                        startTag: function() {
                            var a = h.match(w);
                            if (a) {
                                var b = {};
                                a[2].replace(t, function(c, d, k, g, r) {
                                    var u = k || g || r || B.test(d) && d || null
                                      , l = document.createElement("div");
                                    l.innerHTML = u;
                                    b[d] = l.textContent || l.innerText || u
                                });
                                return {
                                    tagName: a[1],
                                    g: b,
                                    s: !!a[3],
                                    length: a[0].length
                                }
                            }
                        },
                        chars: function() {
                            var a = h.indexOf("<");
                            return {
                                length: 0 <= a ? a : h.length
                            }
                        }
                    }
                      , f = function() {
                        for (var a in z)
                            if (z[a].test(h)) {
                                var b = e[a]();
                                return b ? (b.type = b.type || a,
                                b.text = h.substr(0, b.length),
                                h = h.slice(b.length),
                                b) : null
                            }
                    };
                    m.G && function() {
                        var a = /^(AREA|BASE|BASEFONT|BR|COL|FRAME|HR|IMG|INPUT|ISINDEX|LINK|META|PARAM|EMBED)$/i
                          , b = /^(COLGROUP|DD|DT|LI|OPTIONS|P|TD|TFOOT|TH|THEAD|TR)$/i
                          , c = [];
                        c.H = function() {
                            return this[this.length - 1]
                        }
                        ;
                        c.v = function(l) {
                            var p = this.H();
                            return p && p.tagName && p.tagName.toUpperCase() === l.toUpperCase()
                        }
                        ;
                        c.V = function(l) {
                            for (var p = 0, x; x = this[p]; p++)
                                if (x.tagName === l)
                                    return !0;
                            return !1
                        }
                        ;
                        var d = function(l) {
                            l && "startTag" === l.type && (l.s = a.test(l.tagName) || l.s);
                            return l
                        }
                          , k = f
                          , g = function() {
                            h = "</" + c.pop().tagName + ">" + h
                        }
                          , r = {
                            startTag: function(l) {
                                var p = l.tagName;
                                "TR" === p.toUpperCase() && c.v("TABLE") ? (h = "<TBODY>" + h,
                                u()) : m.oa && b.test(p) && c.V(p) ? c.v(p) ? g() : (h = "</" + l.tagName + ">" + h,
                                u()) : l.s || c.push(l)
                            },
                            endTag: function(l) {
                                c.H() ? m.W && !c.v(l.tagName) ? g() : c.pop() : m.W && (k(),
                                u())
                            }
                        }
                          , u = function() {
                            var l = h
                              , p = d(k());
                            h = l;
                            if (p && r[p.type])
                                r[p.type](p)
                        };
                        f = function() {
                            u();
                            return d(k())
                        }
                    }();
                    return {
                        append: function(a) {
                            h += a
                        },
                        ea: f,
                        sa: function(a) {
                            for (var b; (b = f()) && (!a[b.type] || !1 !== a[b.type](b)); )
                                ;
                        },
                        clear: function() {
                            var a = h;
                            h = "";
                            return a
                        },
                        ta: function() {
                            return h
                        },
                        stack: []
                    }
                }
                var v = function() {
                    var h = {}
                      , m = this.document.createElement("div");
                    m.innerHTML = "<P><I></P></I>";
                    h.va = "<P><I></P></I>" !== m.innerHTML;
                    m.innerHTML = "<P><i><P></P></i></P>";
                    h.ua = 2 === m.childNodes.length;
                    return h
                }()
                  , w = /^<([\-A-Za-z0-9_]+)((?:\s+[\w\-]+(?:\s*=?\s*(?:(?:"[^"]*")|(?:'[^']*')|[^>\s]+))?)*)\s*(\/?)>/
                  , q = /^<\/([\-A-Za-z0-9_]+)[^>]*>/
                  , t = /([\-A-Za-z0-9_]+)(?:\s*=\s*(?:(?:"((?:\\.|[^"])*)")|(?:'((?:\\.|[^'])*)')|([^>\s]+)))?/g
                  , B = /^(checked|compact|declare|defer|disabled|ismap|multiple|nohref|noresize|noshade|nowrap|readonly|selected)$/i;
                n.supports = v;
                for (var A in v)
                    ;
                E = n
            }
            )();
            (function() {
                function n() {}
                function v(e) {
                    return void 0 !== e && null !== e
                }
                function w(e, f, a) {
                    var b, c = e && e.length || 0;
                    for (b = 0; b < c; b++)
                        f.call(a, e[b], b)
                }
                function q(e, f, a) {
                    for (var b in e)
                        e.hasOwnProperty(b) && f.call(a, b, e[b])
                }
                function t(e, f) {
                    q(f, function(a, b) {
                        e[a] = b
                    });
                    return e
                }
                function B(e, f) {
                    e = e || {};
                    q(f, function(a, b) {
                        v(e[a]) || (e[a] = b)
                    });
                    return e
                }
                function A(e) {
                    try {
                        return y.call(e)
                    } catch (a) {
                        var f = [];
                        w(e, function(b) {
                            f.push(b)
                        });
                        return f
                    }
                }
                var h = {
                    J: n,
                    K: n,
                    L: n,
                    M: n,
                    O: n,
                    P: function(e) {
                        return e
                    },
                    done: n,
                    error: function(e) {
                        throw e;
                    },
                    fa: !1
                }
                  , m = this;
                if (!m.postscribe) {
                    var y = Array.prototype.slice
                      , z = function() {
                        function e(a, b, c) {
                            var d = "data-ps-" + b;
                            if (2 === arguments.length) {
                                var k = a.getAttribute(d);
                                return v(k) ? String(k) : k
                            }
                            v(c) && "" !== c ? a.setAttribute(d, c) : a.removeAttribute(d)
                        }
                        function f(a, b) {
                            var c = a.ownerDocument;
                            t(this, {
                                root: a,
                                options: b,
                                l: c.defaultView || c.parentWindow,
                                i: c,
                                o: E("", {
                                    N: !0
                                }),
                                u: [a],
                                B: "",
                                C: c.createElement(a.nodeName),
                                j: [],
                                h: []
                            });
                            e(this.C, "proxyof", 0)
                        }
                        f.prototype.write = function() {
                            [].push.apply(this.h, arguments);
                            for (var a; !this.m && this.h.length; )
                                a = this.h.shift(),
                                "function" === typeof a ? this.U(a) : this.D(a)
                        }
                        ;
                        f.prototype.U = function(a) {
                            var b = {
                                type: "function",
                                value: a.name || a.toString()
                            };
                            this.A(b);
                            a.call(this.l, this.i);
                            this.I(b)
                        }
                        ;
                        f.prototype.D = function(a) {
                            this.o.append(a);
                            for (var b, c = [], d, k; (b = this.o.ea()) && !(d = b && "tagName"in b ? !!~b.tagName.toLowerCase().indexOf("script") : !1) && !(k = b && "tagName"in b ? !!~b.tagName.toLowerCase().indexOf("style") : !1); )
                                c.push(b);
                            this.ka(c);
                            d && this.X(b);
                            k && this.Y(b)
                        }
                        ;
                        f.prototype.ka = function(a) {
                            var b = this.R(a);
                            b.F && (b.Z = this.B + b.F,
                            this.B += b.proxy,
                            this.C.innerHTML = b.Z,
                            this.ia())
                        }
                        ;
                        f.prototype.R = function(a) {
                            var b = this.u.length
                              , c = []
                              , d = []
                              , k = [];
                            w(a, function(g) {
                                c.push(g.text);
                                if (g.g) {
                                    if (!/^noscript$/i.test(g.tagName)) {
                                        var r = b++;
                                        d.push(g.text.replace(/(\/?>)/, " data-ps-id=" + r + " $1"));
                                        "ps-script" !== g.g.id && "ps-style" !== g.g.id && k.push("atomicTag" === g.type ? "" : "<" + g.tagName + " data-ps-proxyof=" + r + (g.s ? " />" : ">"))
                                    }
                                } else
                                    d.push(g.text),
                                    k.push("endTag" === g.type ? g.text : "")
                            });
                            return {
                                wa: a,
                                raw: c.join(""),
                                F: d.join(""),
                                proxy: k.join("")
                            }
                        }
                        ;
                        f.prototype.ia = function() {
                            for (var a, b = [this.C]; v(a = b.shift()); ) {
                                var c = 1 === a.nodeType;
                                if (!c || !e(a, "proxyof")) {
                                    c && (this.u[e(a, "id")] = a,
                                    e(a, "id", null));
                                    var d = a.parentNode && e(a.parentNode, "proxyof");
                                    d && this.u[d].appendChild(a)
                                }
                                b.unshift.apply(b, A(a.childNodes))
                            }
                        }
                        ;
                        f.prototype.X = function(a) {
                            var b = this.o.clear();
                            b && this.h.unshift(b);
                            a.src = a.g.src || a.g.ma;
                            a.src && this.j.length ? this.m = a : this.A(a);
                            var c = this;
                            this.ja(a, function() {
                                c.I(a)
                            })
                        }
                        ;
                        f.prototype.Y = function(a) {
                            var b = this.o.clear();
                            b && this.h.unshift(b);
                            a.type = a.g.type || a.g.TYPE || "text/css";
                            this.la(a);
                            b && this.write()
                        }
                        ;
                        f.prototype.la = function(a) {
                            var b = this.T(a);
                            this.ba(b);
                            a.content && (b.styleSheet && !b.sheet ? b.styleSheet.cssText = a.content : b.appendChild(this.i.createTextNode(a.content)))
                        }
                        ;
                        f.prototype.T = function(a) {
                            var b = this.i.createElement(a.tagName);
                            b.setAttribute("type", a.type);
                            q(a.g, function(c, d) {
                                b.setAttribute(c, d)
                            });
                            return b
                        }
                        ;
                        f.prototype.ba = function(a) {
                            this.D('<span id="ps-style"/>');
                            var b = this.i.getElementById("ps-style");
                            b.parentNode.replaceChild(a, b)
                        }
                        ;
                        f.prototype.A = function(a) {
                            a.ca = this.h;
                            this.h = [];
                            this.j.unshift(a)
                        }
                        ;
                        f.prototype.I = function(a) {
                            a !== this.j[0] ? this.options.error({
                                message: "Bad script nesting or script finished twice"
                            }) : (this.j.shift(),
                            this.write.apply(this, a.ca),
                            !this.j.length && this.m && (this.A(this.m),
                            this.m = null))
                        }
                        ;
                        f.prototype.ja = function(a, b) {
                            var c = this.S(a)
                              , d = this.ha(c)
                              , k = this.options.J;
                            a.src && (c.src = a.src,
                            this.ga(c, d ? k : function() {
                                b();
                                k()
                            }
                            ));
                            try {
                                this.aa(c),
                                a.src && !d || b()
                            } catch (g) {
                                this.options.error(g),
                                b()
                            }
                        }
                        ;
                        f.prototype.S = function(a) {
                            var b = this.i.createElement(a.tagName);
                            q(a.g, function(c, d) {
                                b.setAttribute(c, d)
                            });
                            a.content && (b.text = a.content);
                            return b
                        }
                        ;
                        f.prototype.aa = function(a) {
                            this.D('<span id="ps-script"/>');
                            var b = this.i.getElementById("ps-script");
                            b.parentNode.replaceChild(a, b)
                        }
                        ;
                        f.prototype.ga = function(a, b) {
                            function c() {
                                a = a.onload = a.onreadystatechange = a.onerror = null
                            }
                            var d = this.options.error;
                            t(a, {
                                onload: function() {
                                    c();
                                    b()
                                },
                                onreadystatechange: function() {
                                    /^(loaded|complete)$/.test(a.readyState) && (c(),
                                    b())
                                },
                                onerror: function() {
                                    var k = {
                                        message: "remote script failed " + a.src
                                    };
                                    c();
                                    d(k);
                                    b()
                                }
                            })
                        }
                        ;
                        f.prototype.ha = function(a) {
                            return !/^script$/i.test(a.nodeName) || !!(this.options.fa && a.src && a.hasAttribute("async"))
                        }
                        ;
                        return f
                    }();
                    m.postscribe = function() {
                        function e() {
                            var d = b.shift(), k;
                            d && (k = d[d.length - 1],
                            k.K(),
                            d.stream = f.apply(null, d),
                            k.L())
                        }
                        function f(d, k, g) {
                            function r(x) {
                                x = g.P(x);
                                c.write(x);
                                g.M(x)
                            }
                            c = new z(d,g);
                            c.id = a++;
                            c.name = g.name || c.id;
                            var u = d.ownerDocument
                              , l = {
                                close: u.close,
                                open: u.open,
                                write: u.write,
                                writeln: u.writeln
                            };
                            t(u, {
                                close: n,
                                open: n,
                                write: function() {
                                    return r(A(arguments).join(""))
                                },
                                writeln: function() {
                                    return r(A(arguments).join("") + "\n")
                                }
                            });
                            var p = c.l.onerror || n;
                            c.l.onerror = function(x, G, H) {
                                g.error({
                                    qa: x + " - " + G + ":" + H
                                });
                                p.apply(c.l, arguments)
                            }
                            ;
                            c.write(k, function() {
                                t(u, l);
                                c.l.onerror = p;
                                g.done();
                                c = null;
                                e()
                            });
                            return c
                        }
                        var a = 0
                          , b = []
                          , c = null;
                        return t(function(d, k, g) {
                            "function" === typeof g && (g = {
                                done: g
                            });
                            g = B(g, h);
                            d = /^#/.test(d) ? m.document.getElementById(d.substr(1)) : d.pa ? d[0] : d;
                            var r = [d, k, g];
                            d.da = {
                                cancel: function() {
                                    r.stream ? r.stream.abort() : r[1] = n
                                }
                            };
                            g.O(r);
                            b.push(r);
                            c || e();
                            return d.da
                        }, {
                            streams: {},
                            ra: b,
                            na: z
                        })
                    }();
                    F = m.postscribe
                }
            }
            )();
            D("google_tag_manager_external.postscribe.installPostscribe", function() {
                var n = window.google_tag_manager;
                n && (n.postscribe || (n.postscribe = window.postscribe || F))
            });
            D("google_tag_manager_external.postscribe.getPostscribe", function() {
                return window.google_tag_manager.postscribe
            });
        }
        ).call(this);
    } catch {}

    var aa, ba = function(a) {
        var b = 0;
        return function() {
            return b < a.length ? {
                done: !1,
                value: a[b++]
            } : {
                done: !0
            }
        }
    }, da = "function" == typeof Object.defineProperties ? Object.defineProperty : function(a, b, c) {
        if (a == Array.prototype || a == Object.prototype)
            return a;
        a[b] = c.value;
        return a
    }
    , ea = function(a) {
        for (var b = ["object" == typeof globalThis && globalThis, a, "object" == typeof window && window, "object" == typeof self && self, "object" == typeof global && global], c = 0; c < b.length; ++c) {
            var d = b[c];
            if (d && d.Math == Math)
                return d
        }
        throw Error("Cannot find global object");
    }, fa = ea(this), ia = function(a, b) {
        if (b)
            a: {
                for (var c = fa, d = a.split("."), e = 0; e < d.length - 1; e++) {
                    var f = d[e];
                    if (!(f in c))
                        break a;
                    c = c[f]
                }
                var g = d[d.length - 1]
                  , h = c[g]
                  , m = b(h);
                m != h && null != m && da(c, g, {
                    configurable: !0,
                    writable: !0,
                    value: m
                })
            }
    }, la = function(a) {
        return a.raw = a
    }, ma = function(a, b) {
        a.raw = b;
        return a
    }, na = function(a) {
        var b = "undefined" != typeof Symbol && Symbol.iterator && a[Symbol.iterator];
        if (b)
            return b.call(a);
        if ("number" == typeof a.length)
            return {
                next: ba(a)
            };
        throw Error(String(a) + " is not an iterable or ArrayLike");
    }, pa = function(a) {
        for (var b, c = []; !(b = a.next()).done; )
            c.push(b.value);
        return c
    }, qa = function(a) {
        return a instanceof Array ? a : pa(na(a))
    }, ra = "function" == typeof Object.assign ? Object.assign : function(a, b) {
        for (var c = 1; c < arguments.length; c++) {
            var d = arguments[c];
            if (d)
                for (var e in d)
                    Object.prototype.hasOwnProperty.call(d, e) && (a[e] = d[e])
        }
        return a
    }
    ;
    ia("Object.assign", function(a) {
        return a || ra
    });
    var sa = "function" == typeof Object.create ? Object.create : function(a) {
        var b = function() {};
        b.prototype = a;
        return new b
    }
    , ta;
    if ("function" == typeof Object.setPrototypeOf)
        ta = Object.setPrototypeOf;
    else {
        var ua;
        a: {
            var va = {
                a: !0
            }
              , wa = {};
            try {
                wa.__proto__ = va;
                ua = wa.a;
                break a
            } catch (a) {}
            ua = !1
        }
        ta = ua ? function(a, b) {
            a.__proto__ = b;
            if (a.__proto__ !== b)
                throw new TypeError(a + " is not extensible");
            return a
        }
        : null
    }
    var xa = ta
      , ya = function(a, b) {
        a.prototype = sa(b.prototype);
        a.prototype.constructor = a;
        if (xa)
            xa(a, b);
        else
            for (var c in b)
                if ("prototype" != c)
                    if (Object.defineProperties) {
                        var d = Object.getOwnPropertyDescriptor(b, c);
                        d && Object.defineProperty(a, c, d)
                    } else
                        a[c] = b[c];
        a.Yn = b.prototype
    }
      , za = function() {
        for (var a = Number(this), b = [], c = a; c < arguments.length; c++)
            b[c - a] = arguments[c];
        return b
    };
    /*

 Copyright The Closure Library Authors.
 SPDX-License-Identifier: Apache-2.0
*/
    var Aa = this || self
      , Ba = function(a, b, c) {
        return a.call.apply(a.bind, arguments)
    }
      , Ca = function(a, b, c) {
        if (!a)
            throw Error();
        if (2 < arguments.length) {
            var d = Array.prototype.slice.call(arguments, 2);
            return function() {
                var e = Array.prototype.slice.call(arguments);
                Array.prototype.unshift.apply(e, d);
                return a.apply(b, e)
            }
        }
        return function() {
            return a.apply(b, arguments)
        }
    }
      , Da = function(a, b, c) {
        Da = Function.prototype.bind && -1 != Function.prototype.bind.toString().indexOf("native code") ? Ba : Ca;
        return Da.apply(null, arguments)
    }
      , Ea = function(a) {
        return a
    };
    var Ga = function(a, b) {
        this.type = a;
        this.data = b
    };
    var Ha = function() {
        this.m = {};
        this.H = {}
    };
    aa = Ha.prototype;
    aa.get = function(a) {
        return this.m["dust." + a]
    }
    ;
    aa.set = function(a, b) {
        a = "dust." + a;
        this.H.hasOwnProperty(a) || (this.m[a] = b)
    }
    ;
    aa.Sh = function(a, b) {
        this.set(a, b);
        this.H["dust." + a] = !0
    }
    ;
    aa.has = function(a) {
        return this.m.hasOwnProperty("dust." + a)
    }
    ;
    aa.zf = function(a) {
        a = "dust." + a;
        this.H.hasOwnProperty(a) || delete this.m[a]
    }
    ;
    var Ia = function() {};
    Ia.prototype.reset = function() {}
    ;
    var Ka = function(a, b) {
        this.T = a;
        this.parent = b;
        this.m = this.F = void 0;
        this.M = function(c, d, e) {
            return c.apply(d, e)
        }
        ;
        this.values = new Ha
    };
    Ka.prototype.add = function(a, b) {
        La(this, a, b, !1)
    }
    ;
    var La = function(a, b, c, d) {
        d ? a.values.Sh(b, c) : a.values.set(b, c)
    };
    Ka.prototype.set = function(a, b) {
        !this.values.has(a) && this.parent && this.parent.has(a) ? this.parent.set(a, b) : this.values.set(a, b)
    }
    ;
    Ka.prototype.get = function(a) {
        return this.values.has(a) ? this.values.get(a) : this.parent ? this.parent.get(a) : void 0
    }
    ;
    Ka.prototype.has = function(a) {
        return !!this.values.has(a) || !(!this.parent || !this.parent.has(a))
    }
    ;
    var Ma = function(a) {
        var b = new Ka(a.T,a);
        a.F && (b.F = a.F);
        b.M = a.M;
        b.m = a.m;
        return b
    };
    Ka.prototype.H = function() {
        return this.T
    }
    ;
    function Na(a, b) {
        for (var c, d = 0; d < b.length && !(c = Oa(a, b[d]),
        c instanceof Ga); d++)
            ;
        return c
    }
    function Oa(a, b) {
        try {
            var c = a.get(String(b[0]));
            if (!c || "function" !== typeof c.invoke)
                throw Error("Attempting to execute non-function " + b[0] + ".");
            return c.invoke.apply(c, [a].concat(b.slice(1)))
        } catch (e) {
            var d = a.F;
            d && d(e, b.context ? {
                id: b[0],
                line: b.context.line
            } : null);
            throw e;
        }
    }
    ;var Qa = function() {
        this.M = new Ia;
        this.m = new Ka(this.M)
    };
    Qa.prototype.H = function() {
        return this.M
    }
    ;
    Qa.prototype.execute = function(a) {
        var b = Array.prototype.slice.call(arguments, 0);
        return this.F(b)
    }
    ;
    Qa.prototype.F = function() {
        for (var a, b = 0; b < arguments.length; b++)
            a = Oa(this.m, arguments[b]);
        return a
    }
    ;
    Qa.prototype.T = function(a) {
        var b = Ma(this.m);
        b.m = a;
        for (var c, d = 1; d < arguments.length; d++)
            c = Oa(b, arguments[d]);
        return c
    }
    ;
    var Ra = function() {
        Ha.call(this);
        this.F = !1
    };
    ya(Ra, Ha);
    var Ta = function(a, b) {
        var c = [], d;
        for (d in a.m)
            if (a.m.hasOwnProperty(d))
                switch (d = d.substr(5),
                b) {
                case 1:
                    c.push(d);
                    break;
                case 2:
                    c.push(a.get(d));
                    break;
                case 3:
                    c.push([d, a.get(d)])
                }
        return c
    };
    Ra.prototype.set = function(a, b) {
        this.F || Ha.prototype.set.call(this, a, b)
    }
    ;
    Ra.prototype.Sh = function(a, b) {
        this.F || Ha.prototype.Sh.call(this, a, b)
    }
    ;
    Ra.prototype.zf = function(a) {
        this.F || Ha.prototype.zf.call(this, a)
    }
    ;
    Ra.prototype.Lb = function() {
        this.F = !0
    }
    ;
    /*
 jQuery (c) 2005, 2012 jQuery Foundation, Inc. jquery.org/license.
*/
    var Ua = /\[object (Boolean|Number|String|Function|Array|Date|RegExp)\]/
      , Va = function(a) {
        if (null == a)
            return String(a);
        var b = Ua.exec(Object.prototype.toString.call(Object(a)));
        return b ? b[1].toLowerCase() : "object"
    }
      , Wa = function(a, b) {
        return Object.prototype.hasOwnProperty.call(Object(a), b)
    }
      , Xa = function(a) {
        if (!a || "object" != Va(a) || a.nodeType || a == a.window)
            return !1;
        try {
            if (a.constructor && !Wa(a, "constructor") && !Wa(a.constructor.prototype, "isPrototypeOf"))
                return !1
        } catch (c) {
            return !1
        }
        for (var b in a)
            ;
        return void 0 === b || Wa(a, b)
    }
      , k = function(a, b) {
        var c = b || ("array" == Va(a) ? [] : {}), d;
        for (d in a)
            if (Wa(a, d)) {
                var e = a[d];
                "array" == Va(e) ? ("array" != Va(c[d]) && (c[d] = []),
                c[d] = k(e, c[d])) : Xa(e) ? (Xa(c[d]) || (c[d] = {}),
                c[d] = k(e, c[d])) : c[d] = e
            }
        return c
    };
    function Ya(a) {
        if (void 0 == a || Array.isArray(a) || Xa(a))
            return !0;
        switch (typeof a) {
        case "boolean":
        case "number":
        case "string":
        case "function":
            return !0
        }
        return !1
    }
    function Za(a) {
        return "number" === typeof a && 0 <= a && isFinite(a) && 0 === a % 1 || "string" === typeof a && "-" !== a[0] && a === "" + parseInt(a)
    }
    ;var $a = function(a) {
        this.m = [];
        this.H = !1;
        this.F = new Ra;
        a = a || [];
        for (var b in a)
            a.hasOwnProperty(b) && (Za(b) ? this.m[Number(b)] = a[Number(b)] : this.F.set(b, a[b]))
    };
    aa = $a.prototype;
    aa.toString = function(a) {
        if (a && 0 <= a.indexOf(this))
            return "";
        for (var b = [], c = 0; c < this.m.length; c++) {
            var d = this.m[c];
            null === d || void 0 === d ? b.push("") : d instanceof $a ? (a = a || [],
            a.push(this),
            b.push(d.toString(a)),
            a.pop()) : b.push(String(d))
        }
        return b.join(",")
    }
    ;
    aa.set = function(a, b) {
        if (!this.H)
            if ("length" === a) {
                if (!Za(b))
                    throw Error("RangeError: Length property must be a valid integer.");
                this.m.length = Number(b)
            } else
                Za(a) ? this.m[Number(a)] = b : this.F.set(a, b)
    }
    ;
    aa.get = function(a) {
        return "length" === a ? this.length() : Za(a) ? this.m[Number(a)] : this.F.get(a)
    }
    ;
    aa.length = function() {
        return this.m.length
    }
    ;
    aa.Zb = function() {
        for (var a = Ta(this.F, 1), b = 0; b < this.m.length; b++)
            a.push(b + "");
        return new $a(a)
    }
    ;
    var ab = function(a, b) {
        Za(b) ? delete a.m[Number(b)] : a.F.zf(b)
    };
    aa = $a.prototype;
    aa.pop = function() {
        return this.m.pop()
    }
    ;
    aa.push = function() {
        return this.m.push.apply(this.m, Array.prototype.slice.call(arguments))
    }
    ;
    aa.shift = function() {
        return this.m.shift()
    }
    ;
    aa.splice = function(a, b) {
        return new $a(this.m.splice.apply(this.m, arguments))
    }
    ;
    aa.unshift = function() {
        return this.m.unshift.apply(this.m, Array.prototype.slice.call(arguments))
    }
    ;
    aa.has = function(a) {
        return Za(a) && this.m.hasOwnProperty(a) || this.F.has(a)
    }
    ;
    aa.Lb = function() {
        this.H = !0;
        Object.freeze(this.m);
        this.F.Lb()
    }
    ;
    function bb(a) {
        for (var b = [], c = 0; c < a.length(); c++)
            a.has(c) && (b[c] = a.get(c));
        return b
    }
    ;var cb = function() {
        Ra.call(this)
    };
    ya(cb, Ra);
    cb.prototype.Zb = function() {
        return new $a(Ta(this, 1))
    }
    ;
    var db = function(a) {
        for (var b = Ta(a, 3), c = new $a, d = 0; d < b.length; d++) {
            var e = new $a(b[d]);
            c.push(e)
        }
        return c
    };
    function eb() {
        for (var a = fb, b = {}, c = 0; c < a.length; ++c)
            b[a[c]] = c;
        return b
    }
    function gb() {
        var a = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
        a += a.toLowerCase() + "0123456789-_";
        return a + "."
    }
    var fb, hb;
    function ib(a) {
        fb = fb || gb();
        hb = hb || eb();
        for (var b = [], c = 0; c < a.length; c += 3) {
            var d = c + 1 < a.length
              , e = c + 2 < a.length
              , f = a.charCodeAt(c)
              , g = d ? a.charCodeAt(c + 1) : 0
              , h = e ? a.charCodeAt(c + 2) : 0
              , m = f >> 2
              , n = (f & 3) << 4 | g >> 4
              , p = (g & 15) << 2 | h >> 6
              , q = h & 63;
            e || (q = 64,
            d || (p = 64));
            b.push(fb[m], fb[n], fb[p], fb[q])
        }
        return b.join("")
    }
    function jb(a) {
        function b(m) {
            for (; d < a.length; ) {
                var n = a.charAt(d++)
                  , p = hb[n];
                if (null != p)
                    return p;
                if (!/^[\s\xa0]*$/.test(n))
                    throw Error("Unknown base64 encoding at char: " + n);
            }
            return m
        }
        fb = fb || gb();
        hb = hb || eb();
        for (var c = "", d = 0; ; ) {
            var e = b(-1)
              , f = b(0)
              , g = b(64)
              , h = b(64);
            if (64 === h && -1 === e)
                return c;
            c += String.fromCharCode(e << 2 | f >> 4);
            64 !== g && (c += String.fromCharCode(f << 4 & 240 | g >> 2),
            64 !== h && (c += String.fromCharCode(g << 6 & 192 | h)))
        }
    }
    ;var kb = {};
    function lb(a, b) {
        kb[a] = kb[a] || [];
        kb[a][b] = !0
    }
    function mb(a) {
        var b = kb[a];
        if (!b || 0 === b.length)
            return "";
        for (var c = [], d = 0, e = 0; e < b.length; e++)
            0 === e % 8 && 0 < e && (c.push(String.fromCharCode(d)),
            d = 0),
            b[e] && (d |= 1 << e % 8);
        0 < d && c.push(String.fromCharCode(d));
        return ib(c.join("")).replace(/\.+$/, "")
    }
    function nb() {
        for (var a = [], b = kb.fdr || [], c = 0; c < b.length; c++)
            b[c] && a.push(c);
        return 0 < a.length ? a : void 0
    }
    ;function ob() {}
    function pb(a) {
        return "function" === typeof a
    }
    function l(a) {
        return "string" === typeof a
    }
    function qb(a) {
        return "number" === typeof a && !isNaN(a)
    }
    function rb(a) {
        return Array.isArray(a) ? a : [a]
    }
    function sb(a, b) {
        if (a && Array.isArray(a))
            for (var c = 0; c < a.length; c++)
                if (a[c] && b(a[c]))
                    return a[c]
    }
    function tb(a, b) {
        if (!qb(a) || !qb(b) || a > b)
            a = 0,
            b = 2147483647;
        return Math.floor(Math.random() * (b - a + 1) + a)
    }
    function ub(a, b) {
        for (var c = new vb, d = 0; d < a.length; d++)
            c.set(a[d], !0);
        for (var e = 0; e < b.length; e++)
            if (c.get(b[e]))
                return !0;
        return !1
    }
    function z(a, b) {
        for (var c in a)
            Object.prototype.hasOwnProperty.call(a, c) && b(c, a[c])
    }
    function wb(a) {
        return !!a && ("[object Arguments]" === Object.prototype.toString.call(a) || Object.prototype.hasOwnProperty.call(a, "callee"))
    }
    function xb(a) {
        return Math.round(Number(a)) || 0
    }
    function yb(a) {
        return "false" === String(a).toLowerCase() ? !1 : !!a
    }
    function zb(a) {
        var b = [];
        if (Array.isArray(a))
            for (var c = 0; c < a.length; c++)
                b.push(String(a[c]));
        return b
    }
    function Ab(a) {
        return a ? a.replace(/^\s+|\s+$/g, "") : ""
    }
    function Bb() {
        return new Date(Date.now())
    }
    function Cb() {
        return Bb().getTime()
    }
    var vb = function() {
        this.prefix = "gtm.";
        this.values = {}
    };
    vb.prototype.set = function(a, b) {
        this.values[this.prefix + a] = b
    }
    ;
    vb.prototype.get = function(a) {
        return this.values[this.prefix + a]
    }
    ;
    function Db(a, b, c) {
        return a && a.hasOwnProperty(b) ? a[b] : c
    }
    function Eb(a) {
        var b = a;
        return function() {
            if (b) {
                var c = b;
                b = void 0;
                try {
                    c()
                } catch (d) {}
            }
        }
    }
    function Fb(a, b) {
        for (var c in b)
            b.hasOwnProperty(c) && (a[c] = b[c])
    }
    function Gb(a, b) {
        for (var c = [], d = 0; d < a.length; d++)
            c.push(a[d]),
            c.push.apply(c, b[a[d]] || []);
        return c
    }
    function Hb(a, b) {
        return a.substring(0, b.length) === b
    }
    function Ib(a, b) {
        var c = G;
        b = b || [];
        for (var d = c, e = 0; e < a.length - 1; e++) {
            if (!d.hasOwnProperty(a[e]))
                return;
            d = d[a[e]];
            if (0 <= b.indexOf(d))
                return
        }
        return d
    }
    function Jb(a, b) {
        for (var c = {}, d = c, e = a.split("."), f = 0; f < e.length - 1; f++)
            d = d[e[f]] = {};
        d[e[e.length - 1]] = b;
        return c
    }
    var Kb = /^\w{1,9}$/;
    function Lb(a, b) {
        a = a || {};
        b = b || ",";
        var c = [];
        z(a, function(d, e) {
            Kb.test(d) && e && c.push(d)
        });
        return c.join(b)
    }
    function Mb(a, b) {
        function c() {
            e && ++d === b && (e(),
            e = null,
            c.done = !0)
        }
        var d = 0
          , e = a;
        c.done = !1;
        return c
    }
    ;var Nb, Ob = function() {
        if (void 0 === Nb) {
            var a = null
              , b = Aa.trustedTypes;
            if (b && b.createPolicy) {
                try {
                    a = b.createPolicy("goog#html", {
                        createHTML: Ea,
                        createScript: Ea,
                        createScriptURL: Ea
                    })
                } catch (c) {
                    Aa.console && Aa.console.error(c.message)
                }
                Nb = a
            } else
                Nb = a
        }
        return Nb
    };
    var Pb = function(a) {
        this.m = a
    };
    Pb.prototype.toString = function() {
        return this.m + ""
    }
    ;
    var Qb = function(a) {
        return a instanceof Pb && a.constructor === Pb ? a.m : "type_error:TrustedResourceUrl"
    }
      , Rb = {}
      , Sb = function(a) {
        var b = a
          , c = Ob()
          , d = c ? c.createScriptURL(b) : b;
        return new Pb(d,Rb)
    };
    /*

 SPDX-License-Identifier: Apache-2.0
*/
    var Tb = la([""])
      , Ub = ma(["\x00"], ["\\0"])
      , Vb = ma(["\n"], ["\\n"])
      , Wb = ma(["\x00"], ["\\u0000"]);
    function Xb(a) {
        return -1 === a.toString().indexOf("`")
    }
    Xb(function(a) {
        return a(Tb)
    }) || Xb(function(a) {
        return a(Ub)
    }) || Xb(function(a) {
        return a(Vb)
    }) || Xb(function(a) {
        return a(Wb)
    });
    var Yb = function(a) {
        this.m = a
    };
    Yb.prototype.toString = function() {
        return this.m
    }
    ;
    var Zb = new Yb("about:invalid#zClosurez");
    var $b = function(a) {
        this.hm = a
    };
    function ac(a) {
        return new $b(function(b) {
            return b.substr(0, a.length + 1).toLowerCase() === a + ":"
        }
        )
    }
    var bc = [ac("data"), ac("http"), ac("https"), ac("mailto"), ac("ftp"), new $b(function(a) {
        return /^[^:]*([/?#]|$)/.test(a)
    }
    )];
    function cc(a, b) {
        b = void 0 === b ? bc : b;
        if (a instanceof Yb)
            return a;
        for (var c = 0; c < b.length; ++c) {
            var d = b[c];
            if (d instanceof $b && d.hm(a))
                return new Yb(a)
        }
    }
    function dc(a) {
        var b;
        b = void 0 === b ? bc : b;
        return cc(a, b) || Zb
    }
    var ec = /^\s*(?!javascript:)(?:[\w+.-]+:|[^:/?#]*(?:[/?#]|$))/i;
    function fc(a) {
        var b;
        if (a instanceof Yb)
            if (a instanceof Yb)
                b = a.m;
            else
                throw Error("");
        else
            b = ec.test(a) ? a : void 0;
        return b
    }
    ;var hc = function() {
        this.m = gc[0].toLowerCase()
    };
    hc.prototype.toString = function() {
        return this.m
    }
    ;
    var ic = Array.prototype.indexOf ? function(a, b) {
        return Array.prototype.indexOf.call(a, b, void 0)
    }
    : function(a, b) {
        if ("string" === typeof a)
            return "string" !== typeof b || 1 != b.length ? -1 : a.indexOf(b, 0);
        for (var c = 0; c < a.length; c++)
            if (c in a && a[c] === b)
                return c;
        return -1
    }
    ;
    var jc = {}
      , kc = function(a) {
        this.m = a
    };
    kc.prototype.toString = function() {
        return this.m.toString()
    }
    ;
    function lc(a, b) {
        var c = [new hc];
        if (0 === c.length)
            throw Error("");
        var d = c.map(function(f) {
            var g;
            if (f instanceof hc)
                g = f.m;
            else
                throw Error("");
            return g
        })
          , e = b.toLowerCase();
        if (d.every(function(f) {
            return 0 !== e.indexOf(f)
        }))
            throw Error('Attribute "' + b + '" does not match any of the allowed prefixes.');
        a.setAttribute(b, "true")
    }
    ;function mc(a, b) {
        var c = fc(b);
        void 0 !== c && (a.action = c)
    }
    ;"ARTICLE SECTION NAV ASIDE H1 H2 H3 H4 H5 H6 HEADER FOOTER ADDRESS P HR PRE BLOCKQUOTE OL UL LH LI DL DT DD FIGURE FIGCAPTION MAIN DIV EM STRONG SMALL S CITE Q DFN ABBR RUBY RB RT RTC RP DATA TIME CODE VAR SAMP KBD SUB SUP I B U MARK BDI BDO SPAN BR WBR INS DEL PICTURE PARAM TRACK MAP TABLE CAPTION COLGROUP COL TBODY THEAD TFOOT TR TD TH SELECT DATALIST OPTGROUP OPTION OUTPUT PROGRESS METER FIELDSET LEGEND DETAILS SUMMARY MENU DIALOG SLOT CANVAS FONT CENTER ACRONYM BASEFONT BIG DIR HGROUP STRIKE TT".split(" ").concat(["BUTTON", "INPUT"]);
    function nc(a) {
        return null === a ? "null" : void 0 === a ? "undefined" : a
    }
    ;var G = window
      , H = document
      , oc = navigator
      , pc = function() {
        var a;
        try {
            a = oc.serviceWorker
        } catch (b) {
            return
        }
        return a
    }
      , qc = H.currentScript && H.currentScript.src
      , rc = function(a, b) {
        var c = G[a];
        G[a] = void 0 === c ? b : c;
        return G[a]
    }
      , sc = function(a, b) {
        b && (a.addEventListener ? a.onload = b : a.onreadystatechange = function() {
            a.readyState in {
                loaded: 1,
                complete: 1
            } && (a.onreadystatechange = null,
            b())
        }
        )
    }
      , tc = {
        async: 1,
        nonce: 1,
        onerror: 1,
        onload: 1,
        src: 1,
        type: 1
    }
      , uc = {
        onload: 1,
        src: 1,
        width: 1,
        height: 1,
        style: 1
    };
    function vc(a, b, c) {
        b && z(b, function(d, e) {
            d = d.toLowerCase();
            c.hasOwnProperty(d) || a.setAttribute(d, e)
        })
    }
    var wc = function(a, b, c, d, e) {
        var f = H.createElement("script");
        vc(f, d, tc);
        f.type = "text/javascript";
        f.async = d && !1 === d.async ? !1 : !0;
        var g;
        g = Sb(nc(a));
        f.src = Qb(g);
        var h, m, n, p = null == (n = (m = (f.ownerDocument && f.ownerDocument.defaultView || window).document).querySelector) ? void 0 : n.call(m, "script[nonce]");
        (h = p ? p.nonce || p.getAttribute("nonce") || "" : "") && f.setAttribute("nonce", h);
        sc(f, b);
        c && (f.onerror = c);
        if (e)
            e.appendChild(f);
        else {
            var q = H.getElementsByTagName("script")[0] || H.body || H.head;
            q.parentNode.insertBefore(f, q)
        }
        return f
    }
      , xc = function() {
        if (qc) {
            var a = qc.toLowerCase();
            if (0 === a.indexOf("https://"))
                return 2;
            if (0 === a.indexOf("http://"))
                return 3
        }
        return 1
    }
      , yc = function(a, b, c, d, e) {
        var f;
        f = void 0 === f ? !0 : f;
        var g = e
          , h = !1;
        g || (g = H.createElement("iframe"),
        h = !0);
        vc(g, c, uc);
        d && z(d, function(n, p) {
            g.dataset[n] = p
        });
        f && (g.height = "0",
        g.width = "0",
        g.style.display = "none",
        g.style.visibility = "hidden");
        void 0 !== a && (g.src = a);
        if (h) {
            var m = H.body && H.body.lastChild || H.body || H.head;
            m.parentNode.insertBefore(g, m)
        }
        sc(g, b);
        return g
    }
      , zc = function(a, b, c, d) {
        var e = new Image(1,1);
        vc(e, d, {});
        e.onload = function() {
            e.onload = null;
            b && b()
        }
        ;
        e.onerror = function() {
            e.onerror = null;
            c && c()
        }
        ;
        e.src = a;
        return e
    }
      , Ac = function(a, b, c, d) {
        a.addEventListener ? a.addEventListener(b, c, !!d) : a.attachEvent && a.attachEvent("on" + b, c)
    }
      , Bc = function(a, b, c) {
        a.removeEventListener ? a.removeEventListener(b, c, !1) : a.detachEvent && a.detachEvent("on" + b, c)
    }
      , I = function(a) {
        G.setTimeout(a, 0)
    }
      , Cc = function(a, b) {
        return a && b && a.attributes && a.attributes[b] ? a.attributes[b].value : null
    }
      , Dc = function(a) {
        var b = a.innerText || a.textContent || "";
        b && " " != b && (b = b.replace(/^[\s\xa0]+|[\s\xa0]+$/g, ""));
        b && (b = b.replace(/(\xa0+|\s{2,}|\n|\r\t)/g, " "));
        return b
    }
      , Ec = function(a) {
        var b = H.createElement("div"), c = b, d, e = nc("A<div>" + a + "</div>"), f = Ob(), g = f ? f.createHTML(e) : e;
        d = new kc(g,jc);
        if (1 === c.nodeType) {
            var h = c.tagName;
            if ("SCRIPT" === h || "STYLE" === h)
                throw Error("");
        }
        c.innerHTML = d instanceof kc && d.constructor === kc ? d.m : "type_error:SafeHtml";
        b = b.lastChild;
        for (var m = []; b.firstChild; )
            m.push(b.removeChild(b.firstChild));
        return m
    }
      , Fc = function(a, b, c) {
        c = c || 100;
        for (var d = {}, e = 0; e < b.length; e++)
            d[b[e]] = !0;
        for (var f = a, g = 0; f && g <= c; g++) {
            if (d[String(f.tagName).toLowerCase()])
                return f;
            f = f.parentElement
        }
        return null
    }
      , Gc = function(a) {
        var b;
        try {
            b = oc.sendBeacon && oc.sendBeacon(a)
        } catch (c) {
            lb("TAGGING", 15)
        }
        b || zc(a)
    }
      , Hc = function(a, b) {
        try {
            if (oc.sendBeacon)
                return oc.sendBeacon(a, b)
        } catch (c) {
            lb("TAGGING", 15)
        }
        return !1
    }
      , Ic = {
        cache: "no-store",
        credentials: "include",
        keepalive: !0,
        method: "POST",
        mode: "no-cors",
        redirect: "follow"
    }
      , Jc = function(a, b, c) {
        if ("fetch"in G) {
            var d = Object.assign({}, Ic);
            b && (d.body = b);
            c && (c.attributionReporting && (d.attributionReporting = c.attributionReporting),
            c.browsingTopics && (d.browsingTopics = c.browsingTopics));
            try {
                return G.fetch(a, d),
                !0
            } catch (e) {}
        }
        if (c && c.noFallback)
            return !1;
        if (b)
            return Hc(a, b);
        Gc(a);
        return !0
    }
      , Kc = function(a, b) {
        var c = a[b];
        c && "string" === typeof c.animVal && (c = c.animVal);
        return c
    }
      , Lc = function() {
        var a = G.performance;
        if (a && pb(a.now))
            return a.now()
    }
      , Mc = function() {
        return G.performance || void 0
    };
    var Nc = function(a, b) {
        return this.evaluate(a) && this.evaluate(b)
    }
      , Oc = function(a, b) {
        return this.evaluate(a) === this.evaluate(b)
    }
      , Pc = function(a, b) {
        return this.evaluate(a) || this.evaluate(b)
    }
      , Qc = function(a, b) {
        a = this.evaluate(a);
        b = this.evaluate(b);
        return -1 < String(a).indexOf(String(b))
    }
      , Rc = function(a, b) {
        a = String(this.evaluate(a));
        b = String(this.evaluate(b));
        return a.substring(0, b.length) === b
    }
      , Sc = function(a, b) {
        a = this.evaluate(a);
        b = this.evaluate(b);
        switch (a) {
        case "pageLocation":
            var c = G.location.href;
            b instanceof cb && b.get("stripProtocol") && (c = c.replace(/^https?:\/\//, ""));
            return c
        }
    };
    var Tc = function(a, b) {
        Ra.call(this);
        this.M = a;
        this.T = b
    };
    ya(Tc, Ra);
    aa = Tc.prototype;
    aa.toString = function() {
        return this.M
    }
    ;
    aa.getName = function() {
        return this.M
    }
    ;
    aa.Zb = function() {
        return new $a(Ta(this, 1))
    }
    ;
    aa.invoke = function(a) {
        return this.T.apply(new Uc(this,a), Array.prototype.slice.call(arguments, 1))
    }
    ;
    aa.fb = function(a) {
        try {
            return this.invoke.apply(this, Array.prototype.slice.call(arguments, 0))
        } catch (b) {}
    }
    ;
    var Uc = function(a, b) {
        this.m = a;
        this.J = b
    };
    Uc.prototype.evaluate = function(a) {
        var b = this.J;
        return Array.isArray(a) ? Oa(b, a) : a
    }
    ;
    Uc.prototype.getName = function() {
        return this.m.getName()
    }
    ;
    Uc.prototype.H = function() {
        return this.J.H()
    }
    ;
    var Vc = function() {
        this.map = new Map
    };
    Vc.prototype.set = function(a, b) {
        this.map.set(a, b)
    }
    ;
    Vc.prototype.get = function(a) {
        return this.map.get(a)
    }
    ;
    var Wc = function() {
        this.keys = [];
        this.values = []
    };
    Wc.prototype.set = function(a, b) {
        this.keys.push(a);
        this.values.push(b)
    }
    ;
    Wc.prototype.get = function(a) {
        var b = this.keys.indexOf(a);
        if (-1 < b)
            return this.values[b]
    }
    ;
    function Xc() {
        try {
            return Map ? new Vc : new Wc
        } catch (a) {
            return new Wc
        }
    }
    ;var Yc = function(a) {
        if (a instanceof Yc)
            return a;
        if (Ya(a))
            throw Error("Type of given value has an equivalent Pixie type.");
        this.value = a
    };
    Yc.prototype.getValue = function() {
        return this.value
    }
    ;
    Yc.prototype.toString = function() {
        return String(this.value)
    }
    ;
    var $c = function(a) {
        Ra.call(this);
        this.promise = a;
        this.set("then", Zc(this));
        this.set("catch", Zc(this, !0));
        this.set("finally", Zc(this, !1, !0))
    };
    ya($c, cb);
    var Zc = function(a, b, c) {
        b = void 0 === b ? !1 : b;
        c = void 0 === c ? !1 : c;
        return new Tc("",function(d, e) {
            b && (e = d,
            d = void 0);
            c && (e = d);
            d instanceof Tc || (d = void 0);
            e instanceof Tc || (e = void 0);
            var f = Ma(this.J)
              , g = function(m) {
                return function(n) {
                    return c ? (m.invoke(f),
                    a.promise) : m.invoke(f, n)
                }
            }
              , h = a.promise.then(d && g(d), e && g(e));
            return new $c(h)
        }
        )
    };
    function J(a, b, c) {
        var d = Xc()
          , e = function(g, h) {
            for (var m = Ta(g, 1), n = 0; n < m.length; n++)
                h[m[n]] = f(g.get(m[n]))
        }
          , f = function(g) {
            var h = d.get(g);
            if (h)
                return h;
            if (g instanceof $a) {
                var m = [];
                d.set(g, m);
                for (var n = g.Zb(), p = 0; p < n.length(); p++)
                    m[n.get(p)] = f(g.get(n.get(p)));
                return m
            }
            if (g instanceof $c)
                return g.promise;
            if (g instanceof cb) {
                var q = {};
                d.set(g, q);
                e(g, q);
                return q
            }
            if (g instanceof Tc) {
                var r = function() {
                    for (var u = Array.prototype.slice.call(arguments, 0), v = 0; v < u.length; v++)
                        u[v] = ad(u[v], b, c);
                    var w = new Ka(b ? b.H() : new Ia);
                    b && (w.m = b.m);
                    return f(g.invoke.apply(g, [w].concat(u)))
                };
                d.set(g, r);
                e(g, r);
                return r
            }
            var t = !1;
            switch (c) {
            case 1:
                t = !0;
                break;
            case 2:
                t = !1;
                break;
            case 3:
                t = !1;
                break;
            default:
            }
            if (g instanceof Yc && t)
                return g.getValue();
            switch (typeof g) {
            case "boolean":
            case "number":
            case "string":
            case "undefined":
                return g;
            case "object":
                if (null === g)
                    return null
            }
        };
        return f(a)
    }
    function ad(a, b, c) {
        var d = Xc()
          , e = function(g, h) {
            for (var m in g)
                g.hasOwnProperty(m) && h.set(m, f(g[m]))
        }
          , f = function(g) {
            var h = d.get(g);
            if (h)
                return h;
            if (Array.isArray(g) || wb(g)) {
                var m = new $a([]);
                d.set(g, m);
                for (var n in g)
                    g.hasOwnProperty(n) && m.set(n, f(g[n]));
                return m
            }
            if (Xa(g)) {
                var p = new cb;
                d.set(g, p);
                e(g, p);
                return p
            }
            if ("function" === typeof g) {
                var q = new Tc("",function() {
                    for (var y = Array.prototype.slice.call(arguments, 0), x = 0; x < y.length; x++)
                        y[x] = J(this.evaluate(y[x]), b, c);
                    return f((0,
                    this.J.M)(g, g, y))
                }
                );
                d.set(g, q);
                e(g, q);
                return q
            }
            var v = typeof g;
            if (null === g || "string" === v || "number" === v || "boolean" === v)
                return g;
            var w = !1;
            switch (c) {
            case 1:
                w = !0;
                break;
            case 2:
                w = !1;
                break;
            default:
            }
            if (void 0 !== g && w)
                return new Yc(g)
        };
        return f(a)
    }
    ;function bd() {
        var a = !1;
        return a
    }
    ;var cd = {
        supportedMethods: "concat every filter forEach hasOwnProperty indexOf join lastIndexOf map pop push reduce reduceRight reverse shift slice some sort splice unshift toString".split(" "),
        concat: function(a) {
            for (var b = [], c = 0; c < this.length(); c++)
                b.push(this.get(c));
            for (var d = 1; d < arguments.length; d++)
                if (arguments[d]instanceof $a)
                    for (var e = arguments[d], f = 0; f < e.length(); f++)
                        b.push(e.get(f));
                else
                    b.push(arguments[d]);
            return new $a(b)
        },
        every: function(a, b) {
            for (var c = this.length(), d = 0; d < this.length() && d < c; d++)
                if (this.has(d) && !b.invoke(a, this.get(d), d, this))
                    return !1;
            return !0
        },
        filter: function(a, b) {
            for (var c = this.length(), d = [], e = 0; e < this.length() && e < c; e++)
                this.has(e) && b.invoke(a, this.get(e), e, this) && d.push(this.get(e));
            return new $a(d)
        },
        forEach: function(a, b) {
            for (var c = this.length(), d = 0; d < this.length() && d < c; d++)
                this.has(d) && b.invoke(a, this.get(d), d, this)
        },
        hasOwnProperty: function(a, b) {
            return this.has(b)
        },
        indexOf: function(a, b, c) {
            var d = this.length()
              , e = void 0 === c ? 0 : Number(c);
            0 > e && (e = Math.max(d + e, 0));
            for (var f = e; f < d; f++)
                if (this.has(f) && this.get(f) === b)
                    return f;
            return -1
        },
        join: function(a, b) {
            for (var c = [], d = 0; d < this.length(); d++)
                c.push(this.get(d));
            return c.join(b)
        },
        lastIndexOf: function(a, b, c) {
            var d = this.length()
              , e = d - 1;
            void 0 !== c && (e = 0 > c ? d + c : Math.min(c, e));
            for (var f = e; 0 <= f; f--)
                if (this.has(f) && this.get(f) === b)
                    return f;
            return -1
        },
        map: function(a, b) {
            for (var c = this.length(), d = [], e = 0; e < this.length() && e < c; e++)
                this.has(e) && (d[e] = b.invoke(a, this.get(e), e, this));
            return new $a(d)
        },
        pop: function() {
            return this.pop()
        },
        push: function(a) {
            return this.push.apply(this, Array.prototype.slice.call(arguments, 1))
        },
        reduce: function(a, b, c) {
            var d = this.length(), e, f = 0;
            if (void 0 !== c)
                e = c;
            else {
                if (0 === d)
                    throw Error("TypeError: Reduce on List with no elements.");
                for (var g = 0; g < d; g++)
                    if (this.has(g)) {
                        e = this.get(g);
                        f = g + 1;
                        break
                    }
                if (g === d)
                    throw Error("TypeError: Reduce on List with no elements.");
            }
            for (var h = f; h < d; h++)
                this.has(h) && (e = b.invoke(a, e, this.get(h), h, this));
            return e
        },
        reduceRight: function(a, b, c) {
            var d = this.length(), e, f = d - 1;
            if (void 0 !== c)
                e = c;
            else {
                if (0 === d)
                    throw Error("TypeError: ReduceRight on List with no elements.");
                for (var g = 1; g <= d; g++)
                    if (this.has(d - g)) {
                        e = this.get(d - g);
                        f = d - (g + 1);
                        break
                    }
                if (g > d)
                    throw Error("TypeError: ReduceRight on List with no elements.");
            }
            for (var h = f; 0 <= h; h--)
                this.has(h) && (e = b.invoke(a, e, this.get(h), h, this));
            return e
        },
        reverse: function() {
            for (var a = bb(this), b = a.length - 1, c = 0; 0 <= b; b--,
            c++)
                a.hasOwnProperty(b) ? this.set(c, a[b]) : ab(this, c);
            return this
        },
        shift: function() {
            return this.shift()
        },
        slice: function(a, b, c) {
            var d = this.length();
            void 0 === b && (b = 0);
            b = 0 > b ? Math.max(d + b, 0) : Math.min(b, d);
            c = void 0 === c ? d : 0 > c ? Math.max(d + c, 0) : Math.min(c, d);
            c = Math.max(b, c);
            for (var e = [], f = b; f < c; f++)
                e.push(this.get(f));
            return new $a(e)
        },
        some: function(a, b) {
            for (var c = this.length(), d = 0; d < this.length() && d < c; d++)
                if (this.has(d) && b.invoke(a, this.get(d), d, this))
                    return !0;
            return !1
        },
        sort: function(a, b) {
            var c = bb(this);
            void 0 === b ? c.sort() : c.sort(function(e, f) {
                return Number(b.invoke(a, e, f))
            });
            for (var d = 0; d < c.length; d++)
                c.hasOwnProperty(d) ? this.set(d, c[d]) : ab(this, d);
            return this
        },
        splice: function(a, b, c) {
            return this.splice.apply(this, Array.prototype.splice.call(arguments, 1, arguments.length - 1))
        },
        toString: function() {
            return this.toString()
        },
        unshift: function(a) {
            return this.unshift.apply(this, Array.prototype.slice.call(arguments, 1))
        }
    };
    var dd = function(a) {
        var b;
        b = Error.call(this, a);
        this.message = b.message;
        "stack"in b && (this.stack = b.stack)
    };
    ya(dd, Error);
    var ed = {
        charAt: 1,
        concat: 1,
        indexOf: 1,
        lastIndexOf: 1,
        match: 1,
        replace: 1,
        search: 1,
        slice: 1,
        split: 1,
        substring: 1,
        toLowerCase: 1,
        toLocaleLowerCase: 1,
        toString: 1,
        toUpperCase: 1,
        toLocaleUpperCase: 1,
        trim: 1
    }
      , fd = new Ga("break")
      , gd = new Ga("continue");
    function hd(a, b) {
        return this.evaluate(a) + this.evaluate(b)
    }
    function id(a, b) {
        return this.evaluate(a) && this.evaluate(b)
    }
    function jd(a, b, c) {
        a = this.evaluate(a);
        b = this.evaluate(b);
        c = this.evaluate(c);
        if (!(c instanceof $a))
            throw Error("Error: Non-List argument given to Apply instruction.");
        if (null === a || void 0 === a) {
            var d = "TypeError: Can't read property " + b + " of " + a + ".";
            if (bd())
                throw new dd(d);
            throw Error(d);
        }
        var e = "number" === typeof a;
        if ("boolean" === typeof a || e) {
            if ("toString" === b) {
                if (e && c.length()) {
                    var f = J(c.get(0));
                    try {
                        return a.toString(f)
                    } catch (x) {}
                }
                return a.toString()
            }
            var g = "TypeError: " + a + "." + b + " is not a function.";
            if (bd())
                throw new dd(g);
            throw Error(g);
        }
        if ("string" === typeof a) {
            if (ed.hasOwnProperty(b)) {
                var h = 2;
                h = 1;
                var m = J(c, void 0, h);
                return ad(a[b].apply(a, m), this.J)
            }
            var n = "TypeError: " + b + " is not a function";
            if (bd())
                throw new dd(n);
            throw Error(n);
        }
        if (a instanceof $a) {
            if (a.has(b)) {
                var p = a.get(b);
                if (p instanceof Tc) {
                    var q = bb(c);
                    q.unshift(this.J);
                    return p.invoke.apply(p, q)
                }
                var r = "TypeError: " + b + " is not a function";
                if (bd())
                    throw new dd(r);
                throw Error(r);
            }
            if (0 <= cd.supportedMethods.indexOf(b)) {
                var t = bb(c);
                t.unshift(this.J);
                return cd[b].apply(a, t)
            }
        }
        if (a instanceof Tc || a instanceof cb) {
            if (a.has(b)) {
                var u = a.get(b);
                if (u instanceof Tc) {
                    var v = bb(c);
                    v.unshift(this.J);
                    return u.invoke.apply(u, v)
                }
                var w = "TypeError: " + b + " is not a function";
                if (bd())
                    throw new dd(w);
                throw Error(w);
            }
            if ("toString" === b)
                return a instanceof Tc ? a.getName() : a.toString();
            if ("hasOwnProperty" === b)
                return a.has.apply(a, bb(c))
        }
        if (a instanceof Yc && "toString" === b)
            return a.toString();
        var y = "TypeError: Object has no '" + b + "' property.";
        if (bd())
            throw new dd(y);
        throw Error(y);
    }
    function kd(a, b) {
        a = this.evaluate(a);
        if ("string" !== typeof a)
            throw Error("Invalid key name given for assignment.");
        var c = this.J;
        if (!c.has(a))
            throw Error("Attempting to assign to undefined value " + b);
        var d = this.evaluate(b);
        c.set(a, d);
        return d
    }
    function ld() {
        var a = Ma(this.J)
          , b = Na(a, Array.prototype.slice.apply(arguments));
        if (b instanceof Ga)
            return b
    }
    function md() {
        return fd
    }
    function nd(a) {
        for (var b = this.evaluate(a), c = 0; c < b.length; c++) {
            var d = this.evaluate(b[c]);
            if (d instanceof Ga)
                return d
        }
    }
    function od() {
        for (var a = this.J, b = 0; b < arguments.length - 1; b += 2) {
            var c = arguments[b];
            if ("string" === typeof c) {
                var d = this.evaluate(arguments[b + 1]);
                La(a, c, d, !0)
            }
        }
    }
    function qd() {
        return gd
    }
    function rd(a, b) {
        return new Ga(a,this.evaluate(b))
    }
    function sd(a, b) {
        var c = new $a;
        b = this.evaluate(b);
        for (var d = 0; d < b.length; d++)
            c.push(b[d]);
        var e = [51, a, c].concat(Array.prototype.splice.call(arguments, 2, arguments.length - 2));
        this.J.add(a, this.evaluate(e))
    }
    function td(a, b) {
        return this.evaluate(a) / this.evaluate(b)
    }
    function ud(a, b) {
        a = this.evaluate(a);
        b = this.evaluate(b);
        var c = a instanceof Yc
          , d = b instanceof Yc;
        return c || d ? c && d ? a.getValue() === b.getValue() : !1 : a == b
    }
    function vd() {
        for (var a, b = 0; b < arguments.length; b++)
            a = this.evaluate(arguments[b]);
        return a
    }
    function wd(a, b, c, d) {
        for (var e = 0; e < b(); e++) {
            var f = a(c(e))
              , g = Na(f, d);
            if (g instanceof Ga) {
                if ("break" === g.type)
                    break;
                if ("return" === g.type)
                    return g
            }
        }
    }
    function xd(a, b, c) {
        if ("string" === typeof b)
            return wd(a, function() {
                return b.length
            }, function(f) {
                return f
            }, c);
        if (b instanceof cb || b instanceof $a || b instanceof Tc) {
            var d = b.Zb()
              , e = d.length();
            return wd(a, function() {
                return e
            }, function(f) {
                return d.get(f)
            }, c)
        }
    }
    function yd(a, b, c) {
        a = this.evaluate(a);
        b = this.evaluate(b);
        c = this.evaluate(c);
        var d = this.J;
        return xd(function(e) {
            d.set(a, e);
            return d
        }, b, c)
    }
    function zd(a, b, c) {
        a = this.evaluate(a);
        b = this.evaluate(b);
        c = this.evaluate(c);
        var d = this.J;
        return xd(function(e) {
            var f = Ma(d);
            La(f, a, e, !0);
            return f
        }, b, c)
    }
    function Ad(a, b, c) {
        a = this.evaluate(a);
        b = this.evaluate(b);
        c = this.evaluate(c);
        var d = this.J;
        return xd(function(e) {
            var f = Ma(d);
            f.add(a, e);
            return f
        }, b, c)
    }
    function Bd(a, b, c) {
        a = this.evaluate(a);
        b = this.evaluate(b);
        c = this.evaluate(c);
        var d = this.J;
        return Cd(function(e) {
            d.set(a, e);
            return d
        }, b, c)
    }
    function Dd(a, b, c) {
        a = this.evaluate(a);
        b = this.evaluate(b);
        c = this.evaluate(c);
        var d = this.J;
        return Cd(function(e) {
            var f = Ma(d);
            La(f, a, e, !0);
            return f
        }, b, c)
    }
    function Ed(a, b, c) {
        a = this.evaluate(a);
        b = this.evaluate(b);
        c = this.evaluate(c);
        var d = this.J;
        return Cd(function(e) {
            var f = Ma(d);
            f.add(a, e);
            return f
        }, b, c)
    }
    function Cd(a, b, c) {
        if ("string" === typeof b)
            return wd(a, function() {
                return b.length
            }, function(d) {
                return b[d]
            }, c);
        if (b instanceof $a)
            return wd(a, function() {
                return b.length()
            }, function(d) {
                return b.get(d)
            }, c);
        if (bd())
            throw new dd("The value is not iterable.");
        throw new TypeError("The value is not iterable.");
    }
    function Fd(a, b, c, d) {
        function e(p, q) {
            for (var r = 0; r < f.length(); r++) {
                var t = f.get(r);
                q.add(t, p.get(t))
            }
        }
        var f = this.evaluate(a);
        if (!(f instanceof $a))
            throw Error("TypeError: Non-List argument given to ForLet instruction.");
        var g = this.J;
        d = this.evaluate(d);
        var h = Ma(g);
        for (e(g, h); Oa(h, b); ) {
            var m = Na(h, d);
            if (m instanceof Ga) {
                if ("break" === m.type)
                    break;
                if ("return" === m.type)
                    return m
            }
            var n = Ma(g);
            e(h, n);
            Oa(n, c);
            h = n
        }
    }
    function Gd(a, b) {
        var c = this.J
          , d = this.evaluate(b);
        if (!(d instanceof $a))
            throw Error("Error: non-List value given for Fn argument names.");
        var e = Array.prototype.slice.call(arguments, 2);
        return new Tc(a,function() {
            return function(f) {
                var g = Ma(c);
                void 0 === g.m && (g.m = this.J.m);
                for (var h = Array.prototype.slice.call(arguments, 0), m = 0; m < h.length; m++)
                    if (h[m] = this.evaluate(h[m]),
                    h[m]instanceof Ga)
                        return h[m];
                for (var n = d.get("length"), p = 0; p < n; p++)
                    p < h.length ? g.add(d.get(p), h[p]) : g.add(d.get(p), void 0);
                g.add("arguments", new $a(h));
                var q = Na(g, e);
                if (q instanceof Ga)
                    return "return" === q.type ? q.data : q
            }
        }())
    }
    function Hd(a) {
        a = this.evaluate(a);
        var b = this.J;
        if (Id && !b.has(a))
            throw new ReferenceError(a + " is not defined.");
        return b.get(a)
    }
    function Jd(a, b) {
        var c;
        a = this.evaluate(a);
        b = this.evaluate(b);
        if (void 0 === a || null === a) {
            var d = "TypeError: Cannot read properties of " + a + " (reading '" + b + "')";
            if (bd())
                throw new dd(d);
            throw Error(d);
        }
        if (a instanceof cb || a instanceof $a || a instanceof Tc)
            c = a.get(b);
        else if ("string" === typeof a)
            "length" === b ? c = a.length : Za(b) && (c = a[b]);
        else if (a instanceof Yc)
            return;
        return c
    }
    function Kd(a, b) {
        return this.evaluate(a) > this.evaluate(b)
    }
    function Ld(a, b) {
        return this.evaluate(a) >= this.evaluate(b)
    }
    function Md(a, b) {
        a = this.evaluate(a);
        b = this.evaluate(b);
        a instanceof Yc && (a = a.getValue());
        b instanceof Yc && (b = b.getValue());
        return a === b
    }
    function Nd(a, b) {
        return !Md.call(this, a, b)
    }
    function Od(a, b, c) {
        var d = [];
        this.evaluate(a) ? d = this.evaluate(b) : c && (d = this.evaluate(c));
        var e = Na(this.J, d);
        if (e instanceof Ga)
            return e
    }
    var Id = !1;
    function Pd(a, b) {
        return this.evaluate(a) < this.evaluate(b)
    }
    function Qd(a, b) {
        return this.evaluate(a) <= this.evaluate(b)
    }
    function Rd() {
        for (var a = new $a, b = 0; b < arguments.length; b++) {
            var c = this.evaluate(arguments[b]);
            a.push(c)
        }
        return a
    }
    function Sd() {
        for (var a = new cb, b = 0; b < arguments.length - 1; b += 2) {
            var c = this.evaluate(arguments[b]) + ""
              , d = this.evaluate(arguments[b + 1]);
            a.set(c, d)
        }
        return a
    }
    function Td(a, b) {
        return this.evaluate(a) % this.evaluate(b)
    }
    function Ud(a, b) {
        return this.evaluate(a) * this.evaluate(b)
    }
    function Vd(a) {
        return -this.evaluate(a)
    }
    function Wd(a) {
        return !this.evaluate(a)
    }
    function Xd(a, b) {
        return !ud.call(this, a, b)
    }
    function Yd() {
        return null
    }
    function Zd(a, b) {
        return this.evaluate(a) || this.evaluate(b)
    }
    function $d(a, b) {
        var c = this.evaluate(a);
        this.evaluate(b);
        return c
    }
    function ae(a) {
        return this.evaluate(a)
    }
    function be() {
        return Array.prototype.slice.apply(arguments)
    }
    function ce(a) {
        return new Ga("return",this.evaluate(a))
    }
    function de(a, b, c) {
        a = this.evaluate(a);
        b = this.evaluate(b);
        c = this.evaluate(c);
        if (null === a || void 0 === a) {
            var d = "TypeError: Can't set property " + b + " of " + a + ".";
            if (bd())
                throw new dd(d);
            throw Error(d);
        }
        (a instanceof Tc || a instanceof $a || a instanceof cb) && a.set(b, c);
        return c
    }
    function ee(a, b) {
        return this.evaluate(a) - this.evaluate(b)
    }
    function fe(a, b, c) {
        a = this.evaluate(a);
        var d = this.evaluate(b)
          , e = this.evaluate(c);
        if (!Array.isArray(d) || !Array.isArray(e))
            throw Error("Error: Malformed switch instruction.");
        for (var f, g = !1, h = 0; h < d.length; h++)
            if (g || a === this.evaluate(d[h]))
                if (f = this.evaluate(e[h]),
                f instanceof Ga) {
                    var m = f.type;
                    if ("break" === m)
                        return;
                    if ("return" === m || "continue" === m)
                        return f
                } else
                    g = !0;
        if (e.length === d.length + 1 && (f = this.evaluate(e[e.length - 1]),
        f instanceof Ga && ("return" === f.type || "continue" === f.type)))
            return f
    }
    function ge(a, b, c) {
        return this.evaluate(a) ? this.evaluate(b) : this.evaluate(c)
    }
    function he(a) {
        a = this.evaluate(a);
        return a instanceof Tc ? "function" : typeof a
    }
    function ie() {
        for (var a = this.J, b = 0; b < arguments.length; b++) {
            var c = arguments[b];
            "string" !== typeof c || a.add(c, void 0)
        }
    }
    function je(a, b, c, d) {
        var e = this.evaluate(d);
        if (this.evaluate(c)) {
            var f = Na(this.J, e);
            if (f instanceof Ga) {
                if ("break" === f.type)
                    return;
                if ("return" === f.type)
                    return f
            }
        }
        for (; this.evaluate(a); ) {
            var g = Na(this.J, e);
            if (g instanceof Ga) {
                if ("break" === g.type)
                    break;
                if ("return" === g.type)
                    return g
            }
            this.evaluate(b)
        }
    }
    function ke(a) {
        return ~Number(this.evaluate(a))
    }
    function le(a, b) {
        return Number(this.evaluate(a)) << Number(this.evaluate(b))
    }
    function me(a, b) {
        return Number(this.evaluate(a)) >> Number(this.evaluate(b))
    }
    function ne(a, b) {
        return Number(this.evaluate(a)) >>> Number(this.evaluate(b))
    }
    function oe(a, b) {
        return Number(this.evaluate(a)) & Number(this.evaluate(b))
    }
    function pe(a, b) {
        return Number(this.evaluate(a)) ^ Number(this.evaluate(b))
    }
    function qe(a, b) {
        return Number(this.evaluate(a)) | Number(this.evaluate(b))
    }
    function re() {}
    function se(a, b, c, d, e) {
        var f = !0;
        try {
            var g = this.evaluate(c);
            if (g instanceof Ga)
                return g
        } catch (r) {
            if (!(r instanceof dd && a))
                throw f = r instanceof dd,
                r;
            var h = Ma(this.J)
              , m = new Yc(r);
            h.add(b, m);
            var n = this.evaluate(d)
              , p = Na(h, n);
            if (p instanceof Ga)
                return p
        } finally {
            if (f && void 0 !== e) {
                var q = this.evaluate(e);
                if (q instanceof Ga)
                    return q
            }
        }
    }
    ;var ue = function() {
        this.m = new Qa;
        te(this)
    };
    ue.prototype.execute = function(a) {
        return this.m.F(a)
    }
    ;
    var te = function(a) {
        var b = function(c, d) {
            var e = new Tc(String(c),d);
            e.Lb();
            a.m.m.set(String(c), e)
        };
        b("map", Sd);
        b("and", Nc);
        b("contains", Qc);
        b("equals", Oc);
        b("or", Pc);
        b("startsWith", Rc);
        b("variable", Sc)
    };
    var we = function() {
        this.F = !1;
        this.m = new Qa;
        ve(this);
        this.F = !0
    };
    we.prototype.execute = function(a) {
        return xe(this.m.F(a))
    }
    ;
    var ye = function(a, b, c) {
        return xe(a.m.T(b, c))
    }
      , ve = function(a) {
        var b = function(c, d) {
            var e = String(c)
              , f = new Tc(e,d);
            f.Lb();
            a.m.m.set(e, f)
        };
        b(0, hd);
        b(1, id);
        b(2, jd);
        b(3, kd);
        b(56, oe);
        b(57, le);
        b(58, ke);
        b(59, qe);
        b(60, me);
        b(61, ne);
        b(62, pe);
        b(53, ld);
        b(4, md);
        b(5, nd);
        b(52, od);
        b(6, qd);
        b(49, rd);
        b(7, Rd);
        b(8, Sd);
        b(9, nd);
        b(50, sd);
        b(10, td);
        b(12, ud);
        b(13, vd);
        b(51, Gd);
        b(47, yd);
        b(54, zd);
        b(55, Ad);
        b(63, Fd);
        b(64, Bd);
        b(65, Dd);
        b(66, Ed);
        b(15, Hd);
        b(16, Jd);
        b(17, Jd);
        b(18, Kd);
        b(19, Ld);
        b(20, Md);
        b(21, Nd);
        b(22, Od);
        b(23, Pd);
        b(24, Qd);
        b(25, Td);
        b(26, Ud);
        b(27, Vd);
        b(28, Wd);
        b(29, Xd);
        b(45, Yd);
        b(30, Zd);
        b(32, $d);
        b(33, $d);
        b(34, ae);
        b(35, ae);
        b(46, be);
        b(36, ce);
        b(43, de);
        b(37, ee);
        b(38, fe);
        b(39, ge);
        b(67, se);
        b(40, he);
        b(44, re);
        b(41, ie);
        b(42, je)
    };
    we.prototype.H = function() {
        return this.m.H()
    }
    ;
    function xe(a) {
        if (a instanceof Ga || a instanceof Tc || a instanceof $a || a instanceof cb || a instanceof Yc || null === a || void 0 === a || "string" === typeof a || "number" === typeof a || "boolean" === typeof a)
            return a
    }
    ;var ze = function(a) {
        this.message = a
    };
    function Ae(a) {
        var b = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_"[a];
        return void 0 === b ? new ze("Value " + a + " can not be encoded in web-safe base64 dictionary.") : b
    }
    ;function Be(a) {
        switch (a) {
        case 1:
            return "1";
        case 2:
        case 4:
            return "0";
        default:
            return "-"
        }
    }
    ;var Ce = function() {
        var a = function(b) {
            return {
                toString: function() {
                    return b
                }
            }
        };
        return {
            rk: a("consent"),
            ei: a("convert_case_to"),
            fi: a("convert_false_to"),
            gi: a("convert_null_to"),
            hi: a("convert_true_to"),
            ii: a("convert_undefined_to"),
            nn: a("debug_mode_metadata"),
            ra: a("function"),
            Pg: a("instance_name"),
            Qk: a("live_only"),
            Rk: a("malware_disabled"),
            Sk: a("metadata"),
            Vk: a("original_activity_id"),
            An: a("original_vendor_template_id"),
            zn: a("once_on_load"),
            Uk: a("once_per_event"),
            oj: a("once_per_load"),
            En: a("priority_override"),
            Gn: a("respected_consent_types"),
            vj: a("setup_tags"),
            pe: a("tag_id"),
            Bj: a("teardown_tags")
        }
    }();
    var De = []
      , Ee = {
        "\x00": "&#0;",
        '"': "&quot;",
        "&": "&amp;",
        "'": "&#39;",
        "<": "&lt;",
        ">": "&gt;",
        "\t": "&#9;",
        "\n": "&#10;",
        "\v": "&#11;",
        "\f": "&#12;",
        "\r": "&#13;",
        " ": "&#32;",
        "-": "&#45;",
        "/": "&#47;",
        "=": "&#61;",
        "`": "&#96;",
        "\u0085": "&#133;",
        "\u00a0": "&#160;",
        "\u2028": "&#8232;",
        "\u2029": "&#8233;"
    }
      , Fe = function(a) {
        return Ee[a]
    }
      , Ge = /[\x00\x22\x26\x27\x3c\x3e]/g;
    var He = /[\x00\x09-\x0d \x22\x26\x27\x2d\/\x3c-\x3e`\x85\xa0\u2028\u2029]/g;
    De[4] = function(a) {
        return String(a).replace(He, Fe)
    }
    ;
    var Ke = /[\x00\x08-\x0d\x22\x26\x27\/\x3c-\x3e\\\x85\u2028\u2029]/g
      , Le = {
        "\x00": "\\x00",
        "\b": "\\x08",
        "\t": "\\t",
        "\n": "\\n",
        "\v": "\\x0b",
        "\f": "\\f",
        "\r": "\\r",
        '"': "\\x22",
        "&": "\\x26",
        "'": "\\x27",
        "/": "\\/",
        "<": "\\x3c",
        "=": "\\x3d",
        ">": "\\x3e",
        "\\": "\\\\",
        "\u0085": "\\x85",
        "\u2028": "\\u2028",
        "\u2029": "\\u2029",
        $: "\\x24",
        "(": "\\x28",
        ")": "\\x29",
        "*": "\\x2a",
        "+": "\\x2b",
        ",": "\\x2c",
        "-": "\\x2d",
        ".": "\\x2e",
        ":": "\\x3a",
        "?": "\\x3f",
        "[": "\\x5b",
        "]": "\\x5d",
        "^": "\\x5e",
        "{": "\\x7b",
        "|": "\\x7c",
        "}": "\\x7d"
    }
      , Me = function(a) {
        return Le[a]
    };
    De[8] = function(a) {
        if (null == a)
            return " null ";
        switch (typeof a) {
        case "boolean":
        case "number":
            return " " + a + " ";
        default:
            return "'" + String(String(a)).replace(Ke, Me) + "'"
        }
    }
    ;
    var Te = /['()]/g
      , Ue = function(a) {
        return "%" + a.charCodeAt(0).toString(16)
    };
    De[12] = function(a) {
        var b = encodeURIComponent(String(a));
        Te.lastIndex = 0;
        return Te.test(b) ? b.replace(Te, Ue) : b
    }
    ;
    var Ve = /[\x00- \x22\x27-\x29\x3c\x3e\\\x7b\x7d\x7f\x85\xa0\u2028\u2029\uff01\uff03\uff04\uff06-\uff0c\uff0f\uff1a\uff1b\uff1d\uff1f\uff20\uff3b\uff3d]/g
      , We = {
        "\x00": "%00",
        "\u0001": "%01",
        "\u0002": "%02",
        "\u0003": "%03",
        "\u0004": "%04",
        "\u0005": "%05",
        "\u0006": "%06",
        "\u0007": "%07",
        "\b": "%08",
        "\t": "%09",
        "\n": "%0A",
        "\v": "%0B",
        "\f": "%0C",
        "\r": "%0D",
        "\u000e": "%0E",
        "\u000f": "%0F",
        "\u0010": "%10",
        "\u0011": "%11",
        "\u0012": "%12",
        "\u0013": "%13",
        "\u0014": "%14",
        "\u0015": "%15",
        "\u0016": "%16",
        "\u0017": "%17",
        "\u0018": "%18",
        "\u0019": "%19",
        "\u001a": "%1A",
        "\u001b": "%1B",
        "\u001c": "%1C",
        "\u001d": "%1D",
        "\u001e": "%1E",
        "\u001f": "%1F",
        " ": "%20",
        '"': "%22",
        "'": "%27",
        "(": "%28",
        ")": "%29",
        "<": "%3C",
        ">": "%3E",
        "\\": "%5C",
        "{": "%7B",
        "}": "%7D",
        "\u007f": "%7F",
        "\u0085": "%C2%85",
        "\u00a0": "%C2%A0",
        "\u2028": "%E2%80%A8",
        "\u2029": "%E2%80%A9",
        "\uff01": "%EF%BC%81",
        "\uff03": "%EF%BC%83",
        "\uff04": "%EF%BC%84",
        "\uff06": "%EF%BC%86",
        "\uff07": "%EF%BC%87",
        "\uff08": "%EF%BC%88",
        "\uff09": "%EF%BC%89",
        "\uff0a": "%EF%BC%8A",
        "\uff0b": "%EF%BC%8B",
        "\uff0c": "%EF%BC%8C",
        "\uff0f": "%EF%BC%8F",
        "\uff1a": "%EF%BC%9A",
        "\uff1b": "%EF%BC%9B",
        "\uff1d": "%EF%BC%9D",
        "\uff1f": "%EF%BC%9F",
        "\uff20": "%EF%BC%A0",
        "\uff3b": "%EF%BC%BB",
        "\uff3d": "%EF%BC%BD"
    }
      , Xe = function(a) {
        return We[a]
    };
    De[16] = function(a) {
        return a
    }
    ;
    var Ze;
    var $e = [], af = [], bf = [], cf = [], df = [], ef = {}, ff, gf, hf = function(a) {
        gf = gf || a
    }, jf = function(a) {}, kf, lf = [], mf = [], nf = function(a, b) {
        var c = {};
        c[Ce.ra] = "__" + a;
        for (var d in b)
            b.hasOwnProperty(d) && (c["vtp_" + d] = b[d]);
        return c
    }, of = function(a, b) {
        var c = a[Ce.ra]
          , d = b && b.event;
        if (!c)
            throw Error("Error: No function name given for function call.");
        var e = ef[c], f = b && 2 === b.type && d.reportMacroDiscrepancy && e && -1 !== lf.indexOf(c), g = {}, h = {}, m;
        for (m in a)
            a.hasOwnProperty(m) && 0 === m.indexOf("vtp_") && (e && (g[m] = a[m]),
            !e || f) && (h[m.substr(4)] = a[m]);
        e && d && d.cachedModelValues && (g.vtp_gtmCachedValues = d.cachedModelValues);
        if (b) {
            if (null == b.name) {
                var n;
                a: {
                    var p = b.type
                      , q = b.index;
                    if (null == q)
                        n = "";
                    else {
                        var r;
                        switch (p) {
                        case 2:
                            r = $e[q];
                            break;
                        case 1:
                            r = cf[q];
                            break;
                        default:
                            n = "";
                            break a
                        }
                        var t = r && r[Ce.Pg];
                        n = t ? String(t) : ""
                    }
                }
                b.name = n
            }
            e && (g.vtp_gtmEntityIndex = b.index,
            g.vtp_gtmEntityName = b.name)
        }
        var u, v, w;
        if (f && -1 === mf.indexOf(c)) {
            mf.push(c);
            var y = Cb();
            u = e(g);
            var x = Cb() - y
              , B = Cb();
            v = Ze(c, h, b);
            w = x - (Cb() - B)
        } else if (e && (u = e(g)),
        !e || f)
            v = Ze(c, h, b);
        f && d && (d.reportMacroDiscrepancy(d.id, c, void 0, !0),
        Ya(u) ? (Array.isArray(u) ? Array.isArray(v) : Xa(u) ? Xa(v) : "function" === typeof u ? "function" === typeof v : u === v) || d.reportMacroDiscrepancy(d.id, c) : u !== v && d.reportMacroDiscrepancy(d.id, c),
        void 0 != w && d.reportMacroDiscrepancy(d.id, c, w));
        return e ? u : v
    }, qf = function(a, b, c) {
        c = c || [];
        var d = {}, e;
        for (e in a)
            a.hasOwnProperty(e) && (d[e] = pf(a[e], b, c));
        return d
    }, pf = function(a, b, c) {
        if (Array.isArray(a)) {
            var d;
            switch (a[0]) {
            case "function_id":
                return a[1];
            case "list":
                d = [];
                for (var e = 1; e < a.length; e++)
                    d.push(pf(a[e], b, c));
                return d;
            case "macro":
                var f = a[1];
                if (c[f])
                    return;
                var g = $e[f];
                if (!g || b.isBlocked(g))
                    return;
                c[f] = !0;
                var h = String(g[Ce.Pg]);
                try {
                    var m = qf(g, b, c);
                    m.vtp_gtmEventId = b.id;
                    b.priorityId && (m.vtp_gtmPriorityId = b.priorityId);
                    d = of(m, {
                        event: b,
                        index: f,
                        type: 2,
                        name: h
                    });
                    kf && (d = kf.ql(d, m))
                } catch (x) {
                    b.logMacroError && b.logMacroError(x, Number(f), h),
                    d = !1
                }
                c[f] = !1;
                return d;
            case "map":
                d = {};
                for (var n = 1; n < a.length; n += 2)
                    d[pf(a[n], b, c)] = pf(a[n + 1], b, c);
                return d;
            case "template":
                d = [];
                for (var p = !1, q = 1; q < a.length; q++) {
                    var r = pf(a[q], b, c);
                    gf && (p = p || gf.dm(r));
                    d.push(r)
                }
                return gf && p ? gf.vl(d) : d.join("");
            case "escape":
                d = pf(a[1], b, c);
                if (gf && Array.isArray(a[1]) && "macro" === a[1][0] && gf.fm(a))
                    return gf.Dm(d);
                d = String(d);
                for (var t = 2; t < a.length; t++)
                    De[a[t]] && (d = De[a[t]](d));
                return d;
            case "tag":
                var u = a[1];
                if (!cf[u])
                    throw Error("Unable to resolve tag reference " + u + ".");
                return {
                    Lj: a[2],
                    index: u
                };
            case "zb":
                var v = {
                    arg0: a[2],
                    arg1: a[3],
                    ignore_case: a[5]
                };
                v[Ce.ra] = a[1];
                var w = rf(v, b, c)
                  , y = !!a[4];
                return y || 2 !== w ? y !== (1 === w) : null;
            default:
                throw Error("Attempting to expand unknown Value type: " + a[0] + ".");
            }
        }
        return a
    }, rf = function(a, b, c) {
        try {
            return ff(qf(a, b, c))
        } catch (d) {
            JSON.stringify(a)
        }
        return 2
    }, sf = function(a) {
        var b = a[Ce.ra];
        if (!b)
            throw Error("Error: No function name given for function call.");
        return !!ef[b]
    };
    var tf = function(a, b, c) {
        var d;
        d = Error.call(this, c);
        this.message = d.message;
        "stack"in d && (this.stack = d.stack);
        this.m = a;
        this.name = "PermissionError"
    };
    ya(tf, Error);
    function uf(a, b) {
        if (Array.isArray(a)) {
            Object.defineProperty(a, "context", {
                value: {
                    line: b[0]
                }
            });
            for (var c = 1; c < a.length; c++)
                uf(a[c], b[c])
        }
    }
    ;var vf = function(a, b) {
        var c;
        c = Error.call(this);
        this.message = c.message;
        "stack"in c && (this.stack = c.stack);
        this.xm = a;
        this.F = b;
        this.m = []
    };
    ya(vf, Error);
    var xf = function() {
        return function(a, b) {
            a instanceof vf || (a = new vf(a,wf));
            b && a.m.push(b);
            throw a;
        }
    };
    function wf(a) {
        if (!a.length)
            return a;
        a.push({
            id: "main",
            line: 0
        });
        for (var b = a.length - 1; 0 < b; b--)
            qb(a[b].id) && a.splice(b++, 1);
        for (var c = a.length - 1; 0 < c; c--)
            a[c].line = a[c - 1].line;
        a.splice(0, 1);
        return a
    }
    ;var Af = function(a) {
        function b(r) {
            for (var t = 0; t < r.length; t++)
                d[r[t]] = !0
        }
        for (var c = [], d = [], e = yf(a), f = 0; f < af.length; f++) {
            var g = af[f]
              , h = zf(g, e);
            if (h) {
                for (var m = g.add || [], n = 0; n < m.length; n++)
                    c[m[n]] = !0;
                b(g.block || [])
            } else
                null === h && b(g.block || []);
        }
        for (var p = [], q = 0; q < cf.length; q++)
            c[q] && !d[q] && (p[q] = !0);
        return p
    }
      , zf = function(a, b) {
        for (var c = a["if"] || [], d = 0; d < c.length; d++) {
            var e = b(c[d]);
            if (0 === e)
                return !1;
            if (2 === e)
                return null
        }
        for (var f = a.unless || [], g = 0; g < f.length; g++) {
            var h = b(f[g]);
            if (2 === h)
                return null;
            if (1 === h)
                return !1
        }
        return !0
    }
      , yf = function(a) {
        var b = [];
        return function(c) {
            void 0 === b[c] && (b[c] = rf(bf[c], a));
            return b[c]
        }
    };
    var Bf = {
        ql: function(a, b) {
            b[Ce.ei] && "string" === typeof a && (a = 1 == b[Ce.ei] ? a.toLowerCase() : a.toUpperCase());
            b.hasOwnProperty(Ce.gi) && null === a && (a = b[Ce.gi]);
            b.hasOwnProperty(Ce.ii) && void 0 === a && (a = b[Ce.ii]);
            b.hasOwnProperty(Ce.hi) && !0 === a && (a = b[Ce.hi]);
            b.hasOwnProperty(Ce.fi) && !1 === a && (a = b[Ce.fi]);
            return a
        }
    };
    var Cf = function() {
        this.m = {}
    }
      , Ef = function(a, b) {
        var c = Df.F, d;
        null != (d = c.m)[a] || (d[a] = []);
        c.m[a].push(function() {
            return b.apply(null, qa(za.apply(0, arguments)))
        })
    };
    function Ff(a, b, c, d) {
        if (a)
            for (var e = 0; e < a.length; e++) {
                var f = void 0
                  , g = "A policy function denied the permission request";
                try {
                    f = a[e](b, c, d),
                    g += "."
                } catch (h) {
                    g = "string" === typeof h ? g + (": " + h) : h instanceof Error ? g + (": " + h.message) : g + "."
                }
                if (!f)
                    throw new tf(c,d,g);
            }
    }
    function Gf(a, b, c) {
        return function() {
            var d = arguments[0];
            if (d) {
                var e = a.m[d]
                  , f = a.m.all;
                if (e || f) {
                    var g = c.apply(void 0, Array.prototype.slice.call(arguments, 0));
                    Ff(e, b, d, g);
                    Ff(f, b, d, g)
                }
            }
        }
    }
    ;var Kf = function() {
        var a = data.permissions || {}
          , b = Hf.ctid
          , c = this;
        this.F = new Cf;
        this.m = {};
        var d = {}
          , e = {}
          , f = Gf(this.F, b, function() {
            var g = arguments[0];
            return g && d[g] ? d[g].apply(void 0, Array.prototype.slice.call(arguments, 0)) : {}
        });
        z(a, function(g, h) {
            var m = {};
            z(h, function(p, q) {
                var r = If(p, q);
                m[p] = r.assert;
                d[p] || (d[p] = r.O);
                r.Fj && !e[p] && (e[p] = r.Fj)
            });
            var n = function(p) {
                var q = za.apply(1, arguments);
                if (!m[p])
                    throw Jf(p, {}, "The requested additional permission " + p + " is not configured.");
                f.apply(null, [p].concat(qa(q)))
            };
            c.m[g] = function(p, q) {
                var r = m[p];
                if (!r)
                    throw Jf(p, {}, "The requested permission " + p + " is not configured.");
                var t = Array.prototype.slice.call(arguments, 0);
                r.apply(void 0, t);
                f.apply(void 0, t);
                var u = e[p];
                u && u.apply(null, [n].concat(qa(t.slice(1))))
            }
        })
    }
      , Lf = function(a) {
        return Df.m[a] || function() {}
    };
    function If(a, b) {
        var c = nf(a, b);
        c.vtp_permissionName = a;
        c.vtp_createPermissionError = Jf;
        try {
            return of(c)
        } catch (d) {
            return {
                assert: function(e) {
                    throw new tf(e,{},"Permission " + e + " is unknown.");
                },
                O: function() {
                    throw new tf(a,{},"Permission " + a + " is unknown.");
                }
            }
        }
    }
    function Jf(a, b, c) {
        return new tf(a,b,c)
    }
    ;var Mf = !1;
    var Nf = {};
    Nf.fn = yb('');
    Nf.yl = yb('');
    var Of = Mf
      , Qf = Nf.yl
      , Rf = Nf.fn;
    var Zf = {}
      , $f = (Zf.uaa = !0,
    Zf.uab = !0,
    Zf.uafvl = !0,
    Zf.uamb = !0,
    Zf.uam = !0,
    Zf.uap = !0,
    Zf.uapv = !0,
    Zf.uaw = !0,
    Zf);
    var dg = /^[a-z$_][\w$]*$/i
      , eg = /^(?:[a-z_$][a-z_$0-9]*\.)*[a-z_$][a-z_$0-9]*(?:\.\*)?$/i
      , fg = function(a, b) {
        for (var c = 0; c < b.length; c++) {
            var d = a
              , e = b[c];
            if (!eg.exec(e))
                throw Error("Invalid key wildcard");
            var f = e.indexOf(".*"), g = -1 !== f && f === e.length - 2, h = g ? e.slice(0, e.length - 2) : e, m;
            a: if (0 === d.length)
                m = !1;
            else {
                for (var n = d.split("."), p = 0; p < n.length; p++)
                    if (!dg.exec(n[p])) {
                        m = !1;
                        break a
                    }
                m = !0
            }
            if (!m || h.length > d.length || !g && d.length != e.length ? 0 : g ? 0 === d.indexOf(h) && (d === h || "." == d.charAt(h.length)) : d === h)
                return !0
        }
        return !1
    };
    var gg = ["matches", "webkitMatchesSelector", "mozMatchesSelector", "msMatchesSelector", "oMatchesSelector"];
    function hg(a, b) {
        a = String(a);
        b = String(b);
        var c = a.length - b.length;
        return 0 <= c && a.indexOf(b, c) === c
    }
    var ig = new vb;
    function jg(a, b, c) {
        var d = c ? "i" : void 0;
        try {
            var e = String(b) + d
              , f = ig.get(e);
            f || (f = new RegExp(b,d),
            ig.set(e, f));
            return f.test(a)
        } catch (g) {
            return !1
        }
    }
    function kg(a, b) {
        return 0 <= String(a).indexOf(String(b))
    }
    function lg(a, b) {
        return String(a) === String(b)
    }
    function mg(a, b) {
        return Number(a) >= Number(b)
    }
    function ng(a, b) {
        return Number(a) <= Number(b)
    }
    function og(a, b) {
        return Number(a) > Number(b)
    }
    function pg(a, b) {
        return Number(a) < Number(b)
    }
    function qg(a, b) {
        return 0 === String(a).indexOf(String(b))
    }
    ;var rg = function(a, b) {
        return a.length && b.length && a.lastIndexOf(b) === a.length - b.length
    }
      , sg = function(a, b) {
        var c = "*" === b.charAt(b.length - 1) || "/" === b || "/*" === b;
        rg(b, "/*") && (b = b.slice(0, -2));
        rg(b, "?") && (b = b.slice(0, -1));
        var d = b.split("*");
        if (!c && 1 === d.length)
            return a === d[0];
        for (var e = -1, f = 0; f < d.length; f++) {
            var g = d[f];
            if (g) {
                e = a.indexOf(g, e);
                if (-1 === e || 0 === f && 0 !== e)
                    return !1;
                e += g.length
            }
        }
        if (c || e === a.length)
            return !0;
        var h = d[d.length - 1];
        return a.lastIndexOf(h) === a.length - h.length
    }
      , tg = /^[a-z0-9-]+$/i
      , ug = /^https:\/\/(\*\.|)((?:[a-z0-9-]+\.)+[a-z0-9-]+)\/(.*)$/i
      , wg = function(a, b) {
        var c;
        if (!(c = !vg(a))) {
            var d;
            a: {
                var e = a.hostname.split(".");
                if (2 > e.length)
                    d = !1;
                else {
                    for (var f = 0; f < e.length; f++)
                        if (!tg.exec(e[f])) {
                            d = !1;
                            break a
                        }
                    d = !0
                }
            }
            c = !d
        }
        if (c)
            return !1;
        for (var g = 0; g < b.length; g++) {
            var h;
            var m = a
              , n = b[g];
            if (!ug.exec(n))
                throw Error("Invalid Wildcard");
            var p = n.slice(8), q = p.slice(0, p.indexOf("/")), r;
            var t = m.hostname
              , u = q;
            if (0 !== u.indexOf("*."))
                r = t.toLowerCase() === u.toLowerCase();
            else {
                u = u.slice(2);
                var v = t.toLowerCase().indexOf(u.toLowerCase());
                r = -1 === v ? !1 : t.length === u.length ? !0 : t.length !== u.length + v ? !1 : "." === t[v - 1]
            }
            if (r) {
                var w = p.slice(p.indexOf("/"));
                h = sg(m.pathname + m.search, w) ? !0 : !1
            } else
                h = !1;
            if (h)
                return !0
        }
        return !1
    }
      , vg = function(a) {
        return "https:" === a.protocol && (!a.port || "443" === a.port)
    };
    var xg = /^[1-9a-zA-Z_-][1-9a-c][1-9a-v]\d$/;
    function yg(a, b) {
        for (var c = "", d = !0; 7 < a; ) {
            var e = a & 31;
            a >>= 5;
            d ? d = !1 : e |= 32;
            c = Ae(e) + c
        }
        a <<= 2;
        d || (a |= 32);
        return c = Ae(a | b) + c
    }
    ;var zg = /^([a-z][a-z0-9]*):(!|\?)(\*|string|boolean|number|Fn|PixieMap|List|OpaqueValue)$/i
      , Ag = {
        Fn: "function",
        PixieMap: "Object",
        List: "Array"
    }
      , K = function(a, b, c) {
        for (var d = 0; d < b.length; d++) {
            var e = zg.exec(b[d]);
            if (!e)
                throw Error("Internal Error in " + a);
            var f = e[1]
              , g = "!" === e[2]
              , h = e[3]
              , m = c[d];
            if (null == m) {
                if (g)
                    throw Error("Error in " + a + ". Required argument " + f + " not supplied.");
            } else if ("*" !== h) {
                var n = typeof m;
                m instanceof Tc ? n = "Fn" : m instanceof $a ? n = "List" : m instanceof cb ? n = "PixieMap" : m instanceof Yc && (n = "OpaqueValue");
                if (n != h)
                    throw Error("Error in " + a + ". Argument " + f + " has type " + (Ag[n] || n) + ", which does not match required type " + (Ag[h] || h) + ".");
            }
        }
    };
    function Bg(a) {
        return "" + a
    }
    function Cg(a, b) {
        var c = [];
        return c
    }
    ;var Dg = function(a, b) {
        var c = new Tc(a,function() {
            for (var d = Array.prototype.slice.call(arguments, 0), e = 0; e < d.length; e++)
                d[e] = this.evaluate(d[e]);
            try {
                return b.apply(this, d)
            } catch (g) {
                if (bd())
                    throw new dd(g.message);
                throw g;
            }
        }
        );
        c.Lb();
        return c
    }
      , Eg = function(a, b) {
        var c = new cb, d;
        for (d in b)
            if (b.hasOwnProperty(d)) {
                var e = b[d];
                pb(e) ? c.set(d, Dg(a + "_" + d, e)) : Xa(e) ? c.set(d, Eg(a + "_" + d, e)) : (qb(e) || l(e) || "boolean" === typeof e) && c.set(d, e)
            }
        c.Lb();
        return c
    };
    var Fg = function(a, b) {
        K(this.getName(), ["apiName:!string", "message:?string"], arguments);
        var c = {}
          , d = new cb;
        return d = Eg("AssertApiSubject", c)
    };
    var Gg = function(a, b) {
        K(this.getName(), ["actual:?*", "message:?string"], arguments);
        if (a instanceof $c)
            throw Error("Argument actual cannot have type Promise. Assertions on asynchronous code aren't supported.");
        var c = {}
          , d = new cb;
        return d = Eg("AssertThatSubject", c)
    };
    function Hg(a) {
        return function() {
            for (var b = [], c = this.J, d = 0; d < arguments.length; ++d)
                b.push(J(arguments[d], c));
            return ad(a.apply(null, b))
        }
    }
    var Jg = function() {
        for (var a = Math, b = Ig, c = {}, d = 0; d < b.length; d++) {
            var e = b[d];
            a.hasOwnProperty(e) && (c[e] = Hg(a[e].bind(a)))
        }
        return c
    };
    var Kg = function(a) {
        var b;
        return b
    };
    var Lg = function(a) {
        var b;
        return b
    };
    var Mg = function(a) {
        try {
            return encodeURI(a)
        } catch (b) {}
    };
    var Ng = function(a) {
        try {
            return encodeURIComponent(a)
        } catch (b) {}
    };
    function Og(a, b) {
        var c = !1;
        return c
    }
    Og.K = "internal.evaluateBooleanExpression";
    var Tg = function(a) {
        K(this.getName(), ["message:?string"], arguments);
    };
    var Ug = function(a, b) {
        K(this.getName(), ["min:!number", "max:!number"], arguments);
        return tb(a, b)
    };
    var Vg = function() {
        return (new Date).getTime()
    };
    var Wg = function(a) {
        if (null === a)
            return "null";
        if (a instanceof $a)
            return "array";
        if (a instanceof Tc)
            return "function";
        if (a instanceof Yc) {
            a = a.getValue();
            if (void 0 === a.constructor || void 0 === a.constructor.name) {
                var b = String(a);
                return b.substring(8, b.length - 1)
            }
            return String(a.constructor.name)
        }
        return typeof a
    };
    var Xg = function(a) {
        function b(c) {
            return function(d) {
                try {
                    return c(d)
                } catch (e) {
                    (Of || Rf) && a.call(this, e.message)
                }
            }
        }
        return {
            parse: b(function(c) {
                return ad(JSON.parse(c))
            }),
            stringify: b(function(c) {
                return JSON.stringify(J(c))
            })
        }
    };
    var Yg = function(a) {
        return xb(J(a, this.J))
    };
    var Zg = function(a) {
        return Number(J(a, this.J))
    };
    var $g = function(a) {
        return null === a ? "null" : void 0 === a ? "undefined" : a.toString()
    };
    var ah = function(a, b, c) {
        var d = null
          , e = !1;
        K(this.getName(), ["tableObj:!List", "keyColumnName:!string", "valueColumnName:!string"], arguments);
        d = new cb;
        for (var f = 0; f < a.length(); f++) {
            var g = a.get(f);
            g instanceof cb && g.has(b) && g.has(c) && (d.set(g.get(b), g.get(c)),
            e = !0)
        }
        return e ? d : null
    };
    var Ig = "floor ceil round max min abs pow sqrt".split(" ");
    var bh = function() {
        var a = {};
        return {
            Il: function(b) {
                return a.hasOwnProperty(b) ? a[b] : void 0
            },
            hk: function(b, c) {
                a[b] = c
            },
            reset: function() {
                a = {}
            }
        }
    }
      , ch = function(a, b) {
        return function() {
            var c = Array.prototype.slice.call(arguments, 0);
            c.unshift(b);
            return Tc.prototype.invoke.apply(a, c)
        }
    }
      , dh = function(a, b) {
        K(this.getName(), ["apiName:!string", "mock:?*"], arguments);
    }
      , eh = function(a, b) {
        K(this.getName(), ["apiName:!string", "mock:!PixieMap"], arguments);
    };
    var fh = {};
    var gh = function(a) {
        var b = new cb;
        if (a instanceof $a)
            for (var c = a.Zb(), d = 0; d < c.length(); d++) {
                var e = c.get(d);
                a.has(e) && b.set(e, a.get(e))
            }
        else if (a instanceof Tc)
            for (var f = Ta(a, 1), g = 0; g < f.length; g++) {
                var h = f[g];
                b.set(h, a.get(h))
            }
        else
            for (var m = 0; m < a.length; m++)
                b.set(m, a[m]);
        return b
    };
    fh.keys = function(a) {
        K(this.getName(), ["input:!*"], arguments);
        if (a instanceof $a || a instanceof Tc || "string" === typeof a)
            a = gh(a);
        if (a instanceof cb)
            return a.Zb();
        return new $a
    }
    ;
    fh.values = function(a) {
        K(this.getName(), ["input:!*"], arguments);
        if (a instanceof $a || a instanceof Tc || "string" === typeof a)
            a = gh(a);
        if (a instanceof cb)
            return new $a(Ta(a, 2));
        return new $a
    }
    ;
    fh.entries = function(a) {
        K(this.getName(), ["input:!*"], arguments);
        if (a instanceof $a || a instanceof Tc || "string" === typeof a)
            a = gh(a);
        if (a instanceof cb)
            return db(a);
        return new $a
    }
    ;
    fh.freeze = function(a) {
        (a instanceof cb || a instanceof $a || a instanceof Tc) && a.Lb();
        return a
    }
    ;
    fh.delete = function(a, b) {
        if (a instanceof cb && !a.F)
            return a.zf(b),
            !0;
        return !1
    }
    ;
    var M = function(a, b, c) {
        var d = a.J.m;
        if (!d)
            throw Error("Missing program state.");
        if (d.Jm) {
            try {
                d.Gj.apply(null, Array.prototype.slice.call(arguments, 1))
            } catch (e) {
                throw lb("TAGGING", 21),
                e;
            }
            return
        }
        d.Gj.apply(null, Array.prototype.slice.call(arguments, 1))
    };
    var hh = function() {
        this.m = {};
        this.F = {};
    };
    hh.prototype.get = function(a, b) {
        var c = this.m.hasOwnProperty(a) ? this.m[a] : void 0;
        return c
    }
    ;
    hh.prototype.add = function(a, b, c) {
        if (this.m.hasOwnProperty(a))
            throw "Attempting to add a function which already exists: " + a + ".";
        if (this.F.hasOwnProperty(a))
            throw "Attempting to add an API with an existing private API name: " + a + ".";
        this.m[a] = c ? void 0 : pb(b) ? Dg(a, b) : Eg(a, b)
    }
    ;
    function ih(a, b) {
        var c = void 0;
        return c
    }
    ;function jh() {
        var a = {};
        return a
    }
    ;function nh(a) {
        return oh ? H.querySelectorAll(a) : null
    }
    function ph(a, b) {
        if (!oh)
            return null;
        if (Element.prototype.closest)
            try {
                return a.closest(b)
            } catch (e) {
                return null
            }
        var c = Element.prototype.matches || Element.prototype.webkitMatchesSelector || Element.prototype.mozMatchesSelector || Element.prototype.msMatchesSelector || Element.prototype.oMatchesSelector
          , d = a;
        if (!H.documentElement.contains(d))
            return null;
        do {
            try {
                if (c.call(d, b))
                    return d
            } catch (e) {
                break
            }
            d = d.parentElement || d.parentNode
        } while (null !== d && 1 === d.nodeType);
        return null
    }
    var qh = !1;
    if (H.querySelectorAll)
        try {
            var rh = H.querySelectorAll(":root");
            rh && 1 == rh.length && rh[0] == H.documentElement && (qh = !0)
        } catch (a) {}
    var oh = qh;
    var sh = /^[0-9A-Fa-f]{64}$/;
    function th(a) {
        try {
            return (new TextEncoder).encode(a)
        } catch (e) {
            for (var b = [], c = 0; c < a.length; c++) {
                var d = a.charCodeAt(c);
                128 > d ? b.push(d) : 2048 > d ? b.push(192 | d >> 6, 128 | d & 63) : 55296 > d || 57344 <= d ? b.push(224 | d >> 12, 128 | d >> 6 & 63, 128 | d & 63) : (d = 65536 + ((d & 1023) << 10 | a.charCodeAt(++c) & 1023),
                b.push(240 | d >> 18, 128 | d >> 12 & 63, 128 | d >> 6 & 63, 128 | d & 63))
            }
            return new Uint8Array(b)
        }
    }
    function uh(a) {
        if ("" === a || "e0" === a)
            return Promise.resolve(a);
        var b;
        if (null == (b = G.crypto) ? 0 : b.subtle) {
            if (sh.test(a))
                return Promise.resolve(a);
            try {
                var c = th(a);
                return G.crypto.subtle.digest("SHA-256", c).then(function(d) {
                    var e = Array.from(new Uint8Array(d)).map(function(f) {
                        return String.fromCharCode(f)
                    }).join("");
                    return G.btoa(e).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "")
                }).catch(function() {
                    return "e2"
                })
            } catch (d) {
                return Promise.resolve("e2")
            }
        } else
            return Promise.resolve("e1")
    }
    ;function O(a) {
        lb("GTM", a)
    }
    ;var yh = function(a) {
        var b = {}
          , c = ["tv.1"]
          , d = 0;
        for (var e = na(a), f = e.next(); !f.done; f = e.next()) {
            var g = f.value;
            if ("" !== g.value) {
                var h, m = void 0, n = g.name, p = g.value, q = vh[n];
                if (q) {
                    var r = null != (m = g.index) ? m : ""
                      , t = q + "__" + d;
                    -1 === wh.indexOf(n) || /^e\d+$/.test(p) || xh.test(p) || sh.test(p) ? h = encodeURIComponent(encodeURIComponent(p)) : (h = "${userData." + t + "|sha256}",
                    b[t] = p,
                    d++);
                    c.push("" + q + r + "." + h)
                }
            }
        }
        var u = c.join("~");
        return {
            Th: {
                userData: b
            },
            Wm: u,
            hn: d
        }
    }
      , Ah = function(a) {
        if (G.Promise)
            try {
                return new Promise(function(b) {
                    zh(a, function(c, d) {
                        b({
                            Sj: c,
                            Kh: d
                        })
                    })
                }
                )
            } catch (b) {}
    }
      , Bh = function(a) {
        for (var b = ["tv.1"], c = 0, d = 0; d < a.length; ++d) {
            var e = a[d].name
              , f = a[d].value
              , g = a[d].index
              , h = vh[e];
            h && f && (-1 === wh.indexOf(e) || /^e\d+$/.test(f) || xh.test(f) || sh.test(f)) && (void 0 !== g && (h += g),
            b.push(h + "." + f),
            c++)
        }
        1 === a.length && "error_code" === a[0].name && (c = 0);
        return {
            Tj: encodeURIComponent(b.join("~")),
            Kh: c
        }
    }
      , zh = function(a, b) {
        Ch(a, function(c) {
            var d = Bh(c);
            b(d.Tj, d.Kh)
        })
    }
      , Kh = function(a) {
        function b(r, t, u, v) {
            var w = Dh(r);
            "" !== w && (sh.test(w) ? h.push({
                name: t,
                value: w,
                index: v
            }) : h.push({
                name: t,
                value: u(w),
                index: v
            }))
        }
        function c(r, t) {
            var u = r;
            if (l(u) || Array.isArray(u)) {
                u = rb(r);
                for (var v = 0; v < u.length; ++v) {
                    var w = Dh(u[v])
                      , y = sh.test(w);
                    t && !y && O(89);
                    !t && y && O(88)
                }
            }
        }
        function d(r, t) {
            var u = r[t];
            c(u, !1);
            var v = Eh[t];
            r[v] && (r[t] && O(90),
            u = r[v],
            c(u, !0));
            return u
        }
        function e(r, t, u) {
            for (var v = rb(d(r, t)), w = 0; w < v.length; ++w)
                b(v[w], t, u)
        }
        function f(r, t, u, v) {
            var w = d(r, t);
            b(w, t, u, v)
        }
        function g(r) {
            return function(t) {
                O(64);
                return r(t)
            }
        }
        var h = [];
        if ("https:" !== G.location.protocol)
            return h.push({
                name: "error_code",
                value: "e3",
                index: void 0
            }),
            h;
        e(a, "email", Fh);
        e(a, "phone_number", Gh);
        e(a, "first_name", g(Hh));
        e(a, "last_name", g(Hh));
        var m = a.home_address || {};
        e(m, "street", g(Ih));
        e(m, "city", g(Ih));
        e(m, "postal_code", g(Jh));
        e(m, "region", g(Ih));
        e(m, "country", g(Jh));
        for (var n = rb(a.address || {}), p = 0; p < n.length; p++) {
            var q = n[p];
            f(q, "first_name", Hh, p);
            f(q, "last_name", Hh, p);
            f(q, "street", Ih, p);
            f(q, "city", Ih, p);
            f(q, "postal_code", Jh, p);
            f(q, "region", Ih, p);
            f(q, "country", Jh, p)
        }
        return h
    }
      , Ch = function(a, b) {
        var c = Kh(a);
        Lh(c, b)
    }
      , Dh = function(a) {
        return null == a ? "" : l(a) ? Ab(String(a)) : "e0"
    }
      , Jh = function(a) {
        return a.replace(Mh, "")
    }
      , Hh = function(a) {
        return Ih(a.replace(/\s/g, ""))
    }
      , Ih = function(a) {
        return Ab(a.replace(Nh, "").toLowerCase())
    }
      , Gh = function(a) {
        a = a.replace(/[\s-()/.]/g, "");
        "+" !== a.charAt(0) && (a = "+" + a);
        return Oh.test(a) ? a : "e0"
    }
      , Fh = function(a) {
        var b = a.toLowerCase().split("@");
        if (2 === b.length) {
            var c = b[0];
            /^(gmail|googlemail)\./.test(b[1]) && (c = c.replace(/\./g, ""));
            c = c + "@" + b[1];
            if (Ph.test(c))
                return c
        }
        return "e0"
    }
      , Lh = function(a, b) {
        a.some(function(c) {
            c.value && wh.indexOf(c.name)
        }) ? b(a) : G.Promise ? Promise.all(a.map(function(c) {
            return c.value && -1 !== wh.indexOf(c.name) ? uh(c.value).then(function(d) {
                c.value = d
            }) : Promise.resolve()
        })).then(function() {
            b(a)
        }).catch(function() {
            b([])
        }) : b([])
    }
      , Nh = /[0-9`~!@#$%^&*()_\-+=:;<>,.?|/\\[\]]/g
      , Ph = /^\S+@\S+\.\S+$/
      , Oh = /^\+\d{10,15}$/
      , Mh = /[.~]/g
      , xh = /^[0-9A-Za-z_-]{43}$/
      , Qh = {}
      , vh = (Qh.email = "em",
    Qh.phone_number = "pn",
    Qh.first_name = "fn",
    Qh.last_name = "ln",
    Qh.street = "sa",
    Qh.city = "ct",
    Qh.region = "rg",
    Qh.country = "co",
    Qh.postal_code = "pc",
    Qh.error_code = "ec",
    Qh)
      , Rh = {}
      , Eh = (Rh.email = "sha256_email_address",
    Rh.phone_number = "sha256_phone_number",
    Rh.first_name = "sha256_first_name",
    Rh.last_name = "sha256_last_name",
    Rh.street = "sha256_street",
    Rh)
      , wh = Object.freeze(["email", "phone_number", "first_name", "last_name", "street"]);
    var P = {
        g: {
            Aa: "ad_personalization",
            R: "ad_storage",
            P: "ad_user_data",
            W: "analytics_storage",
            kc: "region",
            mc: "consent_updated",
            Ue: "wait_for_update",
            ki: "app_remove",
            li: "app_store_refund",
            mi: "app_store_subscription_cancel",
            ni: "app_store_subscription_convert",
            oi: "app_store_subscription_renew",
            uk: "consent_update",
            Xf: "add_payment_info",
            Yf: "add_shipping_info",
            nc: "add_to_cart",
            oc: "remove_from_cart",
            Zf: "view_cart",
            Pb: "begin_checkout",
            qc: "select_item",
            hb: "view_item_list",
            Bb: "select_promotion",
            ib: "view_promotion",
            Ja: "purchase",
            sc: "refund",
            Na: "view_item",
            cg: "add_to_wishlist",
            vk: "exception",
            ri: "first_open",
            si: "first_visit",
            fa: "gtag.config",
            Ra: "gtag.get",
            ui: "in_app_purchase",
            Qb: "page_view",
            wk: "screen_view",
            vi: "session_start",
            xk: "timing_complete",
            yk: "track_social",
            uc: "user_engagement",
            jb: "gclgb",
            Sa: "gclid",
            wi: "gclgs",
            xi: "gclst",
            ja: "ads_data_redaction",
            yi: "gad_source",
            Id: "gclid_url",
            zi: "gclsrc",
            dg: "gbraid",
            Ve: "wbraid",
            oa: "allow_ad_personalization_signals",
            We: "allow_custom_scripts",
            Xe: "allow_display_features",
            Jd: "allow_enhanced_conversions",
            kb: "allow_google_signals",
            Ea: "allow_interest_groups",
            zk: "app_id",
            Ak: "app_installer_id",
            Bk: "app_name",
            Ck: "app_version",
            Cb: "auid",
            Ai: "auto_detection_enabled",
            Rb: "aw_remarketing",
            Ye: "aw_remarketing_only",
            Kd: "discount",
            Ld: "aw_feed_country",
            Md: "aw_feed_language",
            ia: "items",
            Nd: "aw_merchant_id",
            eg: "aw_basket_type",
            Qc: "campaign_content",
            Rc: "campaign_id",
            Sc: "campaign_medium",
            Tc: "campaign_name",
            Uc: "campaign",
            Vc: "campaign_source",
            Wc: "campaign_term",
            lb: "client_id",
            Bi: "rnd",
            fg: "consent_update_type",
            Ci: "content_group",
            Di: "content_type",
            Za: "conversion_cookie_prefix",
            Xc: "conversion_id",
            wa: "conversion_linker",
            Ei: "conversion_linker_disabled",
            Sb: "conversion_api",
            Ze: "cookie_deprecation",
            Ta: "cookie_domain",
            Ua: "cookie_expires",
            ab: "cookie_flags",
            vc: "cookie_name",
            Db: "cookie_path",
            Oa: "cookie_prefix",
            wc: "cookie_update",
            xc: "country",
            Ba: "currency",
            Od: "customer_lifetime_value",
            Yc: "custom_map",
            gg: "gcldc",
            Pd: "dclid",
            Fi: "debug_mode",
            la: "developer_id",
            Gi: "disable_merchant_reported_purchases",
            Zc: "dc_custom_params",
            Hi: "dc_natural_search",
            hg: "dynamic_event_settings",
            ig: "affiliation",
            Qd: "checkout_option",
            af: "checkout_step",
            jg: "coupon",
            bd: "item_list_name",
            bf: "list_name",
            Ii: "promotions",
            dd: "shipping",
            cf: "tax",
            Rd: "engagement_time_msec",
            Sd: "enhanced_client_id",
            Td: "enhanced_conversions",
            kg: "enhanced_conversions_automatic_settings",
            Ud: "estimated_delivery_date",
            df: "euid_logged_in_state",
            ed: "event_callback",
            Dk: "event_category",
            ob: "event_developer_id_string",
            Ek: "event_label",
            fd: "event",
            Vd: "event_settings",
            Wd: "event_timeout",
            Fk: "description",
            Gk: "fatal",
            Ji: "experiments",
            ef: "firebase_id",
            yc: "first_party_collection",
            Xd: "_x_20",
            pb: "_x_19",
            Ki: "fledge_drop_reason",
            lg: "fledge",
            mg: "flight_error_code",
            ng: "flight_error_message",
            Li: "fl_activity_category",
            Mi: "fl_activity_group",
            og: "fl_advertiser_id",
            Ni: "fl_ar_dedupe",
            pg: "match_id",
            Oi: "fl_random_number",
            Pi: "tran",
            Qi: "u",
            Yd: "gac_gclid",
            zc: "gac_wbraid",
            qg: "gac_wbraid_multiple_conversions",
            rg: "ga_restrict_domain",
            ff: "ga_temp_client_id",
            Ac: "gdpr_applies",
            sg: "geo_granularity",
            Eb: "value_callback",
            qb: "value_key",
            Hk: "google_ng",
            Ik: "google_ono",
            Tb: "google_signals",
            ug: "google_tld",
            Zd: "groups",
            vg: "gsa_experiment_id",
            Ri: "gtm_up",
            Fb: "iframe_state",
            gd: "ignore_referrer",
            hf: "internal_traffic_results",
            Ub: "is_legacy_converted",
            Gb: "is_legacy_loaded",
            ae: "is_passthrough",
            hd: "_lps",
            Pa: "language",
            be: "legacy_developer_id_string",
            xa: "linker",
            Bc: "accept_incoming",
            sb: "decorate_forms",
            Z: "domains",
            Hb: "url_position",
            wg: "method",
            Jk: "name",
            jd: "new_customer",
            xg: "non_interaction",
            Si: "optimize_id",
            Ti: "page_hostname",
            kd: "page_path",
            Fa: "page_referrer",
            Ib: "page_title",
            yg: "passengers",
            zg: "phone_conversion_callback",
            Ui: "phone_conversion_country_code",
            Ag: "phone_conversion_css_class",
            Vi: "phone_conversion_ids",
            Bg: "phone_conversion_number",
            Cg: "phone_conversion_options",
            Dg: "_protected_audience_enabled",
            ld: "quantity",
            ce: "redact_device_info",
            jf: "referral_exclusion_definition",
            Vb: "restricted_data_processing",
            Wi: "retoken",
            Kk: "sample_rate",
            kf: "screen_name",
            Jb: "screen_resolution",
            Xi: "search_term",
            Ka: "send_page_view",
            Wb: "send_to",
            md: "server_container_url",
            nd: "session_duration",
            de: "session_engaged",
            lf: "session_engaged_time",
            tb: "session_id",
            ee: "session_number",
            Eg: "_shared_user_id",
            od: "delivery_postal_code",
            Lk: "temporary_client_id",
            nf: "topmost_url",
            Yi: "tracking_id",
            pf: "traffic_type",
            Ca: "transaction_id",
            Kb: "transport_url",
            Fg: "trip_type",
            Xb: "update",
            Va: "url_passthrough",
            qf: "_user_agent_architecture",
            rf: "_user_agent_bitness",
            tf: "_user_agent_full_version_list",
            uf: "_user_agent_mobile",
            vf: "_user_agent_model",
            wf: "_user_agent_platform",
            xf: "_user_agent_platform_version",
            yf: "_user_agent_wow64",
            Ga: "user_data",
            Gg: "user_data_auto_latency",
            Hg: "user_data_auto_meta",
            Ig: "user_data_auto_multi",
            Jg: "user_data_auto_selectors",
            Kg: "user_data_auto_status",
            pd: "user_data_mode",
            fe: "user_data_settings",
            Da: "user_id",
            cb: "user_properties",
            Zi: "_user_region",
            he: "us_privacy_string",
            qa: "value",
            Lg: "wbraid_multiple_conversions",
            ij: "_host_name",
            jj: "_in_page_command",
            kj: "_is_passthrough_cid",
            Mb: "non_personalized_ads",
            oe: "_sst_parameters",
            nb: "conversion_label",
            ya: "page_location",
            rb: "global_developer_id_string",
            Cc: "tc_privacy_string"
        }
    }
      , Sh = {}
      , Th = Object.freeze((Sh[P.g.oa] = 1,
    Sh[P.g.Xe] = 1,
    Sh[P.g.Jd] = 1,
    Sh[P.g.kb] = 1,
    Sh[P.g.ia] = 1,
    Sh[P.g.Ta] = 1,
    Sh[P.g.Ua] = 1,
    Sh[P.g.ab] = 1,
    Sh[P.g.vc] = 1,
    Sh[P.g.Db] = 1,
    Sh[P.g.Oa] = 1,
    Sh[P.g.wc] = 1,
    Sh[P.g.Yc] = 1,
    Sh[P.g.la] = 1,
    Sh[P.g.hg] = 1,
    Sh[P.g.ed] = 1,
    Sh[P.g.Vd] = 1,
    Sh[P.g.Wd] = 1,
    Sh[P.g.yc] = 1,
    Sh[P.g.rg] = 1,
    Sh[P.g.Tb] = 1,
    Sh[P.g.ug] = 1,
    Sh[P.g.Zd] = 1,
    Sh[P.g.hf] = 1,
    Sh[P.g.Ub] = 1,
    Sh[P.g.Gb] = 1,
    Sh[P.g.xa] = 1,
    Sh[P.g.jf] = 1,
    Sh[P.g.Vb] = 1,
    Sh[P.g.Ka] = 1,
    Sh[P.g.Wb] = 1,
    Sh[P.g.md] = 1,
    Sh[P.g.nd] = 1,
    Sh[P.g.lf] = 1,
    Sh[P.g.od] = 1,
    Sh[P.g.Kb] = 1,
    Sh[P.g.Xb] = 1,
    Sh[P.g.fe] = 1,
    Sh[P.g.cb] = 1,
    Sh[P.g.oe] = 1,
    Sh));
    Object.freeze([P.g.ya, P.g.Fa, P.g.Ib, P.g.Pa, P.g.kf, P.g.Da, P.g.ef, P.g.Ci]);
    var Uh = {}
      , Vh = Object.freeze((Uh[P.g.ki] = 1,
    Uh[P.g.li] = 1,
    Uh[P.g.mi] = 1,
    Uh[P.g.ni] = 1,
    Uh[P.g.oi] = 1,
    Uh[P.g.ri] = 1,
    Uh[P.g.si] = 1,
    Uh[P.g.ui] = 1,
    Uh[P.g.vi] = 1,
    Uh[P.g.uc] = 1,
    Uh))
      , Wh = {}
      , Xh = Object.freeze((Wh[P.g.Xf] = 1,
    Wh[P.g.Yf] = 1,
    Wh[P.g.nc] = 1,
    Wh[P.g.oc] = 1,
    Wh[P.g.Zf] = 1,
    Wh[P.g.Pb] = 1,
    Wh[P.g.qc] = 1,
    Wh[P.g.hb] = 1,
    Wh[P.g.Bb] = 1,
    Wh[P.g.ib] = 1,
    Wh[P.g.Ja] = 1,
    Wh[P.g.sc] = 1,
    Wh[P.g.Na] = 1,
    Wh[P.g.cg] = 1,
    Wh))
      , Yh = Object.freeze([P.g.oa, P.g.kb, P.g.wc, P.g.yc, P.g.gd, P.g.Ka, P.g.Xb])
      , Zh = Object.freeze([].concat(qa(Yh)))
      , $h = Object.freeze([P.g.Ua, P.g.Wd, P.g.nd, P.g.lf, P.g.Rd])
      , ai = Object.freeze([].concat(qa($h)))
      , bi = {}
      , ci = (bi[P.g.R] = "1",
    bi[P.g.W] = "2",
    bi[P.g.P] = "3",
    bi[P.g.Aa] = "4",
    bi)
      , di = {}
      , ei = Object.freeze((di[P.g.oa] = 1,
    di[P.g.Jd] = 1,
    di[P.g.Ea] = 1,
    di[P.g.Rb] = 1,
    di[P.g.Ye] = 1,
    di[P.g.Kd] = 1,
    di[P.g.Ld] = 1,
    di[P.g.Md] = 1,
    di[P.g.ia] = 1,
    di[P.g.Nd] = 1,
    di[P.g.Za] = 1,
    di[P.g.wa] = 1,
    di[P.g.Ta] = 1,
    di[P.g.Ua] = 1,
    di[P.g.ab] = 1,
    di[P.g.Oa] = 1,
    di[P.g.Ba] = 1,
    di[P.g.Od] = 1,
    di[P.g.la] = 1,
    di[P.g.Gi] = 1,
    di[P.g.Td] = 1,
    di[P.g.Ud] = 1,
    di[P.g.ef] = 1,
    di[P.g.yc] = 1,
    di[P.g.Ub] = 1,
    di[P.g.Gb] = 1,
    di[P.g.Pa] = 1,
    di[P.g.jd] = 1,
    di[P.g.ya] = 1,
    di[P.g.Fa] = 1,
    di[P.g.zg] = 1,
    di[P.g.Ag] = 1,
    di[P.g.Bg] = 1,
    di[P.g.Cg] = 1,
    di[P.g.Vb] = 1,
    di[P.g.Ka] = 1,
    di[P.g.Wb] = 1,
    di[P.g.md] = 1,
    di[P.g.od] = 1,
    di[P.g.Ca] = 1,
    di[P.g.Kb] = 1,
    di[P.g.Xb] = 1,
    di[P.g.Va] = 1,
    di[P.g.Ga] = 1,
    di[P.g.Da] = 1,
    di[P.g.qa] = 1,
    di))
      , fi = {}
      , gi = Object.freeze((fi.search = "s",
    fi.youtube = "y",
    fi.playstore = "p",
    fi.shopping = "h",
    fi.ads = "a",
    fi.maps = "m",
    fi));
    Object.freeze(P.g);
    var hi = {}
      , ii = G.google_tag_manager = G.google_tag_manager || {};
    hi.Qg = "45f0";
    hi.ne = Number("0") || 0;
    hi.Ya = "dataLayer";
    hi.ln = "ChEI8ICcsgYQ8dHNp+nUlcfaARIkAPQ5GRuCNMoMguomjQCvrnUsvHeS4DHbUepn8IrU17up07YkGgJTMg\x3d\x3d";
    var ji = {
        __cl: 1,
        __ecl: 1,
        __ehl: 1,
        __evl: 1,
        __fal: 1,
        __fil: 1,
        __fsl: 1,
        __hl: 1,
        __jel: 1,
        __lcl: 1,
        __sdl: 1,
        __tl: 1,
        __ytl: 1
    }, ki = {
        __paused: 1,
        __tg: 1
    }, li;
    for (li in ji)
        ji.hasOwnProperty(li) && (ki[li] = 1);
    var mi = yb(""), ni, oi = !1;
    ni = oi;
    var pi, qi = !1;
    pi = qi;
    var ri, si = !1;
    ri = si;
    hi.Hd = "www.googletagmanager.com";
    var ti = "" + hi.Hd + (ni ? "/gtag/js" : "/gtm.js")
      , ui = null
      , vi = null
      , wi = {}
      , xi = {};
    function yi() {
        var a = ii.sequence || 1;
        ii.sequence = a + 1;
        return a
    }
    hi.sk = "";
    var zi = "";
    hi.Ef = zi;
    var Ai = new function() {
        this.m = "";
        this.M = this.F = !1;
        this.Wa = this.T = this.da = this.H = ""
    }
    ;
    function Bi() {
        var a = Ai.H.length;
        return "/" === Ai.H[a - 1] ? Ai.H.substring(0, a - 1) : Ai.H
    }
    function Ci(a) {
        for (var b = {}, c = na(a.split("|")), d = c.next(); !d.done; d = c.next())
            b[d.value] = !0;
        return b
    }
    var Di = new vb
      , Ei = {}
      , Fi = {}
      , Ii = {
        name: hi.Ya,
        set: function(a, b) {
            k(Jb(a, b), Ei);
            Gi()
        },
        get: function(a) {
            return Hi(a, 2)
        },
        reset: function() {
            Di = new vb;
            Ei = {};
            Gi()
        }
    };
    function Hi(a, b) {
        return 2 != b ? Di.get(a) : Ji(a)
    }
    function Ji(a, b) {
        var c = a.split(".");
        b = b || [];
        for (var d = Ei, e = 0; e < c.length; e++) {
            if (null === d)
                return !1;
            if (void 0 === d)
                break;
            d = d[c[e]];
            if (-1 !== b.indexOf(d))
                return
        }
        return d
    }
    function Ki(a, b) {
        Fi.hasOwnProperty(a) || (Di.set(a, b),
        k(Jb(a, b), Ei),
        Gi())
    }
    function Li() {
        for (var a = ["gtm.allowlist", "gtm.blocklist", "gtm.whitelist", "gtm.blacklist", "tagTypeBlacklist"], b = 0; b < a.length; b++) {
            var c = a[b]
              , d = Hi(c, 1);
            if (Array.isArray(d) || Xa(d))
                d = k(d);
            Fi[c] = d
        }
    }
    function Gi(a) {
        z(Fi, function(b, c) {
            Di.set(b, c);
            k(Jb(b), Ei);
            k(Jb(b, c), Ei);
            a && delete Fi[b]
        })
    }
    function Mi(a, b) {
        var c, d = 1 !== (void 0 === b ? 2 : b) ? Ji(a) : Di.get(a);
        "array" === Va(d) || "object" === Va(d) ? c = k(d) : c = d;
        return c
    }
    ;var Ni = function(a, b, c) {
        if (!c)
            return !1;
        var d = c.selector_type, e = String(c.value), f;
        if ("js_variable" === d) {
            e = e.replace(/\["?'?/g, ".").replace(/"?'?\]/g, "");
            for (var g = e.split(","), h = 0; h < g.length; h++) {
                var m = g[h].trim();
                if (m) {
                    if (0 === m.indexOf("dataLayer."))
                        f = Hi(m.substring(10));
                    else {
                        var n = m.split(".");
                        f = G[n.shift()];
                        for (var p = 0; p < n.length; p++)
                            f = f && f[n[p]]
                    }
                    if (void 0 !== f)
                        break
                }
            }
        } else if ("css_selector" === d && oh) {
            var q = nh(e);
            if (q && 0 < q.length) {
                f = [];
                for (var r = 0; r < q.length && r < ("email" === b || "phone_number" === b ? 5 : 1); r++)
                    f.push(Dc(q[r]) || Ab(q[r].value));
                f = 1 === f.length ? f[0] : f
            }
        }
        return f ? (a[b] = f,
        !0) : !1
    }
      , Oi = function(a) {
        if (a) {
            var b = {}
              , c = !1;
            c = Ni(b, "email", a.email) || c;
            c = Ni(b, "phone_number", a.phone) || c;
            b.address = [];
            for (var d = a.name_and_address || [], e = 0; e < d.length; e++) {
                var f = {};
                c = Ni(f, "first_name", d[e].first_name) || c;
                c = Ni(f, "last_name", d[e].last_name) || c;
                c = Ni(f, "street", d[e].street) || c;
                c = Ni(f, "city", d[e].city) || c;
                c = Ni(f, "region", d[e].region) || c;
                c = Ni(f, "country", d[e].country) || c;
                c = Ni(f, "postal_code", d[e].postal_code) || c;
                b.address.push(f)
            }
            return c ? b : void 0
        }
    }
      , Pi = function(a) {
        return Xa(a) ? !!a.enable_code : !1
    };
    function Qi(a, b) {
        if ("" === a)
            return b;
        var c = Number(a);
        return isNaN(c) ? b : c
    }
    ;var Ri = []
      , Si = {};
    function Ti(a) {
        return void 0 === Ri[a] ? !1 : Ri[a]
    }
    ;var Ui = [];
    function Vi(a) {
        switch (a) {
        case 0:
            return 0;
        case 27:
            return 7;
        case 35:
            return 1;
        case 36:
            return 2;
        case 42:
            return 3;
        case 51:
            return 6;
        case 61:
            return 4;
        case 72:
            return 5
        }
    }
    function S(a) {
        Ui[a] = !0;
        var b = Vi(a);
        void 0 !== b && (Ri[b] = !0)
    }
    S(22);
    S(18);
    S(19);
    S(20);
    S(21);
    S(37);
    S(56);
    S(40);
    S(53);
    S(26);
    S(11);
    S(79);
    S(10);
    S(87);
    S(78);
    S(43);
    S(63);
    S(33);
    S(6);
    S(4);
    S(59);
    S(75);
    S(49);
    S(46);
    S(69);
    S(85);
    S(23);
    S(24);
    S(66);
    S(84);
    S(60);
    S(90);
    S(88);
    S(61);
    S(5);
    S(72);
    S(65);
    Si[1] = Qi('1', 6E4);
    Si[3] = Qi('10', 1);
    Si[2] = Qi('', 50);
    S(8);
    S(70);
    S(83);
    S(76);
    S(81);
    function T(a) {
        return !!Ui[a]
    }
    var Zi = /:[0-9]+$/
      , $i = /^\d+\.fls\.doubleclick\.net$/
      , aj = function(a, b, c, d) {
        for (var e = [], f = na(a.split("&")), g = f.next(); !g.done; g = f.next()) {
            var h = na(g.value.split("="))
              , m = h.next().value
              , n = pa(h);
            if (decodeURIComponent(m.replace(/\+/g, " ")) === b) {
                var p = n.join("=");
                if (!c)
                    return d ? p : decodeURIComponent(p.replace(/\+/g, " "));
                e.push(d ? p : decodeURIComponent(p.replace(/\+/g, " ")))
            }
        }
        return c ? e : void 0
    }
      , dj = function(a, b, c, d, e) {
        b && (b = String(b).toLowerCase());
        if ("protocol" === b || "port" === b)
            a.protocol = bj(a.protocol) || bj(G.location.protocol);
        "port" === b ? a.port = String(Number(a.hostname ? a.port : G.location.port) || ("http" === a.protocol ? 80 : "https" === a.protocol ? 443 : "")) : "host" === b && (a.hostname = (a.hostname || G.location.hostname).replace(Zi, "").toLowerCase());
        return cj(a, b, c, d, e)
    }
      , cj = function(a, b, c, d, e) {
        var f, g = bj(a.protocol);
        b && (b = String(b).toLowerCase());
        switch (b) {
        case "url_no_fragment":
            f = ej(a);
            break;
        case "protocol":
            f = g;
            break;
        case "host":
            f = a.hostname.replace(Zi, "").toLowerCase();
            if (c) {
                var h = /^www\d*\./.exec(f);
                h && h[0] && (f = f.substr(h[0].length))
            }
            break;
        case "port":
            f = String(Number(a.port) || ("http" === g ? 80 : "https" === g ? 443 : ""));
            break;
        case "path":
            a.pathname || a.hostname || lb("TAGGING", 1);
            f = "/" === a.pathname.substr(0, 1) ? a.pathname : "/" + a.pathname;
            var m = f.split("/");
            0 <= (d || []).indexOf(m[m.length - 1]) && (m[m.length - 1] = "");
            f = m.join("/");
            break;
        case "query":
            f = a.search.replace("?", "");
            e && (f = aj(f, e, !1));
            break;
        case "extension":
            var n = a.pathname.split(".");
            f = 1 < n.length ? n[n.length - 1] : "";
            f = f.split("/")[0];
            break;
        case "fragment":
            f = a.hash.replace("#", "");
            break;
        default:
            f = a && a.href
        }
        return f
    }
      , bj = function(a) {
        return a ? a.replace(":", "").toLowerCase() : ""
    }
      , ej = function(a) {
        var b = "";
        if (a && a.href) {
            var c = a.href.indexOf("#");
            b = 0 > c ? a.href : a.href.substr(0, c)
        }
        return b
    }
      , fj = {}
      , gj = 0
      , hj = function(a) {
        var b = fj[a];
        if (!b) {
            var c = H.createElement("a");
            a && (c.href = a);
            var d = c.pathname;
            "/" !== d[0] && (a || lb("TAGGING", 1),
            d = "/" + d);
            var e = c.hostname.replace(Zi, "");
            b = {
                href: c.href,
                protocol: c.protocol,
                host: c.host,
                hostname: e,
                pathname: d,
                search: c.search,
                hash: c.hash,
                port: c.port
            };
            5 > gj && (fj[a] = b,
            gj++)
        }
        return b
    }
      , ij = function(a) {
        function b(n) {
            var p = n.split("=")[0];
            return 0 > d.indexOf(p) ? n : p + "=0"
        }
        function c(n) {
            return n.split("&").map(b).filter(function(p) {
                return void 0 !== p
            }).join("&")
        }
        var d = "gclid dclid gbraid wbraid gclaw gcldc gclha gclgf gclgb _gl".split(" ")
          , e = hj(a)
          , f = a.split(/[?#]/)[0]
          , g = e.search
          , h = e.hash;
        "?" === g[0] && (g = g.substring(1));
        "#" === h[0] && (h = h.substring(1));
        g = c(g);
        h = c(h);
        "" !== g && (g = "?" + g);
        "" !== h && (h = "#" + h);
        var m = "" + f + g + h;
        "/" === m[m.length - 1] && (m = m.substring(0, m.length - 1));
        return m
    }
      , jj = function(a) {
        var b = hj(G.location.href)
          , c = dj(b, "host", !1);
        if (c && c.match($i)) {
            var d = dj(b, "path").split(a + "=");
            if (1 < d.length)
                return d[1].split(";")[0].split("?")[0]
        }
    };
    var kj = {
        "https://www.google.com": "/g",
        "https://www.googleadservices.com": "/as",
        "https://pagead2.googlesyndication.com": "/gs"
    };
    function lj(a, b) {
        if (a) {
            var c = "" + a;
            0 !== c.indexOf("http://") && 0 !== c.indexOf("https://") && (c = "https://" + c);
            "/" === c[c.length - 1] && (c = c.substring(0, c.length - 1));
            return hj("" + c + b).href
        }
    }
    function mj() {
        return Ai.F || pi
    }
    function nj() {
        return !!hi.Ef && "SGTM_TOKEN" !== hi.Ef.split("@@").join("")
    }
    function oj(a) {
        for (var b = na([P.g.md, P.g.Kb]), c = b.next(); !c.done; c = b.next()) {
            var d = U(a, c.value);
            if (d)
                return d
        }
    }
    function pj(a, b) {
        return Ai.F ? "" + Bi() + (b ? kj[a] || "" : "") : a
    }
    ;function qj(a) {
        var b = String(a[Ce.ra] || "").replace(/_/g, "");
        0 === b.indexOf("cvt") && (b = "cvt");
        return b
    }
    var rj = 0 <= G.location.search.indexOf("?gtm_latency=") || 0 <= G.location.search.indexOf("&gtm_latency=");
    var tj = function(a, b) {
        var c = sj();
        c.pending || (c.pending = []);
        sb(c.pending, function(d) {
            return d.target.ctid === a.ctid && d.target.isDestination === a.isDestination
        }) || c.pending.push({
            target: a,
            onLoad: b
        })
    }
      , uj = function() {
        this.container = {};
        this.destination = {};
        this.canonical = {};
        this.pending = [];
        this.siloed = []
    }
      , sj = function() {
        var a = rc("google_tag_data", {})
          , b = a.tidr;
        b || (b = new uj,
        a.tidr = b);
        return b
    };
    var vj = {}
      , wj = !1
      , Hf = {
        ctid: "GTM-M86QHGF",
        canonicalContainerId: "32196322",
        Uj: "GTM-M86QHGF",
        Vj: "GTM-M86QHGF"
    };
    vj.je = yb("");
    function xj() {
        var a = yj();
        return wj ? a.map(zj) : a
    }
    function Aj() {
        var a = Bj();
        return wj ? a.map(zj) : a
    }
    function Cj() {
        return Dj(Hf.ctid)
    }
    function Ej() {
        return Dj(Hf.canonicalContainerId || "_" + Hf.ctid)
    }
    function yj() {
        return Hf.Uj ? Hf.Uj.split("|") : [Hf.ctid]
    }
    function Bj() {
        return Hf.Vj ? Hf.Vj.split("|") : []
    }
    function Fj() {
        var a = Gj(Hj())
          , b = a && a.parent;
        if (b)
            return Gj(b)
    }
    function Ij() {
        var a = Gj(Hj());
        if (a) {
            for (; a.parent; ) {
                var b = Gj(a.parent);
                if (!b)
                    break;
                a = b
            }
            return a
        }
    }
    function Gj(a) {
        var b = sj();
        return a.isDestination ? b.destination[a.ctid] : b.container[a.ctid]
    }
    function Dj(a) {
        return wj ? zj(a) : a
    }
    function zj(a) {
        return "siloed_" + a
    }
    function Jj(a) {
        return wj ? Pj(a) : a
    }
    function Pj(a) {
        a = String(a);
        return 0 === a.indexOf("siloed_") ? a.substring(7) : a
    }
    function Qj() {
        var a = !1;
        if (a) {
            var b = sj();
            if (b.siloed) {
                for (var c = [], d = yj().map(zj), e = Bj().map(zj), f = {}, g = 0; g < b.siloed.length; f = {
                    If: void 0
                },
                g++)
                    f.If = b.siloed[g],
                    !wj && sb(f.If.isDestination ? e : d, function(h) {
                        return function(m) {
                            return m === h.If.ctid
                        }
                    }(f)) ? wj = !0 : c.push(f.If);
                b.siloed = c
            }
        }
    }
    function Rj() {
        var a = sj();
        if (a.pending) {
            for (var b, c = [], d = !1, e = xj(), f = Aj(), g = {}, h = 0; h < a.pending.length; g = {
                Ne: void 0
            },
            h++)
                g.Ne = a.pending[h],
                sb(g.Ne.target.isDestination ? f : e, function(m) {
                    return function(n) {
                        return n === m.Ne.target.ctid
                    }
                }(g)) ? d || (b = g.Ne.onLoad,
                d = !0) : c.push(g.Ne);
            a.pending = c;
            if (b)
                try {
                    b(Ej())
                } catch (m) {}
        }
    }
    function Sj() {
        for (var a = Hf.ctid, b = xj(), c = Aj(), d = function(n, p) {
            var q = {
                canonicalContainerId: Hf.canonicalContainerId,
                scriptContainerId: a,
                state: 2,
                containers: b.slice(),
                destinations: c.slice()
            };
            qc && (q.scriptSource = qc);
            var r = p ? e.destination : e.container
              , t = r[n];
            t ? (p && 0 === t.state && O(93),
            Object.assign(t, q)) : r[n] = q
        }, e = sj(), f = na(b), g = f.next(); !g.done; g = f.next())
            d(g.value, !1);
        for (var h = na(c), m = h.next(); !m.done; m = h.next())
            d(m.value, !0);
        e.canonical[Ej()] = {};
        Rj()
    }
    function Tj(a) {
        return !!sj().container[a]
    }
    function Uj(a) {
        var b = sj().destination[a];
        return !!b && !!b.state
    }
    function Hj() {
        return {
            ctid: Cj(),
            isDestination: vj.je
        }
    }
    function Vj(a) {
        var b = sj();
        (b.siloed = b.siloed || []).push(a)
    }
    function Wj() {
        var a = sj().container, b;
        for (b in a)
            if (a.hasOwnProperty(b) && 1 === a[b].state)
                return !0;
        return !1
    }
    function Xj() {
        var a = {};
        z(sj().destination, function(b, c) {
            0 === c.state && (a[Pj(b)] = c)
        });
        return a
    }
    function Yj(a) {
        return !!(a && a.parent && a.context && 1 === a.context.source && 0 !== a.parent.ctid.indexOf("GTM-"))
    }
    var Zj = {
        sampleRate: "0.005000",
        nk: "",
        mk: Number("5"),
        Zn: Number("")
    }
      , ak = []
      , bk = []
      , ck = [];
    function dk(a) {
        T(23) ? bk.push(a) : ak.push(a)
    }
    function ek(a) {
        T(23) ? ck.push(a) : ak.push(a)
    }
    var fk = !1, gk;
    if (!(gk = rj)) {
        var hk = Math.random()
          , ik = Zj.sampleRate;
        gk = hk < Number(ik)
    }
    var jk = gk
      , kk = "?id=" + Hf.ctid
      , lk = void 0
      , mk = {}
      , nk = void 0
      , ok = new function() {
        var a = 5;
        0 < Zj.mk && (a = Zj.mk);
        this.F = a;
        this.m = 0;
        this.H = []
    }
      , pk = 1E3;
    function qk(a, b, c, d) {
        var e = lk;
        if (void 0 === e)
            if (c)
                e = yi();
            else
                return "";
        var f = [pj("https://www.googletagmanager.com"), "/a", kk]
          , g = ak;
        T(23) && (f = [pj("https://www.googletagmanager.com"), a ? "/td" : "/a", kk],
        g = a ? ck : bk);
        for (var h = na(g), m = h.next(); !m.done; m = h.next())
            for (var n = m.value, p = n({
                eventId: e,
                Xa: !!b,
                Kj: !!d,
                Nc: function() {
                    fk = !0
                }
            }), q = na(p), r = q.next(); !r.done; r = q.next()) {
                var t = na(r.value)
                  , u = t.next().value
                  , v = t.next().value;
                f.push("&" + u + "=" + v)
            }
        f.push("&z=0");
        return f.join("")
    }
    function rk() {
        if (T(24)) {
            var a = qk(!0, !0);
            fk && (T(23) || (a = a.replace("/a?", "/td?")),
            zc(a),
            fk = !1)
        }
    }
    function sk() {
        nk && (G.clearTimeout(nk),
        nk = void 0);
        if (void 0 !== lk && tk) {
            rk();
            var a;
            (a = mk[lk]) || (a = ok.m < ok.F ? !1 : 1E3 > Cb() - ok.H[ok.m % ok.F]);
            if (a || 0 >= pk--)
                O(1),
                mk[lk] = !0;
            else {
                var b = ok.m++ % ok.F;
                ok.H[b] = Cb();
                var c = qk(!1, !0);
                zc(c);
                var d = T(23) ? qk(!0, !0) : c.replace("/a?", "/td?");
                fk && zc(d);
                tk = fk = !1
            }
        }
    }
    var tk = !1;
    function uk(a) {
        mk[a] ? rk() : (a !== lk && (sk(),
        lk = a),
        tk = !0,
        nk || (nk = G.setTimeout(sk, 500)),
        2022 <= qk(!1).length && sk())
    }
    var vk = tb();
    function wk() {
        vk = tb()
    }
    function xk() {
        return [["v", "3"], ["t", "t"], ["pid", String(vk)]]
    }
    var yk = function(a, b) {
        var c = function() {};
        c.prototype = a.prototype;
        var d = new c;
        a.apply(d, Array.prototype.slice.call(arguments, 1));
        return d
    }
      , zk = function(a) {
        var b = a;
        return function() {
            if (b) {
                var c = b;
                b = null;
                c()
            }
        }
    };
    var Ak = function(a, b, c) {
        a.addEventListener && a.addEventListener(b, c, !1)
    };
    var Bk, Ck;
    a: {
        for (var Dk = ["CLOSURE_FLAGS"], Ek = Aa, Fk = 0; Fk < Dk.length; Fk++)
            if (Ek = Ek[Dk[Fk]],
            null == Ek) {
                Ck = null;
                break a
            }
        Ck = Ek
    }
    var Gk = Ck && Ck[610401301];
    Bk = null != Gk ? Gk : !1;
    function Hk() {
        var a = Aa.navigator;
        if (a) {
            var b = a.userAgent;
            if (b)
                return b
        }
        return ""
    }
    var Ik, Jk = Aa.navigator;
    Ik = Jk ? Jk.userAgentData || null : null;
    function Kk(a) {
        return Bk ? Ik ? Ik.brands.some(function(b) {
            var c = b.brand;
            return c && -1 != c.indexOf(a)
        }) : !1 : !1
    }
    function Lk(a) {
        return -1 != Hk().indexOf(a)
    }
    ;function Mk() {
        return Bk ? !!Ik && 0 < Ik.brands.length : !1
    }
    function Nk() {
        return Mk() ? !1 : Lk("Opera")
    }
    function Ok() {
        return Lk("Firefox") || Lk("FxiOS")
    }
    function Pk() {
        return Mk() ? Kk("Chromium") : (Lk("Chrome") || Lk("CriOS")) && !(Mk() ? 0 : Lk("Edge")) || Lk("Silk")
    }
    ;function Qk() {
        return Bk ? !!Ik && !!Ik.platform : !1
    }
    function Rk() {
        return Lk("iPhone") && !Lk("iPod") && !Lk("iPad")
    }
    function Sk() {
        Rk() || Lk("iPad") || Lk("iPod")
    }
    ;var Tk = function(a) {
        Tk[" "](a);
        return a
    };
    Tk[" "] = function() {}
    ;
    Nk();
    Mk() || Lk("Trident") || Lk("MSIE");
    Lk("Edge");
    !Lk("Gecko") || -1 != Hk().toLowerCase().indexOf("webkit") && !Lk("Edge") || Lk("Trident") || Lk("MSIE") || Lk("Edge");
    -1 != Hk().toLowerCase().indexOf("webkit") && !Lk("Edge") && Lk("Mobile");
    Qk() || Lk("Macintosh");
    Qk() || Lk("Windows");
    (Qk() ? "Linux" === Ik.platform : Lk("Linux")) || Qk() || Lk("CrOS");
    Qk() || Lk("Android");
    Rk();
    Lk("iPad");
    Lk("iPod");
    Sk();
    Hk().toLowerCase().indexOf("kaios");
    var Uk = function(a, b, c, d) {
        for (var e = b, f = c.length; 0 <= (e = a.indexOf(c, e)) && e < d; ) {
            var g = a.charCodeAt(e - 1);
            if (38 == g || 63 == g) {
                var h = a.charCodeAt(e + f);
                if (!h || 61 == h || 38 == h || 35 == h)
                    return e
            }
            e += f + 1
        }
        return -1
    }
      , Vk = /#|$/
      , Wk = function(a, b) {
        var c = a.search(Vk)
          , d = Uk(a, 0, b, c);
        if (0 > d)
            return null;
        var e = a.indexOf("&", d);
        if (0 > e || e > c)
            e = c;
        d += b.length + 1;
        return decodeURIComponent(a.slice(d, -1 !== e ? e : 0).replace(/\+/g, " "))
    }
      , Xk = /[?&]($|#)/
      , Yk = function(a, b, c) {
        for (var d, e = a.search(Vk), f = 0, g, h = []; 0 <= (g = Uk(a, f, b, e)); )
            h.push(a.substring(f, g)),
            f = Math.min(a.indexOf("&", g) + 1 || e, e);
        h.push(a.slice(f));
        d = h.join("").replace(Xk, "$1");
        var m, n = null != c ? "=" + encodeURIComponent(String(c)) : "";
        var p = b + n;
        if (p) {
            var q, r = d.indexOf("#");
            0 > r && (r = d.length);
            var t = d.indexOf("?"), u;
            0 > t || t > r ? (t = r,
            u = "") : u = d.substring(t + 1, r);
            q = [d.slice(0, t), u, d.slice(r)];
            var v = q[1];
            q[1] = p ? v ? v + "&" + p : p : v;
            m = q[0] + (q[1] ? "?" + q[1] : "") + q[2]
        } else
            m = d;
        return m
    };
    var Zk = function(a) {
        try {
            var b;
            if (b = !!a && null != a.location.href)
                a: {
                    try {
                        Tk(a.foo);
                        b = !0;
                        break a
                    } catch (c) {}
                    b = !1
                }
            return b
        } catch (c) {
            return !1
        }
    }
      , $k = function(a, b) {
        if (a)
            for (var c in a)
                Object.prototype.hasOwnProperty.call(a, c) && b(a[c], c, a)
    };
    function al(a) {
        if (!a || !H.head)
            return null;
        var b = bl("META");
        H.head.appendChild(b);
        b.httpEquiv = "origin-trial";
        b.content = a;
        return b
    }
    var cl = function(a) {
        if (G.top == G)
            return 0;
        if (void 0 === a ? 0 : a) {
            var b = G.location.ancestorOrigins;
            if (b)
                return b[b.length - 1] == G.location.origin ? 1 : 2
        }
        return Zk(G.top) ? 1 : 2
    }
      , bl = function(a, b) {
        b = void 0 === b ? document : b;
        return b.createElement(String(a).toLowerCase())
    };
    var dl = "", el, fl = [], gl = !1;
    function hl() {
        var a = [];
        dl && a.push(["dl", encodeURIComponent(dl)]);
        0 < fl.length && a.push(["tdp", fl.join(".")]);
        void 0 !== el && a.push(["frm", String(el)]);
        return a
    }
    var il = function(a) {
        var b = gl ? [] : hl();
        !gl && a.Xa && (gl = !0,
        b.length && a.Nc());
        return b
    };
    var jl = []
      , kl = [];
    function ll(a) {
        -1 === kl.indexOf(a) && (jl.push(a),
        kl.push(a))
    }
    function ml(a) {
        if (!jl.length)
            return [];
        for (var b = hl(), c = na(jl), d = c.next(); !d.done; d = c.next())
            b.push([d.value, "1"]);
        a.Xa && (a.Nc(),
        jl.length = 0);
        return b
    }
    ;function nl(a) {
        lb("HEALTH", a)
    }
    ;var ol;
    try {
        ol = JSON.parse(jb("eyIwIjoiVVMiLCIxIjoiVVMtVkEiLCIyIjpmYWxzZSwiMyI6IiIsIjQiOiIiLCI1Ijp0cnVlLCI2IjpmYWxzZSwiNyI6ImFkX3N0b3JhZ2V8YW5hbHl0aWNzX3N0b3JhZ2V8YWRfdXNlcl9kYXRhfGFkX3BlcnNvbmFsaXphdGlvbiJ9"))
    } catch (a) {
        O(123),
        nl(2),
        ol = {}
    }
    function pl() {
        return ol["0"] || ""
    }
    function ql() {
        var a = !1;
        return a
    }
    function rl() {
        return !1 !== ol["6"]
    }
    function sl() {
        var a = "";
        return a
    }
    function tl() {
        var a = !1;
        a = !!ol["5"];
        return a
    }
    function ul() {
        var a = "";
        return a
    }
    var vl = new function(a, b) {
        this.m = a;
        this.defaultValue = void 0 === b ? !1 : b
    }
    (1933);
    function wl() {
        var a = rc("google_tag_data", {});
        return a.ics = a.ics || new xl
    }
    var xl = function() {
        this.entries = {};
        this.waitPeriodTimedOut = this.wasSetLate = this.accessedAny = this.accessedDefault = this.usedImplicit = this.usedUpdate = this.usedDefault = this.usedDeclare = this.active = !1;
        this.m = []
    };
    xl.prototype.default = function(a, b, c, d, e, f, g) {
        this.usedDefault || this.usedDeclare || !this.accessedDefault && !this.accessedAny || (this.wasSetLate = !0);
        this.usedDefault = this.active = !0;
        lb("TAGGING", 19);
        null == b ? lb("TAGGING", 18) : yl(this, a, "granted" === b, c, d, e, f, g)
    }
    ;
    xl.prototype.waitForUpdate = function(a, b, c) {
        for (var d = 0; d < a.length; d++)
            yl(this, a[d], void 0, void 0, "", "", b, c)
    }
    ;
    var yl = function(a, b, c, d, e, f, g, h) {
        var m = a.entries
          , n = m[b] || {}
          , p = n.region
          , q = d && l(d) ? d.toUpperCase() : void 0;
        e = e.toUpperCase();
        f = f.toUpperCase();
        if ("" === e || q === f || (q === e ? p !== f : !q && !p)) {
            var r = !!(g && 0 < g && void 0 === n.update)
              , t = {
                region: q,
                declare_region: n.declare_region,
                implicit: n.implicit,
                default: void 0 !== c ? c : n.default,
                declare: n.declare,
                update: n.update,
                quiet: r
            };
            if ("" !== e || !1 !== n.default)
                m[b] = t;
            r && G.setTimeout(function() {
                m[b] === t && t.quiet && (lb("TAGGING", 2),
                a.waitPeriodTimedOut = !0,
                a.clearTimeout(b, void 0, h),
                a.notifyListeners())
            }, g)
        }
    };
    aa = xl.prototype;
    aa.clearTimeout = function(a, b, c) {
        var d = [a], e = (null == c ? void 0 : c.delegatedConsentTypes) || {}, f;
        for (f in e)
            e.hasOwnProperty(f) && e[f] === a && d.push(f);
        var g = this.entries[a] || {}
          , h = this.getConsentState(a, c);
        if (g.quiet) {
            g.quiet = !1;
            for (var m = na(d), n = m.next(); !n.done; n = m.next())
                zl(this, n.value)
        } else if (void 0 !== b && h !== b)
            for (var p = na(d), q = p.next(); !q.done; q = p.next())
                zl(this, q.value)
    }
    ;
    aa.update = function(a, b, c) {
        this.usedDefault || this.usedDeclare || this.usedUpdate || !this.accessedAny || (this.wasSetLate = !0);
        this.usedUpdate = this.active = !0;
        if (null != b) {
            var d = this.getConsentState(a, c)
              , e = this.entries;
            (e[a] = e[a] || {}).update = "granted" === b;
            this.clearTimeout(a, d, c)
        }
    }
    ;
    aa.declare = function(a, b, c, d, e) {
        this.usedDeclare = this.active = !0;
        var f = this.entries
          , g = f[a] || {}
          , h = g.declare_region
          , m = c && l(c) ? c.toUpperCase() : void 0;
        d = d.toUpperCase();
        e = e.toUpperCase();
        if ("" === d || m === e || (m === d ? h !== e : !m && !h)) {
            var n = {
                region: g.region,
                declare_region: m,
                declare: "granted" === b,
                implicit: g.implicit,
                default: g.default,
                update: g.update,
                quiet: g.quiet
            };
            if ("" !== d || !1 !== g.declare)
                f[a] = n
        }
    }
    ;
    aa.implicit = function(a, b) {
        this.usedImplicit = !0;
        var c = this.entries
          , d = c[a] = c[a] || {};
        !1 !== d.implicit && (d.implicit = "granted" === b)
    }
    ;
    aa.getConsentState = function(a, b) {
        var c = this.entries
          , d = c[a] || {}
          , e = d.update;
        if (void 0 !== e)
            return e ? 1 : 2;
        e = d.default;
        if (void 0 !== e)
            return e ? 1 : 2;
        if (null == b ? 0 : b.delegatedConsentTypes.hasOwnProperty(a)) {
            var f = c[b.delegatedConsentTypes[a]] || {};
            e = f.update;
            if (void 0 !== e)
                return e ? 1 : 2;
            e = f.default;
            if (void 0 !== e)
                return e ? 1 : 2
        }
        e = d.declare;
        if (void 0 !== e)
            return e ? 1 : 2;
        e = d.implicit;
        return void 0 !== e ? e ? 3 : 4 : 0
    }
    ;
    aa.addListener = function(a, b) {
        this.m.push({
            consentTypes: a,
            Dl: b
        })
    }
    ;
    var zl = function(a, b) {
        for (var c = 0; c < a.m.length; ++c) {
            var d = a.m[c];
            Array.isArray(d.consentTypes) && -1 !== d.consentTypes.indexOf(b) && (d.Wj = !0)
        }
    };
    xl.prototype.notifyListeners = function(a, b) {
        for (var c = 0; c < this.m.length; ++c) {
            var d = this.m[c];
            if (d.Wj) {
                d.Wj = !1;
                try {
                    d.Dl({
                        consentEventId: a,
                        consentPriorityId: b
                    })
                } catch (e) {}
            }
        }
    }
    ;
    var Bl = function() {
        var a = Al
          , b = "vh";
        if (a.vh && a.hasOwnProperty(b))
            return a.vh;
        var c = new a;
        return a.vh = c
    };
    var Al = function() {
        var a = {};
        this.m = function() {
            var b = vl.m
              , c = vl.defaultValue;
            return null != a[b] ? a[b] : c
        }
        ;
        this.F = function() {
            a[vl.m] = !0
        }
    };
    var Cl = !1
      , Dl = !1
      , El = {
        delegatedConsentTypes: {},
        corePlatformServices: {},
        usedCorePlatformServices: !1
    }
      , Fl = function(a) {
        var b = wl();
        b.accessedAny = !0;
        return (l(a) ? [a] : a).every(function(c) {
            switch (b.getConsentState(c, El)) {
            case 1:
            case 3:
                return !0;
            case 2:
            case 4:
                return !1;
            default:
                return !0
            }
        })
    }
      , Gl = function(a) {
        var b = wl();
        b.accessedAny = !0;
        return b.getConsentState(a, El)
    }
      , Hl = function(a) {
        for (var b = {}, c = na(a), d = c.next(); !d.done; d = c.next()) {
            var e = d.value;
            b[e] = !1 !== El.corePlatformServices[e]
        }
        return b
    }
      , Il = function(a) {
        var b = wl();
        b.accessedAny = !0;
        return !(b.entries[a] || {}).quiet
    }
      , Jl = function() {
        if (!Bl().m())
            return !1;
        var a = wl();
        a.accessedAny = !0;
        return a.active
    }
      , Kl = function(a, b) {
        wl().addListener(a, b)
    }
      , Ll = function(a, b) {
        wl().notifyListeners(a, b)
    }
      , Ml = function(a, b) {
        function c() {
            for (var e = 0; e < b.length; e++)
                if (!Il(b[e]))
                    return !0;
            return !1
        }
        if (c()) {
            var d = !1;
            Kl(b, function(e) {
                d || c() || (d = !0,
                a(e))
            })
        } else
            a({})
    }
      , Nl = function(a, b) {
        function c() {
            for (var h = [], m = 0; m < e.length; m++) {
                var n = e[m];
                Fl(n) && !f[n] && h.push(n)
            }
            return h
        }
        function d(h) {
            for (var m = 0; m < h.length; m++)
                f[h[m]] = !0
        }
        var e = l(b) ? [b] : b
          , f = {}
          , g = c();
        g.length !== e.length && (d(g),
        Kl(e, function(h) {
            function m(q) {
                0 !== q.length && (d(q),
                h.consentTypes = q,
                a(h))
            }
            var n = c();
            if (0 !== n.length) {
                var p = Object.keys(f).length;
                n.length + p >= e.length ? m(n) : G.setTimeout(function() {
                    m(c())
                }, 500)
            }
        }))
    };
    var Ol = [P.g.R, P.g.W, P.g.P, P.g.Aa], Pl, Ql;
    function Rl(a) {
        for (var b = a[P.g.kc], c = Array.isArray(b) ? b : [b], d = {
            De: 0
        }; d.De < c.length; d = {
            De: d.De
        },
        ++d.De)
            z(a, function(e) {
                return function(f, g) {
                    if (f !== P.g.kc) {
                        var h = c[e.De]
                          , m = pl()
                          , n = ol["1"] || "";
                        Dl = !0;
                        Cl && lb("TAGGING", 20);
                        wl().declare(f, g, h, m, n)
                    }
                }
            }(d))
    }
    function Sl(a) {
        !Ql && Pl && ll("crc");
        Ql = !0;
        var b = a[P.g.kc];
        b && O(40);
        var c = a[P.g.Ue];
        c && O(41);
        for (var d = Array.isArray(b) ? b : [b], e = {
            Ee: 0
        }; e.Ee < d.length; e = {
            Ee: e.Ee
        },
        ++e.Ee)
            z(a, function(f) {
                return function(g, h) {
                    if (g !== P.g.kc && g !== P.g.Ue) {
                        var m = d[f.Ee]
                          , n = Number(c)
                          , p = pl()
                          , q = ol["1"] || "";
                        n = void 0 === n ? 0 : n;
                        Cl = !0;
                        Dl && lb("TAGGING", 20);
                        wl().default(g, h, m, p, q, n, El)
                    }
                }
            }(e))
    }
    function Tl(a, b) {
        Pl = !0;
        z(a, function(c, d) {
            Cl = !0;
            Dl && lb("TAGGING", 20);
            wl().update(c, d, El)
        });
        Ll(b.eventId, b.priorityId)
    }
    function Ul(a) {
        a.hasOwnProperty("all") && z(gi, function(b) {
            El.corePlatformServices[b] = "granted" === a.all;
            El.usedCorePlatformServices = !0
        });
        z(a, function(b, c) {
            "all" !== b && (El.corePlatformServices[b] = "granted" === c,
            El.usedCorePlatformServices = !0)
        })
    }
    function W(a) {
        Array.isArray(a) || (a = [a]);
        return a.every(function(b) {
            return Fl(b)
        })
    }
    function Vl(a, b) {
        Kl(a, b)
    }
    function Wl(a, b) {
        Nl(a, b)
    }
    function Xl(a, b) {
        Ml(a, b)
    }
    function Yl() {
        var a = [P.g.R, P.g.Aa, P.g.P];
        wl().waitForUpdate(a, 500, El)
    }
    function Zl(a) {
        for (var b = na(a), c = b.next(); !c.done; c = b.next()) {
            var d = c.value;
            wl().clearTimeout(d, void 0, El)
        }
        Ll()
    }
    var $l = function() {
        if (void 0 === ii.pscdl) {
            var a = function(b) {
                ii.pscdl = b
            };
            try {
                "cookieDeprecationLabel"in oc ? (a("pending"),
                oc.cookieDeprecationLabel.getValue().then(a)) : a("noapi")
            } catch (b) {
                a("error")
            }
        }
    };
    var am = /[A-Z]+/
      , bm = /\s/;
    function cm(a, b) {
        if (l(a)) {
            a = Ab(a);
            var c = a.indexOf("-");
            if (!(0 > c)) {
                var d = a.substring(0, c);
                if (am.test(d)) {
                    var e = a.substring(c + 1), f;
                    if (b) {
                        var g = function(n) {
                            var p = n.indexOf("/");
                            return 0 > p ? [n] : [n.substring(0, p), n.substring(p + 1)]
                        };
                        f = g(e);
                        if ("DC" === d && 2 === f.length) {
                            var h = g(f[1]);
                            2 === h.length && (f[1] = h[0],
                            f.push(h[1]))
                        }
                    } else {
                        f = e.split("/");
                        for (var m = 0; m < f.length; m++)
                            if (!f[m] || bm.test(f[m]) && ("AW" !== d || 1 !== m))
                                return
                    }
                    return {
                        id: a,
                        prefix: d,
                        ka: d + "-" + f[0],
                        ma: f
                    }
                }
            }
        }
    }
    function dm(a, b) {
        for (var c = {}, d = 0; d < a.length; ++d) {
            var e = cm(a[d], b);
            e && (c[e.id] = e)
        }
        em(c);
        var f = [];
        z(c, function(g, h) {
            f.push(h)
        });
        return f
    }
    function em(a) {
        var b = [], c;
        for (c in a)
            if (a.hasOwnProperty(c)) {
                var d = a[c];
                "AW" === d.prefix && d.ma[fm[2]] && b.push(d.ka)
            }
        for (var e = 0; e < b.length; ++e)
            delete a[b[e]]
    }
    var gm = {}
      , fm = (gm[0] = 0,
    gm[1] = 0,
    gm[2] = 1,
    gm[3] = 0,
    gm[4] = 1,
    gm[5] = 2,
    gm[6] = 0,
    gm[7] = 0,
    gm[8] = 0,
    gm);
    var hm = []
      , im = {
        initialized: 11,
        complete: 12,
        interactive: 13
    }
      , jm = {}
      , km = Object.freeze((jm[P.g.Ka] = !0,
    jm))
      , lm = 0 <= H.location.search.indexOf("?gtm_diagnostics=") || 0 <= H.location.search.indexOf("&gtm_diagnostics=");
    function mm(a, b, c) {
        if (jk && "config" === a) {
            var d, e = null == (d = cm(b)) ? void 0 : d.ma;
            if (!(e && 1 < e.length)) {
                var f, g = rc("google_tag_data", {});
                g.td || (g.td = {});
                f = g.td;
                var h = k(c.M);
                k(c.m, h);
                var m = [], n;
                for (n in f)
                    if (f.hasOwnProperty(n)) {
                        var p = nm(f[n], h);
                        p.length && (lm && console.log(p),
                        m.push(n))
                    }
                m.length && (m.length && jk && hm.push(b + "*" + m.join(".")),
                lb("TAGGING", im[H.readyState] || 14));
                f[b] = h
            }
        }
    }
    function om(a, b) {
        var c = {}, d;
        for (d in b)
            b.hasOwnProperty(d) && (c[d] = !0);
        for (var e in a)
            a.hasOwnProperty(e) && (c[e] = !0);
        return c
    }
    function nm(a, b, c, d) {
        c = void 0 === c ? {} : c;
        d = void 0 === d ? "" : d;
        if (a === b)
            return [];
        var e = function(r, t) {
            var u;
            "object" === Va(t) ? u = t[r] : "array" === Va(t) && (u = t[r]);
            return void 0 === u ? km[r] : u
        }, f = om(a, b), g;
        for (g in f)
            if (f.hasOwnProperty(g)) {
                var h = (d ? d + "." : "") + g
                  , m = e(g, a)
                  , n = e(g, b)
                  , p = "object" === Va(m) || "array" === Va(m)
                  , q = "object" === Va(n) || "array" === Va(n);
                if (p && q)
                    nm(m, n, c, h);
                else if (p || q || m !== n)
                    c[h] = !0
            }
        return Object.keys(c)
    }
    function pm(a) {
        if (!hm.length)
            return [];
        var b = [["tdc", hm.join("!")]];
        a.Xa && (a.Nc(),
        hm.length = 0);
        return b
    }
    ;var qm = function(a, b, c, d, e, f, g, h, m, n, p) {
        this.eventId = a;
        this.priorityId = b;
        this.m = c;
        this.T = d;
        this.H = e;
        this.M = f;
        this.F = g;
        this.eventMetadata = h;
        this.onSuccess = m;
        this.onFailure = n;
        this.isGtmEvent = p
    }
      , rm = function(a, b) {
        var c = [];
        switch (b) {
        case 3:
            c.push(a.m);
            c.push(a.T);
            c.push(a.H);
            c.push(a.M);
            c.push(a.F);
            break;
        case 2:
            c.push(a.m);
            break;
        case 1:
            c.push(a.T);
            c.push(a.H);
            c.push(a.M);
            c.push(a.F);
            break;
        case 4:
            c.push(a.m),
            c.push(a.T),
            c.push(a.H),
            c.push(a.M)
        }
        return c
    }
      , U = function(a, b, c, d) {
        for (var e = na(rm(a, void 0 === d ? 3 : d)), f = e.next(); !f.done; f = e.next()) {
            var g = f.value;
            if (void 0 !== g[b])
                return g[b]
        }
        return c
    }
      , sm = function(a) {
        for (var b = {}, c = rm(a, 4), d = na(c), e = d.next(); !e.done; e = d.next())
            for (var f = Object.keys(e.value), g = na(f), h = g.next(); !h.done; h = g.next())
                b[h.value] = 1;
        return Object.keys(b)
    }
      , tm = function(a, b, c) {
        function d(n) {
            Xa(n) && z(n, function(p, q) {
                f = !0;
                e[p] = q
            })
        }
        var e = {}
          , f = !1
          , g = rm(a, void 0 === c ? 3 : c);
        g.reverse();
        for (var h = na(g), m = h.next(); !m.done; m = h.next())
            d(m.value[b]);
        return f ? e : void 0
    }
      , um = function(a) {
        for (var b = [P.g.Uc, P.g.Qc, P.g.Rc, P.g.Sc, P.g.Tc, P.g.Vc, P.g.Wc], c = rm(a, 3), d = na(c), e = d.next(); !e.done; e = d.next()) {
            for (var f = e.value, g = {}, h = !1, m = na(b), n = m.next(); !n.done; n = m.next()) {
                var p = n.value;
                void 0 !== f[p] && (g[p] = f[p],
                h = !0)
            }
            var q = h ? g : void 0;
            if (q)
                return q
        }
        return {}
    }
      , vm = function(a, b) {
        this.eventId = a;
        this.priorityId = b;
        this.F = {};
        this.T = {};
        this.m = {};
        this.H = {};
        this.da = {};
        this.M = {};
        this.eventMetadata = {};
        this.isGtmEvent = !1;
        this.onSuccess = function() {}
        ;
        this.onFailure = function() {}
    }
      , wm = function(a, b) {
        a.F = b;
        return a
    }
      , xm = function(a, b) {
        a.T = b;
        return a
    }
      , ym = function(a, b) {
        a.m = b;
        return a
    }
      , zm = function(a, b) {
        a.H = b;
        return a
    }
      , Am = function(a, b) {
        a.da = b;
        return a
    }
      , Bm = function(a, b) {
        a.M = b;
        return a
    }
      , Cm = function(a, b) {
        a.eventMetadata = b || {};
        return a
    }
      , Dm = function(a, b) {
        a.onSuccess = b;
        return a
    }
      , Em = function(a, b) {
        a.onFailure = b;
        return a
    }
      , Fm = function(a, b) {
        a.isGtmEvent = b;
        return a
    }
      , Gm = function(a) {
        return new qm(a.eventId,a.priorityId,a.F,a.T,a.m,a.H,a.M,a.eventMetadata,a.onSuccess,a.onFailure,a.isGtmEvent)
    };
    var Hm = {};
    function Im(a, b, c) {
        jk && void 0 !== a && (Hm[a] = Hm[a] || [],
        Hm[a].push(c + b),
        uk(a))
    }
    function Jm(a) {
        var b = a.eventId
          , c = a.Xa
          , d = []
          , e = Hm[b] || [];
        e.length && d.push(["epr", e.join(".")]);
        c && delete Hm[b];
        return d
    }
    ;var Lm = function(a, b) {
        var c = cm(Dj(a), !0);
        c && Km.register(c, b)
    }
      , Mm = function(a, b, c, d) {
        var e = cm(c, d.isGtmEvent);
        e && Km.push("event", [b, a], e, d)
    }
      , Nm = function(a, b, c, d) {
        var e = cm(c, d.isGtmEvent);
        e && Km.push("get", [a, b], e, d)
    }
      , Pm = function(a) {
        var b = cm(Dj(a), !0), c;
        b ? c = Om(Km, b).m : c = {};
        return c
    }
      , Qm = function(a, b) {
        var c = cm(Dj(a), !0);
        if (c) {
            var d = Km
              , e = k(b);
            k(Om(d, c).m, e);
            Om(d, c).m = e
        }
    }
      , Rm = function() {
        this.status = 1;
        this.T = {};
        this.m = {};
        this.F = {};
        this.da = null;
        this.M = {};
        this.H = !1
    }
      , Sm = function(a, b, c, d) {
        var e = Cb();
        this.type = a;
        this.F = e;
        this.m = b;
        this.args = c;
        this.messageContext = d
    }
      , Tm = function() {
        this.F = {};
        this.H = {};
        this.m = []
    }
      , Om = function(a, b) {
        var c = b.ka;
        return a.F[c] = a.F[c] || new Rm
    }
      , Um = function(a, b, c, d) {
        if (d.m) {
            var e = Om(a, d.m)
              , f = e.da;
            if (f) {
                var g = k(c)
                  , h = k(e.T[d.m.id])
                  , m = k(e.M)
                  , n = k(e.m)
                  , p = k(a.H)
                  , q = {};
                if (jk)
                    try {
                        q = k(Ei)
                    } catch (v) {
                        O(72)
                    }
                var r = d.m.prefix
                  , t = function(v) {
                    Im(d.messageContext.eventId, r, v)
                }
                  , u = Gm(Fm(Em(Dm(Cm(Am(zm(Bm(ym(xm(wm(new vm(d.messageContext.eventId,d.messageContext.priorityId), g), h), m), n), p), q), d.messageContext.eventMetadata), function() {
                    if (t) {
                        var v = t;
                        t = void 0;
                        v("2");
                        if (d.messageContext.onSuccess)
                            d.messageContext.onSuccess()
                    }
                }), function() {
                    if (t) {
                        var v = t;
                        t = void 0;
                        v("3");
                        if (d.messageContext.onFailure)
                            d.messageContext.onFailure()
                    }
                }), !!d.messageContext.isGtmEvent));
                try {
                    Im(d.messageContext.eventId, r, "1"),
                    mm(d.type, d.m.id, u),
                    f(d.m.id, b, d.F, u)
                } catch (v) {
                    Im(d.messageContext.eventId, r, "4")
                }
            }
        }
    };
    Tm.prototype.register = function(a, b, c) {
        var d = Om(this, a);
        3 !== d.status && (d.da = b,
        d.status = 3,
        c && (k(d.m, c),
        d.m = c),
        this.flush())
    }
    ;
    Tm.prototype.push = function(a, b, c, d) {
        void 0 !== c && (1 === Om(this, c).status && (Om(this, c).status = 2,
        this.push("require", [{}], c, {})),
        Om(this, c).H && (d.deferrable = !1));
        this.m.push(new Sm(a,c,b,d));
        d.deferrable || this.flush()
    }
    ;
    Tm.prototype.flush = function(a) {
        for (var b = this, c = [], d = !1, e = {}; this.m.length; e = {
            Ec: void 0,
            lh: void 0
        }) {
            var f = this.m[0]
              , g = f.m;
            if (f.messageContext.deferrable)
                !g || Om(this, g).H ? (f.messageContext.deferrable = !1,
                this.m.push(f)) : c.push(f),
                this.m.shift();
            else {
                switch (f.type) {
                case "require":
                    if (3 !== Om(this, g).status && !a) {
                        this.m.push.apply(this.m, c);
                        return
                    }
                    break;
                case "set":
                    z(f.args[0], function(r, t) {
                        k(Jb(r, t), b.H)
                    });
                    break;
                case "config":
                    var h = Om(this, g);
                    e.Ec = {};
                    z(f.args[0], function(r) {
                        return function(t, u) {
                            k(Jb(t, u), r.Ec)
                        }
                    }(e));
                    var m = !!e.Ec[P.g.Xb];
                    delete e.Ec[P.g.Xb];
                    var n = g.ka === g.id;
                    m || (n ? h.M = {} : h.T[g.id] = {});
                    h.H && m || Um(this, P.g.fa, e.Ec, f);
                    h.H = !0;
                    n ? k(e.Ec, h.M) : (k(e.Ec, h.T[g.id]),
                    O(70));
                    d = !0;
                    break;
                case "event":
                    e.lh = {};
                    z(f.args[0], function(r) {
                        return function(t, u) {
                            k(Jb(t, u), r.lh)
                        }
                    }(e));
                    Um(this, f.args[1], e.lh, f);
                    break;
                case "get":
                    var p = {}
                      , q = (p[P.g.qb] = f.args[0],
                    p[P.g.Eb] = f.args[1],
                    p);
                    Um(this, P.g.Ra, q, f)
                }
                this.m.shift();
                Vm(this, f)
            }
        }
        this.m.push.apply(this.m, c);
        d && this.flush()
    }
    ;
    var Vm = function(a, b) {
        if ("require" !== b.type)
            if (b.m)
                for (var c = Om(a, b.m).F[b.type] || [], d = 0; d < c.length; d++)
                    c[d]();
            else
                for (var e in a.F)
                    if (a.F.hasOwnProperty(e)) {
                        var f = a.F[e];
                        if (f && f.F)
                            for (var g = f.F[b.type] || [], h = 0; h < g.length; h++)
                                g[h]()
                    }
    }
      , Km = new Tm;
    function Wm(a, b, c, d) {
        d = void 0 === d ? !1 : d;
        a.google_image_requests || (a.google_image_requests = []);
        var e = bl("IMG", a.document);
        if (c) {
            var f = function() {
                if (c) {
                    var g = a.google_image_requests
                      , h = ic(g, e);
                    0 <= h && Array.prototype.splice.call(g, h, 1)
                }
                e.removeEventListener && e.removeEventListener("load", f, !1);
                e.removeEventListener && e.removeEventListener("error", f, !1)
            };
            Ak(e, "load", f);
            Ak(e, "error", f)
        }
        d && (e.attributionSrc = "");
        e.src = b;
        a.google_image_requests.push(e)
    }
    var Ym = function(a) {
        var b;
        b = void 0 === b ? !1 : b;
        var c = "https://pagead2.googlesyndication.com/pagead/gen_204?id=tcfe";
        $k(a, function(d, e) {
            if (d || 0 === d)
                c += "&" + e + "=" + encodeURIComponent("" + d)
        });
        Xm(c, b)
    }
      , Xm = function(a, b) {
        var c = window, d;
        b = void 0 === b ? !1 : b;
        d = void 0 === d ? !1 : d;
        if (c.fetch) {
            var e = {
                keepalive: !0,
                credentials: "include",
                redirect: "follow",
                method: "get",
                mode: "no-cors"
            };
            d && (e.mode = "cors",
            "setAttributionReporting"in XMLHttpRequest.prototype ? e.attributionReporting = {
                eventSourceEligible: "true",
                triggerEligible: "false"
            } : e.headers = {
                "Attribution-Reporting-Eligible": "event-source"
            });
            c.fetch(a, e)
        } else
            Wm(c, a, void 0 === b ? !1 : b, void 0 === d ? !1 : d)
    };
    var Zm = function() {
        this.T = this.T;
        this.H = this.H
    };
    Zm.prototype.T = !1;
    Zm.prototype.addOnDisposeCallback = function(a, b) {
        this.T ? void 0 !== b ? a.call(b) : a() : (this.H || (this.H = []),
        this.H.push(void 0 !== b ? Da(a, b) : a))
    }
    ;
    var $m = function(a) {
        void 0 !== a.addtlConsent && "string" !== typeof a.addtlConsent && (a.addtlConsent = void 0);
        void 0 !== a.gdprApplies && "boolean" !== typeof a.gdprApplies && (a.gdprApplies = void 0);
        return void 0 !== a.tcString && "string" !== typeof a.tcString || void 0 !== a.listenerId && "number" !== typeof a.listenerId ? 2 : a.cmpStatus && "error" !== a.cmpStatus ? 0 : 3
    }
      , an = function(a, b) {
        b = void 0 === b ? {} : b;
        Zm.call(this);
        this.F = a;
        this.m = null;
        this.Wa = {};
        this.Dc = 0;
        var c;
        this.Yb = null != (c = b.Zm) ? c : 500;
        var d;
        this.da = null != (d = b.Nn) ? d : !1;
        this.M = null
    };
    ya(an, Zm);
    var cn = function(a) {
        return "function" === typeof a.F.__tcfapi || null != bn(a)
    };
    an.prototype.addEventListener = function(a) {
        var b = this
          , c = {
            internalBlockOnErrors: this.da
        }
          , d = zk(function() {
            return a(c)
        })
          , e = 0;
        -1 !== this.Yb && (e = setTimeout(function() {
            c.tcString = "tcunavailable";
            c.internalErrorState = 1;
            d()
        }, this.Yb));
        var f = function(g, h) {
            clearTimeout(e);
            g ? (c = g,
            c.internalErrorState = $m(c),
            c.internalBlockOnErrors = b.da,
            h && 0 === c.internalErrorState || (c.tcString = "tcunavailable",
            h || (c.internalErrorState = 3))) : (c.tcString = "tcunavailable",
            c.internalErrorState = 3);
            a(c)
        };
        try {
            dn(this, "addEventListener", f)
        } catch (g) {
            c.tcString = "tcunavailable",
            c.internalErrorState = 3,
            e && (clearTimeout(e),
            e = 0),
            d()
        }
    }
    ;
    an.prototype.removeEventListener = function(a) {
        a && a.listenerId && dn(this, "removeEventListener", null, a.listenerId)
    }
    ;
    var fn = function(a, b, c) {
        var d;
        d = void 0 === d ? "755" : d;
        var e;
        a: {
            if (a.publisher && a.publisher.restrictions) {
                var f = a.publisher.restrictions[b];
                if (void 0 !== f) {
                    e = f[void 0 === d ? "755" : d];
                    break a
                }
            }
            e = void 0
        }
        var g = e;
        if (0 === g)
            return !1;
        var h = c;
        2 === c ? (h = 0,
        2 === g && (h = 1)) : 3 === c && (h = 1,
        1 === g && (h = 0));
        var m;
        if (0 === h)
            if (a.purpose && a.vendor) {
                var n = en(a.vendor.consents, void 0 === d ? "755" : d);
                m = n && "1" === b && a.purposeOneTreatment && "CH" === a.publisherCC ? !0 : n && en(a.purpose.consents, b)
            } else
                m = !0;
        else
            m = 1 === h ? a.purpose && a.vendor ? en(a.purpose.legitimateInterests, b) && en(a.vendor.legitimateInterests, void 0 === d ? "755" : d) : !0 : !0;
        return m
    }
      , en = function(a, b) {
        return !(!a || !a[b])
    }
      , dn = function(a, b, c, d) {
        c || (c = function() {}
        );
        if ("function" === typeof a.F.__tcfapi) {
            var e = a.F.__tcfapi;
            e(b, 2, c, d)
        } else if (bn(a)) {
            gn(a);
            var f = ++a.Dc;
            a.Wa[f] = c;
            if (a.m) {
                var g = {};
                a.m.postMessage((g.__tcfapiCall = {
                    command: b,
                    version: 2,
                    callId: f,
                    parameter: d
                },
                g), "*")
            }
        } else
            c({}, !1)
    }
      , bn = function(a) {
        if (a.m)
            return a.m;
        var b;
        a: {
            for (var c = a.F, d = 0; 50 > d; ++d) {
                var e;
                try {
                    e = !(!c.frames || !c.frames.__tcfapiLocator)
                } catch (h) {
                    e = !1
                }
                if (e) {
                    b = c;
                    break a
                }
                var f;
                b: {
                    try {
                        var g = c.parent;
                        if (g && g != c) {
                            f = g;
                            break b
                        }
                    } catch (h) {}
                    f = null
                }
                if (!(c = f))
                    break
            }
            b = null
        }
        a.m = b;
        return a.m
    }
      , gn = function(a) {
        a.M || (a.M = function(b) {
            try {
                var c;
                c = ("string" === typeof b.data ? JSON.parse(b.data) : b.data).__tcfapiReturn;
                a.Wa[c.callId](c.returnValue, c.success)
            } catch (d) {}
        }
        ,
        Ak(a.F, "message", a.M))
    }
      , hn = function(a) {
        if (!1 === a.gdprApplies)
            return !0;
        void 0 === a.internalErrorState && (a.internalErrorState = $m(a));
        return "error" === a.cmpStatus || 0 !== a.internalErrorState ? a.internalBlockOnErrors ? (Ym({
            e: String(a.internalErrorState)
        }),
        !1) : !0 : "loaded" !== a.cmpStatus || "tcloaded" !== a.eventStatus && "useractioncomplete" !== a.eventStatus ? !1 : !0
    };
    var jn = {
        1: 0,
        3: 0,
        4: 0,
        7: 3,
        9: 3,
        10: 3
    };
    function kn() {
        var a = ii.tcf || {};
        return ii.tcf = a
    }
    var ln = function() {
        return new an(G,{
            Zm: -1
        })
    }
      , rn = function() {
        var a = kn()
          , b = ln();
        cn(b) && !mn() && !nn() && O(124);
        if (!a.active && cn(b)) {
            mn() && (a.active = !0,
            a.jc = {},
            a.cmpId = 0,
            a.tcfPolicyVersion = 0,
            wl().active = !0,
            a.tcString = "tcunavailable");
            Yl();
            try {
                b.addEventListener(function(c) {
                    if (0 !== c.internalErrorState)
                        on(a),
                        Zl([P.g.R, P.g.Aa, P.g.P]),
                        wl().active = !0;
                    else if (a.gdprApplies = c.gdprApplies,
                    a.cmpId = c.cmpId,
                    a.enableAdvertiserConsentMode = c.enableAdvertiserConsentMode,
                    nn() && (a.active = !0),
                    !pn(c) || mn() || nn()) {
                        a.tcfPolicyVersion = c.tcfPolicyVersion;
                        var d;
                        if (!1 === c.gdprApplies) {
                            var e = {}, f;
                            for (f in jn)
                                jn.hasOwnProperty(f) && (e[f] = !0);
                            d = e;
                            b.removeEventListener(c)
                        } else if (pn(c)) {
                            var g = {}, h;
                            for (h in jn)
                                if (jn.hasOwnProperty(h))
                                    if ("1" === h) {
                                        var m, n = c, p = {
                                            Hl: !0
                                        };
                                        p = void 0 === p ? {} : p;
                                        m = hn(n) ? !1 === n.gdprApplies ? !0 : "tcunavailable" === n.tcString ? !p.Oj : (p.Oj || void 0 !== n.gdprApplies || p.Hl) && (p.Oj || "string" === typeof n.tcString && n.tcString.length) ? fn(n, "1", 0) : !0 : !1;
                                        g["1"] = m
                                    } else
                                        g[h] = fn(c, h, jn[h]);
                            d = g
                        }
                        if (d) {
                            a.tcString = c.tcString || "tcempty";
                            a.jc = d;
                            var q = {}
                              , r = (q[P.g.R] = a.jc["1"] ? "granted" : "denied",
                            q);
                            !0 !== a.gdprApplies ? (Zl([P.g.R, P.g.Aa, P.g.P]),
                            wl().active = !0) : (r[P.g.Aa] = a.jc["3"] && a.jc["4"] ? "granted" : "denied",
                            "number" === typeof a.tcfPolicyVersion && 4 <= a.tcfPolicyVersion ? r[P.g.P] = a.jc["1"] && a.jc["7"] ? "granted" : "denied" : Zl([P.g.P]),
                            Tl(r, {
                                eventId: 0
                            }, {
                                gdprApplies: a ? a.gdprApplies : void 0,
                                tcString: qn() || ""
                            }))
                        }
                    } else
                        Zl([P.g.R, P.g.Aa, P.g.P])
                })
            } catch (c) {
                on(a),
                Zl([P.g.R, P.g.Aa, P.g.P]),
                wl().active = !0
            }
        }
    };
    function on(a) {
        a.type = "e";
        a.tcString = "tcunavailable"
    }
    function pn(a) {
        return "tcloaded" === a.eventStatus || "useractioncomplete" === a.eventStatus || "cmpuishown" === a.eventStatus
    }
    var mn = function() {
        return !0 === G.gtag_enable_tcf_support
    };
    function nn() {
        return !0 === kn().enableAdvertiserConsentMode
    }
    var qn = function() {
        var a = kn();
        if (a.active)
            return a.tcString
    }
      , sn = function() {
        var a = kn();
        if (a.active && void 0 !== a.gdprApplies)
            return a.gdprApplies ? "1" : "0"
    }
      , tn = function(a) {
        if (!jn.hasOwnProperty(String(a)))
            return !0;
        var b = kn();
        return b.active && b.jc ? !!b.jc[String(a)] : !0
    };
    var un = [P.g.R, P.g.W, P.g.P, P.g.Aa]
      , vn = {}
      , wn = (vn[P.g.R] = 1,
    vn[P.g.W] = 2,
    vn);
    function xn(a) {
        if (void 0 === a)
            return 0;
        switch (U(a, P.g.oa)) {
        case void 0:
            return 1;
        case !1:
            return 3;
        default:
            return 2
        }
    }
    var yn = function(a) {
        var b = xn(a);
        if (3 === b)
            return !1;
        switch (Gl(P.g.Aa)) {
        case 1:
        case 3:
            return !0;
        case 2:
            return !1;
        case 4:
            return 2 === b;
        case 0:
            return !0;
        default:
            return !1
        }
    }
      , zn = function() {
        return Jl() || !Fl(P.g.R) || !Fl(P.g.W)
    }
      , An = function() {
        var a = {}, b;
        for (b in wn)
            wn.hasOwnProperty(b) && (a[wn[b]] = Gl(b));
        return "G1" + Be(a[1] || 0) + Be(a[2] || 0)
    }
      , Bn = {}
      , Cn = (Bn[P.g.R] = 0,
    Bn[P.g.W] = 1,
    Bn[P.g.P] = 2,
    Bn[P.g.Aa] = 3,
    Bn);
    function Dn(a) {
        switch (a) {
        case void 0:
            return 1;
        case !0:
            return 3;
        case !1:
            return 2;
        default:
            return 0
        }
    }
    var En = function(a) {
        for (var b = "1", c = 0; c < un.length; c++) {
            var d = b, e, f = un[c], g = El.delegatedConsentTypes[f];
            e = void 0 === g ? 0 : Cn.hasOwnProperty(g) ? 12 | Cn[g] : 8;
            var h = wl();
            h.accessedAny = !0;
            var m = h.entries[f] || {};
            e = e << 2 | Dn(m.implicit);
            b = d + ("" + "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_"[e] + "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_"[Dn(m.declare) << 4 | Dn(m.default) << 2 | Dn(m.update)])
        }
        var n = b, p;
        p = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_"[(Jl() ? 1 : 0) << 2 | xn(a)];
        return n + p
    }
      , Fn = function() {
        if (!Fl(P.g.P))
            return "-";
        for (var a = Object.keys(gi), b = Hl(a), c = "", d = na(a), e = d.next(); !e.done; e = d.next()) {
            var f = e.value;
            b[f] && (c += gi[f])
        }
        return c || "-"
    }
      , Pn = function() {
        return rl() || (mn() || nn()) && "1" === sn() ? "1" : "0"
    }
      , Qn = function() {
        return (rl() ? !0 : !(!mn() && !nn()) && "1" === sn()) || !Fl(P.g.P)
    }
      , Rn = function() {
        var a = "0", b = "0", c;
        var d = kn();
        c = d.active ? d.cmpId : void 0;
        "number" === typeof c && 0 <= c && 4095 >= c && (a = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_"[c >> 6 & 63],
        b = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_"[c & 63]);
        var e = "0", f;
        var g = kn();
        f = g.active ? g.tcfPolicyVersion : void 0;
        "number" === typeof f && 0 <= f && 63 >= f && (e = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_"[f]);
        var h = 0;
        rl() && (h |= 1);
        "1" === sn() && (h |= 2);
        mn() && (h |= 4);
        var m;
        var n = kn();
        m = void 0 !== n.enableAdvertiserConsentMode ? n.enableAdvertiserConsentMode ? "1" : "0" : void 0;
        "1" === m && (h |= 8);
        wl().waitPeriodTimedOut && (h |= 16);
        return "1" + a + b + e + "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_"[h]
    };
    function Sn() {
        var a = !1;
        return a
    }
    ;var Tn = {
        UA: 1,
        AW: 2,
        DC: 3,
        G: 4,
        GF: 5,
        GT: 12,
        GTM: 14,
        HA: 6,
        MC: 7
    };
    function Un(a) {
        a = void 0 === a ? {} : a;
        var b = Hf.ctid.split("-")[0].toUpperCase()
          , c = {};
        c.ctid = Hf.ctid;
        c.Im = hi.ne;
        c.Mm = hi.Qg;
        c.im = vj.je ? 2 : 1;
        c.Tm = a.gk;
        c.ue = Hf.canonicalContainerId;
        c.ue !== a.za && (c.za = a.za);
        if (T(62)) {
            var d = Fj();
            c.ym = d ? d.canonicalContainerId : void 0
        }
        ni ? (c.Pf = Tn[b],
        c.Pf || (c.Pf = 0)) : c.Pf = ri ? 13 : 10;
        Ai.M ? (c.Nf = 0,
        c.ml = 2) : pi ? c.Nf = 1 : Sn() ? c.Nf = 2 : c.Nf = 3;
        var e = {};
        e[6] = wj;
        c.pl = e;
        var f = a.Hf, g;
        var h = c.Pf
          , m = c.Nf;
        void 0 === h ? g = "" : (m || (m = 0),
        g = "" + yg(1, 1) + Ae(h << 2 | m));
        var n = c.ml, p = 4 + g + (n ? "" + yg(2, 1) + Ae(n) : ""), q, r = c.Mm;
        q = r && xg.test(r) ? "" + yg(3, 2) + r : "";
        var t, u = c.Im;
        t = u ? "" + yg(4, 1) + Ae(u) : "";
        var v;
        var w = c.ctid;
        if (w && f) {
            var y = w.split("-")
              , x = y[0].toUpperCase();
            if ("GTM" !== x && "OPT" !== x)
                v = "";
            else {
                var B = y[1];
                v = "" + yg(5, 3) + Ae(1 + B.length) + (c.im || 0) + B
            }
        } else
            v = "";
        var A = c.Tm, D = c.ue, E = c.za, C = c.Xn, F = p + q + t + v + (A ? "" + yg(6, 1) + Ae(A) : "") + (D ? "" + yg(7, 3) + Ae(D.length) + D : "") + (E ? "" + yg(8, 3) + Ae(E.length) + E : "") + (C ? "" + yg(9, 3) + Ae(C.length) + C : ""), L;
        var N = c.pl;
        N = void 0 === N ? {} : N;
        for (var Q = [], V = na(Object.keys(N)), ca = V.next(); !ca.done; ca = V.next()) {
            var Z = ca.value;
            Q[Number(Z)] = N[Z]
        }
        if (Q.length) {
            var R = yg(10, 3), oa;
            if (0 === Q.length)
                oa = Ae(0);
            else {
                for (var ka = [], ha = 0, ja = !1, Ja = 0; Ja < Q.length; Ja++) {
                    ja = !0;
                    var Fa = Ja % 6;
                    Q[Ja] && (ha |= 1 << Fa);
                    5 === Fa && (ka.push(Ae(ha)),
                    ha = 0,
                    ja = !1)
                }
                ja && ka.push(Ae(ha));
                oa = ka.join("")
            }
            var Pa = oa;
            L = "" + R + Ae(Pa.length) + Pa
        } else
            L = "";
        var Sa = c.ym;
        return F + L + (Sa ? "" + yg(11, 3) + Ae(Sa.length) + Sa : "")
    }
    ;var Vn = {
        Rg: "service_worker_endpoint",
        Sg: "shared_user_id",
        Tg: "shared_user_id_requested",
        Ug: "shared_user_id_source"
    }, Wn;
    function Xn(a) {
        Wn || (Wn = Object.keys(Vn).map(function(b) {
            return Vn[b]
        }));
        return Wn.includes(a)
    }
    function Yn(a, b) {
        if (Xn(a)) {
            var c = rc("google_tag_data", {})
              , d = c.xcd;
            d || (d = {},
            c.xcd = d);
            var e = d[a];
            e ? e.set(b) : d[a] = {
                set: function(f) {
                    b = f
                },
                get: function() {
                    return b
                }
            }
        }
    }
    function Zn(a) {
        if (Xn(a)) {
            var b, c;
            return null == (b = rc("google_tag_data", {}).xcd) ? void 0 : null == (c = b[a]) ? void 0 : c.get()
        }
    }
    ;function $n(a) {
        return "null" !== a.origin
    }
    ;function ao(a, b, c, d) {
        var e;
        if (bo(d)) {
            for (var f = [], g = String(b || co()).split(";"), h = 0; h < g.length; h++) {
                var m = g[h].split("=")
                  , n = m[0].replace(/^\s*|\s*$/g, "");
                if (n && n == a) {
                    var p = m.slice(1).join("=").replace(/^\s*|\s*$/g, "");
                    p && c && (p = decodeURIComponent(p));
                    f.push(p)
                }
            }
            e = f
        } else
            e = [];
        return e
    }
    function eo(a, b, c, d, e) {
        if (bo(e)) {
            var f = fo(a, d, e);
            if (1 === f.length)
                return f[0].id;
            if (0 !== f.length) {
                f = go(f, function(g) {
                    return g.xl
                }, b);
                if (1 === f.length)
                    return f[0].id;
                f = go(f, function(g) {
                    return g.Am
                }, c);
                return f[0] ? f[0].id : void 0
            }
        }
    }
    function ho(a, b, c, d) {
        var e = co()
          , f = window;
        $n(f) && (f.document.cookie = a);
        var g = co();
        return e !== g || void 0 !== c && 0 <= ao(b, g, !1, d).indexOf(c)
    }
    function io(a, b, c, d) {
        function e(w, y, x) {
            if (null == x)
                return delete h[y],
                w;
            h[y] = x;
            return w + "; " + y + "=" + x
        }
        function f(w, y) {
            if (null == y)
                return w;
            h[y] = !0;
            return w + "; " + y
        }
        if (!bo(c.zb))
            return 2;
        var g;
        null == b ? g = a + "=deleted; expires=" + (new Date(0)).toUTCString() : (c.encode && (b = encodeURIComponent(b)),
        b = jo(b),
        g = a + "=" + b);
        var h = {};
        g = e(g, "path", c.path);
        var m;
        c.expires instanceof Date ? m = c.expires.toUTCString() : null != c.expires && (m = "" + c.expires);
        g = e(g, "expires", m);
        g = e(g, "max-age", c.mm);
        g = e(g, "samesite", c.Nm);
        c.Om && (g = f(g, "secure"));
        var n = c.domain;
        if (n && "auto" === n.toLowerCase()) {
            for (var p = ko(), q = void 0, r = !1, t = 0; t < p.length; ++t) {
                var u = "none" !== p[t] ? p[t] : void 0
                  , v = e(g, "domain", u);
                v = f(v, c.flags);
                try {
                    d && d(a, h)
                } catch (w) {
                    q = w;
                    continue
                }
                r = !0;
                if (!lo(u, c.path) && ho(v, a, b, c.zb))
                    return 0
            }
            if (q && !r)
                throw q;
            return 1
        }
        n && "none" !== n.toLowerCase() && (g = e(g, "domain", n));
        g = f(g, c.flags);
        d && d(a, h);
        return lo(n, c.path) ? 1 : ho(g, a, b, c.zb) ? 0 : 1
    }
    function mo(a, b, c) {
        null == c.path && (c.path = "/");
        c.domain || (c.domain = "auto");
        return io(a, b, c)
    }
    function go(a, b, c) {
        for (var d = [], e = [], f, g = 0; g < a.length; g++) {
            var h = a[g]
              , m = b(h);
            m === c ? d.push(h) : void 0 === f || m < f ? (e = [h],
            f = m) : m === f && e.push(h)
        }
        return 0 < d.length ? d : e
    }
    function fo(a, b, c) {
        for (var d = [], e = ao(a, void 0, void 0, c), f = 0; f < e.length; f++) {
            var g = e[f].split(".")
              , h = g.shift();
            if (!b || !h || -1 !== b.indexOf(h)) {
                var m = g.shift();
                if (m) {
                    var n = m.split("-");
                    d.push({
                        id: g.join("."),
                        xl: Number(n[0]) || 1,
                        Am: Number(n[1]) || 1
                    })
                }
            }
        }
        return d
    }
    function jo(a) {
        a && 1200 < a.length && (a = a.substring(0, 1200));
        return a
    }
    var no = /^(www\.)?google(\.com?)?(\.[a-z]{2})?$/
      , oo = /(^|\.)doubleclick\.net$/i;
    function lo(a, b) {
        return void 0 !== a && (oo.test(window.document.location.hostname) || "/" === b && no.test(a))
    }
    function po(a) {
        if (!a)
            return 1;
        a = 0 === a.indexOf(".") ? a.substring(1) : a;
        return a.split(".").length
    }
    function qo(a) {
        if (!a || "/" === a)
            return 1;
        "/" !== a[0] && (a = "/" + a);
        "/" !== a[a.length - 1] && (a += "/");
        return a.split("/").length - 1
    }
    function ro(a, b) {
        var c = "" + po(a)
          , d = qo(b);
        1 < d && (c += "-" + d);
        return c
    }
    var co = function() {
        return $n(window) ? window.document.cookie : ""
    }
      , bo = function(a) {
        return a && Bl().m() ? (Array.isArray(a) ? a : [a]).every(function(b) {
            return Il(b) && Fl(b)
        }) : !0
    }
      , ko = function() {
        var a = []
          , b = window.document.location.hostname.split(".");
        if (4 === b.length) {
            var c = b[b.length - 1];
            if (Number(c).toString() === c)
                return ["none"]
        }
        for (var d = b.length - 2; 0 <= d; d--)
            a.push(b.slice(d).join("."));
        var e = window.document.location.hostname;
        oo.test(e) || no.test(e) || a.push("none");
        return a
    };
    function so(a) {
        var b = Math.round(2147483647 * Math.random()), c;
        if (a) {
            var d = 1, e, f, g;
            if (a)
                for (d = 0,
                f = a.length - 1; 0 <= f; f--)
                    g = a.charCodeAt(f),
                    d = (d << 6 & 268435455) + g + (g << 14),
                    e = d & 266338304,
                    d = 0 !== e ? d ^ e >> 21 : d;
            c = String(b ^ d & 2147483647)
        } else
            c = String(b);
        return c
    }
    function to(a) {
        return [so(a), Math.round(Cb() / 1E3)].join(".")
    }
    function uo(a, b, c, d, e) {
        var f = po(b);
        return eo(a, f, qo(c), d, e)
    }
    function vo(a, b, c, d) {
        return [b, ro(c, d), a].join(".")
    }
    ;function wo(a, b, c, d) {
        var e, f = Number(null != a.yb ? a.yb : void 0);
        0 !== f && (e = new Date((b || Cb()) + 1E3 * (f || 7776E3)));
        return {
            path: a.path,
            domain: a.domain,
            flags: a.flags,
            encode: !!c,
            expires: e,
            zb: d
        }
    }
    ;var xo;
    function yo() {
        function a(g) {
            c(g.target || g.srcElement || {})
        }
        function b(g) {
            d(g.target || g.srcElement || {})
        }
        var c = zo
          , d = Ao
          , e = Bo();
        if (!e.init) {
            Ac(H, "mousedown", a);
            Ac(H, "keyup", a);
            Ac(H, "submit", b);
            var f = HTMLFormElement.prototype.submit;
            HTMLFormElement.prototype.submit = function() {
                d(this);
                f.call(this)
            }
            ;
            e.init = !0
        }
    }
    function Co(a, b, c, d, e) {
        var f = {
            callback: a,
            domains: b,
            fragment: 2 === c,
            placement: c,
            forms: d,
            sameHost: e
        };
        Bo().decorators.push(f)
    }
    function Do(a, b, c) {
        for (var d = Bo().decorators, e = {}, f = 0; f < d.length; ++f) {
            var g = d[f], h;
            if (h = !c || g.forms)
                a: {
                    var m = g.domains
                      , n = a
                      , p = !!g.sameHost;
                    if (m && (p || n !== H.location.hostname))
                        for (var q = 0; q < m.length; q++)
                            if (m[q]instanceof RegExp) {
                                if (m[q].test(n)) {
                                    h = !0;
                                    break a
                                }
                            } else if (0 <= n.indexOf(m[q]) || p && 0 <= m[q].indexOf(n)) {
                                h = !0;
                                break a
                            }
                    h = !1
                }
            if (h) {
                var r = g.placement;
                void 0 === r && (r = g.fragment ? 2 : 1);
                r === b && Fb(e, g.callback())
            }
        }
        return e
    }
    function Bo() {
        var a = rc("google_tag_data", {})
          , b = a.gl;
        b && b.decorators || (b = {
            decorators: []
        },
        a.gl = b);
        return b
    }
    ;var Eo = /(.*?)\*(.*?)\*(.*)/
      , Fo = /^https?:\/\/([^\/]*?)\.?cdn\.ampproject\.org\/?(.*)/
      , Go = /^(?:www\.|m\.|amp\.)+/
      , Ho = /([^?#]+)(\?[^#]*)?(#.*)?/;
    function Io(a) {
        var b = Ho.exec(a);
        if (b)
            return {
                Hh: b[1],
                query: b[2],
                fragment: b[3]
            }
    }
    function Jo(a, b) {
        var c = [oc.userAgent, (new Date).getTimezoneOffset(), oc.userLanguage || oc.language, Math.floor(Cb() / 60 / 1E3) - (void 0 === b ? 0 : b), a].join("*"), d;
        if (!(d = xo)) {
            for (var e = Array(256), f = 0; 256 > f; f++) {
                for (var g = f, h = 0; 8 > h; h++)
                    g = g & 1 ? g >>> 1 ^ 3988292384 : g >>> 1;
                e[f] = g
            }
            d = e
        }
        xo = d;
        for (var m = 4294967295, n = 0; n < c.length; n++)
            m = m >>> 8 ^ xo[(m ^ c.charCodeAt(n)) & 255];
        return ((m ^ -1) >>> 0).toString(36)
    }
    function Ko() {
        return function(a) {
            var b = hj(G.location.href)
              , c = b.search.replace("?", "")
              , d = aj(c, "_gl", !1, !0) || "";
            a.query = Lo(d) || {};
            var e = dj(b, "fragment"), f;
            var g = -1;
            if (Hb(e, "_gl="))
                g = 4;
            else {
                var h = e.indexOf("&_gl=");
                0 < h && (g = h + 3 + 2)
            }
            if (0 > g)
                f = void 0;
            else {
                var m = e.indexOf("&", g);
                f = 0 > m ? e.substring(g) : e.substring(g, m)
            }
            a.fragment = Lo(f || "") || {}
        }
    }
    function Mo(a) {
        var b = Ko()
          , c = Bo();
        c.data || (c.data = {
            query: {},
            fragment: {}
        },
        b(c.data));
        var d = {}
          , e = c.data;
        e && (Fb(d, e.query),
        a && Fb(d, e.fragment));
        return d
    }
    var Lo = function(a) {
        try {
            var b = No(a, 3);
            if (void 0 !== b) {
                for (var c = {}, d = b ? b.split("*") : [], e = 0; e + 1 < d.length; e += 2) {
                    var f = d[e]
                      , g = jb(d[e + 1]);
                    c[f] = g
                }
                lb("TAGGING", 6);
                return c
            }
        } catch (h) {
            lb("TAGGING", 8)
        }
    };
    function No(a, b) {
        if (a) {
            var c;
            a: {
                for (var d = a, e = 0; 3 > e; ++e) {
                    var f = Eo.exec(d);
                    if (f) {
                        c = f;
                        break a
                    }
                    d = decodeURIComponent(d)
                }
                c = void 0
            }
            var g = c;
            if (g && "1" === g[1]) {
                var h = g[3], m;
                a: {
                    for (var n = g[2], p = 0; p < b; ++p)
                        if (n === Jo(h, p)) {
                            m = !0;
                            break a
                        }
                    m = !1
                }
                if (m)
                    return h;
                lb("TAGGING", 7)
            }
        }
    }
    function Oo(a, b, c, d, e) {
        function f(p) {
            var q = p
              , r = (new RegExp("(.*?)(^|&)" + a + "=([^&]*)&?(.*)")).exec(q)
              , t = q;
            if (r) {
                var u = r[2]
                  , v = r[4];
                t = r[1];
                v && (t = t + u + v)
            }
            p = t;
            var w = p.charAt(p.length - 1);
            p && "&" !== w && (p += "&");
            return p + n
        }
        d = void 0 === d ? !1 : d;
        e = void 0 === e ? !1 : e;
        var g = Io(c);
        if (!g)
            return "";
        var h = g.query || ""
          , m = g.fragment || ""
          , n = a + "=" + b;
        d ? 0 !== m.substring(1).length && e || (m = "#" + f(m.substring(1))) : h = "?" + f(h.substring(1));
        return "" + g.Hh + h + m
    }
    function Po(a, b) {
        function c(n, p, q) {
            var r;
            a: {
                for (var t in n)
                    if (n.hasOwnProperty(t)) {
                        r = !0;
                        break a
                    }
                r = !1
            }
            if (r) {
                var u, v = [], w;
                for (w in n)
                    if (n.hasOwnProperty(w)) {
                        var y = n[w];
                        void 0 !== y && y === y && null !== y && "[object Object]" !== y.toString() && (v.push(w),
                        v.push(ib(String(y))))
                    }
                var x = v.join("*");
                u = ["1", Jo(x), x].join("*");
                d ? (Ti(3) || Ti(1) || !p) && Qo("_gl", u, a, p, q) : Ro("_gl", u, a, p, q)
            }
        }
        var d = "FORM" === (a.tagName || "").toUpperCase()
          , e = Do(b, 1, d)
          , f = Do(b, 2, d)
          , g = Do(b, 4, d)
          , h = Do(b, 3, d);
        c(e, !1, !1);
        c(f, !0, !1);
        Ti(1) && c(g, !0, !0);
        for (var m in h)
            h.hasOwnProperty(m) && So(m, h[m], a)
    }
    function So(a, b, c) {
        "a" === c.tagName.toLowerCase() ? Ro(a, b, c) : "form" === c.tagName.toLowerCase() && Qo(a, b, c)
    }
    function Ro(a, b, c, d, e) {
        d = void 0 === d ? !1 : d;
        e = void 0 === e ? !1 : e;
        var f;
        if (f = c.href) {
            var g;
            if (!(g = !Ti(4) || d)) {
                var h = G.location.href
                  , m = Io(c.href)
                  , n = Io(h);
                g = !(m && n && m.Hh === n.Hh && m.query === n.query && m.fragment)
            }
            f = g
        }
        if (f) {
            var p = Oo(a, b, c.href, d, e);
            ec.test(p) && (c.href = p)
        }
    }
    function Qo(a, b, c, d, e) {
        d = void 0 === d ? !1 : d;
        e = void 0 === e ? !1 : e;
        if (c && c.action) {
            var f = (c.method || "").toLowerCase();
            if ("get" !== f || d) {
                if ("get" === f || "post" === f) {
                    var g = Oo(a, b, c.action, d, e);
                    ec.test(g) && (c.action = g)
                }
            } else {
                for (var h = c.childNodes || [], m = !1, n = 0; n < h.length; n++) {
                    var p = h[n];
                    if (p.name === a) {
                        p.setAttribute("value", b);
                        m = !0;
                        break
                    }
                }
                if (!m) {
                    var q = H.createElement("input");
                    q.setAttribute("type", "hidden");
                    q.setAttribute("name", a);
                    q.setAttribute("value", b);
                    c.appendChild(q)
                }
            }
        }
    }
    function zo(a) {
        try {
            var b;
            a: {
                for (var c = a, d = 100; c && 0 < d; ) {
                    if (c.href && c.nodeName.match(/^a(?:rea)?$/i)) {
                        b = c;
                        break a
                    }
                    c = c.parentNode;
                    d--
                }
                b = null
            }
            var e = b;
            if (e) {
                var f = e.protocol;
                "http:" !== f && "https:" !== f || Po(e, e.hostname)
            }
        } catch (g) {}
    }
    function Ao(a) {
        try {
            if (a.action) {
                var b = dj(hj(a.action), "host");
                Po(a, b)
            }
        } catch (c) {}
    }
    function To(a, b, c, d) {
        yo();
        var e = "fragment" === c ? 2 : 1;
        d = !!d;
        Co(a, b, e, d, !1);
        2 === e && lb("TAGGING", 23);
        d && lb("TAGGING", 24)
    }
    function Uo(a, b) {
        yo();
        Co(a, [cj(G.location, "host", !0)], b, !0, !0)
    }
    function Vo() {
        var a = H.location.hostname
          , b = Fo.exec(H.referrer);
        if (!b)
            return !1;
        var c = b[2]
          , d = b[1]
          , e = "";
        if (c) {
            var f = c.split("/")
              , g = f[1];
            e = "s" === g ? decodeURIComponent(f[2]) : decodeURIComponent(g)
        } else if (d) {
            if (0 === d.indexOf("xn--"))
                return !1;
            e = d.replace(/-/g, ".").replace(/\.\./g, "-")
        }
        var h = a.replace(Go, ""), m = e.replace(Go, ""), n;
        if (!(n = h === m)) {
            var p = "." + m;
            n = h.substring(h.length - p.length, h.length) === p
        }
        return n
    }
    function Wo(a, b) {
        return !1 === a ? !1 : a || b || Vo()
    }
    ;var Xo = ["1"]
      , Yo = {}
      , Zo = {};
    function $o(a, b) {
        b = void 0 === b ? !0 : b;
        var c = ap(a.prefix);
        if (!Yo[c])
            if (bp(c, a.path, a.domain)) {
                var d = Zo[ap(a.prefix)];
                cp(a, d ? d.id : void 0, d ? d.Dh : void 0)
            } else {
                var e = jj("auiddc");
                if (e)
                    lb("TAGGING", 17),
                    Yo[c] = e;
                else if (b) {
                    var f = ap(a.prefix)
                      , g = to();
                    dp(f, g, a);
                    bp(c, a.path, a.domain)
                }
            }
    }
    function cp(a, b, c) {
        var d = ap(a.prefix)
          , e = Yo[d];
        if (e) {
            var f = e.split(".");
            if (2 === f.length) {
                var g = Number(f[1]) || 0;
                if (g) {
                    var h = e;
                    b && (h = e + "." + b + "." + (c ? c : Math.floor(Cb() / 1E3)));
                    dp(d, h, a, 1E3 * g)
                }
            }
        }
    }
    function dp(a, b, c, d) {
        var e = vo(b, "1", c.domain, c.path)
          , f = wo(c, d);
        f.zb = ep();
        mo(a, e, f)
    }
    function bp(a, b, c) {
        var d = uo(a, b, c, Xo, ep());
        if (!d)
            return !1;
        fp(a, d);
        return !0
    }
    function fp(a, b) {
        var c = b.split(".");
        5 === c.length ? (Yo[a] = c.slice(0, 2).join("."),
        Zo[a] = {
            id: c.slice(2, 4).join("."),
            Dh: Number(c[4]) || 0
        }) : 3 === c.length ? Zo[a] = {
            id: c.slice(0, 2).join("."),
            Dh: Number(c[2]) || 0
        } : Yo[a] = b
    }
    function ap(a) {
        return (a || "_gcl") + "_au"
    }
    function gp(a) {
        function b() {
            Fl(c) && a()
        }
        var c = ep();
        Ml(function() {
            b();
            Fl(c) || Nl(b, c)
        }, c)
    }
    function hp(a) {
        var b = Mo(!0)
          , c = ap(a.prefix);
        gp(function() {
            var d = b[c];
            if (d) {
                fp(c, d);
                var e = 1E3 * Number(Yo[c].split(".")[1]);
                if (e) {
                    lb("TAGGING", 16);
                    var f = wo(a, e);
                    f.zb = ep();
                    var g = vo(d, "1", a.domain, a.path);
                    mo(c, g, f)
                }
            }
        })
    }
    function ip(a, b, c, d, e) {
        e = e || {};
        var f = function() {
            var g = {}
              , h = uo(a, e.path, e.domain, Xo, ep());
            h && (g[a] = h);
            return g
        };
        gp(function() {
            To(f, b, c, d)
        })
    }
    function ep() {
        return ["ad_storage", "ad_user_data"]
    }
    ;function jp(a) {
        for (var b = [], c = H.cookie.split(";"), d = new RegExp("^\\s*" + (a || "_gac") + "_(UA-\\d+-\\d+)=\\s*(.+?)\\s*$"), e = 0; e < c.length; e++) {
            var f = c[e].match(d);
            f && b.push({
                Vh: f[1],
                value: f[2],
                timestamp: Number(f[2].split(".")[1]) || 0
            })
        }
        b.sort(function(g, h) {
            return h.timestamp - g.timestamp
        });
        return b
    }
    function kp(a, b) {
        var c = jp(a)
          , d = {};
        if (!c || !c.length)
            return d;
        for (var e = 0; e < c.length; e++) {
            var f = c[e].value.split(".");
            if (!("1" !== f[0] || b && 3 > f.length || !b && 3 !== f.length) && Number(f[1])) {
                d[c[e].Vh] || (d[c[e].Vh] = []);
                var g = {
                    version: f[0],
                    timestamp: 1E3 * Number(f[1]),
                    ba: f[2]
                };
                b && 3 < f.length && (g.labels = f.slice(3));
                d[c[e].Vh].push(g)
            }
        }
        return d
    }
    ;var lp = {}
      , mp = (lp.k = {
        Ma: /^[\w-]+$/
    },
    lp.b = {
        Ma: /^[\w-]+$/,
        Ph: !0
    },
    lp.i = {
        Ma: /^[1-9]\d*$/
    },
    lp);
    var np = {}
      , op = (np[5] = {
        version: "2",
        jn: ["2"],
        dk: "ad_storage",
        Hj: ["k", "i", "b"]
    },
    np);
    function pp(a, b) {
        var c = b.Ma;
        return "function" === typeof c ? c(a) : c.test(a)
    }
    function qp(a) {
        for (var b = na(Object.keys(a)), c = b.next(), d = {}; !c.done; d = {
            we: void 0
        },
        c = b.next()) {
            var e = c.value
              , f = a[e];
            d.we = mp[e];
            d.we ? d.we.Ph ? a[e] = Array.isArray(f) ? f.filter(function(g) {
                return function(h) {
                    return pp(h, g.we)
                }
            }(d)) : void 0 : "string" === typeof f && pp(f, d.we) || (a[e] = void 0) : a[e] = void 0
        }
        return a
    }
    function rp(a) {
        var b = {}
          , c = op[5];
        if (c) {
            for (var d = c.Hj, e = na(a.split("$")), f = e.next(); !f.done; f = e.next()) {
                var g = f.value
                  , h = g[0];
                if (-1 !== d.indexOf(h))
                    try {
                        var m = decodeURIComponent(g.substring(1))
                          , n = mp[h];
                        n && (n.Ph ? (b[h] = b[h] || [],
                        b[h].push(m)) : b[h] = m)
                    } catch (p) {}
            }
            return qp(b)
        }
    }
    function sp(a) {
        var b = op[5];
        if (b) {
            for (var c = [], d = na(b.Hj), e = d.next(); !e.done; e = d.next()) {
                var f = e.value
                  , g = mp[f];
                if (g) {
                    var h = a[f];
                    if (void 0 !== h)
                        if (g.Ph && Array.isArray(h))
                            for (var m = na(h), n = m.next(); !n.done; n = m.next())
                                c.push(encodeURIComponent("" + f + n.value));
                        else
                            c.push(encodeURIComponent("" + f + h))
                }
            }
            return c.join("$")
        }
    }
    ;function tp(a) {
        var b = op[5];
        if (b) {
            for (var c = [], d = ao(a, void 0, void 0, b.dk), e = na(d), f = e.next(); !f.done; f = e.next()) {
                var g = f.value.split(".")
                  , h = g.shift();
                if (-1 !== b.jn.indexOf(h)) {
                    g.shift();
                    var m = g.join(".");
                    c.push(rp(m))
                }
            }
            return c
        }
    }
    function up(a, b, c, d) {
        c = c || {};
        var e = sp(b);
        if (e) {
            var f = op[5]
              , g = [f.version, ro(c.domain, c.path), e].join(".");
            mo(a, g, wo(c, d, void 0, f.dk))
        }
    }
    ;var vp = /^\w+$/
      , wp = /^[\w-]+$/
      , xp = {}
      , yp = (xp.aw = "_aw",
    xp.dc = "_dc",
    xp.gf = "_gf",
    xp.gp = "_gp",
    xp.gs = "_gs",
    xp.ha = "_ha",
    xp.ag = "_ag",
    xp.gb = "_gb",
    xp);
    function zp() {
        return ["ad_storage", "ad_user_data"]
    }
    function Ap(a) {
        return !Bl().m() || Fl(a)
    }
    function Bp(a, b) {
        function c() {
            var d = Ap(b);
            d && a();
            return d
        }
        Ml(function() {
            c() || Nl(c, b)
        }, b)
    }
    function Cp(a) {
        return Dp(a).map(function(b) {
            return b.ba
        })
    }
    function Ep(a) {
        return Fp(a).filter(function(b) {
            return b.ba
        }).map(function(b) {
            return b.ba
        })
    }
    function Fp(a) {
        var b = Gp(a.prefix)
          , c = Hp("gb", b)
          , d = Hp("ag", b);
        if (!d || !c)
            return [];
        var e = function(h) {
            return function(m) {
                m.type = h;
                return m
            }
        }
          , f = Dp(c).map(e("gb"))
          , g = (Ti(6) ? Ip(d) : []).map(e("ag"));
        return f.concat(g).sort(function(h, m) {
            return m.timestamp - h.timestamp
        })
    }
    function Jp(a, b, c, d, e) {
        var f = sb(a, function(g) {
            return g.ba === c
        });
        f ? (f.timestamp = Math.max(f.timestamp, d),
        f.labels = Kp(f.labels || [], e || [])) : a.push({
            version: b,
            ba: c,
            timestamp: d,
            labels: e
        })
    }
    function Ip(a) {
        for (var b = tp(a) || [], c = [], d = na(b), e = d.next(); !e.done; e = d.next()) {
            var f = e.value
              , g = f
              , h = Lp(f);
            h && Jp(c, "2", g.k, h, g.b || [])
        }
        return c.sort(function(m, n) {
            return n.timestamp - m.timestamp
        })
    }
    function Dp(a) {
        for (var b = [], c = ao(a, H.cookie, void 0, zp()), d = na(c), e = d.next(); !e.done; e = d.next()) {
            var f = Mp(e.value);
            if (null != f) {
                var g = f;
                Jp(b, g.version, g.ba, g.timestamp, g.labels)
            }
        }
        b.sort(function(h, m) {
            return m.timestamp - h.timestamp
        });
        return Np(b)
    }
    function Kp(a, b) {
        if (!a.length)
            return b;
        if (!b.length)
            return a;
        var c = {};
        return a.concat(b).filter(function(d) {
            return c.hasOwnProperty(d) ? !1 : c[d] = !0
        })
    }
    function Gp(a) {
        return a && "string" === typeof a && a.match(vp) ? a : "_gcl"
    }
    function Op(a, b) {
        var c = Ti(6), d = Ti(7), e = hj(a), f = dj(e, "query", !1, void 0, "gclid"), g = dj(e, "query", !1, void 0, "gclsrc"), h = dj(e, "query", !1, void 0, "wbraid"), m;
        c && (m = dj(e, "query", !1, void 0, "gbraid"));
        var n;
        d && (n = dj(e, "query", !1, void 0, "gad_source"));
        var p = dj(e, "query", !1, void 0, "dclid");
        if (b && (!f || !g || !h || c && !m)) {
            var q = e.hash.replace("#", "");
            f = f || aj(q, "gclid", !1);
            g = g || aj(q, "gclsrc", !1);
            h = h || aj(q, "wbraid", !1);
            c && (m = m || aj(q, "gbraid", !1));
            d && (n = n || aj(q, "gad_source", !1))
        }
        return Pp(f, g, p, h, m, n)
    }
    function Qp() {
        return Op(G.location.href, !0)
    }
    function Pp(a, b, c, d, e, f) {
        var g = {}
          , h = function(m, n) {
            g[n] || (g[n] = []);
            g[n].push(m)
        };
        g.gclid = a;
        g.gclsrc = b;
        g.dclid = c;
        if (void 0 !== a && a.match(wp))
            switch (b) {
            case void 0:
                h(a, "aw");
                break;
            case "aw.ds":
                h(a, "aw");
                h(a, "dc");
                break;
            case "ds":
                h(a, "dc");
                break;
            case "3p.ds":
                h(a, "dc");
                break;
            case "gf":
                h(a, "gf");
                break;
            case "ha":
                h(a, "ha")
            }
        c && h(c, "dc");
        void 0 !== d && wp.test(d) && (g.wbraid = d,
        h(d, "gb"));
        Ti(6) && void 0 !== e && wp.test(e) && (g.gbraid = e,
        h(e, "ag"));
        Ti(7) && void 0 !== f && wp.test(f) && (g.gad_source = f,
        h(f, "gs"));
        return g
    }
    function Rp(a) {
        var b = Qp();
        if (Ti(5)) {
            for (var c = !0, d = na(Object.keys(b)), e = d.next(); !e.done; e = d.next())
                if (void 0 !== b[e.value]) {
                    c = !1;
                    break
                }
            c && (b = Op(G.document.referrer, !1))
        }
        Sp(b, !1, a)
    }
    function Sp(a, b, c, d, e) {
        c = c || {};
        e = e || [];
        var f = Gp(c.prefix)
          , g = d || Cb()
          , h = Math.round(g / 1E3)
          , m = zp()
          , n = !1
          , p = !1
          , q = function() {
            if (Ap(m)) {
                var r = wo(c, g, !0);
                r.zb = m;
                for (var t = function(F, L) {
                    var N = Hp(F, f);
                    N && (mo(N, L, r),
                    "gb" !== F && (n = !0))
                }, u = function(F) {
                    var L = ["GCL", h, F];
                    0 < e.length && L.push(e.join("."));
                    return L.join(".")
                }, v = na(["aw", "dc", "gf", "ha", "gp"]), w = v.next(); !w.done; w = v.next()) {
                    var y = w.value;
                    a[y] && t(y, u(a[y][0]))
                }
                if (!n && a.gb) {
                    var x = a.gb[0]
                      , B = Hp("gb", f);
                    !b && Dp(B).some(function(F) {
                        return F.ba === x && F.labels && 0 < F.labels.length
                    }) || t("gb", u(x))
                }
            }
            if (!p && Ti(6) && a.gbraid && Ap("ad_storage") && (p = !0,
            !n)) {
                var A = a.gbraid
                  , D = Hp("ag", f);
                if (b || !(Ti(6) ? Ip(D) : []).some(function(F) {
                    return F.ba === A && F.labels && 0 < F.labels.length
                })) {
                    var E = {}
                      , C = (E.k = A,
                    E.i = "" + h,
                    E.b = e,
                    E);
                    up(D, C, c, g)
                }
            }
            Tp(a, f, g, c)
        };
        Ml(function() {
            q();
            Ap(m) || Nl(q, m)
        }, m)
    }
    function Tp(a, b, c, d) {
        if (Ti(7) && void 0 !== a.gad_source && Ap("ad_storage")) {
            var e = Hp("gs", b);
            if (e) {
                var f = Math.round((Cb() - (Lc() || 0)) / 1E3)
                  , g = {}
                  , h = (g.k = a.gad_source,
                g.i = "" + f,
                g);
                up(e, h, d, c)
            }
        }
    }
    function Up(a, b) {
        var c = Mo(!0);
        Bp(function() {
            for (var d = Gp(b.prefix), e = 0; e < a.length; ++e) {
                var f = a[e];
                if (void 0 !== yp[f]) {
                    var g = Hp(f, d)
                      , h = c[g];
                    if (h) {
                        var m = Math.min(Vp(h), Cb()), n;
                        b: {
                            for (var p = m, q = ao(g, H.cookie, void 0, zp()), r = 0; r < q.length; ++r)
                                if (Vp(q[r]) > p) {
                                    n = !0;
                                    break b
                                }
                            n = !1
                        }
                        if (!n) {
                            var t = wo(b, m, !0);
                            t.zb = zp();
                            mo(g, h, t)
                        }
                    }
                }
            }
            Sp(Pp(c.gclid, c.gclsrc), !1, b)
        }, zp())
    }
    function Wp(a) {
        var b = [];
        Ti(6) && b.push("ag");
        if (0 !== b.length) {
            var c = Mo(!0)
              , d = Gp(a.prefix);
            Bp(function() {
                for (var e = 0; e < b.length; ++e) {
                    var f = Hp(b[e], d);
                    if (f) {
                        var g = c[f];
                        if (g) {
                            var h = rp(g);
                            if (h) {
                                var m = Lp(h);
                                m || (m = Cb());
                                var n;
                                a: {
                                    for (var p = m, q = tp(f), r = 0; r < q.length; ++r)
                                        if (Lp(q[r]) > p) {
                                            n = !0;
                                            break a
                                        }
                                    n = !1
                                }
                                if (n)
                                    break;
                                h.i = "" + Math.round(m / 1E3);
                                up(f, h, a, m)
                            }
                        }
                    }
                }
            }, ["ad_storage"])
        }
    }
    function Hp(a, b) {
        var c = yp[a];
        if (void 0 !== c)
            return b + c
    }
    function Vp(a) {
        return 0 !== Xp(a.split(".")).length ? 1E3 * (Number(a.split(".")[1]) || 0) : 0
    }
    function Lp(a) {
        return a ? 1E3 * (Number(a.i) || 0) : 0
    }
    function Mp(a) {
        var b = Xp(a.split("."));
        return 0 === b.length ? null : {
            version: b[0],
            ba: b[2],
            timestamp: 1E3 * (Number(b[1]) || 0),
            labels: b.slice(3)
        }
    }
    function Xp(a) {
        return 3 > a.length || "GCL" !== a[0] && "1" !== a[0] || !/^\d+$/.test(a[1]) || !wp.test(a[2]) ? [] : a
    }
    function Yp(a, b, c, d, e) {
        if (Array.isArray(b) && $n(G)) {
            var f = Gp(e)
              , g = function() {
                for (var h = {}, m = 0; m < a.length; ++m) {
                    var n = Hp(a[m], f);
                    if (n) {
                        var p = ao(n, H.cookie, void 0, zp());
                        p.length && (h[n] = p.sort()[p.length - 1])
                    }
                }
                return h
            };
            Bp(function() {
                To(g, b, c, d)
            }, zp())
        }
    }
    function Zp(a, b, c, d) {
        if (Array.isArray(a) && $n(G)) {
            var e = [];
            Ti(6) && e.push("ag");
            if (0 !== e.length) {
                var f = Gp(d)
                  , g = function() {
                    for (var h = {}, m = 0; m < e.length; ++m) {
                        var n = Hp(e[m], f);
                        if (!n)
                            return {};
                        var p = tp(n);
                        if (p.length) {
                            var q = p.sort(function(r, t) {
                                return Lp(t) - Lp(r)
                            })[0];
                            h[n] = sp(q)
                        }
                    }
                    return h
                };
                Bp(function() {
                    To(g, a, b, c)
                }, ["ad_storage"])
            }
        }
    }
    function Np(a) {
        return a.filter(function(b) {
            return wp.test(b.ba)
        })
    }
    function $p(a, b) {
        if ($n(G)) {
            for (var c = Gp(b.prefix), d = {}, e = 0; e < a.length; e++)
                yp[a[e]] && (d[a[e]] = yp[a[e]]);
            Bp(function() {
                z(d, function(f, g) {
                    var h = ao(c + g, H.cookie, void 0, zp());
                    h.sort(function(t, u) {
                        return Vp(u) - Vp(t)
                    });
                    if (h.length) {
                        var m = h[0], n = Vp(m), p = 0 !== Xp(m.split(".")).length ? m.split(".").slice(3) : [], q = {}, r;
                        r = 0 !== Xp(m.split(".")).length ? m.split(".")[2] : void 0;
                        q[f] = [r];
                        Sp(q, !0, b, n, p)
                    }
                })
            }, zp())
        }
    }
    function aq(a) {
        var b = []
          , c = [];
        Ti(6) && (b.push("ag"),
        c.push("gbraid"));
        0 !== b.length && Bp(function() {
            for (var d = Gp(a.prefix), e = 0; e < b.length; ++e) {
                var f = Hp(b[e], d);
                if (!f)
                    break;
                var g = tp(f);
                if (g.length) {
                    var h = g.sort(function(q, r) {
                        return Lp(r) - Lp(q)
                    })[0]
                      , m = Lp(h)
                      , n = h.b
                      , p = {};
                    p[c[e]] = h.k;
                    Sp(p, !0, a, m, n)
                }
            }
        }, ["ad_storage"])
    }
    function bq(a, b) {
        for (var c = 0; c < b.length; ++c)
            if (a[b[c]])
                return !0;
        return !1
    }
    function cq(a) {
        function b(e, f, g) {
            g && (e[f] = g)
        }
        if (Jl()) {
            var c = Qp();
            if (bq(c, a)) {
                var d = {};
                b(d, "gclid", c.gclid);
                b(d, "dclid", c.dclid);
                b(d, "gclsrc", c.gclsrc);
                b(d, "wbraid", c.wbraid);
                Ti(6) && b(d, "gbraid", c.gbraid);
                Uo(function() {
                    return d
                }, 3);
                Uo(function() {
                    var e = {};
                    return e._up = "1",
                    e
                }, 1)
            }
        }
    }
    function dq(a) {
        if (!Ti(1))
            return null;
        var b = Mo(!0).gad_source;
        if (null != b)
            return G.location.hash = "",
            b;
        if (Ti(2)) {
            var c = hj(G.location.href);
            b = dj(c, "query", !1, void 0, "gad_source");
            if (null != b)
                return b;
            var d = Qp();
            if (bq(d, a))
                return "0"
        }
        return null
    }
    function eq(a) {
        var b = dq(a);
        null != b && Uo(function() {
            var c = {};
            return c.gad_source = b,
            c
        }, 4)
    }
    function fq(a, b, c) {
        var d = [];
        if (0 === b.length)
            return d;
        for (var e = {}, f = 0; f < b.length; f++) {
            var g = b[f]
              , h = g.type ? g.type : "gcl";
            -1 === (g.labels || []).indexOf(c) ? (a.push(0),
            e[h] || d.push(g)) : a.push(1);
            e[h] = !0
        }
        return d
    }
    function gq(a, b, c, d) {
        var e = [];
        c = c || {};
        if (!Ap(zp()))
            return e;
        var f = Dp(a)
          , g = fq(e, f, b);
        if (g.length && !d)
            for (var h = na(g), m = h.next(); !m.done; m = h.next()) {
                var n = m.value
                  , p = n.timestamp
                  , q = [n.version, Math.round(p / 1E3), n.ba].concat(n.labels || [], [b]).join(".")
                  , r = wo(c, p, !0);
                r.zb = zp();
                mo(a, q, r)
            }
        return e
    }
    function hq(a, b) {
        var c = [];
        b = b || {};
        var d = Fp(b)
          , e = fq(c, d, a);
        if (e.length)
            for (var f = na(e), g = f.next(); !g.done; g = f.next()) {
                var h = g.value
                  , m = Gp(b.prefix)
                  , n = Hp(h.type, m);
                if (!n)
                    break;
                var p = h
                  , q = p.version
                  , r = p.ba
                  , t = p.labels
                  , u = p.timestamp
                  , v = Math.round(u / 1E3);
                if ("ag" === h.type) {
                    var w = {}
                      , y = (w.k = r,
                    w.i = "" + v,
                    w.b = (t || []).concat([a]),
                    w);
                    up(n, y, b, u)
                } else if ("gb" === h.type) {
                    var x = [q, v, r].concat(t || [], [a]).join(".")
                      , B = wo(b, u, !0);
                    B.zb = zp();
                    mo(n, x, B)
                }
            }
        return c
    }
    function iq(a, b) {
        var c = Gp(b)
          , d = Hp(a, c);
        if (!d)
            return 0;
        var e;
        e = "ag" === a ? Ti(6) ? Ip(d) : [] : Dp(d);
        for (var f = 0, g = 0; g < e.length; g++)
            f = Math.max(f, e[g].timestamp);
        return f
    }
    function jq(a) {
        for (var b = 0, c = na(Object.keys(a)), d = c.next(); !d.done; d = c.next())
            for (var e = a[d.value], f = 0; f < e.length; f++)
                b = Math.max(b, Number(e[f].timestamp));
        return b
    }
    function kq(a, b) {
        var c = Math.max(iq("aw", a), jq(Ap(zp()) ? kp() : {}))
          , d = Math.max(iq("gb", a), jq(Ap(zp()) ? kp("_gac_gb", !0) : {}));
        Ti(6) && b && (d = Math.max(d, iq("ag", a)));
        return d > c
    }
    ;var lq = function(a, b, c) {
        var d = ii.joined_auid = ii.joined_auid || {}
          , e = (c ? a || "_gcl" : "") + "." + b;
        if (d[e])
            return !0;
        d[e] = !0;
        return !1
    }
      , mq = function() {
        var a = hj(G.location.href)
          , b = dj(a, "query", !1, void 0, "gad_source");
        if (void 0 === b) {
            var c = a.hash.replace("#", "");
            b = aj(c, "gad_source", !1)
        }
        return b
    }
      , nq = function() {
        var a = hj(G.location.href).search.replace("?", "");
        return "1" === aj(a, "gad", !1, !0)
    }
      , oq = function() {
        var a = 1 === cl(!0) ? G.top.location.href : G.location.href;
        return a = a.replace(/[\?#].*$/, "")
    }
      , pq = function(a) {
        var b = [];
        z(a, function(c, d) {
            d = Np(d);
            for (var e = [], f = 0; f < d.length; f++)
                e.push(d[f].ba);
            e.length && b.push(c + ":" + e.join(","))
        });
        return b.join(";")
    }
      , rq = function(a, b, c) {
        if ("aw" === a || "dc" === a || "gb" === a) {
            var d = jj("gcl" + a);
            if (d)
                return d.split(".")
        }
        var e = Gp(b);
        if ("_gcl" === e) {
            var f = !W(qq()) && c, g;
            g = Qp()[a] || [];
            if (0 < g.length)
                return f ? ["0"] : g
        }
        var h = Hp(a, e);
        return h ? Cp(h) : []
    }
      , sq = function(a) {
        var b = qq();
        Xl(function() {
            a();
            W(b) || Nl(a, b)
        }, b)
    }
      , qq = function() {
        return [P.g.R, P.g.P]
    }
      , tq = /^(www\.)?google(\.com?)?(\.[a-z]{2}t?)?$/
      , uq = /^www.googleadservices.com$/
      , vq = function(a, b) {
        return rq("aw", a, b)
    }
      , wq = function(a, b) {
        return rq("dc", a, b)
    }
      , xq = function(a, b, c, d, e) {
        var f = Qp()
          , g = []
          , h = f.gclid
          , m = f.dclid
          , n = f.gclsrc || "aw"
          , p = nq()
          , q = mq();
        !h || "aw.ds" !== n && "aw" !== n && "ds" !== n && "3p.ds" !== n || g.push({
            ba: h,
            Be: n
        });
        m && g.push({
            ba: m,
            Be: "ds"
        });
        0 === g.length && f.wbraid && g.push({
            ba: f.wbraid,
            Be: "gb"
        });
        0 === g.length && "aw.ds" === n && g.push({
            ba: "",
            Be: "aw.ds"
        });
        sq(function() {
            if (T(74) || W(P.g.R)) {
                var r = W(qq());
                $o(a);
                var t = []
                  , u = r ? Yo[ap(a.prefix)] : void 0;
                u && t.push("auid=" + u);
                if (T(70) && W(P.g.P)) {
                    e && t.push("userId=" + e);
                    var v = Zn(Vn.Sg);
                    if (void 0 === v)
                        Yn(Vn.Tg, !0);
                    else {
                        var w = Zn(Vn.Ug);
                        t.push("ga_uid=" + w + "." + v)
                    }
                }
                var y = H.referrer ? dj(hj(H.referrer), "host") : ""
                  , x = r || !d ? g : [];
                0 === x.length && (tq.test(y) || uq.test(y)) && x.push({
                    ba: "",
                    Be: ""
                });
                if (0 !== x.length || p || void 0 !== q) {
                    y && t.push("ref=" + encodeURIComponent(y));
                    var B = oq();
                    t.push("url=" + encodeURIComponent(B));
                    t.push("tft=" + Cb());
                    var A = Lc();
                    void 0 !== A && t.push("tfd=" + Math.round(A));
                    var D = cl(!0);
                    t.push("frm=" + D);
                    p && t.push("gad=1");
                    void 0 !== q && t.push("gad_source=" + encodeURIComponent(q));
                    var E = c;
                    void 0 === E && (E = Km.H[P.g.oa]);
                    var C = {}
                      , F = Gm(wm(new vm(0), (C[P.g.oa] = E,
                    C)));
                    t.push("gtm=" + Un({
                        za: b
                    }));
                    zn() && t.push("gcs=" + An());
                    t.push("gcd=" + En(F));
                    Qn() && t.push("dma_cps=" + Fn());
                    t.push("dma=" + Pn());
                    yn(F) ? t.push("npa=0") : t.push("npa=1");
                    cn(ln()) && t.push("tcfd=" + Rn());
                    var L = sn();
                    L && t.push("gdpr=" + L);
                    var N = qn();
                    N && t.push("gdpr_consent=" + N);
                    T(13) && t.push("apve=" + (T(14) ? 1 : 0));
                    Ai.m && t.push("tag_exp=" + Ai.m);
                    var Q = r ? 'https://adservice.google.com/pagead/regclk' : "https://adservice.googlesyndication.com/pagead/regclk";
                    if (0 < x.length)
                        for (var V = 0; V < x.length; V++) {
                            var ca = x[V]
                              , Z = ca.ba
                              , R = ca.Be;
                            if (!lq(a.prefix, R + "." + Z, void 0 !== u)) {
                                var oa = Q + "?" + t.join("&");
                                "" !== Z ? oa = "gb" === R ? oa + "&wbraid=" + Z : oa + "&gclid=" + Z + "&gclsrc=" + R : "aw.ds" === R && (oa += "&gclsrc=aw.ds");
                                Gc(oa)
                            }
                        }
                    else if ((p || void 0 !== q) && !lq(a.prefix, "gad", void 0 !== u)) {
                        var ka = Q + "?" + t.join("&");
                        Gc(ka)
                    }
                }
            }
        })
    };
    var yq, zq = !1;
    function Aq() {
        zq = !0;
        yq = yq || {}
    }
    function Bq(a) {
        zq || Aq();
        return yq[a]
    }
    var Cq = function(a, b, c) {
        this.eventName = b;
        this.o = c;
        this.D = {};
        this.isAborted = !1;
        this.target = a;
        this.metadata = k(c.eventMetadata || {}, {})
    };
    Cq.prototype.copyToHitData = function(a, b, c) {
        var d = U(this.o, a);
        void 0 === d && (d = b);
        if (void 0 !== d && void 0 !== c && l(d) && T(46))
            try {
                d = c(d)
            } catch (e) {}
        void 0 !== d && (this.D[a] = d)
    }
    ;
    var Dq = function(a, b, c) {
        var d = Bq(a.target.ka);
        return d && void 0 !== d[b] ? d[b] : c
    };
    function Eq() {
        ii.dedupe_gclid || (ii.dedupe_gclid = to());
        return ii.dedupe_gclid
    }
    ;var Fq = /^(www\.)?google(\.com?)?(\.[a-z]{2}t?)?$/
      , Gq = /^www.googleadservices.com$/;
    function Hq(a) {
        a || (a = Iq());
        return a.gn ? !1 : a.Sl || a.Tl || a.Vl || a.Ul || a.th || a.nh || a.Gl || a.Kl ? !0 : !1
    }
    function Iq() {
        var a = {}
          , b = Mo(!0);
        a.gn = !!b._up;
        var c = Qp();
        a.Sl = void 0 !== c.aw;
        a.Tl = void 0 !== c.dc;
        a.Vl = void 0 !== c.wbraid;
        a.Ul = void 0 !== c.gbraid;
        var d = hj(G.location.href)
          , e = dj(d, "query", !1, void 0, "gad");
        a.th = void 0 !== e;
        if (!a.th) {
            var f = d.hash.replace("#", "")
              , g = aj(f, "gad", !1);
            a.th = void 0 !== g
        }
        a.nh = dj(d, "query", !1, void 0, "gad_source");
        if (void 0 === a.nh) {
            var h = d.hash.replace("#", "")
              , m = aj(h, "gad_source", !1);
            a.nh = m
        }
        var n = H.referrer ? dj(hj(H.referrer), "host") : "";
        a.Kl = Fq.test(n);
        a.Gl = Gq.test(n);
        return a
    }
    ;var Jq = RegExp("^UA-\\d+-\\d+%3A[\\w-]+(?:%2C[\\w-]+)*(?:%3BUA-\\d+-\\d+%3A[\\w-]+(?:%2C[\\w-]+)*)*$")
      , Kq = /^~?[\w-]+(?:\.~?[\w-]+)*$/
      , Lq = /^\d+\.fls\.doubleclick\.net$/
      , Mq = /;gac=([^;?]+)/
      , Nq = /;gacgb=([^;?]+)/;
    function Oq(a, b) {
        if (Lq.test(H.location.host)) {
            var c = H.location.href.match(b);
            return c && 2 === c.length && c[1].match(Jq) ? decodeURIComponent(c[1]) : ""
        }
        for (var d = [], e = na(Object.keys(a)), f = e.next(); !f.done; f = e.next()) {
            for (var g = f.value, h = [], m = a[g], n = 0; n < m.length; n++)
                h.push(m[n].ba);
            d.push(g + ":" + h.join(","))
        }
        return 0 < d.length ? d.join(";") : ""
    }
    function Pq(a, b, c) {
        for (var d = Ap(zp()) ? kp("_gac_gb", !0) : {}, e = [], f = !1, g = na(Object.keys(d)), h = g.next(); !h.done; h = g.next()) {
            var m = h.value
              , n = gq("_gac_gb_" + m, a, b, c);
            f = f || 0 !== n.length && n.some(function(p) {
                return 1 === p
            });
            e.push(m + ":" + n.join(","))
        }
        return {
            Fl: f ? e.join(";") : "",
            El: Oq(d, Nq)
        }
    }
    function Qq(a) {
        var b = H.location.href.match(new RegExp(";" + a + "=([^;?]+)"));
        return b && 2 === b.length && b[1].match(Kq) ? b[1] : void 0
    }
    function Rq(a) {
        var b = {
            oh: void 0,
            qh: void 0
        }, c, d;
        Lq.test(H.location.host) && (c = Qq("gclgs"),
        d = Qq("gclst"));
        if (c && d)
            b.oh = c,
            b.qh = d;
        else {
            var e = Cb()
              , f = Ip((a || "_gcl") + "_gs")
              , g = f.map(function(m) {
                return m.ba
            })
              , h = f.map(function(m) {
                return e - m.timestamp
            });
            0 < g.length && 0 < h.length && (b.oh = g.join("."),
            b.qh = h.join("."))
        }
        return b
    }
    function Sq(a, b, c) {
        if (Lq.test(H.location.host)) {
            var d = Qq(c);
            if (d)
                return [{
                    ba: d
                }]
        } else {
            if ("gclid" === b)
                return Dp((a || "_gcl") + "_aw");
            if ("wbraid" === b)
                return Dp((a || "_gcl") + "_gb");
            if ("braids" === b)
                return Fp({
                    prefix: a
                })
        }
        return []
    }
    function Tq(a) {
        return Sq(a, "gclid", "gclaw").map(function(b) {
            return b.ba
        }).join(".")
    }
    function Uq(a) {
        return Sq(a, "wbraid", "gclgb").map(function(b) {
            return b.ba
        }).join(".")
    }
    function Vq(a) {
        return Sq(a, "braids", "gclgb").map(function(b) {
            return b.ba
        }).join(".")
    }
    function Wq(a, b) {
        return Lq.test(H.location.host) ? !(Qq("gclaw") || Qq("gac")) : kq(a, b)
    }
    function Xq(a, b) {
        var c;
        c = T(51) ? hq(a, b) : gq((b && b.prefix || "_gcl") + "_gb", a, b);
        return 0 === c.length || c.every(function(d) {
            return 0 === d
        }) ? "" : c.join(".")
    }
    ;var Yq = function() {
        if (pb(G.__uspapi)) {
            var a = "";
            try {
                G.__uspapi("getUSPData", 1, function(b, c) {
                    if (c && b) {
                        var d = b.uspString;
                        d && RegExp("^[\\da-zA-Z-]{1,20}$").test(d) && (a = d)
                    }
                })
            } catch (b) {}
            return a
        }
    };
    var ar = function(a) {
        if (a.eventName === P.g.fa && "page_view" === a.metadata.hit_type)
            if (T(14)) {
                a.metadata.redact_click_ids = null != U(a.o, P.g.ja) && !1 !== U(a.o, P.g.ja) && !W([P.g.R, P.g.P]);
                var b = Zq(a)
                  , c = !1 !== U(a.o, P.g.wa);
                c || (a.D[P.g.Ei] = "1");
                var d = Gp(b.prefix);
                if (!a.metadata.consent_updated) {
                    var e = U(a.o, P.g.Va)
                      , f = U(a.o, P.g.xa) || {};
                    $q({
                        vd: c,
                        zd: f,
                        Fd: e,
                        fc: b
                    });
                    var g;
                    var h = ii.ads_pageview = ii.ads_pageview || {};
                    g = h[d] ? !1 : h[d] = !0;
                    if (!g) {
                        a.isAborted = !0;
                        return
                    }
                }
                a.D[P.g.fd] = P.g.Qb;
                if (a.metadata.consent_updated)
                    a.D[P.g.fd] = P.g.uk,
                    a.D[P.g.mc] = "1";
                else {
                    var m = Qp();
                    a.D[P.g.Id] = m.gclid;
                    a.D[P.g.Pd] = m.dclid;
                    a.D[P.g.zi] = m.gclsrc;
                    a.D[P.g.Id] || a.D[P.g.Pd] || (a.D[P.g.Ve] = m.wbraid,
                    a.D[P.g.dg] = m.gbraid);
                    a.D[P.g.Fa] = H.referrer ? dj(hj(H.referrer), "host") : "";
                    a.D[P.g.ya] = oq();
                    a.D[P.g.yi] = mq();
                    a.D[P.g.Fb] = cl(!0);
                    var n = Iq();
                    Hq(n) && (a.D[P.g.hd] = "1");
                    a.D[P.g.Bi] = Eq();
                    "1" === Mo(!1)._up && (a.D[P.g.Ri] = "1")
                }
                var p = W([P.g.R, P.g.P]);
                c && p && ($o(b),
                a.D[P.g.Cb] = Yo[ap(b.prefix)]);
                a.D[P.g.jb] = void 0;
                a.D[P.g.Sa] = void 0;
                var q = T(51);
                if (!a.D[P.g.Id] && !a.D[P.g.Pd] && Wq(d, q)) {
                    var r = q ? Ep(b) : Cp(d + "_gb");
                    0 < r.length && (a.D[P.g.jb] = r.join("."))
                } else if (!a.D[P.g.Ve] && p) {
                    var t = Cp(d + "_aw");
                    0 < t.length && (a.D[P.g.Sa] = t.join("."))
                }
                a.o.isGtmEvent && (a.o.m[P.g.oa] = Km.H[P.g.oa]);
                yn(a.o) ? a.D[P.g.Mb] = !1 : a.D[P.g.Mb] = !0;
                a.metadata.add_tag_timing = !0;
                var u = Yq();
                void 0 !== u && (a.D[P.g.he] = u || "error");
                var v = sn();
                v && (a.D[P.g.Ac] = v);
                var w = qn();
                w && (a.D[P.g.Cc] = w);
                a.metadata.speculative = !1
            } else
                a.isAborted = !0
    }
      , Zq = function(a) {
        var b = {
            prefix: U(a.o, P.g.Za) || U(a.o, P.g.Oa),
            domain: U(a.o, P.g.Ta),
            yb: U(a.o, P.g.Ua),
            flags: U(a.o, P.g.ab)
        };
        a.o.isGtmEvent && (b.path = U(a.o, P.g.Db));
        return b
    }
      , br = function(a, b) {
        var c = a.vd
          , d = a.za
          , e = a.allowAdPersonalizationSignals
          , f = a.Bd
          , g = a.Pn
          , h = a.kk;
        $q({
            vd: c,
            zd: a.zd,
            Fd: a.Fd,
            fc: b
        });
        c && !0 !== g && (null != h ? h = String(h) : h = void 0,
        xq(b, d, e, f, h))
    }
      , $q = function(a) {
        var b = a.zd
          , c = a.Fd
          , d = a.fc;
        a.vd && (Wo(b[P.g.Bc], !!b[P.g.Z]) && (Up(cr, d),
        Wp(d),
        hp(d)),
        Rp(d),
        $p(cr, d),
        aq(d));
        b[P.g.Z] && (Yp(cr, b[P.g.Z], b[P.g.Hb], !!b[P.g.sb], d.prefix),
        Zp(b[P.g.Z], b[P.g.Hb], !!b[P.g.sb], d.prefix),
        ip(ap(d.prefix), b[P.g.Z], b[P.g.Hb], !!b[P.g.sb], d),
        ip("FPAU", b[P.g.Z], b[P.g.Hb], !!b[P.g.sb], d));
        c && cq(dr);
        eq(dr)
    }
      , er = function(a, b, c, d) {
        var e = a.lk
          , f = a.callback
          , g = a.Rj;
        if ("function" === typeof f)
            if (e === P.g.Sa && void 0 === g) {
                var h = d(b.prefix, c);
                0 === h.length ? f(void 0) : 1 === h.length ? f(h[0]) : f(h)
            } else
                e === P.g.Cb ? (O(65),
                $o(b, !1),
                f(Yo[ap(b.prefix)])) : f(g)
    }
      , cr = ["aw", "dc", "gb"]
      , dr = ["aw", "dc", "gb", "ag"];
    function fr(a) {
        var b = U(a.o, P.g.Gb)
          , c = U(a.o, P.g.Ub);
        b && !c ? (a.eventName !== P.g.fa && a.eventName !== P.g.uc && O(131),
        a.isAborted = !0) : !b && c && (O(132),
        a.isAborted = !0)
    }
    function gr(a) {
        var b = W(P.g.R) ? ii.pscdl : "denied";
        null != b && (a.D[P.g.Ze] = b)
    }
    function hr(a) {
        if (T(66)) {
            var b = cl(!0);
            a.D[P.g.Fb] = b
        }
    }
    ;var ir = function(a) {
        if (a)
            switch (a._tag_mode) {
            case "CODE":
                return "c";
            case "AUTO":
                return "a";
            case "MANUAL":
                return "m";
            default:
                return "c"
            }
    }
      , jr = function(a) {
        var b = a && a[P.g.kg];
        return b && b[P.g.Ai]
    }
      , kr = function(a) {
        if (a && a.length) {
            for (var b = [], c = 0; c < a.length; ++c) {
                var d = a[c];
                d && d.estimated_delivery_date ? b.push("" + d.estimated_delivery_date) : b.push("")
            }
            return b.join(",")
        }
    };
    var lr = function(a, b) {
        var c = a && !W([P.g.R, P.g.P]);
        return b && c ? "0" : b
    }
      , nr = function(a) {
        Xl(function() {
            function b(w) {
                var y = W([P.g.R, P.g.P]), x = h && y, B = g.prefix || "_gcl", A;
                ii.reported_gclid || (ii.reported_gclid = {});
                A = ii.reported_gclid;
                var D = (x ? B : "") + "." + (W(P.g.R) ? 1 : 0) + "." + (W(P.g.P) ? 1 : 0);
                if (!A[D]) {
                    A[D] = !0;
                    var E = {}
                      , C = function(ca, Z) {
                        if (Z || "number" === typeof Z)
                            E[ca] = Z.toString()
                    }
                      , F = "https://www.google.com";
                    zn() && (C("gcs", An()),
                    w && C("gcu", 1));
                    C("gcd", En(f));
                    Ai.m && C("tag_exp", Ai.m);
                    if (Jl()) {
                        C("rnd", Eq());
                        if ((!n || p && "aw.ds" !== p) && y) {
                            var L = Cp(B + "_aw");
                            C("gclaw", L.join("."))
                        }
                        C("url", String(G.location).split(/[?#]/)[0]);
                        C("dclid", lr(d, q));
                        y || (F = "https://pagead2.googlesyndication.com")
                    }
                    Qn() && C("dma_cps", Fn());
                    C("dma", Pn());
                    C("npa", yn(f) ? 0 : 1);
                    cn(ln()) && C("tcfd", Rn());
                    C("gdpr_consent", qn() || "");
                    C("gdpr", sn() || "");
                    "1" === Mo(!1)._up && C("gtm_up", 1);
                    C("gclid", lr(d, n));
                    C("gclsrc", p);
                    if (!(E.hasOwnProperty("gclid") || E.hasOwnProperty("dclid") || E.hasOwnProperty("gclaw")) && (C("gbraid", lr(d, r)),
                    !E.hasOwnProperty("gbraid") && Jl() && y)) {
                        var N = Cp(B + "_gb");
                        0 < N.length && C("gclgb", N.join("."))
                    }
                    C("gtm", Un({
                        za: f.eventMetadata.source_canonical_id,
                        Hf: !e
                    }));
                    h && W(P.g.R) && ($o(g || {}),
                    x && C("auid", Yo[ap(g.prefix)] || ""));
                    mr || a.Jj && C("did", a.Jj);
                    a.rh && C("gdid", a.rh);
                    a.jh && C("edid", a.jh);
                    void 0 !== a.uh && C("frm", a.uh);
                    T(13) && C("apve", T(14) ? 1 : 0);
                    var Q = Object.keys(E).map(function(ca) {
                        return ca + "=" + encodeURIComponent(E[ca])
                    })
                      , V = F + "/pagead/landing?" + Q.join("&");
                    Gc(V)
                }
            }
            var c = !!a.bh
              , d = !!a.Bd
              , e = a.targetId
              , f = a.o
              , g = void 0 === a.fc ? {} : a.fc
              , h = void 0 === a.Lf ? !0 : a.Lf
              , m = Qp()
              , n = m.gclid || ""
              , p = m.gclsrc
              , q = m.dclid || ""
              , r = m.wbraid || ""
              , t = !c && ((!n || p && "aw.ds" !== p ? !1 : !0) || r)
              , u = Jl();
            if (t || u)
                if (u) {
                    var v = [P.g.R, P.g.P, P.g.Aa];
                    b();
                    (function() {
                        W(v) || Wl(function(w) {
                            return b(!0, w.consentEventId, w.consentPriorityId)
                        }, v)
                    }
                    )()
                } else
                    b()
        }, [P.g.R, P.g.P, P.g.Aa])
    }
      , mr = !1;
    function or(a, b, c, d) {
        var e = xc(), f;
        if (1 === e)
            a: {
                var g = ti;
                g = g.toLowerCase();
                for (var h = "https://" + g, m = "http://" + g, n = 1, p = H.getElementsByTagName("script"), q = 0; q < p.length && 100 > q; q++) {
                    var r = p[q].src;
                    if (r) {
                        r = r.toLowerCase();
                        if (0 === r.indexOf(m)) {
                            f = 3;
                            break a
                        }
                        1 === n && 0 === r.indexOf(h) && (n = 2)
                    }
                }
                f = n
            }
        else
            f = e;
        return (2 === f || d || "http:" != G.location.protocol ? a : b) + c
    }
    ;var pr = function(a, b) {
        T(5) && (a.dma = Pn(),
        Qn() && (a.dmaCps = Fn()),
        yn(b) ? a.npa = "0" : a.npa = "1")
    }
      , rr = function(a, b, c) {
        if (G[a.functionName])
            return b.Gh && I(b.Gh),
            G[a.functionName];
        var d = qr();
        G[a.functionName] = d;
        if (a.Gf)
            for (var e = 0; e < a.Gf.length; e++)
                G[a.Gf[e]] = G[a.Gf[e]] || qr();
        a.Kf && void 0 === G[a.Kf] && (G[a.Kf] = c);
        wc(or("https://", "http://", a.Rh), b.Gh, b.wm);
        return d
    }
      , qr = function() {
        var a = function() {
            a.q = a.q || [];
            a.q.push(arguments)
        };
        return a
    }
      , sr = {
        functionName: "_googWcmImpl",
        Kf: "_googWcmAk",
        Rh: "www.gstatic.com/wcm/loader.js"
    }
      , tr = {
        functionName: "_gaPhoneImpl",
        Kf: "ga_wpid",
        Rh: "www.gstatic.com/gaphone/loader.js"
    }
      , ur = {
        qk: "9",
        Xk: "5"
    }
      , vr = {
        functionName: "_googCallTrackingImpl",
        Gf: [tr.functionName, sr.functionName],
        Rh: "www.gstatic.com/call-tracking/call-tracking_" + (ur.qk || ur.Xk) + ".js"
    }
      , wr = {}
      , xr = function(a, b, c, d, e) {
        O(22);
        if (c) {
            e = e || {};
            var f = rr(sr, e, a)
              , g = {
                ak: a,
                cl: b
            };
            void 0 === e.Nb && (g.autoreplace = c);
            pr(g, d);
            f(2, e.Nb, g, c, 0, Bb(), e.options)
        }
    }
      , yr = function(a, b, c, d, e) {
        O(21);
        if (b && c) {
            e = e || {};
            for (var f = {
                countryNameCode: c,
                destinationNumber: b,
                retrievalTime: Bb()
            }, g = 0; g < a.length; g++) {
                var h = a[g];
                wr[h.id] || (h && "AW" === h.prefix && !f.adData && 2 <= h.ma.length ? (f.adData = {
                    ak: h.ma[fm[1]],
                    cl: h.ma[fm[2]]
                },
                pr(f.adData, d),
                wr[h.id] = !0) : h && "UA" === h.prefix && !f.gaData && (f.gaData = {
                    gaWpid: h.ka
                },
                wr[h.id] = !0))
            }
            (f.gaData || f.adData) && rr(vr, e)(e.Nb, f, e.options)
        }
    }
      , zr = function() {
        var a = !1;
        return a
    }
      , Ar = function(a, b) {
        if (a)
            if (Sn()) {} else if (a = l(a) ? cm(Jj(a)) : cm(Jj(a.id))) {
                var c = void 0
                  , d = !1
                  , e = U(b, P.g.Vi);
                if (e && Array.isArray(e)) {
                    c = [];
                    for (var f = 0; f < e.length; f++) {
                        var g = cm(e[f]);
                        g && (c.push(g),
                        (a.id === g.id || a.id === a.ka && a.ka === g.ka) && (d = !0))
                    }
                }
                if (!c || d) {
                    var h = U(b, P.g.Bg), m;
                    if (h) {
                        Array.isArray(h) ? m = h : m = [h];
                        var n = U(b, P.g.zg)
                          , p = U(b, P.g.Ag)
                          , q = U(b, P.g.Cg)
                          , r = U(b, P.g.Ui)
                          , t = n || p
                          , u = 1;
                        "UA" !== a.prefix || c || (u = 5);
                        for (var v = 0; v < m.length; v++)
                            if (v < u)
                                if (c)
                                    yr(c, m[v], r, b, {
                                        Nb: t,
                                        options: q
                                    });
                                else if ("AW" === a.prefix && a.ma[fm[2]])
                                    zr() ? yr([a], m[v], r || "US", b, {
                                        Nb: t,
                                        options: q
                                    }) : xr(a.ma[fm[1]], a.ma[fm[2]], m[v], b, {
                                        Nb: t,
                                        options: q
                                    });
                                else if ("UA" === a.prefix)
                                    if (zr())
                                        yr([a], m[v], r || "US", b, {
                                            Nb: t
                                        });
                                    else {
                                        var w = a.ka
                                          , y = m[v]
                                          , x = {
                                            Nb: t
                                        };
                                        O(23);
                                        if (y) {
                                            x = x || {};
                                            var B = rr(tr, x, w)
                                              , A = {};
                                            void 0 !== x.Nb ? A.receiver = x.Nb : A.replace = y;
                                            A.ga_wpid = w;
                                            A.destination = y;
                                            B(2, Bb(), A)
                                        }
                                    }
                    }
                }
            }
    };
    function Br(a) {
        return {
            getDestinationId: function() {
                return a.target.ka
            },
            getEventName: function() {
                return a.eventName
            },
            setEventName: function(b) {
                a.eventName = b
            },
            getHitData: function(b) {
                return a.D[b]
            },
            setHitData: function(b, c) {
                a.D[b] = c
            },
            setHitDataIfNotDefined: function(b, c) {
                void 0 === a.D[b] && (a.D[b] = c)
            },
            copyToHitData: function(b, c) {
                a.copyToHitData(b, c)
            },
            getMetadata: function(b) {
                return a.metadata[b]
            },
            setMetadata: function(b, c) {
                a.metadata[b] = c
            },
            isAborted: function() {
                return a.isAborted
            },
            abort: function() {
                a.isAborted = !0
            },
            getFromEventContext: function(b) {
                return U(a.o, b)
            },
            Mj: function() {
                return a
            },
            getHitKeys: function() {
                return Object.keys(a.D)
            }
        }
    }
    ;var Dr = function(a) {
        var b = Cr[a.target.ka];
        if (!a.isAborted && b)
            for (var c = Br(a), d = 0; d < b.length; ++d) {
                try {
                    b[d](c)
                } catch (e) {
                    a.isAborted = !0
                }
                if (a.isAborted)
                    break
            }
    }
      , Er = function(a, b) {
        var c = Cr[a];
        c || (c = Cr[a] = []);
        c.push(b)
    }
      , Cr = {};
    var Gr = function(a) {
        if (W(Fr)) {
            a = a || {};
            $o(a, !1);
            var b = Zo[ap(Gp(a.prefix))];
            if (b && !(18E5 < Cb() - 1E3 * b.Dh)) {
                var c = b.id
                  , d = c.split(".");
                if (2 === d.length && !(864E5 < Cb() - 1E3 * (Number(d[1]) || 0)))
                    return c
            }
        }
    }
      , Fr = P.g.R;
    var Hr = function() {
        var a = oc && oc.userAgent || "";
        if (0 > a.indexOf("Safari") || /Chrome|Coast|Opera|Edg|Silk|Android/.test(a))
            return !1;
        var b = (/Version\/([\d\.]+)/.exec(a) || [])[1] || "";
        if ("" === b)
            return !1;
        for (var c = ["14", "1", "1"], d = b.split("."), e = 0; e < d.length; e++) {
            if (void 0 === c[e])
                return !0;
            if (d[e] !== c[e])
                return Number(d[e]) > Number(c[e])
        }
        return d.length >= c.length
    };
    function Ir() {
        var a = G.screen;
        return {
            width: a ? a.width : 0,
            height: a ? a.height : 0
        }
    }
    function Jr(a) {
        if (H.hidden)
            return !0;
        var b = a.getBoundingClientRect();
        if (b.top === b.bottom || b.left === b.right || !G.getComputedStyle)
            return !0;
        var c = G.getComputedStyle(a, null);
        if ("hidden" === c.visibility)
            return !0;
        for (var d = a, e = c; d; ) {
            if ("none" === e.display)
                return !0;
            var f = e.opacity
              , g = e.filter;
            if (g) {
                var h = g.indexOf("opacity(");
                0 <= h && (g = g.substring(h + 8, g.indexOf(")", h)),
                "%" === g.charAt(g.length - 1) && (g = g.substring(0, g.length - 1)),
                f = String(Math.min(Number(g), Number(f))))
            }
            if (void 0 !== f && 0 >= Number(f))
                return !0;
            (d = d.parentElement) && (e = G.getComputedStyle(d, null))
        }
        return !1
    }
    var Lr = function(a) {
        var b = Kr()
          , c = b.height
          , d = b.width
          , e = a.getBoundingClientRect()
          , f = e.bottom - e.top
          , g = e.right - e.left;
        return f && g ? (1 - Math.min((Math.max(0 - e.left, 0) + Math.max(e.right - d, 0)) / g, 1)) * (1 - Math.min((Math.max(0 - e.top, 0) + Math.max(e.bottom - c, 0)) / f, 1)) : 0
    }
      , Kr = function() {
        var a = H.body, b = H.documentElement || a && a.parentElement, c, d;
        if (H.compatMode && "BackCompat" !== H.compatMode)
            c = b ? b.clientHeight : 0,
            d = b ? b.clientWidth : 0;
        else {
            var e = function(f, g) {
                return f && g ? Math.min(f, g) : Math.max(f, g)
            };
            c = e(b ? b.clientHeight : 0, a ? a.clientHeight : 0);
            d = e(b ? b.clientWidth : 0, a ? a.clientWidth : 0)
        }
        return {
            width: d,
            height: c
        }
    };
    var Tr = function(a, b, c) {
        var d = a.element
          , e = {
            aa: a.aa,
            type: a.sa,
            tagName: d.tagName
        };
        b && (e.querySelector = Sr(d));
        c && (e.isVisible = !Jr(d));
        return e
    }
      , Ur = function(a, b, c) {
        return Tr({
            element: a.element,
            aa: a.aa,
            sa: "1"
        }, b, c)
    }
      , Vr = function(a) {
        var b = !!a.xd + "." + !!a.yd;
        a && a.ye && a.ye.length && (b += "." + a.ye.join("."));
        a && a.vb && (b += "." + a.vb.email + "." + a.vb.phone + "." + a.vb.address);
        return b
    }
      , Yr = function(a) {
        if (0 != a.length) {
            var b;
            b = Wr(a, function(c) {
                return !Xr.test(c.aa)
            });
            b = Wr(b, function(c) {
                return "INPUT" === c.element.tagName.toUpperCase()
            });
            b = Wr(b, function(c) {
                return !Jr(c.element)
            });
            return b[0]
        }
    }
      , Zr = function(a, b) {
        if (!b || 0 === b.length)
            return a;
        for (var c = [], d = 0; d < a.length; d++) {
            for (var e = !0, f = 0; f < b.length; f++) {
                var g = b[f];
                if (g && ph(a[d].element, g)) {
                    e = !1;
                    break
                }
            }
            e && c.push(a[d])
        }
        return c
    }
      , Wr = function(a, b) {
        if (1 >= a.length)
            return a;
        var c = a.filter(b);
        return 0 == c.length ? a : c
    }
      , Sr = function(a) {
        var b;
        if (a === H.body)
            b = "body";
        else {
            var c;
            if (a.id)
                c = "#" + a.id;
            else {
                var d;
                if (a.parentElement) {
                    var e;
                    a: {
                        var f = a.parentElement;
                        if (f) {
                            for (var g = 0; g < f.childElementCount; g++)
                                if (f.children[g] === a) {
                                    e = g + 1;
                                    break a
                                }
                            e = -1
                        } else
                            e = 1
                    }
                    d = Sr(a.parentElement) + ">:nth-child(" + e + ")"
                } else
                    d = "";
                c = d
            }
            b = c
        }
        return b
    }
      , as = function(a) {
        for (var b = [], c = 0; c < a.length; c++) {
            var d = a[c]
              , e = d.textContent;
            "INPUT" === d.tagName.toUpperCase() && d.value && (e = d.value);
            if (e) {
                var f = e.match($r);
                if (f) {
                    var g = f[0], h;
                    if (G.location) {
                        var m = cj(G.location, "host", !0);
                        h = 0 <= g.toLowerCase().indexOf(m)
                    } else
                        h = !1;
                    h || b.push({
                        element: d,
                        aa: g
                    })
                }
            }
        }
        return b
    }
      , es = function() {
        var a = []
          , b = H.body;
        if (!b)
            return {
                elements: a,
                status: "4"
            };
        for (var c = b.querySelectorAll("*"), d = 0; d < c.length && 1E4 > d; d++) {
            var e = c[d];
            if (!(0 <= bs.indexOf(e.tagName.toUpperCase())) && e.children instanceof HTMLCollection) {
                for (var f = !1, g = 0; g < e.childElementCount && 1E4 > g; g++)
                    if (!(0 <= cs.indexOf(e.children[g].tagName.toUpperCase()))) {
                        f = !0;
                        break
                    }
                (!f || T(17) && -1 !== ds.indexOf(e.tagName)) && a.push(e)
            }
        }
        return {
            elements: a,
            status: 1E4 < c.length ? "2" : "1"
        }
    }
      , fs = !1;
    var $r = /[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i
      , gs = /@(gmail|googlemail)\./i
      , Xr = /support|noreply/i
      , bs = "SCRIPT STYLE IMG SVG PATH BR NOSCRIPT TEXTAREA".split(" ")
      , cs = ["BR"]
      , hs = {
        pn: "1",
        Cn: "2",
        tn: "3",
        wn: "4",
        mn: "5",
        Dn: "6",
        yn: "7"
    }
      , is = {}
      , ds = ["INPUT", "SELECT"];
    var Bs = function(a) {
        a = a || {
            xd: !0,
            yd: !0,
            Qf: void 0
        };
        a.vb = a.vb || {
            email: !0,
            phone: !1,
            address: !1
        };
        var b = Vr(a)
          , c = is[b];
        if (c && 200 > Cb() - c.timestamp)
            return c.result;
        var d = es(), e = d.status, f = [], g, h, m = [];
        if (!T(17)) {
            if (a.vb && a.vb.email) {
                var n = as(d.elements);
                f = Zr(n, a && a.ye);
                g = Yr(f);
                10 < n.length && (e = "3")
            }
            !a.Qf && g && (f = [g]);
            for (var p = 0; p < f.length; p++)
                m.push(Ur(f[p], a.xd, a.yd));
            m = m.slice(0, 10)
        } else if (a.vb) {}
        g && (h = Ur(g, a.xd, a.yd));
        var D = {
            elements: m,
            Lh: h,
            status: e
        };
        is[b] = {
            timestamp: Cb(),
            result: D
        };
        return D
    }
      , Cs = function(a) {
        return a.tagName + ":" + a.isVisible + ":" + a.aa.length + ":" + gs.test(a.aa)
    };
    var Js = Number('') || 5
      , Ks = Number('') || 50
      , Ls = tb();
    var Ns = function(a, b) {
        a && (Ms("sid", a.targetId, b),
        Ms("cc", a.clientCount, b),
        Ms("tl", a.totalLifeMs, b),
        Ms("hc", a.heartbeatCount, b),
        Ms("cl", a.clientLifeMs, b))
    }
      , Ms = function(a, b, c) {
        null != b && c.push(a + "=" + b)
    }
      , Os = function() {
        var a = H.referrer;
        if (a) {
            var b;
            return dj(hj(a), "host") === (null == (b = G.location) ? void 0 : b.host) ? 1 : 2
        }
        return 0
    }
      , Ps = function(a) {
        this.T = a;
        this.H = 0
    };
    Ps.prototype.F = function(a, b, c, d) {
        var e = Os(), f, g = [];
        f = G === G.top && 0 !== e && b ? 1 < (null == b ? void 0 : b.clientCount) ? 2 === e ? 1 : 2 : 2 === e ? 0 : 3 : 4;
        a && Ms("si", a.Mf, g);
        Ms("m", 0, g);
        Ms("iss", f, g);
        Ms("if", c, g);
        Ns(b, g);
        d && Ms("fm", encodeURIComponent(d.substring(0, Ks)), g);
        this.M(g);
    }
    ;
    Ps.prototype.m = function(a, b, c, d, e) {
        var f = [];
        Ms("m", 1, f);
        Ms("s", a, f);
        Ms("po", Os(), f);
        b && (Ms("st", b.state, f),
        Ms("si", b.Mf, f),
        Ms("sm", b.Sf, f));
        Ns(c, f);
        Ms("c", d, f);
        e && Ms("fm", encodeURIComponent(e.substring(0, Ks)), f);
        this.M(f);
    }
    ;
    Ps.prototype.M = function(a) {
        a = void 0 === a ? [] : a;
        !jk || this.H >= Js || (Ms("pid", Ls, a),
        Ms("bc", ++this.H, a),
        a.unshift("ctid=" + Hf.ctid + "&t=s"),
        this.T("https://www.googletagmanager.com/a?" + a.join("&")))
    }
    ;
    var Qs = {
        Yk: Number('') || 500,
        Nk: Number('') || 5E3,
        lj: Number('20') || 10,
        tk: Number('') || 5E3
    };
    function Rs(a) {
        return a.performance && a.performance.now() || Date.now()
    }
    var Ss = function(a, b) {
        var c;
        var d = function(e, f, g) {
            g = void 0 === g ? {} : g;
            this.bl = e;
            this.H = g;
            this.m = f;
            this.id = String(Math.floor(Number.MAX_SAFE_INTEGER * Math.random()));
            this.da = this.Wa = this.heartbeatCount = this.al = 0;
            this.nj = !1;
            this.F = {};
            this.state = 0;
            this.Mf = Rs(this.m);
            this.Sf = Rs(this.m);
            this.T = 10
        };
        d.prototype.init = function() {
            this.M(1);
            this.Yb()
        }
        ;
        d.prototype.getState = function() {
            return {
                state: this.state,
                Mf: Math.round(Rs(this.m) - this.Mf),
                Sf: Math.round(Rs(this.m) - this.Sf)
            }
        }
        ;
        d.prototype.M = function(e) {
            this.state !== e && (this.state = e,
            this.Sf = Rs(this.m))
        }
        ;
        d.prototype.rj = function() {
            return String(this.al++)
        }
        ;
        d.prototype.Yb = function() {
            var e = this;
            this.heartbeatCount++;
            this.Dc({
                type: 0,
                clientId: this.id,
                requestId: this.rj(),
                maxDelay: this.pj()
            }, function(f) {
                if (0 === f.type) {
                    var g;
                    if (null != (null == (g = f.failure) ? void 0 : g.failureType))
                        if (f.stats && (e.stats = f.stats),
                        e.da++,
                        f.isDead || e.da > Qs.lj) {
                            var h = f.isDead && f.failure.failureType;
                            e.T = h || 10;
                            e.M(4);
                            e.Zk();
                            var m, n;
                            null == (n = (m = e.H).sm) || n.call(m, {
                                failureType: h,
                                data: f.failure.data
                            })
                        } else
                            e.M(3),
                            e.wj();
                    else {
                        if (e.heartbeatCount > f.stats.heartbeatCount + Qs.lj) {
                            e.heartbeatCount = f.stats.heartbeatCount;
                            var p, q;
                            null == (q = (p = e.H).onFailure) || q.call(p, {
                                failureType: 13
                            })
                        }
                        e.stats = f.stats;
                        var r = e.state;
                        e.M(2);
                        if (2 !== r)
                            if (e.nj) {
                                var t, u;
                                null == (u = (t = e.H).Un) || u.call(t)
                            } else {
                                e.nj = !0;
                                var v, w;
                                null == (w = (v = e.H).vm) || w.call(v)
                            }
                        e.da = 0;
                        e.fl();
                        e.wj()
                    }
                }
            })
        }
        ;
        d.prototype.pj = function() {
            return 2 === this.state ? Qs.Nk : Qs.Yk
        }
        ;
        d.prototype.wj = function() {
            var e = this;
            this.m.setTimeout(function() {
                e.Yb()
            }, Math.max(0, this.pj() - (Rs(this.m) - this.Wa)))
        }
        ;
        d.prototype.kl = function(e, f, g) {
            var h = this;
            this.Dc({
                type: 1,
                clientId: this.id,
                requestId: this.rj(),
                command: e
            }, function(m) {
                if (1 === m.type)
                    if (m.result)
                        f(m.result);
                    else {
                        var n, p, q, r = {
                            failureType: null != (q = null == (n = m.failure) ? void 0 : n.failureType) ? q : 12,
                            data: null == (p = m.failure) ? void 0 : p.data
                        }, t, u;
                        null == (u = (t = h.H).onFailure) || u.call(t, r);
                        g(r)
                    }
            })
        }
        ;
        d.prototype.Dc = function(e, f) {
            var g = this;
            if (4 === this.state)
                e.failure = {
                    failureType: this.T
                },
                f(e);
            else {
                var h = 2 !== this.state && 0 != e.type, m = e.requestId, n, p = this.m.setTimeout(function() {
                    var r = g.F[m];
                    r && g.mj(r, 7)
                }, null != (n = e.maxDelay) ? n : Qs.tk), q = {
                    request: e,
                    fk: f,
                    Yj: h,
                    lm: p
                };
                this.F[m] = q;
                h || this.Cj(q)
            }
        }
        ;
        d.prototype.Cj = function(e) {
            this.Wa = Rs(this.m);
            e.Yj = !1;
            this.bl(e.request)
        }
        ;
        d.prototype.fl = function() {
            for (var e in this.F) {
                var f = this.F[e];
                f.Yj && this.Cj(f)
            }
        }
        ;
        d.prototype.Zk = function() {
            for (var e in this.F)
                this.mj(this.F[e], this.T)
        }
        ;
        d.prototype.mj = function(e, f) {
            this.Af(e);
            var g = e.request;
            g.failure = {
                failureType: f
            };
            e.fk(g)
        }
        ;
        d.prototype.Af = function(e) {
            delete this.F[e.request.requestId];
            this.m.clearTimeout(e.lm)
        }
        ;
        d.prototype.Ql = function(e) {
            this.Wa = Rs(this.m);
            var f = this.F[e.requestId];
            if (f)
                this.Af(f),
                f.fk(e);
            else {
                var g, h;
                null == (h = (g = this.H).onFailure) || h.call(g, {
                    failureType: 14
                })
            }
        }
        ;
        c = new d(a,G,b);
        return c
    };
    var Ts = "https://" + hi.Hd + "/gtm/static/", Us;
    var Vs = function() {
        Us || (Us = new Ps(function(a) {
            return void zc(a)
        }
        ));
        return Us
    }
      , Ws = function(a) {
        if (!a) {
            var b = Ai.Wa;
            a = b ? b : Ts
        }
        var c;
        try {
            c = new URL(a)
        } catch (d) {
            return null
        }
        return "https:" !== c.protocol ? null : c
    }
      , Xs = function(a) {
        var b = Zn(Vn.Rg);
        return b && b[a]
    }
      , Ys = function(a, b, c) {
        var d = Vs()
          , e = this;
        this.initTime = c;
        this.T = this.M = !1;
        this.da = null;
        this.F = d;
        this.m = 15;
        this.H = this.sl(a);
        G.setTimeout(function() {
            return e.Qj()
        }, 1E3);
        I(function() {
            e.Yl(a, b)
        })
    };
    aa = Ys.prototype;
    aa.delegate = function(a, b, c) {
        2 !== this.getState() ? (this.F.m(this.m, void 0, void 0, a.commandType),
        c({
            failureType: this.m
        })) : this.H.kl(a, b, c)
    }
    ;
    aa.getState = function() {
        return this.H.getState().state
    }
    ;
    aa.Yl = function(a, b) {
        var c = G.location.origin
          , d = this
          , e = yc();
        try {
            var f = e.contentDocument.createElement("iframe")
              , g = a.pathname
              , h = b ? "&1p=1" : "";
            yc(("/" === g[g.length - 1] ? a.toString() : a.toString() + "/") + "sw_iframe.html?origin=" + encodeURIComponent(c) + h, void 0, void 0, void 0, f);
            var m = function() {
                e.contentDocument.body.appendChild(f);
                f.addEventListener("load", function() {
                    d.da = f.contentWindow;
                    e.contentWindow.addEventListener("message", function(n) {
                        n.origin === a.origin && d.H.Ql(n.data)
                    });
                    d.Qj()
                })
            };
            "complete" === e.contentDocument.readyState ? m() : e.contentWindow.addEventListener("load", function() {
                m()
            })
        } catch (n) {
            e.parentElement.removeChild(e),
            this.m = 11,
            this.F.F(void 0, void 0, this.m, n.toString())
        }
    }
    ;
    aa.sl = function(a) {
        var b = this
          , c = Ss(function(d) {
            var e;
            null == (e = b.da) || e.postMessage(d, a.origin)
        }, {
            vm: function() {
                b.M = !0;
                b.F.F(c.getState(), c.stats)
            },
            sm: function(d) {
                b.M ? (b.m = (null == d ? void 0 : d.failureType) || 10,
                b.F.m(b.m, c.getState(), c.stats, void 0, null == d ? void 0 : d.data)) : (b.m = (null == d ? void 0 : d.failureType) || 4,
                b.F.F(c.getState(), c.stats, b.m, null == d ? void 0 : d.data))
            },
            onFailure: function(d) {
                b.m = d.failureType;
                b.F.m(b.m, c.getState(), c.stats, d.command, d.data)
            }
        });
        return c
    }
    ;
    aa.Qj = function() {
        this.T || this.H.init();
        this.T = !0
    }
    ;
    function Zs(a, b) {
        var c = G.location.origin;
        if (!c)
            return;
        Ai.F && (a = "" + c + Bi() + "/_");
        var d = Ws(a);
        if (null === d || Xs(d.origin))
            return;
        if (!pc()) {
            Vs().F(void 0, void 0, 6);
            return
        }
        var e = new Ys(d,!!a,b || Math.round(Cb()))
          , f = Zn(Vn.Rg);
        f || (f = {},
        Yn(Vn.Rg, f));
        f[d.origin] = e;
    }
    function $s(a, b, c, d) {
        var e;
        if (null == (e = Xs(a)) || !e.delegate) {
            var f = pc() ? 16 : 6;
            Vs().m(f, void 0, void 0, b.commandType);
            d({
                failureType: f
            });
            return
        }
        Xs(a).delegate(b, c, d);
    }
    function at(a, b, c, d) {
        var e = Ws();
        if (null === e) {
            d(pc() ? 16 : 6);
            return
        }
        var f, g = null == (f = Xs(e.origin)) ? void 0 : f.initTime, h = Math.round(Cb());
        $s(e.origin, {
            commandType: 0,
            params: {
                url: a,
                method: 0,
                templates: b,
                body: "",
                processResponse: !1,
                sinceInit: g ? h - g : void 0
            }
        }, function() {
            c()
        }, function(m) {
            d(m.failureType)
        });
    }
    function bt(a, b, c, d) {
        var e = Ws(a);
        if (null === e) {
            d("_is_sw=f" + (pc() ? 16 : 6) + "te");
            return
        }
        var f = b ? 1 : 0, g = Math.round(Cb()), h, m = null == (h = Xs(e.origin)) ? void 0 : h.initTime, n = m ? g - m : void 0;
        $s(e.origin, {
            commandType: 0,
            params: {
                url: a,
                method: f,
                templates: c,
                body: b || "",
                processResponse: !0,
                sinceInit: n,
                attributionReporting: !0
            }
        }, function() {}, function(p) {
            var q = "_is_sw=f" + p.failureType, r, t = null == (r = Xs(e.origin)) ? void 0 : r.getState();
            void 0 != t && (q += "s" + t);
            d(n ? q + ("t" + n) : q + "te")
        });
    }
    var ct = void 0;
    function dt(a) {
        var b = [];
        return b
    }
    ;var et = function(a) {
        for (var b = [], c = 0, d = 0; d < a.length; d++) {
            var e = a.charCodeAt(d);
            128 > e ? b[c++] = e : (2048 > e ? b[c++] = e >> 6 | 192 : (55296 == (e & 64512) && d + 1 < a.length && 56320 == (a.charCodeAt(d + 1) & 64512) ? (e = 65536 + ((e & 1023) << 10) + (a.charCodeAt(++d) & 1023),
            b[c++] = e >> 18 | 240,
            b[c++] = e >> 12 & 63 | 128) : b[c++] = e >> 12 | 224,
            b[c++] = e >> 6 & 63 | 128),
            b[c++] = e & 63 | 128)
        }
        return b
    };
    Ok();
    Rk() || Lk("iPod");
    Lk("iPad");
    !Lk("Android") || Pk() || Ok() || Nk() || Lk("Silk");
    Pk();
    !Lk("Safari") || Pk() || (Mk() ? 0 : Lk("Coast")) || Nk() || (Mk() ? 0 : Lk("Edge")) || (Mk() ? Kk("Microsoft Edge") : Lk("Edg/")) || (Mk() ? Kk("Opera") : Lk("OPR")) || Ok() || Lk("Silk") || Lk("Android") || Sk();
    var ft = {}
      , gt = null
      , ht = function(a) {
        for (var b = [], c = 0, d = 0; d < a.length; d++) {
            var e = a.charCodeAt(d);
            255 < e && (b[c++] = e & 255,
            e >>= 8);
            b[c++] = e
        }
        var f = 4;
        void 0 === f && (f = 0);
        if (!gt) {
            gt = {};
            for (var g = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789".split(""), h = ["+/=", "+/", "-_=", "-_.", "-_"], m = 0; 5 > m; m++) {
                var n = g.concat(h[m].split(""));
                ft[m] = n;
                for (var p = 0; p < n.length; p++) {
                    var q = n[p];
                    void 0 === gt[q] && (gt[q] = p)
                }
            }
        }
        for (var r = ft[f], t = Array(Math.floor(b.length / 3)), u = r[64] || "", v = 0, w = 0; v < b.length - 2; v += 3) {
            var y = b[v]
              , x = b[v + 1]
              , B = b[v + 2]
              , A = r[y >> 2]
              , D = r[(y & 3) << 4 | x >> 4]
              , E = r[(x & 15) << 2 | B >> 6]
              , C = r[B & 63];
            t[w++] = "" + A + D + E + C
        }
        var F = 0
          , L = u;
        switch (b.length - v) {
        case 2:
            F = b[v + 1],
            L = r[(F & 15) << 2] || u;
        case 1:
            var N = b[v];
            t[w] = "" + r[N >> 2] + r[(N & 3) << 4 | F >> 4] + L + u
        }
        return t.join("")
    };
    Object.freeze(new function() {}
    );
    Object.freeze(new function() {}
    );
    var it = "platform platformVersion architecture model uaFullVersion bitness fullVersionList wow64".split(" ");
    function jt(a) {
        var b;
        return null != (b = a.google_tag_data) ? b : a.google_tag_data = {}
    }
    function kt() {
        var a = G.google_tag_data, b;
        if (null != a && a.uach) {
            var c = a.uach
              , d = Object.assign({}, c);
            c.fullVersionList && (d.fullVersionList = c.fullVersionList.slice(0));
            b = d
        } else
            b = null;
        return b
    }
    function lt() {
        var a, b;
        return null != (b = null == (a = G.google_tag_data) ? void 0 : a.uach_promise) ? b : null
    }
    function mt(a) {
        var b, c;
        return "function" === typeof (null == (b = a.navigator) ? void 0 : null == (c = b.userAgentData) ? void 0 : c.getHighEntropyValues)
    }
    function nt() {
        var a = G;
        if (!mt(a))
            return null;
        var b = jt(a);
        if (b.uach_promise)
            return b.uach_promise;
        var c = a.navigator.userAgentData.getHighEntropyValues(it).then(function(d) {
            null != b.uach || (b.uach = d);
            return d
        });
        return b.uach_promise = c
    }
    ;var ot, pt = function() {
        if (mt(G) && (ot = Cb(),
        !lt())) {
            var a = nt();
            a && (a.then(function() {
                O(95);
            }),
            a.catch(function() {
                O(96)
            }))
        }
    }, rt = function(a) {
        var b = qt.dn
          , c = function(g, h) {
            try {
                a(g, h)
            } catch (m) {}
        }
          , d = kt();
        if (d)
            c(d);
        else {
            var e = lt();
            if (e) {
                b = Math.min(Math.max(isFinite(b) ? b : 0, 0), 1E3);
                var f = G.setTimeout(function() {
                    c.He || (c.He = !0,
                    O(106),
                    c(null, Error("Timeout")))
                }, b);
                e.then(function(g) {
                    c.He || (c.He = !0,
                    O(104),
                    G.clearTimeout(f),
                    c(g))
                }).catch(function(g) {
                    c.He || (c.He = !0,
                    O(105),
                    G.clearTimeout(f),
                    c(null, g))
                })
            } else
                c(null)
        }
    }, st = function(a, b) {
        a && (b.D[P.g.qf] = a.architecture,
        b.D[P.g.rf] = a.bitness,
        a.fullVersionList && (b.D[P.g.tf] = a.fullVersionList.map(function(c) {
            return encodeURIComponent(c.brand || "") + ";" + encodeURIComponent(c.version || "")
        }).join("|")),
        b.D[P.g.uf] = a.mobile ? "1" : "0",
        b.D[P.g.vf] = a.model,
        b.D[P.g.wf] = a.platform,
        b.D[P.g.xf] = a.platformVersion,
        b.D[P.g.yf] = a.wow64 ? "1" : "0")
    };
    function tt(a) {
        var b;
        b = void 0 === b ? document : b;
        var c;
        return !(null == (c = b.featurePolicy) || !c.allowedFeatures().includes(a))
    }
    ;var ut = !1;
    function vt() {
        if (tt("join-ad-interest-group") && pb(oc.joinAdInterestGroup))
            return !0;
        ut || (al(''),
        ut = !0);
        return tt("join-ad-interest-group") && pb(oc.joinAdInterestGroup)
    }
    function wt(a, b) {
        var c = void 0 === Si[3] ? 1 : Si[3]
          , d = 'iframe[data-tagging-id="' + b + '"]'
          , e = [];
        try {
            if (1 === c) {
                var f = H.querySelector(d);
                f && (e = [f])
            } else
                e = Array.from(H.querySelectorAll(d))
        } catch (q) {}
        var g;
        a: {
            try {
                g = H.querySelectorAll('iframe[allow="join-ad-interest-group"][data-tagging-id*="-"]');
                break a
            } catch (q) {}
            g = void 0
        }
        var h = g, m = ((null == h ? void 0 : h.length) || 0) >= (void 0 === Si[2] ? 50 : Si[2]), n;
        if (n = 1 <= e.length) {
            var p = Number(e[e.length - 1].dataset.loadTime);
            void 0 !== p && Cb() - p < (void 0 === Si[1] ? 6E4 : Si[1]) ? (lb("TAGGING", 9),
            n = !0) : n = !1
        }
        if (!n) {
            if (1 === c)
                if (1 <= e.length)
                    xt(e[0]);
                else {
                    if (m) {
                        lb("TAGGING", 10);
                        return
                    }
                }
            else
                e.length >= c ? xt(e[0]) : m && xt(h[0]);
            yc(a, void 0, {
                allow: "join-ad-interest-group"
            }, {
                taggingId: b,
                loadTime: Cb()
            })
        }
    }
    function xt(a) {
        try {
            a.parentNode.removeChild(a)
        } catch (b) {}
    }
    function zt() {
        return "https://td.doubleclick.net"
    }
    ;var At = function() {
        return [P.g.R, P.g.P]
    }
      , Bt = function(a) {
        if (null != a) {
            var b = String(a).substring(0, 512)
              , c = b.indexOf("#");
            return -1 == c ? b : b.substring(0, c)
        }
        return ""
    }
      , Ct = function() {
        var a = H.title;
        if (void 0 == a || "" == a)
            return "";
        var b = function(d) {
            try {
                return decodeURIComponent(d),
                !0
            } catch (e) {
                return !1
            }
        };
        a = encodeURIComponent(a);
        for (var c = 256; !b(a.substr(0, c)); )
            c--;
        return decodeURIComponent(a.substr(0, c))
    }
      , Dt = function(a) {
        a.metadata.speculative_in_message || (a.metadata.speculative = !1)
    }
      , Et = function(a, b) {
        Array.isArray(b) || (b = [b]);
        return 0 <= b.indexOf(a.metadata.hit_type)
    }
      , Ft = function(a) {
        var b = a.target.ma[fm[1]];
        if (b) {
            a.D[P.g.Xc] = b;
            var c = a.target.ma[fm[2]];
            c && (a.D[P.g.nb] = c)
        } else
            a.isAborted = !0
    }
      , Gt = function(a) {
        if (Et(a, ["conversion", "remarketing", "user_data_lead", "user_data_web"])) {
            var b = a.D[P.g.nb]
              , c = !0 === U(a.o, P.g.Ye);
            c && (a.metadata.remarketing_only = !0);
            switch (a.metadata.hit_type) {
            case "conversion":
                !c && b && Dt(a);
                -1 !== oc.userAgent.toLowerCase().indexOf("firefox") && (a.metadata.is_gcp_conversion = !0);
                break;
            case "user_data_lead":
            case "user_data_web":
                !c && b && (a.isAborted = !0);
                break;
            case "remarketing":
                !c && b || Dt(a)
            }
            Et(a, ["conversion", "remarketing"]) && (a.D[P.g.ij] = a.metadata.is_gcp_conversion ? "www.google.com" : "www.googleadservices.com")
        }
    }
      , Ht = function(a) {
        Et(a, ["conversion", "remarketing"])
    }
      , It = function(a) {
        if (!a.metadata.consent_updated && Et(a, ["conversion", "remarketing"])) {
            var b = cl(!1);
            a.D[P.g.Fb] = b;
            var c = U(a.o, P.g.ya);
            c || (c = 1 === b ? G.top.location.href : G.location.href);
            a.D[P.g.ya] = Bt(c);
            a.copyToHitData(P.g.Fa, H.referrer);
            a.D[P.g.Ib] = Ct();
            a.copyToHitData(P.g.Pa);
            var d = Ir();
            a.D[P.g.Jb] = d.width + "x" + d.height;
            for (var e, f = G, g = f; f && f != f.parent; )
                f = f.parent,
                Zk(f) && (g = f);
            e = g;
            var h;
            var m = e.location.href;
            if (e === e.top)
                h = {
                    url: m,
                    gm: !0
                };
            else {
                var n = !1
                  , p = e.document;
                p && p.referrer && (m = p.referrer,
                e.parent === e.top && (n = !0));
                var q = e.location.ancestorOrigins;
                if (q) {
                    var r = q[q.length - 1];
                    r && -1 === m.indexOf(r) && (n = !1,
                    m = r)
                }
                h = {
                    url: m,
                    gm: n
                }
            }
            var t = h;
            t.url && c !== t.url && (a.D[P.g.nf] = Bt(t.url))
        }
    }
      , Jt = function(a) {
        Et(a, ["conversion", "remarketing"]) && (a.copyToHitData(P.g.Ca),
        a.copyToHitData(P.g.qa),
        a.copyToHitData(P.g.Ba))
    }
      , Kt = function(a) {
        var b = ["conversion", "remarketing"];
        T(70) && b.push("page_view", "user_data_lead", "user_data_web");
        if (Et(a, b) && W(P.g.P) && (a.copyToHitData(P.g.Da),
        T(70))) {
            var c = Zn(Vn.Sg);
            if (void 0 === c)
                Yn(Vn.Tg, !0);
            else {
                var d = Zn(Vn.Ug);
                a.D[P.g.Eg] = d + "." + c
            }
        }
    }
      , Lt = function(a) {
        if (!mt(G))
            O(87);
        else if (void 0 !== ot) {
            O(85);
            var b = kt();
            b ? st(b, a) : O(86)
        }
    }
      , Ot = function(a) {
        Et(a, ["conversion"]) && W(P.g.P) && (!0 === G._gtmpcm || Hr() ? a.D[P.g.Sb] = "2" : T(22) && (Mt || tt("attribution-reporting") || (al(''),
        Mt = !0),
        Nt || (Nt = !0,
        al('A4oIpR6f5aUXFRMbL6t6qaMk4lrHWxcV3DcrzORsA9sEsIk1FBRMFzzhfMNLuUpokZH40FV8s7iiXtt/729v8A4AAACFeyJvcmlnaW4iOiJodHRwczovL3d3dy5nb29nbGV0YWdtYW5hZ2VyLmNvbTo0NDMiLCJmZWF0dXJlIjoiQXR0cmlidXRpb25SZXBvcnRpbmdDcm9zc0FwcFdlYiIsImV4cGlyeSI6MTcxNDUyMTU5OSwiaXNUaGlyZFBhcnR5Ijp0cnVlfQ\x3d\x3d')),
        tt("attribution-reporting") && (a.D[P.g.Sb] = "1")))
    }
      , Pt = function(a) {
        if (Et(a, ["conversion", "remarketing"]) && T(18)) {
            var b = function(c) {
                return T(20) ? (lb("fdr", c),
                !0) : !1
            };
            if (W(P.g.R) || b(0))
                if (W(P.g.P) || b(1))
                    if (!1 !== U(a.o, P.g.Ea) || b(2))
                        if (yn(a.o) || b(3))
                            if (!1 !== U(a.o, P.g.Rb) || b(4))
                                if (!1 !== (T(21) ? a.eventName === P.g.fa ? U(a.o, P.g.Ka) : void 0 : U(a.o, P.g.Ka)) || b(5))
                                    if (vt() || b(6))
                                        T(20) && nb() ? (a.D[P.g.Ki] = mb("fdr"),
                                        delete kb.fdr) : (a.D[P.g.lg] = "1",
                                        a.metadata.send_fledge_experiment = !0)
        }
    }
      , Qt = function(a) {
        a.metadata.conversion_linker_enabled = !1 !== U(a.o, P.g.wa);
        a.metadata.cookie_options = Zq(a);
        a.metadata.redact_ads_data = null != U(a.o, P.g.ja) && !1 !== U(a.o, P.g.ja);
        a.metadata.allow_ad_personalization = yn(a.o)
    }
      , Rt = function(a) {
        if (Dq(a, "ccd_add_1p_data", !1) && W(At())) {
            var b = a.o.F[P.g.fe];
            if (Pi(b)) {
                var c = U(a.o, P.g.Ga);
                null === c ? a.metadata.user_data_from_code = null : (b.enable_code && Xa(c) && (a.metadata.user_data_from_code = c),
                Xa(b.selectors) && (a.metadata.user_data_from_manual = Oi(b.selectors)))
            }
        }
    }
      , St = function(a) {
        var b = !a.metadata.send_user_data_hit && Et(a, ["conversion", "user_data_web"])
          , c = !Dq(a, "ccd_add_1p_data", !1) && Et(a, "user_data_lead");
        if ((b || c) && W(P.g.R)) {
            var d = "conversion" === a.metadata.hit_type
              , e = a.o
              , f = void 0
              , g = U(e, P.g.Ga);
            if (d) {
                var h = (U(e, P.g.Td) || {})[String(a.D[P.g.nb])];
                if (!0 === U(e, P.g.Jd) || h) {
                    var m;
                    var n;
                    if (h)
                        b: {
                            switch (h.enhanced_conversions_mode) {
                            case "manual":
                                if (g && Xa(g)) {
                                    n = g;
                                    break b
                                }
                                var p = h.enhanced_conversions_manual_var;
                                n = void 0 !== p ? p : G.enhanced_conversion_data;
                                break b;
                            case "automatic":
                                n = Oi(h[P.g.kg]);
                                break b
                            }
                            n = void 0
                        }
                    else
                        n = G.enhanced_conversion_data;
                    var q = n, r = (h || {}).enhanced_conversions_mode, t;
                    if (q) {
                        if ("manual" === r)
                            switch (q._tag_mode) {
                            case "CODE":
                                t = "c";
                                break;
                            case "AUTO":
                                t = "a";
                                break;
                            case "MANUAL":
                                t = "m";
                                break;
                            default:
                                t = "c"
                            }
                        else
                            t = "automatic" === r ? jr(h) ? "a" : "m" : "c";
                        m = {
                            aa: q,
                            jk: t
                        }
                    } else
                        m = {
                            aa: q,
                            jk: void 0
                        };
                    var u = m
                      , v = u.jk;
                    f = u.aa;
                    a.D[P.g.pd] = v
                }
            } else if (a.o.isGtmEvent) {
                Dt(a);
                a.metadata.user_data = g;
                a.D[P.g.pd] = ir(g);
                return
            }
            a.metadata.user_data = f
        }
    }
      , Tt = function(a) {
        Et(a, ["conversion", "remarketing"]) && (a.o.isGtmEvent ? "conversion" !== a.metadata.hit_type && a.eventName && (a.D[P.g.fd] = a.eventName) : a.D[P.g.fd] = a.eventName,
        z(a.o.m, function(b, c) {
            ei[b.split(".")[0]] || (a.D[b] = c)
        }))
    }
      , Ut = function(a) {
        if (a.eventName === P.g.fa && !a.metadata.consent_updated && (a.metadata.is_config_command = !0,
        Et(a, "conversion") && (a.metadata.speculative = !0),
        !Et(a, "remarketing") || !1 !== U(a.o, P.g.Rb) && !1 !== U(a.o, P.g.Ka) || (a.metadata.speculative = !0),
        Et(a, "landing_page"))) {
            var b = U(a.o, P.g.xa) || {}
              , c = U(a.o, P.g.Va)
              , d = a.metadata.conversion_linker_enabled
              , e = a.metadata.source_canonical_id
              , f = yn(a.o)
              , g = a.metadata.redact_ads_data
              , h = {
                vd: d,
                zd: b,
                Fd: c,
                za: e,
                allowAdPersonalizationSignals: f,
                Bd: g,
                kk: U(a.o, P.g.Da)
            }
              , m = a.metadata.cookie_options;
            br(h, m);
            Ar(a.target, a.o);
            nr({
                bh: !1,
                Bd: g,
                targetId: a.target.id,
                o: a.o,
                fc: d ? m : void 0,
                Lf: d,
                Jj: a.D[P.g.be],
                rh: a.D[P.g.rb],
                jh: a.D[P.g.ob],
                uh: a.D[P.g.Fb]
            });
            a.isAborted = !0
        }
    }
      , Vt = function(a) {
        if (!Dq(a, "hasPreAutoPiiCcdRule", !1) && Et(a, "conversion") && W(P.g.R)) {
            var b = (U(a.o, P.g.Td) || {})[String(a.D[P.g.nb])], c = a.D[P.g.Xc], d;
            if (!(d = jr(b)))
                if (tl())
                    if (fs)
                        d = !0;
                    else {
                        var e = Bq("AW-" + c);
                        d = !!e && !!e.preAutoPii
                    }
                else
                    d = !1;
            if (d) {
                var f = Cb()
                  , g = Bs({
                    xd: !0,
                    yd: !0,
                    Qf: !0
                });
                if (0 !== g.elements.length) {
                    for (var h = [], m = 0; m < g.elements.length; ++m) {
                        var n = g.elements[m];
                        h.push(n.querySelector + "*" + Cs(n) + "*" + n.type)
                    }
                    a.D[P.g.Ig] = h.join("~");
                    var p = g.Lh;
                    p && (a.D[P.g.Jg] = p.querySelector,
                    a.D[P.g.Hg] = Cs(p));
                    a.D[P.g.Gg] = String(Cb() - f);
                    a.D[P.g.Kg] = g.status
                }
            }
        }
    }
      , Wt = function(a) {
        if (a.eventName === P.g.Ra && !a.o.isGtmEvent) {
            if (!a.metadata.consent_updated && Et(a, "conversion")) {
                var b = U(a.o, P.g.Eb);
                if ("function" !== typeof b)
                    return;
                var c = String(U(a.o, P.g.qb))
                  , d = a.D[c]
                  , e = U(a.o, c);
                c === P.g.Sa || c === P.g.Cb ? er({
                    lk: c,
                    callback: b,
                    Rj: e
                }, a.metadata.cookie_options, a.metadata.redact_ads_data, vq) : b(d || e)
            }
            a.isAborted = !0
        }
    }
      , Xt = function(a) {
        if (Et(a, "conversion") && W(P.g.R) && (a.D[P.g.jb] || a.D[P.g.zc])) {
            var b = a.D[P.g.nb]
              , c = k(a.metadata.cookie_options)
              , d = Gp(c.prefix);
            c.prefix = "_gcl" === d ? "" : d;
            if (a.D[P.g.jb]) {
                var e = Xq(b, c);
                e && (a.D[P.g.Lg] = e)
            }
            if (a.D[P.g.zc]) {
                var f = Pq(b, c).Fl;
                f && (a.D[P.g.qg] = f)
            }
        }
    }
      , Yt = function(a) {
        var b = T(7), c = a.o, d, e, f;
        if (!b) {
            var g = tm(c, P.g.la);
            d = Lb(Xa(g) ? g : {})
        }
        var h = tm(c, P.g.la, 1)
          , m = tm(c, P.g.la, 2);
        e = Lb(Xa(h) ? h : {}, ".");
        f = Lb(Xa(m) ? m : {}, ".");
        b || (a.D[P.g.be] = d);
        a.D[P.g.rb] = e;
        a.D[P.g.ob] = f
    }
      , Zt = function(a) {
        if (Et(a, ["conversion", "remarketing"])) {
            var b = "conversion" === a.metadata.hit_type;
            b && a.eventName !== P.g.Ja || (a.copyToHitData(P.g.ia),
            b && (a.copyToHitData(P.g.Nd),
            a.copyToHitData(P.g.Ld),
            a.copyToHitData(P.g.Md),
            a.copyToHitData(P.g.Kd),
            a.D[P.g.eg] = a.eventName))
        }
    }
      , $t = function(a) {
        if (Et(a, ["conversion", "remarketing", "user_data_lead", "user_data_web"])) {
            var b = a.o;
            if (Et(a, ["conversion", "remarketing"])) {
                var c = U(b, P.g.Vb);
                if (!0 === c || !1 === c)
                    a.D[P.g.Vb] = c
            }
            yn(b) ? a.D[P.g.Mb] = !1 : (a.D[P.g.Mb] = !0,
            Et(a, "remarketing") && (a.isAborted = !0))
        }
    }
      , au = function(a) {
        Et(a, "conversion") && (a.copyToHitData(P.g.jd),
        a.copyToHitData(P.g.Od),
        a.copyToHitData(P.g.od),
        a.copyToHitData(P.g.Ud),
        a.copyToHitData(P.g.xc),
        a.copyToHitData(P.g.dd))
    }
      , bu = function(a) {
        Dr(a);
    }
      , cu = function(a) {
        if (Et(a, ["conversion", "remarketing"]) && G.__gsaExp && G.__gsaExp.id) {
            var b = G.__gsaExp.id;
            if (pb(b))
                try {
                    var c = Number(b());
                    isNaN(c) || (a.D[P.g.vg] = c)
                } catch (d) {}
        }
    }
      , du = function(a) {
        if (Et(a, ["conversion", "remarketing"])) {
            var b = Yq();
            void 0 !== b && (a.D[P.g.he] = b || "error");
            var c = sn();
            c && (a.D[P.g.Ac] = c);
            var d = qn();
            d && (a.D[P.g.Cc] = d)
        }
    }
      , eu = function(a) {
        Et(a, ["conversion"]) && "1" === Mo(!1)._up && (a.D[P.g.ae] = !0)
    }
      , fu = function(a) {
        Et(a, ["conversion"]) && (a.metadata.redact_click_ids = !!a.metadata.redact_ads_data && !W(At()))
    }
      , gu = function(a) {
        if (Et(a, ["conversion", "user_data_lead", "user_data_web"]) && W(P.g.R) && a.metadata.conversion_linker_enabled) {
            var b = a.metadata.cookie_options
              , c = Gp(b.prefix);
            "_gcl" === c && (c = "");
            if (T(27)) {
                var d = Rq(c);
                a.D[P.g.wi] = d.oh;
                a.D[P.g.xi] = d.qh
            }
            var e = T(51);
            if (W(P.g.P))
                if (Wq(c, e)) {
                    var f = e ? Vq(c) : Uq(c);
                    f && (a.D[P.g.jb] = f);
                    if (!c) {
                        var g = a.D[P.g.nb];
                        b = k(b);
                        b.prefix = c;
                        var h = Pq(g, b, !0).El;
                        h && (a.D[P.g.zc] = h)
                    }
                } else {
                    var m = Tq(c);
                    m && (a.D[P.g.Sa] = m);
                    if (!c) {
                        var n = Oq(Ap(zp()) ? kp() : {}, Mq);
                        n && (a.D[P.g.Yd] = n)
                    }
                }
        }
    }
      , hu = function(a) {
        if (Et(a, ["conversion", "remarketing", "user_data_lead", "user_data_web"]) && a.metadata.conversion_linker_enabled && W(P.g.R)) {
            var b = !T(3);
            if ("remarketing" !== a.metadata.hit_type || b) {
                var c = a.metadata.cookie_options;
                $o(c, "conversion" === a.metadata.hit_type && a.eventName !== P.g.Ra);
                W(P.g.P) && (a.D[P.g.Cb] = Yo[ap(c.prefix)])
            }
        }
    }
      , iu = function(a) {
        mj() || oj(a.o) || T(67) && Zs(void 0, Math.round(Cb()))
    }
      , ju = function() {}
      , ku = function(a) {
        if (Et(a, ["conversion"])) {
            var b = Gr(a.metadata.cookie_options);
            if (b && !a.D[P.g.Ca]) {
                var c = to(a.D[P.g.nb]);
                a.D[P.g.Ca] = c
            }
            b && (a.D[P.g.tb] = b,
            a.metadata.send_ccm_parallel_ping = !0)
        }
    }
      , lu = function(a) {
        var b = W(At());
        switch (a.metadata.hit_type) {
        case "user_data_lead":
        case "user_data_web":
            a.isAborted = !b || !!a.metadata.consent_updated;
            break;
        case "remarketing":
            a.isAborted = !b;
            break;
        case "conversion":
            a.metadata.consent_updated && (a.D[P.g.mc] = !0)
        }
    }
      , mu = function(a) {
        Et(a, ["conversion"]) && a.o.eventMetadata.is_external_event && (a.D[P.g.jj] = !0)
    }
      , nu = function(a) {
        if (!a.metadata.consent_updated && T(16) && Et(a, ["conversion"])) {
            var b = Iq();
            Hq(b) && (a.D[P.g.hd] = "1",
            a.metadata.add_tag_timing = !0)
        }
    }
      , ou = function(a) {
        var b;
        if ("gtag.config" !== a.eventName && a.metadata.send_user_data_hit)
            switch (a.metadata.hit_type) {
            case "user_data_web":
                b = 97;
                Dt(a);
                break;
            case "user_data_lead":
                b = 98;
                Dt(a);
                break;
            case "conversion":
                b = 99
            }
        !a.metadata.speculative && b && O(b);
        !0 === a.metadata.speculative && (a.isAborted = !0)
    }
      , pu = function(a) {
        T(14) && a.eventName === P.g.fa && Et(a, "page_view") && !a.metadata.consent_updated && !a.o.isGtmEvent ? Ar(a.target, a.o) : Et(a, "call_conversion") && (Ar(a.target, a.o),
        a.isAborted = !0)
    }
      , Mt = !1
      , Nt = !1;
    var ru = function(a, b) {
        var c = {}
          , d = function(f, g) {
            var h;
            h = !0 === g ? "1" : !1 === g ? "0" : encodeURIComponent(String(g));
            c[f] = h
        };
        z(a.D, function(f, g) {
            var h = qu[f];
            h && void 0 !== g && "" !== g && (!a.metadata.redact_click_ids || f !== P.g.Id && f !== P.g.Pd && f !== P.g.Ve && f !== P.g.dg || (g = "0"),
            d(h, g))
        });
        d("gtm", Un({
            za: a.metadata.source_canonical_id
        }));
        zn() && d("gcs", An());
        d("gcd", En(a.o));
        Qn() && d("dma_cps", Fn());
        d("dma", Pn());
        cn(ln()) && d("tcfd", Rn());
        Ai.m && d("tag_exp", Ai.m);
        if (a.metadata.add_tag_timing) {
            d("tft", Cb());
            var e = Lc();
            void 0 !== e && d("tfd", Math.round(e))
        }
        T(13) && d("apve", T(14) ? "1" : "0");
        b(c)
    }
      , su = function(a) {
        ru(a, function(b) {
            var c = [];
            z(b, function(f, g) {
                c.push(f + "=" + g)
            });
            var d;
            d = "page_view" === a.metadata.hit_type ? pj(W([P.g.R, P.g.P]) ? "https://www.google.com" : "https://pagead2.googlesyndication.com", !0) + "/ccm/collect" : void 0;
            var e = d + "?" + c.join("&");
            Gc(e);
            if (pb(a.o.onSuccess))
                a.o.onSuccess()
        })
    }
      , tu = {}
      , qu = (tu[P.g.mc] = "gcu",
    tu[P.g.jb] = "gclgb",
    tu[P.g.Sa] = "gclaw",
    tu[P.g.yi] = "gad_source",
    tu[P.g.Id] = "gclid",
    tu[P.g.zi] = "gclsrc",
    tu[P.g.dg] = "gbraid",
    tu[P.g.Ve] = "wbraid",
    tu[P.g.Cb] = "auid",
    tu[P.g.Bi] = "rnd",
    tu[P.g.Ei] = "ncl",
    tu[P.g.gg] = "gcldc",
    tu[P.g.Pd] = "dclid",
    tu[P.g.ob] = "edid",
    tu[P.g.fd] = "en",
    tu[P.g.Ac] = "gdpr",
    tu[P.g.rb] = "gdid",
    tu[P.g.Ri] = "gtm_up",
    tu[P.g.Fb] = "frm",
    tu[P.g.hd] = "lps",
    tu[P.g.be] = "did",
    tu[P.g.ya] = "dl",
    tu[P.g.Fa] = "dr",
    tu[P.g.Eg] = "ga_uid",
    tu[P.g.Cc] = "gdpr_consent",
    tu[P.g.Da] = "uid",
    tu[P.g.he] = "us_privacy",
    tu[P.g.Mb] = "npa",
    tu);
    var uu = {
        N: {
            Yh: "ads_conversion_hit",
            Gd: "container_execute_start",
            bi: "container_setup_end",
            Uf: "container_setup_start",
            Zh: "container_blocking_end",
            ai: "container_execute_end",
            di: "container_yield_end",
            Vf: "container_yield_start",
            bj: "event_execute_end",
            aj: "event_evaluation_end",
            Mg: "event_evaluation_start",
            cj: "event_setup_end",
            ie: "event_setup_start",
            ej: "ga4_conversion_hit",
            ke: "page_load",
            Bn: "pageview",
            ac: "snippet_load",
            xj: "tag_callback_error",
            yj: "tag_callback_failure",
            zj: "tag_callback_success",
            Aj: "tag_execute_end",
            sd: "tag_execute_start"
        }
    };
    function vu() {
        function a(c, d) {
            var e = mb(d);
            e && b.push([c, e])
        }
        var b = [];
        a("u", "GTM");
        a("ut", "TAGGING");
        a("h", "HEALTH");
        return b
    }
    ;var wu = !1;
    var ev = function(a, b) {}
      , fv = function(a, b) {}
      , gv = function(a, b) {}
      , hv = function(a, b) {}
      , iv = function() {
        var a = {};
        return a
    }
      , Wu = function(a) {
        a = void 0 === a ? !0 : a;
        var b = {};
        return b
    }
      , jv = function() {}
      , kv = function(a, b) {}
      , lv = function(a, b, c) {}
      , mv = function() {};
    function nv(a, b) {
        var c = G, d, e = c.GooglebQhCsO;
        e || (e = {},
        c.GooglebQhCsO = e);
        d = e;
        if (d[a])
            return !1;
        d[a] = [];
        d[a][0] = b;
        return !0
    }
    ;var ov = function(a, b, c) {
        var d = Wk(a, "fmt");
        if (b) {
            var e = Wk(a, "random")
              , f = Wk(a, "label") || "";
            if (!e)
                return !1;
            var g = ht(decodeURIComponent(f.replace(/\+/g, " ")) + ":" + decodeURIComponent(e.replace(/\+/g, " ")));
            if (!nv(g, b))
                return !1
        }
        d && 4 != d && (a = Yk(a, "rfmt", d));
        var h = Yk(a, "fmt", 4);
        wc(h, function() {
            G.google_noFurtherRedirects && b && b.call && (G.google_noFurtherRedirects = null,
            b())
        }, void 0, c, H.getElementsByTagName("script")[0].parentElement || void 0);
        return !0
    };
    var pv = function(a) {
        for (var b = {}, c = 0; c < a.length; c++) {
            var d = a[c]
              , e = void 0;
            if (d.hasOwnProperty("google_business_vertical")) {
                e = d.google_business_vertical;
                var f = {};
                b[e] = b[e] || (f.google_business_vertical = e,
                f)
            } else
                e = "",
                b.hasOwnProperty(e) || (b[e] = {});
            var g = b[e], h;
            for (h in d)
                "google_business_vertical" !== h && (h in g || (g[h] = []),
                g[h].push(d[h]))
        }
        return Object.keys(b).map(function(m) {
            return b[m]
        })
    }
      , rv = function(a) {
        if (!a || !a.length)
            return [];
        for (var b = [], c = 0; c < a.length; ++c) {
            var d = a[c];
            if (d) {
                var e = {};
                b.push((e.id = qv(d),
                e.origin = d.origin,
                e.destination = d.destination,
                e.start_date = d.start_date,
                e.end_date = d.end_date,
                e.location_id = d.location_id,
                e.google_business_vertical = d.google_business_vertical,
                e))
            }
        }
        return b
    }
      , sv = function(a) {
        if (!a || !a.length)
            return [];
        for (var b = [], c = 0; c < a.length; ++c) {
            var d = a[c];
            d && b.push({
                item_id: qv(d),
                quantity: d.quantity,
                value: d.price,
                start_date: d.start_date,
                end_date: d.end_date
            })
        }
        return b
    }
      , qv = function(a) {
        null != a.id && null != a.item_id && O(138);
        var b = a.id;
        T(12) && (null != a.item_id ? b = a.item_id : null == b && (b = a.item_name));
        return b
    }
      , uv = function(a) {
        if (!a)
            return "";
        for (var b = [], c = 0; c < a.length; c++) {
            var d = a[c]
              , e = [];
            d && (e.push(tv(d.value)),
            e.push(tv(d.quantity)),
            e.push(tv(d.item_id)),
            e.push(tv(d.start_date)),
            e.push(tv(d.end_date)),
            b.push("(" + e.join("*") + ")"))
        }
        return 0 < b.length ? b.join("") : ""
    }
      , tv = function(a) {
        return "number" !== typeof a && "string" !== typeof a ? "" : a.toString()
    }
      , wv = function(a, b) {
        var c = vv(b);
        return "" + a + (a && c ? ";" : "") + c
    }
      , vv = function(a) {
        if (!a || "object" !== typeof a || "function" === typeof a.join)
            return "";
        var b = [];
        z(a, function(c, d) {
            var e, f;
            if (Array.isArray(d)) {
                for (var g = [], h = 0; h < d.length; ++h) {
                    var m = xv(d[h]);
                    void 0 != m && g.push(m)
                }
                f = 0 !== g.length ? g.join(",") : void 0
            } else
                f = xv(d);
            e = f;
            var n = xv(c);
            n && void 0 != e && b.push(n + "=" + e)
        });
        return b.join(";")
    }
      , xv = function(a) {
        var b = typeof a;
        if (null != a && "object" !== b && "function" !== b)
            return String(a).replace(/,/g, "\\,").replace(/;/g, "\\;").replace(/=/g, "\\=")
    }
      , yv = function(a, b) {
        var c = []
          , d = function(f, g) {
            var h = !0 === $f[f];
            null == g || !h && "" === g || (!0 === g && (g = 1),
            !1 === g && (g = 0),
            c.push(f + "=" + encodeURIComponent(g)))
        }
          , e = a.metadata.hit_type;
        "conversion" !== e && "remarketing" !== e || d("random", a.metadata.event_start_timestamp_ms);
        z(b, d);
        return c.join("&")
    }
      , zv = function(a, b) {
        var c = a.metadata.hit_type, d = a.D[P.g.Xc], e = W([P.g.R, P.g.P]), f = [], g, h = a.o.onSuccess, m, n = Sn() ? 2 : 3, p = 0, q = function(A) {
            f.push(A);
            A.Ia && p++
        }, r = void 0;
        switch (c) {
        case "conversion":
            m = "/pagead/conversion";
            var t = "";
            e ? a.metadata.is_gcp_conversion ? (g = "https://www.google.com",
            m = "/pagead/1p-conversion",
            r = 8) : (g = "https://www.googleadservices.com",
            r = 5) : (g = "https://pagead2.googlesyndication.com",
            r = 6);
            a.metadata.is_gcp_conversion && (t = "&gcp=1&sscte=1&ct_cookie_present=1");
            var u = {
                La: "" + pj(g, !0) + m + "/" + d + "/?" + yv(a, b) + t,
                format: n,
                Ia: !0,
                endpoint: r
            };
            W(P.g.P) && (u.attributes = {
                attributionsrc: ""
            });
            q(u);
            a.metadata.send_ccm_parallel_ping && (r = a.metadata.is_gcp_conversion ? 23 : 22,
            q({
                La: "" + pj(g, !0) + "/ccm/conversion/" + d + "/?" + yv(a, b) + t,
                format: 2,
                Ia: !0,
                endpoint: r
            }));
            if (a.metadata.is_gcp_conversion) {
                t = "&gcp=1&ct_cookie_present=1";
                var v = e ? {
                    pk: "https://googleads.g.doubleclick.net",
                    endpoint: 9
                } : {
                    pk: g,
                    endpoint: void 0
                }
                  , w = v.endpoint;
                q({
                    La: "" + pj(v.pk) + "/pagead/viewthroughconversion/" + d + "/?" + yv(a, b) + t,
                    format: n,
                    Ia: !0,
                    endpoint: w
                })
            }
            break;
        case "remarketing":
            var y = b.data || ""
              , x = pv(rv(a.D[P.g.ia]));
            if (x.length) {
                for (var B = 0; B < x.length; B++)
                    b.data = wv(y, x[B]),
                    q({
                        La: "" + pj("https://googleads.g.doubleclick.net") + "/pagead/viewthroughconversion/" + d + "/?" + yv(a, b),
                        format: n,
                        Ia: !0,
                        endpoint: 9
                    }),
                    a.metadata.send_fledge_experiment && q({
                        La: "" + zt() + "/td/rul/" + d + "?" + yv(a, b),
                        format: 4,
                        Ia: !1,
                        endpoint: 44
                    }),
                    a.metadata.event_start_timestamp_ms += 1;
                a.metadata.send_fledge_experiment = !1
            } else
                q({
                    La: "" + pj("https://googleads.g.doubleclick.net") + "/pagead/viewthroughconversion/" + d + "/?" + yv(a, b),
                    format: n,
                    Ia: !0,
                    endpoint: 9
                });
            break;
        case "user_data_lead":
            q({
                La: "" + pj("https://google.com") + "/pagead/form-data/" + d + "?" + yv(a, b),
                format: 1,
                Ia: !0,
                endpoint: 21
            });
            break;
        case "user_data_web":
            q({
                La: "" + pj("https://google.com") + "/ccm/form-data/" + d + "?" + yv(a, b),
                format: 1,
                Ia: !0,
                endpoint: 11
            })
        }
        1 < f.length && pb(a.o.onSuccess) && (h = Mb(a.o.onSuccess, p));
        Sn() || "conversion" !== c && "remarketing" !== c || !a.metadata.send_fledge_experiment || (T(19) && "conversion" === c && (b.ct_cookie_present = 0),
        q({
            La: "" + zt() + "/td/rul/" + d + "?" + yv(a, b),
            format: 4,
            Ia: !1,
            endpoint: 44
        }));
        return {
            onSuccess: h,
            Wl: f
        }
    }
      , Av = function(a, b, c, d, e, f, g) {
        fv(c.o.eventId, c.eventName);
        var h = function() {
            e && e()
        };
        switch (b) {
        case 1:
            Gc(a);
            e && e();
            break;
        case 2:
            zc(a, h, void 0, f);
            break;
        case 3:
            var m = !1;
            try {
                m = ov(a, h, f)
            } catch (q) {
                m = !1
            }
            m || Av(a, 2, c, d, h, f, g);
            break;
        case 4:
            var n = "AW-" + c.D[P.g.Xc]
              , p = c.D[P.g.nb];
            p && (n = n + "/" + p);
            wt(a, n)
        }
    }
      , Bv = {}
      , Cv = (Bv[P.g.mc] = "gcu",
    Bv[P.g.jb] = "gclgb",
    Bv[P.g.Sa] = "gclaw",
    Bv[P.g.wi] = "gclgs",
    Bv[P.g.xi] = "gclst",
    Bv[P.g.Cb] = "auid",
    Bv[P.g.Kd] = "dscnt",
    Bv[P.g.Ld] = "fcntr",
    Bv[P.g.Md] = "flng",
    Bv[P.g.Nd] = "mid",
    Bv[P.g.eg] = "bttype",
    Bv[P.g.nb] = "label",
    Bv[P.g.Sb] = "capi",
    Bv[P.g.Ze] = "pscdl",
    Bv[P.g.Ba] = "currency_code",
    Bv[P.g.Od] = "vdltv",
    Bv[P.g.Fi] = "_dbg",
    Bv[P.g.Ud] = "oedeld",
    Bv[P.g.ob] = "edid",
    Bv[P.g.Ki] = "fdr",
    Bv[P.g.lg] = "fledge",
    Bv[P.g.Yd] = "gac",
    Bv[P.g.zc] = "gacgb",
    Bv[P.g.qg] = "gacmcov",
    Bv[P.g.Ac] = "gdpr",
    Bv[P.g.rb] = "gdid",
    Bv[P.g.vg] = "gsaexp",
    Bv[P.g.Fb] = "frm",
    Bv[P.g.ae] = "gtm_up",
    Bv[P.g.hd] = "lps",
    Bv[P.g.be] = "did",
    Bv[P.g.jd] = void 0,
    Bv[P.g.Ib] = "tiba",
    Bv[P.g.Vb] = "rdp",
    Bv[P.g.tb] = "ecsid",
    Bv[P.g.Eg] = "ga_uid",
    Bv[P.g.od] = "delopc",
    Bv[P.g.Cc] = "gdpr_consent",
    Bv[P.g.Ca] = "oid",
    Bv[P.g.qf] = "uaa",
    Bv[P.g.rf] = "uab",
    Bv[P.g.tf] = "uafvl",
    Bv[P.g.uf] = "uamb",
    Bv[P.g.vf] = "uam",
    Bv[P.g.wf] = "uap",
    Bv[P.g.xf] = "uapv",
    Bv[P.g.yf] = "uaw",
    Bv[P.g.Gg] = "ec_lat",
    Bv[P.g.Hg] = "ec_meta",
    Bv[P.g.Ig] = "ec_m",
    Bv[P.g.Jg] = "ec_sel",
    Bv[P.g.Kg] = "ec_s",
    Bv[P.g.pd] = "ec_mode",
    Bv[P.g.Da] = "userId",
    Bv[P.g.he] = "us_privacy",
    Bv[P.g.qa] = "value",
    Bv[P.g.Lg] = "mcov",
    Bv[P.g.ij] = "hn",
    Bv[P.g.jj] = "gtm_ee",
    Bv[P.g.Mb] = "npa",
    Bv[P.g.Xc] = null,
    Bv[P.g.Jb] = null,
    Bv[P.g.Pa] = null,
    Bv[P.g.ia] = null,
    Bv[P.g.ya] = null,
    Bv[P.g.Fa] = null,
    Bv[P.g.nf] = null,
    Bv)
      , Ev = function(a) {
        "page_view" === a.metadata.hit_type ? su(a) : Dv(a, function(b, c) {
            for (var d = zv(a, b), e = d.onSuccess, f = d.Wl, g = {}, h = 0; h < f.length; g = {
                La: void 0,
                mh: void 0,
                Ia: void 0,
                Wg: void 0,
                ih: void 0
            },
            h++) {
                var m = f[h];
                g.La = m.La;
                g.mh = m.format;
                g.Ia = m.Ia;
                g.Wg = m.attributes;
                g.ih = m.endpoint;
                var n = void 0;
                if (null != (n = c) && n.Sm) {
                    var p = function(u) {
                        return function(v) {
                            Lh(c.qm, function(w) {
                                var y = Bh(w)
                                  , x = u.La;
                                if (v) {
                                    var B = Un({
                                        za: a.metadata.source_canonical_id,
                                        gk: v
                                    });
                                    x = x.replace(b.gtm, B)
                                }
                                Av(x + "&em=" + encodeURIComponent(y.Tj), u.mh, a, b, u.Ia ? e : void 0, u.Wg, u.ih)
                            })
                        }
                    }(g)
                      , q = c
                      , r = q.Th
                      , t = "" + g.La + q.Xm.join("");
                    at(t, r, g.Ia && e ? e : function() {}
                    , p)
                } else
                    Av(g.La, g.mh, a, b, g.Ia ? e : void 0, g.Wg, g.ih)
            }
        })
    }
      , Dv = function(a, b) {
        var c = a.metadata.hit_type, d = {}, e = {}, f, g = [], h = a.metadata.event_start_timestamp_ms;
        if ("conversion" === c || "remarketing" === c)
            d.cv = "11",
            d.fst = h,
            d.fmt = 3,
            d.bg = "ffffff",
            d.guid = "ON",
            d.async = "1";
        var m = dq(["aw", "dc"]);
        null != m && (d.gad_source = m);
        d.gtm = Un({
            za: a.metadata.source_canonical_id
        });
        "remarketing" !== c && zn() && (d.gcs = An());
        d.gcd = En(a.o);
        Qn() && (d.dma_cps = Fn());
        d.dma = Pn();
        cn(ln()) && (d.tcfd = Rn());
        Ai.m && (d.tag_exp = Ai.m);
        if (a.D[P.g.Jb]) {
            var n = a.D[P.g.Jb].split("x");
            2 === n.length && (d.u_w = n[0],
            d.u_h = n[1])
        }
        if (a.D[P.g.Pa]) {
            var p = a.D[P.g.Pa];
            2 === p.length ? d.hl = p : 5 === p.length && (d.hl = p.substring(0, 2),
            d.gl = p.substring(3, 5))
        }
        var q = a.metadata.redact_click_ids
          , r = function(C, F) {
            var L = a.D[F];
            L && (d[C] = q ? ij(L) : L)
        };
        r("url", P.g.ya);
        r("ref", P.g.Fa);
        r("top", P.g.nf);
        z(a.D, function(C, F) {
            if (Cv.hasOwnProperty(C)) {
                var L = Cv[C];
                L && (d[L] = F)
            } else
                e[C] = F
        });
        var t = a.D[P.g.jd];
        void 0 != t && "" !== t && (d.vdnc = String(t));
        var u = a.D[P.g.dd];
        void 0 !== u && (d.shf = u);
        var v = a.D[P.g.xc];
        void 0 !== v && (d.delc = v);
        if (T(16) && a.metadata.add_tag_timing) {
            d.tft = Cb();
            var w = Lc();
            void 0 !== w && (d.tfd = Math.round(w))
        }
        d.data = vv(e);
        var y = a.D[P.g.ia];
        y && "conversion" === c && (d.iedeld = kr(y),
        d.item = uv(sv(y)));
        if (("conversion" === c || "user_data_lead" === c || "user_data_web" === c) && a.metadata.user_data)
            if (!W(P.g.P) || T(11) && !W(P.g.R))
                d.ec_mode = void 0;
            else {
                var x = function() {
                    if ("user_data_web" === c) {
                        var C;
                        var F = a.metadata.cookie_options;
                        F = F || {};
                        var L;
                        if (W(Fr)) {
                            (L = Gr(F)) || (L = to());
                            var N = F
                              , Q = ap(N.prefix);
                            cp(N, L);
                            delete Yo[Q];
                            delete Zo[Q];
                            bp(Q, N.path, N.domain);
                            C = Gr(F)
                        } else
                            C = void 0;
                        d.ecsid = C
                    }
                };
                if ("conversion" !== c && T(67)) {
                    d.gtm = Un({
                        za: a.metadata.source_canonical_id,
                        gk: 3
                    });
                    var B = Kh(a.metadata.user_data)
                      , A = yh(B)
                      , D = A.hn;
                    f = {
                        Sm: !0,
                        Th: A.Th,
                        Xm: ["&em=" + A.Wm],
                        qm: B
                    };
                    0 < D && x()
                } else {
                    var E = Ah(a.metadata.user_data);
                    E && g.push(E.then(function(C) {
                        d.em = C.Sj;
                        0 < C.Kh && x();
                        if (T(58) && d.em) {
                            d._is_ee = 1;
                            var F = void 0;
                            return F
                        }
                        T(57) && (d._is_ee = 0,
                        d._es = 0)
                    }))
                }
            }
        if (g.length)
            try {
                Promise.all(g).then(function() {
                    b(d)
                });
                return
            } catch (C) {}
        b(d, f)
    };
    function Fv(a, b) {
        if (data.entities) {
            var c = data.entities[a];
            if (c)
                return c[b]
        }
    }
    ;function Gv(a, b, c) {
        c = void 0 === c ? !1 : c;
        Hv().addRestriction(0, a, b, c)
    }
    function Iv(a, b, c) {
        c = void 0 === c ? !1 : c;
        Hv().addRestriction(1, a, b, c)
    }
    function Jv() {
        var a = Ej();
        return Hv().getRestrictions(1, a)
    }
    var Kv = function() {
        this.m = {};
        this.F = {}
    }
      , Lv = function(a, b) {
        var c = a.m[b];
        c || (c = {
            _entity: {
                internal: [],
                external: []
            },
            _event: {
                internal: [],
                external: []
            }
        },
        a.m[b] = c);
        return c
    };
    Kv.prototype.addRestriction = function(a, b, c, d) {
        d = void 0 === d ? !1 : d;
        if (!d || !this.F[b]) {
            var e = Lv(this, b);
            0 === a ? d ? e._entity.external.push(c) : e._entity.internal.push(c) : 1 === a && (d ? e._event.external.push(c) : e._event.internal.push(c))
        }
    }
    ;
    Kv.prototype.getRestrictions = function(a, b) {
        var c = Lv(this, b);
        if (0 === a) {
            var d, e;
            return [].concat(qa((null == c ? void 0 : null == (d = c._entity) ? void 0 : d.internal) || []), qa((null == c ? void 0 : null == (e = c._entity) ? void 0 : e.external) || []))
        }
        if (1 === a) {
            var f, g;
            return [].concat(qa((null == c ? void 0 : null == (f = c._event) ? void 0 : f.internal) || []), qa((null == c ? void 0 : null == (g = c._event) ? void 0 : g.external) || []))
        }
        return []
    }
    ;
    Kv.prototype.getExternalRestrictions = function(a, b) {
        var c = Lv(this, b), d, e;
        return 0 === a ? (null == c ? void 0 : null == (d = c._entity) ? void 0 : d.external) || [] : (null == c ? void 0 : null == (e = c._event) ? void 0 : e.external) || []
    }
    ;
    Kv.prototype.removeExternalRestrictions = function(a) {
        var b = Lv(this, a);
        b._event && (b._event.external = []);
        b._entity && (b._entity.external = []);
        this.F[a] = !0
    }
    ;
    function Hv() {
        var a = ii.r;
        a || (a = new Kv,
        ii.r = a);
        return a
    }
    ;var Mv = new RegExp(/^(.*\.)?(google|youtube|blogger|withgoogle)(\.com?)?(\.[a-z]{2})?\.?$/)
      , Nv = {
        cl: ["ecl"],
        customPixels: ["nonGooglePixels"],
        ecl: ["cl"],
        ehl: ["hl"],
        gaawc: ["googtag"],
        hl: ["ehl"],
        html: ["customScripts", "customPixels", "nonGooglePixels", "nonGoogleScripts", "nonGoogleIframes"],
        customScripts: ["html", "customPixels", "nonGooglePixels", "nonGoogleScripts", "nonGoogleIframes"],
        nonGooglePixels: [],
        nonGoogleScripts: ["nonGooglePixels"],
        nonGoogleIframes: ["nonGooglePixels"]
    }
      , Ov = {
        cl: ["ecl"],
        customPixels: ["customScripts", "html"],
        ecl: ["cl"],
        ehl: ["hl"],
        gaawc: ["googtag"],
        hl: ["ehl"],
        html: ["customScripts"],
        customScripts: ["html"],
        nonGooglePixels: ["customPixels", "customScripts", "html", "nonGoogleScripts", "nonGoogleIframes"],
        nonGoogleScripts: ["customScripts", "html"],
        nonGoogleIframes: ["customScripts", "html", "nonGoogleScripts"]
    }
      , Pv = "google customPixels customScripts html nonGooglePixels nonGoogleScripts nonGoogleIframes".split(" ");
    function Qv() {
        var a = Hi("gtm.allowlist") || Hi("gtm.whitelist");
        a && O(9);
        ni && (a = ["google", "gtagfl", "lcl", "zone"]);
        Mv.test(G.location && G.location.hostname) && (ni ? O(116) : (O(117),
        Rv && (a = [],
        window.console && window.console.log && window.console.log("GTM blocked. See go/13687728."))));
        var b = a && Gb(zb(a), Nv)
          , c = Hi("gtm.blocklist") || Hi("gtm.blacklist");
        c || (c = Hi("tagTypeBlacklist")) && O(3);
        c ? O(8) : c = [];
        Mv.test(G.location && G.location.hostname) && (c = zb(c),
        c.push("nonGooglePixels", "nonGoogleScripts", "sandboxedScripts"));
        0 <= zb(c).indexOf("google") && O(2);
        var d = c && Gb(zb(c), Ov)
          , e = {};
        return function(f) {
            var g = f && f[Ce.ra];
            if (!g || "string" !== typeof g)
                return !0;
            g = g.replace(/^_*/, "");
            if (void 0 !== e[g])
                return e[g];
            var h = xi[g] || []
              , m = !0;
            if (a) {
                var n;
                if (n = m)
                    a: {
                        if (0 > b.indexOf(g))
                            if (h && 0 < h.length)
                                for (var p = 0; p < h.length; p++) {
                                    if (0 > b.indexOf(h[p])) {
                                        O(11);
                                        n = !1;
                                        break a
                                    }
                                }
                            else {
                                n = !1;
                                break a
                            }
                        n = !0
                    }
                m = n
            }
            var q = !1;
            if (c) {
                var r = 0 <= d.indexOf(g);
                if (r)
                    q = r;
                else {
                    var t = ub(d, h || []);
                    t && O(10);
                    q = t
                }
            }
            var u = !m || q;
            u || !(0 <= h.indexOf("sandboxedScripts")) || b && -1 !== b.indexOf("sandboxedScripts") || (u = ub(d, Pv));
            return e[g] = u
        }
    }
    var Rv = !1;
    Rv = !0;
    function Sv() {
        wj && Gv(Ej(), function(a) {
            var b = nf(a.entityId), c;
            if (sf(b)) {
                var d = b[Ce.ra];
                if (!d)
                    throw "Error: No function name given for function call.";
                var e = ef[d];
                c = !!e && !!e.runInSiloedMode
            } else
                c = !!Fv(b[Ce.ra], 4);
            return c
        })
    }
    var Uv = function(a, b, c, d, e) {
        if (!Tv()) {
            var f = d.siloed ? zj(a) : a;
            if (!Tj(f)) {
                var g = "?id=" + encodeURIComponent(a) + "&l=" + hi.Ya
                  , h = 0 === a.indexOf("GTM-");
                h || (g += "&cx=c");
                T(54) && (g += "&gtm=" + Un());
                var m = nj();
                m && (g += "&sign=" + hi.Ef);
                var n = c ? "/gtag/js" : "/gtm.js"
                  , p = mj() ? lj(b, n + g) : void 0;
                if (!p) {
                    var q = hi.Hd + n;
                    m && qc && h ? (q = qc.replace(/^(?:https?:\/\/)?/i, "").split(/[?#]/)[0],
                    p = or("https://", "http://", q + g)) : p = Ai.F ? Bi() + n + g : or("https://", "http://", q + g)
                }
                d.siloed && Vj({
                    ctid: f,
                    isDestination: !1
                });
                var r = Hj();
                sj().container[f] = {
                    state: 1,
                    context: d,
                    parent: r
                };
                tj({
                    ctid: f,
                    isDestination: !1
                }, e);
                wc(p)
            }
        }
    }
      , Vv = function(a, b, c, d) {
        if (!Tv()) {
            var e = c.siloed ? zj(a) : a;
            if (!Uj(e))
                if (!c.siloed && Wj())
                    sj().destination[e] = {
                        state: 0,
                        transportUrl: b,
                        context: c,
                        parent: Hj()
                    },
                    tj({
                        ctid: e,
                        isDestination: !0
                    }, d),
                    O(91);
                else {
                    var f = "/gtag/destination?id=" + encodeURIComponent(a) + "&l=" + hi.Ya + "&cx=c";
                    T(54) && (f += "&gtm=" + Un());
                    nj() && (f += "&sign=" + hi.Ef);
                    var g = mj() ? lj(b, f) : void 0;
                    g || (g = Ai.F ? Bi() + f : or("https://", "http://", hi.Hd + f));
                    c.siloed && Vj({
                        ctid: e,
                        isDestination: !0
                    });
                    sj().destination[e] = {
                        state: 1,
                        context: c,
                        parent: Hj()
                    };
                    tj({
                        ctid: e,
                        isDestination: !0
                    }, d);
                    wc(g)
                }
        }
    };
    function Tv() {
        if (Sn()) {
            return !0
        }
        return !1
    }
    ;var Wv = !1
      , Xv = 0
      , Yv = [];
    function Zv(a) {
        if (!Wv) {
            var b = H.createEventObject
              , c = "complete" === H.readyState
              , d = "interactive" === H.readyState;
            if (!a || "readystatechange" !== a.type || c || !b && d) {
                Wv = !0;
                for (var e = 0; e < Yv.length; e++)
                    I(Yv[e])
            }
            Yv.push = function() {
                for (var f = za.apply(0, arguments), g = 0; g < f.length; g++)
                    I(f[g]);
                return 0
            }
        }
    }
    function $v() {
        if (!Wv && 140 > Xv) {
            Xv++;
            try {
                var a, b;
                null == (b = (a = H.documentElement).doScroll) || b.call(a, "left");
                Zv()
            } catch (c) {
                G.setTimeout($v, 50)
            }
        }
    }
    function aw(a) {
        Wv ? a() : Yv.push(a)
    }
    ;function cw(a, b, c) {
        return {
            entityType: a,
            indexInOriginContainer: b,
            nameInOriginContainer: c,
            originContainerId: Cj()
        }
    }
    ;var ew = function(a, b) {
        this.m = !1;
        this.M = [];
        this.eventData = {
            tags: []
        };
        this.T = !1;
        this.F = this.H = 0;
        dw(this, a, b)
    }
      , fw = function(a, b, c, d) {
        if (ki.hasOwnProperty(b) || "__zone" === b)
            return -1;
        var e = {};
        Xa(d) && (e = k(d, e));
        e.id = c;
        e.status = "timeout";
        return a.eventData.tags.push(e) - 1
    }
      , gw = function(a, b, c, d) {
        var e = a.eventData.tags[b];
        e && (e.status = c,
        e.executionTime = d)
    }
      , hw = function(a) {
        if (!a.m) {
            for (var b = a.M, c = 0; c < b.length; c++)
                b[c]();
            a.m = !0;
            a.M.length = 0
        }
    }
      , dw = function(a, b, c) {
        void 0 !== b && a.qe(b);
        c && G.setTimeout(function() {
            hw(a)
        }, Number(c))
    };
    ew.prototype.qe = function(a) {
        var b = this
          , c = Eb(function() {
            I(function() {
                a(Cj(), b.eventData)
            })
        });
        this.m ? c() : this.M.push(c)
    }
    ;
    var iw = function(a) {
        a.H++;
        return Eb(function() {
            a.F++;
            a.T && a.F >= a.H && hw(a)
        })
    }
      , jw = function(a) {
        a.T = !0;
        a.F >= a.H && hw(a)
    };
    var kw = {}
      , mw = function() {
        return G[lw()]
    };
    var nw = function(a) {
        G.GoogleAnalyticsObject || (G.GoogleAnalyticsObject = a || "ga");
        var b = G.GoogleAnalyticsObject;
        if (G[b])
            G.hasOwnProperty(b);
        else {
            var c = function() {
                c.q = c.q || [];
                c.q.push(arguments)
            };
            c.l = Number(Bb());
            G[b] = c
        }
        return G[b]
    }
      , ow = function(a) {
        if (Jl()) {
            var b = mw();
            b(a + "require", "linker");
            b(a + "linker:passthrough", !0)
        }
    };
    function lw() {
        return G.GoogleAnalyticsObject || "ga"
    }
    var pw = function() {
        var a = Cj();
    }
      , qw = function(a, b) {
        return function() {
            var c = mw()
              , d = c && c.getByName && c.getByName(a);
            if (d) {
                var e = d.get("sendHitTask");
                d.set("sendHitTask", function(f) {
                    var g = f.get("hitPayload")
                      , h = f.get("hitCallback")
                      , m = 0 > g.indexOf("&tid=" + b);
                    m && (f.set("hitPayload", g.replace(/&tid=UA-[0-9]+-[0-9]+/, "&tid=" + b), !0),
                    f.set("hitCallback", void 0, !0));
                    e(f);
                    m && (f.set("hitPayload", g, !0),
                    f.set("hitCallback", h, !0),
                    f.set("_x_19", void 0, !0),
                    e(f))
                })
            }
        }
    };
    var Ww = ["es", "1"]
      , Xw = {}
      , Yw = {};
    function Zw(a, b) {
        if (jk) {
            var c;
            c = b.match(/^(gtm|gtag)\./) ? encodeURIComponent(b) : "*";
            Xw[a] = [["e", c], ["eid", a]];
            uk(a)
        }
    }
    function $w(a) {
        var b = a.eventId
          , c = a.Xa;
        if (!Xw[b])
            return [];
        var d = [];
        Yw[b] || d.push(Ww);
        d.push.apply(d, qa(Xw[b]));
        c && (Yw[b] = !0);
        return d
    }
    ;var ax = {}
      , bx = {}
      , cx = {};
    function dx(a, b, c, d) {
        jk && T(63) && ((void 0 === d ? 0 : d) ? (cx[b] = cx[b] || 0,
        ++cx[b]) : void 0 !== c ? (bx[a] = bx[a] || {},
        bx[a][b] = Math.round(c)) : (ax[a] = ax[a] || {},
        ax[a][b] = (ax[a][b] || 0) + 1))
    }
    function ex(a) {
        var b = a.eventId, c = a.Xa, d = ax[b] || {}, e = [], f;
        for (f in d)
            d.hasOwnProperty(f) && e.push("" + f + d[f]);
        c && delete ax[b];
        return e.length ? [["md", e.join(".")]] : []
    }
    function fx(a) {
        var b = a.eventId, c = a.Xa, d = bx[b] || {}, e = [], f;
        for (f in d)
            d.hasOwnProperty(f) && e.push("" + f + d[f]);
        c && delete bx[b];
        return e.length ? [["mtd", e.join(".")]] : []
    }
    function gx() {
        for (var a = [], b = na(Object.keys(cx)), c = b.next(); !c.done; c = b.next()) {
            var d = c.value;
            a.push("" + d + cx[d])
        }
        return a.length ? [["mec", a.join(".")]] : []
    }
    ;var hx = {}
      , ix = {};
    function jx(a, b, c) {
        if (jk && b) {
            var d = qj(b);
            hx[a] = hx[a] || [];
            hx[a].push(c + d);
            var e = (sf(b) ? "1" : "2") + d;
            ix[a] = ix[a] || [];
            ix[a].push(e);
            uk(a)
        }
    }
    function kx(a) {
        var b = a.eventId
          , c = a.Xa
          , d = []
          , e = hx[b] || [];
        e.length && d.push(["tr", e.join(".")]);
        var f = ix[b] || [];
        f.length && d.push(["ti", f.join(".")]);
        c && (delete hx[b],
        delete ix[b]);
        return d
    }
    ;function lx(a, b, c, d) {
        var e = cf[a]
          , f = mx(a, b, c, d);
        if (!f)
            return null;
        var g = pf(e[Ce.vj], c, []);
        if (g && g.length) {
            var h = g[0];
            f = lx(h.index, {
                onSuccess: f,
                onFailure: 1 === h.Lj ? b.terminate : f,
                terminate: b.terminate
            }, c, d)
        }
        return f
    }
    function mx(a, b, c, d) {
        function e() {
            if (f[Ce.Rk])
                h();
            else {
                var w = qf(f, c, [])
                  , y = w[Ce.rk];
                if (null != y)
                    for (var x = 0; x < y.length; x++)
                        if (!W(y[x])) {
                            h();
                            return
                        }
                var B = fw(c.bc, String(f[Ce.ra]), Number(f[Ce.pe]), w[Ce.Sk])
                  , A = !1;
                w.vtp_gtmOnSuccess = function() {
                    if (!A) {
                        A = !0;
                        var C = Cb() - E;
                        jx(c.id, cf[a], "5");
                        gw(c.bc, B, "success", C);
                        T(55) && lv(c, f, uu.N.zj);
                        g()
                    }
                }
                ;
                w.vtp_gtmOnFailure = function() {
                    if (!A) {
                        A = !0;
                        var C = Cb() - E;
                        jx(c.id, cf[a], "6");
                        gw(c.bc, B, "failure", C);
                        T(55) && lv(c, f, uu.N.yj);
                        h()
                    }
                }
                ;
                w.vtp_gtmTagId = f.tag_id;
                w.vtp_gtmEventId = c.id;
                c.priorityId && (w.vtp_gtmPriorityId = c.priorityId);
                jx(c.id, f, "1");
                var D = function() {
                    nl(3);
                    var C = Cb() - E;
                    jx(c.id, f, "7");
                    gw(c.bc, B, "exception", C);
                    T(55) && lv(c, f, uu.N.xj);
                    A || (A = !0,
                    h())
                };
                T(55) && kv(c, f);
                var E = Cb();
                try {
                    of(w, {
                        event: c,
                        index: a,
                        type: 1
                    })
                } catch (C) {
                    D(C)
                }
                T(55) && lv(c, f, uu.N.Aj)
            }
        }
        var f = cf[a]
          , g = b.onSuccess
          , h = b.onFailure
          , m = b.terminate;
        if (c.isBlocked(f))
            return null;
        var n = pf(f[Ce.Bj], c, []);
        if (n && n.length) {
            var p = n[0]
              , q = lx(p.index, {
                onSuccess: g,
                onFailure: h,
                terminate: m
            }, c, d);
            if (!q)
                return null;
            g = q;
            h = 2 === p.Lj ? m : q
        }
        if (f[Ce.oj] || f[Ce.Uk]) {
            var r = f[Ce.oj] ? df : c.Um
              , t = g
              , u = h;
            if (!r[a]) {
                e = Eb(e);
                var v = nx(a, r, e);
                g = v.onSuccess;
                h = v.onFailure
            }
            return function() {
                r[a](t, u)
            }
        }
        return e
    }
    function nx(a, b, c) {
        var d = []
          , e = [];
        b[a] = ox(d, e, c);
        return {
            onSuccess: function() {
                b[a] = px;
                for (var f = 0; f < d.length; f++)
                    d[f]()
            },
            onFailure: function() {
                b[a] = qx;
                for (var f = 0; f < e.length; f++)
                    e[f]()
            }
        }
    }
    function ox(a, b, c) {
        return function(d, e) {
            a.push(d);
            b.push(e);
            c()
        }
    }
    function px(a) {
        a()
    }
    function qx(a, b) {
        b()
    }
    ;var tx = function(a, b) {
        for (var c = [], d = 0; d < cf.length; d++)
            if (a[d]) {
                var e = cf[d];
                var f = iw(b.bc);
                try {
                    var g = lx(d, {
                        onSuccess: f,
                        onFailure: f,
                        terminate: f
                    }, b, d);
                    if (g) {
                        var h = e[Ce.ra];
                        if (!h)
                            throw "Error: No function name given for function call.";
                        var m = ef[h];
                        c.push({
                            ik: d,
                            Xj: (m ? m.priorityOverride || 0 : 0) || Fv(e[Ce.ra], 1) || 0,
                            execute: g
                        })
                    } else
                        rx(d, b),
                        f()
                } catch (p) {
                    f()
                }
            }
        c.sort(sx);
        for (var n = 0; n < c.length; n++)
            c[n].execute();
        return 0 < c.length
    };
    function sx(a, b) {
        var c, d = b.Xj, e = a.Xj;
        c = d > e ? 1 : d < e ? -1 : 0;
        var f;
        if (0 !== c)
            f = c;
        else {
            var g = a.ik
              , h = b.ik;
            f = g > h ? 1 : g < h ? -1 : 0
        }
        return f
    }
    function rx(a, b) {
        if (jk) {
            var c = function(d) {
                var e = b.isBlocked(cf[d]) ? "3" : "4"
                  , f = pf(cf[d][Ce.vj], b, []);
                f && f.length && c(f[0].index);
                jx(b.id, cf[d], e);
                var g = pf(cf[d][Ce.Bj], b, []);
                g && g.length && c(g[0].index)
            };
            c(a)
        }
    }
    var wx = !1, ux;
    var Cx = function(a) {
        var b = a["gtm.uniqueEventId"]
          , c = a["gtm.priorityId"]
          , d = a.event;
        if (T(55)) {}
        if ("gtm.js" === d) {
            if (wx)
                return !1;
            wx = !0
        }
        var e = !1
          , f = Jv()
          , g = k(a);
        if (!f.every(function(t) {
            return t({
                originalEventData: g
            })
        })) {
            if ("gtm.js" !== d && "gtm.init" !== d && "gtm.init_consent" !== d)
                return !1;
            e = !0
        }
        Zw(b, d);
        var h = a.eventCallback
          , m = a.eventTimeout
          , n = {
            id: b,
            priorityId: c,
            name: d,
            isBlocked: yx(g, e),
            Um: [],
            logMacroError: function() {
                O(6);
                nl(0)
            },
            cachedModelValues: zx(),
            bc: new ew(function() {
                if (T(55)) {}
                h && h.apply(h, [].slice.call(arguments, 0))
            }
            ,m),
            originalEventData: g
        };
        T(63) && jk && (n.reportMacroDiscrepancy = dx);
        T(55) && gv(n.id, n.name);
        var p = Af(n);
        T(55) && hv(n.id, n.name);
        e && (p = Ax(p));
        if (T(55)) {}
        var q = tx(p, n)
          , r = !1;
        jw(n.bc);
        "gtm.js" !== d && "gtm.sync" !== d || pw();
        return Bx(p, q) || r
    };
    function zx() {
        var a = {};
        a.event = Mi("event", 1);
        a.ecommerce = Mi("ecommerce", 1);
        a.gtm = Mi("gtm");
        a.eventModel = Mi("eventModel");
        return a
    }
    function yx(a, b) {
        var c = Qv();
        return function(d) {
            if (c(d))
                return !0;
            var e = d && d[Ce.ra];
            if (!e || "string" != typeof e)
                return !0;
            e = e.replace(/^_*/, "");
            var f, g = Ej();
            f = Hv().getRestrictions(0, g);
            var h = a;
            b && (h = k(a),
            h["gtm.uniqueEventId"] = Number.MAX_SAFE_INTEGER);
            for (var m = xi[e] || [], n = na(f), p = n.next(); !p.done; p = n.next()) {
                var q = p.value;
                try {
                    if (!q({
                        entityId: e,
                        securityGroups: m,
                        originalEventData: h
                    }))
                        return !0
                } catch (r) {
                    return !0
                }
            }
            return !1
        }
    }
    function Ax(a) {
        for (var b = [], c = 0; c < a.length; c++)
            if (a[c]) {
                var d = String(cf[c][Ce.ra]);
                if (ji[d] || void 0 !== cf[c][Ce.Vk] || Fv(d, 2))
                    b[c] = !0
            }
        return b
    }
    function Bx(a, b) {
        if (!b)
            return b;
        for (var c = 0; c < a.length; c++)
            if (a[c] && cf[c] && !ki[String(cf[c][Ce.ra])])
                return !0;
        return !1
    }
    var Dx = 0;
    function Ex() {
        if (1 === Dx && jk) {
            var a = qk(!0, !0, !0, !0);
            fk && (T(23) || (a = a.replace("/a?", "/td?")),
            Jc(a),
            fk = !1)
        }
    }
    var Fx = function(a) {
        if (!a.Kj || 1 !== Dx)
            return [];
        a.Nc();
        var b = hl();
        b.push(["mcc", "1"]);
        Dx = 3;
        return b
    };
    function Gx(a, b) {
        return 1 === arguments.length ? Hx("set", a) : Hx("set", a, b)
    }
    function Ix(a, b) {
        return 1 === arguments.length ? Hx("config", a) : Hx("config", a, b)
    }
    function Jx(a, b, c) {
        c = c || {};
        c[P.g.Wb] = a;
        return Hx("event", b, c)
    }
    function Hx() {
        return arguments
    }
    ;var Kx = function() {
        this.messages = [];
        this.m = []
    };
    Kx.prototype.enqueue = function(a, b, c) {
        var d = this.messages.length + 1;
        a["gtm.uniqueEventId"] = b;
        a["gtm.priorityId"] = d;
        var e = Object.assign({}, c, {
            eventId: b,
            priorityId: d,
            fromContainerExecution: !0
        })
          , f = {
            message: a,
            notBeforeEventId: b,
            priorityId: d,
            messageContext: e
        };
        this.messages.push(f);
        for (var g = 0; g < this.m.length; g++)
            try {
                this.m[g](f)
            } catch (h) {}
    }
    ;
    Kx.prototype.listen = function(a) {
        this.m.push(a)
    }
    ;
    Kx.prototype.get = function() {
        for (var a = {}, b = 0; b < this.messages.length; b++) {
            var c = this.messages[b]
              , d = a[c.notBeforeEventId];
            d || (d = [],
            a[c.notBeforeEventId] = d);
            d.push(c)
        }
        return a
    }
    ;
    Kx.prototype.prune = function(a) {
        for (var b = [], c = [], d = 0; d < this.messages.length; d++) {
            var e = this.messages[d];
            e.notBeforeEventId === a ? b.push(e) : c.push(e)
        }
        this.messages = c;
        return b
    }
    ;
    function Lx(a, b, c) {
        c.eventMetadata = c.eventMetadata || {};
        c.eventMetadata.source_canonical_id = Hf.canonicalContainerId;
        Mx().enqueue(a, b, c)
    }
    function Nx() {
        var a = Ox;
        Mx().listen(a)
    }
    function Mx() {
        var a = ii.mb;
        a || (a = new Kx,
        ii.mb = a);
        return a
    }
    ;var Df;
    var Px = {}
      , Qx = {};
    function Rx(a, b) {
        for (var c = [], d = [], e = {}, f = 0; f < a.length; e = {
            Jh: void 0,
            sh: void 0
        },
        f++) {
            var g = a[f];
            if (0 <= g.indexOf("-")) {
                if (e.Jh = cm(g, b),
                e.Jh) {
                    var h = Aj();
                    sb(h, function(r) {
                        return function(t) {
                            return r.Jh.ka === t
                        }
                    }(e)) ? c.push(g) : d.push(g)
                }
            } else {
                var m = Px[g] || [];
                e.sh = {};
                m.forEach(function(r) {
                    return function(t) {
                        r.sh[t] = !0
                    }
                }(e));
                for (var n = xj(), p = 0; p < n.length; p++)
                    if (e.sh[n[p]]) {
                        c = c.concat(Aj());
                        break
                    }
                var q = Qx[g] || [];
                q.length && (c = c.concat(q))
            }
        }
        return {
            km: c,
            om: d
        }
    }
    function Sx(a) {
        z(Px, function(b, c) {
            var d = c.indexOf(a);
            0 <= d && c.splice(d, 1)
        })
    }
    function Tx(a) {
        z(Qx, function(b, c) {
            var d = c.indexOf(a);
            0 <= d && c.splice(d, 1)
        })
    }
    var Ux = "HA GF G UA AW DC MC".split(" ")
      , Vx = !1
      , Wx = !1
      , Xx = !1
      , Yx = !1;
    function Zx(a, b) {
        a.hasOwnProperty("gtm.uniqueEventId") || Object.defineProperty(a, "gtm.uniqueEventId", {
            value: yi()
        });
        b.eventId = a["gtm.uniqueEventId"];
        b.priorityId = a["gtm.priorityId"];
        return {
            eventId: b.eventId,
            priorityId: b.priorityId
        }
    }
    var $x = void 0
      , ay = void 0;
    function by(a, b, c) {
        var d = k(a);
        d.eventId = void 0;
        d.inheritParentConfig = void 0;
        Object.keys(b).some(function(f) {
            return void 0 !== b[f]
        }) && O(136);
        var e = k(b);
        k(c, e);
        Lx(Ix(xj()[0], e), a.eventId, d)
    }
    function cy(a) {
        for (var b = na([P.g.md, P.g.Kb]), c = b.next(); !c.done; c = b.next()) {
            var d = c.value
              , e = a && a[d] || Km.H[d];
            if (e)
                return e
        }
    }
    var dy = [P.g.md, P.g.Kb, P.g.yc, P.g.lb, P.g.tb, P.g.Da, P.g.xa, P.g.Oa, P.g.Ta, P.g.Db]
      , ey = {
        config: function(a, b) {
            var c = Zx(a, b);
            if (!(2 > a.length) && l(a[1])) {
                var d = {};
                if (2 < a.length) {
                    if (void 0 != a[2] && !Xa(a[2]) || 3 < a.length)
                        return;
                    d = a[2]
                }
                var e = cm(a[1], b.isGtmEvent);
                if (e) {
                    var f, g, h;
                    a: {
                        if (!vj.je) {
                            var m = Gj(Hj());
                            if (Yj(m)) {
                                var n = m.parent
                                  , p = n.isDestination;
                                h = {
                                    zm: Gj(n),
                                    jm: p
                                };
                                break a
                            }
                        }
                        h = void 0
                    }
                    var q = h;
                    q && (f = q.zm,
                    g = q.jm);
                    Zw(c.eventId, "gtag.config");
                    var r = e.ka
                      , t = e.id !== r;
                    if (t ? -1 === Aj().indexOf(r) : -1 === xj().indexOf(r)) {
                        if (!b.inheritParentConfig && !d[P.g.Gb]) {
                            var u = cy(d);
                            if (t)
                                Vv(r, u, {
                                    source: 2,
                                    fromContainerExecution: b.fromContainerExecution
                                });
                            else if (void 0 !== f && -1 !== f.containers.indexOf(r)) {
                                var v = d;
                                $x ? by(b, v, $x) : ay || (ay = k(v))
                            } else
                                Uv(r, u, !0, {
                                    source: 2,
                                    fromContainerExecution: b.fromContainerExecution
                                })
                        }
                    } else {
                        if (f && (O(128),
                        g && O(130),
                        b.inheritParentConfig)) {
                            var w;
                            var y = d;
                            ay ? (by(b, ay, y),
                            w = !1) : (!y[P.g.Xb] && mi && $x || ($x = k(y)),
                            w = !0);
                            w && f.containers && f.containers.join(",");
                            return
                        }
                        var x = d;
                        if (!Xx && (Xx = !0,
                        Wx))
                            for (var B = na(dy), A = B.next(); !A.done; A = B.next())
                                if (x.hasOwnProperty(A.value)) {
                                    ll("erc");
                                    break
                                }
                        T(81) && jk && (1 === Dx && Bc(G, "pagehide", Ex),
                        Dx = 2);
                        if (mi && !t && !d[P.g.Xb]) {
                            var D = Yx;
                            Yx = !0;
                            if (D)
                                return
                        }
                        Vx || O(43);
                        if (!b.noTargetGroup)
                            if (t) {
                                Tx(e.id);
                                var E = e.id
                                  , C = d[P.g.Zd] || "default";
                                C = String(C).split(",");
                                for (var F = 0; F < C.length; F++) {
                                    var L = Qx[C[F]] || [];
                                    Qx[C[F]] = L;
                                    0 > L.indexOf(E) && L.push(E)
                                }
                            } else {
                                Sx(e.id);
                                var N = e.id
                                  , Q = d[P.g.Zd] || "default";
                                Q = Q.toString().split(",");
                                for (var V = 0; V < Q.length; V++) {
                                    var ca = Px[Q[V]] || [];
                                    Px[Q[V]] = ca;
                                    0 > ca.indexOf(N) && ca.push(N)
                                }
                            }
                        delete d[P.g.Zd];
                        var Z = b.eventMetadata || {};
                        Z.hasOwnProperty("is_external_event") || (Z.is_external_event = !b.fromContainerExecution);
                        b.eventMetadata = Z;
                        delete d[P.g.ed];
                        for (var R = t ? [e.id] : Aj(), oa = 0; oa < R.length; oa++) {
                            var ka = d
                              , ha = R[oa]
                              , ja = k(b)
                              , Ja = cm(ha, ja.isGtmEvent);
                            Ja && Km.push("config", [ka], Ja, ja)
                        }
                    }
                }
            }
        },
        consent: function(a, b) {
            if (3 === a.length) {
                O(39);
                var c = Zx(a, b)
                  , d = a[1]
                  , e = a[2];
                b.fromContainerExecution || (e[P.g.P] && O(139),
                e[P.g.Aa] && O(140));
                "default" === d ? Sl(e) : "update" === d ? Tl(e, c) : "declare" === d && b.fromContainerExecution && Rl(e)
            }
        },
        event: function(a, b) {
            var c = a[1];
            if (!(2 > a.length) && l(c)) {
                var d;
                if (2 < a.length) {
                    if (!Xa(a[2]) && void 0 != a[2] || 3 < a.length)
                        return;
                    d = a[2]
                }
                var e = d
                  , f = {}
                  , g = (f.event = c,
                f);
                e && (g.eventModel = k(e),
                e[P.g.ed] && (g.eventCallback = e[P.g.ed]),
                e[P.g.Wd] && (g.eventTimeout = e[P.g.Wd]));
                var h = Zx(a, b)
                  , m = h.eventId
                  , n = h.priorityId;
                g["gtm.uniqueEventId"] = m;
                n && (g["gtm.priorityId"] = n);
                if ("optimize.callback" === c)
                    return g.eventModel = g.eventModel || {},
                    g;
                var p;
                var q = d
                  , r = q && q[P.g.Wb];
                void 0 === r && (r = Hi(P.g.Wb, 2),
                void 0 === r && (r = "default"));
                if (l(r) || Array.isArray(r)) {
                    var t;
                    t = b.isGtmEvent ? l(r) ? [r] : r : r.toString().replace(/\s+/g, "").split(",");
                    var u = Rx(t, b.isGtmEvent)
                      , v = u.km
                      , w = u.om;
                    if (w.length)
                        for (var y = cy(q), x = 0; x < w.length; x++) {
                            var B = cm(w[x], b.isGtmEvent);
                            B && Vv(B.ka, y, {
                                source: 3,
                                fromContainerExecution: b.fromContainerExecution
                            })
                        }
                    p = dm(v, b.isGtmEvent)
                } else
                    p = void 0;
                var A = p;
                if (A) {
                    var D;
                    !A.length || (null == (D = b.eventMetadata) ? 0 : D.em_event) || (Wx = !0);
                    Zw(m, c);
                    for (var E = [], C = 0; C < A.length; C++) {
                        var F = A[C]
                          , L = k(b);
                        if (-1 !== Ux.indexOf(Jj(F.prefix))) {
                            var N = k(d)
                              , Q = L.eventMetadata || {};
                            Q.hasOwnProperty("is_external_event") || (Q.is_external_event = !L.fromContainerExecution);
                            L.eventMetadata = Q;
                            delete N[P.g.ed];
                            Mm(c, N, F.id, L);
                            T(81) && jk && 0 === Dx && (Ac(G, "pagehide", Ex),
                            Dx = 1)
                        }
                        E.push(F.id)
                    }
                    g.eventModel = g.eventModel || {};
                    0 < A.length ? g.eventModel[P.g.Wb] = E.join() : delete g.eventModel[P.g.Wb];
                    Vx || O(43);
                    void 0 === b.noGtmEvent && b.eventMetadata && b.eventMetadata.syn_or_mod && (b.noGtmEvent = !0);
                    g.eventModel[P.g.Ub] && (b.noGtmEvent = !0);
                    return b.noGtmEvent ? void 0 : g
                }
            }
        },
        get: function(a, b) {
            O(53);
            if (4 === a.length && l(a[1]) && l(a[2]) && pb(a[3])) {
                var c = cm(a[1], b.isGtmEvent)
                  , d = String(a[2])
                  , e = a[3];
                if (c) {
                    Vx || O(43);
                    var f = cy();
                    if (!sb(Aj(), function(h) {
                        return c.ka === h
                    }))
                        Vv(c.ka, f, {
                            source: 4,
                            fromContainerExecution: b.fromContainerExecution
                        });
                    else if (-1 !== Ux.indexOf(Jj(c.prefix))) {
                        Zx(a, b);
                        var g = {};
                        k((g[P.g.qb] = d,
                        g[P.g.Eb] = e,
                        g));
                        Nm(d, function(h) {
                            I(function() {
                                return e(h)
                            })
                        }, c.id, b)
                    }
                }
            }
        },
        js: function(a, b) {
            if (2 == a.length && a[1].getTime) {
                Vx = !0;
                var c = Zx(a, b)
                  , d = c.eventId
                  , e = c.priorityId
                  , f = {};
                return f.event = "gtm.js",
                f["gtm.start"] = a[1].getTime(),
                f["gtm.uniqueEventId"] = d,
                f["gtm.priorityId"] = e,
                f
            }
        },
        policy: function(a) {
            if (3 === a.length && l(a[1]) && pb(a[2])) {
                if (Ef(a[1], a[2]),
                O(74),
                "all" === a[1]) {
                    O(75);
                    var b = !1;
                    try {
                        b = a[2](Cj(), "unknown", {})
                    } catch (c) {}
                    b || O(76)
                }
            } else
                O(73)
        },
        set: function(a, b) {
            var c;
            2 == a.length && Xa(a[1]) ? c = k(a[1]) : 3 == a.length && l(a[1]) && (c = {},
            Xa(a[2]) || Array.isArray(a[2]) ? c[a[1]] = k(a[2]) : c[a[1]] = a[2]);
            if (c) {
                var d = Zx(a, b)
                  , e = d.eventId
                  , f = d.priorityId;
                k(c);
                var g = k(c);
                Km.push("set", [g], void 0, b);
                c["gtm.uniqueEventId"] = e;
                f && (c["gtm.priorityId"] = f);
                delete c.event;
                b.overwriteModelFields = !0;
                return c
            }
        }
    }
      , fy = {
        policy: !0
    };
    var hy = function(a) {
        if (gy(a))
            return a;
        this.value = a
    };
    hy.prototype.getUntrustedMessageValue = function() {
        return this.value
    }
    ;
    var gy = function(a) {
        return !a || "object" !== Va(a) || Xa(a) ? !1 : "getUntrustedMessageValue"in a
    };
    hy.prototype.getUntrustedMessageValue = hy.prototype.getUntrustedMessageValue;
    var iy = !1
      , jy = [];
    function ky() {
        if (!iy) {
            iy = !0;
            for (var a = 0; a < jy.length; a++)
                I(jy[a])
        }
    }
    function ly(a) {
        iy ? I(a) : jy.push(a)
    }
    ;var my = 0
      , ny = {}
      , oy = []
      , py = []
      , qy = !1
      , ry = !1;
    function sy(a, b) {
        return a.messageContext.eventId - b.messageContext.eventId || a.messageContext.priorityId - b.messageContext.priorityId
    }
    var ty = function(a) {
        return G[hi.Ya].push(a)
    }
      , uy = function(a, b, c) {
        a.eventCallback = b;
        c && (a.eventTimeout = c);
        return ty(a)
    }
      , vy = function(a, b) {
        if (!qb(b) || 0 > b)
            b = 0;
        var c = ii[hi.Ya]
          , d = 0
          , e = !1
          , f = void 0;
        f = G.setTimeout(function() {
            e || (e = !0,
            a());
            f = void 0
        }, b);
        return function() {
            var g = c ? c.subscribers : 1;
            ++d === g && (f && (G.clearTimeout(f),
            f = void 0),
            e || (a(),
            e = !0))
        }
    };
    function wy(a, b) {
        var c = a._clear || b.overwriteModelFields;
        z(a, function(e, f) {
            "_clear" !== e && (c && Ki(e),
            Ki(e, f))
        });
        ui || (ui = a["gtm.start"]);
        var d = a["gtm.uniqueEventId"];
        if (!a.event)
            return !1;
        "number" !== typeof d && (d = yi(),
        a["gtm.uniqueEventId"] = d,
        Ki("gtm.uniqueEventId", d));
        return Cx(a)
    }
    function xy(a) {
        if (null == a || "object" !== typeof a)
            return !1;
        if (a.event)
            return !0;
        if (wb(a)) {
            var b = a[0];
            if ("config" === b || "event" === b || "js" === b || "get" === b)
                return !0
        }
        return !1
    }
    function yy() {
        var a;
        if (py.length)
            a = py.shift();
        else if (oy.length)
            a = oy.shift();
        else
            return;
        var b;
        var c = a;
        if (qy || !xy(c.message))
            b = c;
        else {
            qy = !0;
            var d = c.message["gtm.uniqueEventId"];
            "number" !== typeof d && (d = c.message["gtm.uniqueEventId"] = yi());
            var e = {}
              , f = {
                message: (e.event = "gtm.init_consent",
                e["gtm.uniqueEventId"] = d - 2,
                e),
                messageContext: {
                    eventId: d - 2
                }
            }
              , g = {}
              , h = {
                message: (g.event = "gtm.init",
                g["gtm.uniqueEventId"] = d - 1,
                g),
                messageContext: {
                    eventId: d - 1
                }
            };
            oy.unshift(h, c);
            if (jk) {
                var m = Hf.ctid;
                if (m) {
                    var n, p = Gj(Hj());
                    n = p && p.context;
                    var q = T(66) ? cl(!0) : void 0
                      , r = Hf.canonicalContainerId
                      , t = hj(G.location.href)
                      , u = t.hostname + t.pathname
                      , v = n && n.fromContainerExecution
                      , w = vj.je
                      , y = n && n.source;
                    dl || (dl = u);
                    fl.push(m + ";" + r + ";" + (v ? 1 : 0) + ";" + (y || 0) + ";" + (w ? 1 : 0));
                    el = q
                }
            }
            b = f
        }
        return b
    }
    function zy() {
        for (var a = !1, b; !ry && (b = yy()); ) {
            ry = !0;
            delete Ei.eventModel;
            Gi();
            var c = b
              , d = c.message
              , e = c.messageContext;
            if (null == d)
                ry = !1;
            else {
                e.fromContainerExecution && Li();
                try {
                    if (pb(d))
                        try {
                            d.call(Ii)
                        } catch (v) {}
                    else if (Array.isArray(d)) {
                        var f = d;
                        if (l(f[0])) {
                            var g = f[0].split(".")
                              , h = g.pop()
                              , m = f.slice(1)
                              , n = Hi(g.join("."), 2);
                            if (null != n)
                                try {
                                    n[h].apply(n, m)
                                } catch (v) {}
                        }
                    } else {
                        var p = void 0;
                        if (wb(d))
                            a: {
                                if (d.length && l(d[0])) {
                                    var q = ey[d[0]];
                                    if (q && (!e.fromContainerExecution || !fy[d[0]])) {
                                        p = q(d, e);
                                        break a
                                    }
                                }
                                p = void 0
                            }
                        else
                            p = d;
                        p && (a = wy(p, e) || a)
                    }
                } finally {
                    e.fromContainerExecution && Gi(!0);
                    var r = d["gtm.uniqueEventId"];
                    if ("number" === typeof r) {
                        for (var t = ny[String(r)] || [], u = 0; u < t.length; u++)
                            py.push(Ay(t[u]));
                        t.length && py.sort(sy);
                        delete ny[String(r)];
                        r > my && (my = r)
                    }
                    ry = !1
                }
            }
        }
        return !a
    }
    function By() {
        if (T(55)) {
            var a = Cy();
        }
        var b = zy();
        if (T(55)) {}
        try {
            var c = Cj()
              , d = G[hi.Ya].hide;
            if (d && void 0 !== d[c] && d.end) {
                d[c] = !1;
                var e = !0, f;
                for (f in d)
                    if (d.hasOwnProperty(f) && !0 === d[f]) {
                        e = !1;
                        break
                    }
                e && (d.end(),
                d.end = null)
            }
        } catch (g) {}
        return b
    }
    function Ox(a) {
        if (my < a.notBeforeEventId) {
            var b = String(a.notBeforeEventId);
            ny[b] = ny[b] || [];
            ny[b].push(a)
        } else
            py.push(Ay(a)),
            py.sort(sy),
            I(function() {
                ry || zy()
            })
    }
    function Ay(a) {
        return {
            message: a.message,
            messageContext: a.messageContext
        }
    }
    var Dy = function() {
        function a(f) {
            var g = {};
            if (gy(f)) {
                var h = f;
                f = gy(h) ? h.getUntrustedMessageValue() : void 0;
                g.fromContainerExecution = !0
            }
            return {
                message: f,
                messageContext: g
            }
        }
        var b = rc(hi.Ya, [])
          , c = ii[hi.Ya] = ii[hi.Ya] || {};
        !0 === c.pruned && O(83);
        ny = Mx().get();
        Nx();
        aw(function() {
            if (!c.gtmDom) {
                c.gtmDom = !0;
                var f = {};
                b.push((f.event = "gtm.dom",
                f))
            }
        });
        ly(function() {
            if (!c.gtmLoad) {
                c.gtmLoad = !0;
                var f = {};
                b.push((f.event = "gtm.load",
                f))
            }
        });
        c.subscribers = (c.subscribers || 0) + 1;
        var d = b.push;
        b.push = function() {
            var f;
            if (0 < ii.SANDBOXED_JS_SEMAPHORE) {
                f = [];
                for (var g = 0; g < arguments.length; g++)
                    f[g] = new hy(arguments[g])
            } else
                f = [].slice.call(arguments, 0);
            var h = f.map(function(q) {
                return a(q)
            });
            oy.push.apply(oy, h);
            var m = d.apply(b, f)
              , n = Math.max(100, Number("1000") || 300);
            if (this.length > n)
                for (O(4),
                c.pruned = !0; this.length > n; )
                    this.shift();
            var p = "boolean" !== typeof m || m;
            return zy() && p
        }
        ;
        var e = b.slice(0).map(function(f) {
            return a(f)
        });
        oy.push.apply(oy, e);
        if (Cy()) {
            if (T(55)) {}
            I(By)
        }
    }
      , Cy = function() {
        var a = !0;
        return a
    };
    function Ey(a) {
        if (null == a || 0 === a.length)
            return !1;
        var b = Number(a)
          , c = Cb();
        return b < c + 3E5 && b > c - 9E5
    }
    function Fy(a) {
        return a && 0 === a.indexOf("pending:") ? Ey(a.substr(8)) : !1
    }
    ;var Gy = !1
      , Hy = function(a) {
        if (Gy)
            return [];
        var b = []
          , c = Fj();
        if (c) {
            var d, e = c.canonicalContainerId || "_" + (c.scriptContainerId || (null == (d = c.destinations) ? void 0 : d[0]));
            b.push(["pcid", e])
        }
        a.Xa && (Gy = !0,
        b.length && a.Nc());
        return b
    };
    function Iy(a) {
        if (a.scriptSource) {
            var b;
            try {
                var c;
                b = null == (c = Mc()) ? void 0 : c.getEntriesByType("resource")
            } catch (h) {}
            if (b) {
                for (var d = {}, e = 0; e < b.length; ++e) {
                    var f = b[e]
                      , g = f.initiatorType;
                    if ("script" === g && f.name === a.scriptSource)
                        return {
                            Km: e,
                            Lm: d
                        };
                    d[g] = 1 + (d[g] || 0)
                }
                O(146)
            } else
                O(145)
        }
    }
    function Jy() {
        if (jk && T(65)) {
            var a = Ij();
            if (!a)
                O(144);
            else if (a.canonicalContainerId) {
                var b = Iy(a);
                if (b) {
                    var c = !1;
                    ek(function(d) {
                        if (c)
                            return [];
                        d.Xa && (c = !0);
                        d.Nc();
                        return [["rtg", String(a.canonicalContainerId)], ["rlo", String(b.Km)], ["slo", String(b.Lm.script || "0")]]
                    })
                }
            }
        }
    }
    ;var dz = function() {};
    var ez = function() {};
    ez.prototype.toString = function() {
        return "undefined"
    }
    ;
    var fz = new ez;
    var hz = function() {
        (ii.rm = ii.rm || {})[Ej()] = function(a) {
            if (gz.hasOwnProperty(a))
                return gz[a]
        }
    }
      , kz = function(a, b, c) {
        if (a instanceof iz) {
            var d = a
              , e = d.m
              , f = b
              , g = String(yi());
            jz[g] = [f, c];
            a = e.call(d, g);
            b = ob
        }
        return {
            Nj: a,
            onSuccess: b
        }
    }
      , lz = function(a) {
        var b = a ? 0 : 1;
        return function(c) {
            O(a ? 134 : 135);
            var d = jz[c];
            if (d && "function" === typeof d[b])
                d[b]();
            jz[c] = void 0
        }
    }
      , iz = function(a) {
        this.valueOf = this.toString;
        this.m = function(b) {
            for (var c = [], d = 0; d < a.length; d++)
                c.push(a[d] === fz ? b : a[d]);
            return c.join("")
        }
    };
    iz.prototype.toString = function() {
        return this.m("undefined")
    }
    ;
    var gz = {}
      , jz = {};
    function mz(a, b) {
        function c(g) {
            var h = hj(g)
              , m = dj(h, "protocol")
              , n = dj(h, "host", !0)
              , p = dj(h, "port")
              , q = dj(h, "path").toLowerCase().replace(/\/$/, "");
            if (void 0 === m || "http" === m && "80" === p || "https" === m && "443" === p)
                m = "web",
                p = "default";
            return [m, n, p, q]
        }
        for (var d = c(String(a)), e = c(String(b)), f = 0; f < d.length; f++)
            if (d[f] !== e[f])
                return !1;
        return !0
    }
    function nz(a) {
        return oz(a) ? 1 : 0
    }
    function oz(a) {
        var b = a.arg0
          , c = a.arg1;
        if (a.any_of && Array.isArray(c)) {
            for (var d = 0; d < c.length; d++) {
                var e = k(a, {});
                k({
                    arg1: c[d],
                    any_of: void 0
                }, e);
                if (nz(e))
                    return !0
            }
            return !1
        }
        switch (a["function"]) {
        case "_cn":
            return kg(b, c);
        case "_css":
            var f;
            a: {
                if (b)
                    try {
                        for (var g = 0; g < gg.length; g++) {
                            var h = gg[g];
                            if (b[h]) {
                                f = b[h](c);
                                break a
                            }
                        }
                    } catch (m) {}
                f = !1
            }
            return f;
        case "_ew":
            return hg(b, c);
        case "_eq":
            return lg(b, c);
        case "_ge":
            return mg(b, c);
        case "_gt":
            return og(b, c);
        case "_lc":
            return 0 <= String(b).split(",").indexOf(String(c));
        case "_le":
            return ng(b, c);
        case "_lt":
            return pg(b, c);
        case "_re":
            return jg(b, c, a.ignore_case);
        case "_sw":
            return qg(b, c);
        case "_um":
            return mz(b, c)
        }
        return !1
    }
    ;function pz() {
        var a;
        a = void 0 === a ? "" : a;
        var b, c;
        return (null == (b = data) ? 0 : null == (c = b.blob) ? 0 : c.hasOwnProperty(1)) ? String(data.blob[1]) : a
    }
    ;function qz() {
        var a = [["cv", T(76) ? pz() : "81"], ["rv", hi.Qg], ["tc", cf.filter(function(b) {
            return b
        }).length]];
        hi.ne && a.push(["x", hi.ne]);
        Ai.m && a.push(["tag_exp", Ai.m]);
        return a
    }
    ;function rz() {
        var a = pl();
        return a.length ? [["exp_geo", a]] : []
    }
    var sz;
    function tz() {
        try {
            null != sz || (sz = (new Intl.DateTimeFormat).resolvedOptions().timeZone)
        } catch (b) {}
        var a;
        return (null == (a = sz) ? 0 : a.length) ? [["exp_tz", sz]] : []
    }
    ;function uz() {
        return !1
    }
    function vz() {
        var a = {};
        return function(b, c, d) {}
    }
    ;function wz() {
        var a = xz;
        return function(b, c, d) {
            var e = d && d.event;
            yz(c);
            var f = 0 === b.indexOf("__cvt_") ? void 0 : 1
              , g = new cb;
            z(c, function(r, t) {
                var u = ad(t, void 0, f);
                void 0 === u && void 0 !== t && O(44);
                g.set(r, u)
            });
            a.m.m.F = xf();
            var h = {
                Gj: Lf(b),
                eventId: null == e ? void 0 : e.id,
                priorityId: void 0 !== e ? e.priorityId : void 0,
                qe: void 0 !== e ? function(r) {
                    e.bc.qe(r)
                }
                : void 0,
                hc: function() {
                    return b
                },
                log: function() {},
                Cl: {
                    index: null == d ? void 0 : d.index,
                    type: null == d ? void 0 : d.type,
                    name: null == d ? void 0 : d.name
                },
                Jm: !!Fv(b, 3),
                originalEventData: null == e ? void 0 : e.originalEventData
            };
            e && e.cachedModelValues && (h.cachedModelValues = {
                gtm: e.cachedModelValues.gtm,
                ecommerce: e.cachedModelValues.ecommerce
            });
            if (uz()) {
                var m = vz(), n, p;
                h.Qa = {
                    Uh: [],
                    se: {},
                    wb: function(r, t, u) {
                        1 === t && (n = r);
                        7 === t && (p = u);
                        m(r, t, u)
                    },
                    Of: bh()
                };
                h.log = function(r) {
                    var t = za.apply(1, arguments);
                    n && m(n, 4, {
                        level: r,
                        source: p,
                        message: t
                    })
                }
            }
            var q = ye(a, h, [b, g]);
            a.m.m.F = void 0;
            q instanceof Ga && "return" === q.type && (q = q.data);
            return J(q, void 0, f)
        }
    }
    function yz(a) {
        var b = a.gtmOnSuccess
          , c = a.gtmOnFailure;
        pb(b) && (a.gtmOnSuccess = function() {
            I(b)
        }
        );
        pb(c) && (a.gtmOnFailure = function() {
            I(c)
        }
        )
    }
    ;function zz(a, b) {
        var c = this;
    }
    zz.U = "addConsentListener";
    var Az = !1;
    function Bz(a) {
        for (var b = 0; b < a.length; ++b)
            if (Az)
                try {
                    a[b]()
                } catch (c) {
                    O(77)
                }
            else
                a[b]()
    }
    function Cz(a, b, c) {
        var d = this, e;
        return e
    }
    Cz.K = "internal.addDataLayerEventListener";
    function Dz(a, b, c) {}
    Dz.U = "addDocumentEventListener";
    function Ez(a, b, c, d) {}
    Ez.U = "addElementEventListener";
    function Fz(a) {
        return a.J.m
    }
    ;function Gz(a) {}
    Gz.U = "addEventCallback";
    var Hz = function(a) {
        return "string" === typeof a ? a : String(yi())
    }
      , Kz = function(a, b) {
        Iz(a, "init", !1) || (Jz(a, "init", !0),
        b())
    }
      , Iz = function(a, b, c) {
        var d = Lz(a);
        return Db(d, b, c)
    }
      , Mz = function(a, b, c, d) {
        var e = Lz(a)
          , f = Db(e, b, d);
        e[b] = c(f)
    }
      , Jz = function(a, b, c) {
        Lz(a)[b] = c
    }
      , Lz = function(a) {
        ii.hasOwnProperty("autoEventsSettings") || (ii.autoEventsSettings = {});
        var b = ii.autoEventsSettings;
        b.hasOwnProperty(a) || (b[a] = {});
        return b[a]
    }
      , Nz = function(a, b, c) {
        var d = {
            event: b,
            "gtm.element": a,
            "gtm.elementClasses": Kc(a, "className"),
            "gtm.elementId": a["for"] || Cc(a, "id") || "",
            "gtm.elementTarget": a.formTarget || Kc(a, "target") || ""
        };
        c && (d["gtm.triggers"] = c.join(","));
        d["gtm.elementUrl"] = (a.attributes && a.attributes.formaction ? a.formAction : "") || a.action || Kc(a, "href") || a.src || a.code || a.codebase || "";
        return d
    };
    function Wz(a) {}
    Wz.K = "internal.addFormAbandonmentListener";
    function Xz(a, b, c, d) {}
    Xz.K = "internal.addFormData";
    var Yz = {}
      , Zz = []
      , $z = {}
      , aA = 0
      , bA = 0;
    function iA(a, b) {}
    iA.K = "internal.addFormInteractionListener";
    function pA(a, b) {}
    pA.K = "internal.addFormSubmitListener";
    function uA(a) {}
    uA.K = "internal.addGaSendListener";
    function vA(a) {
        if (!a)
            return {};
        var b = a.Cl;
        return cw(b.type, b.index, b.name)
    }
    function wA(a) {
        return a ? {
            originatingEntity: vA(a)
        } : {}
    }
    ;var yA = function(a, b, c) {
        xA().updateZone(a, b, c)
    }
      , AA = function(a, b, c, d, e, f) {
        var g = xA();
        c = c && Gb(c, zA);
        for (var h = g.createZone(a, c), m = 0; m < b.length; m++) {
            var n = String(b[m]);
            if (g.registerChild(n, Cj(), h)) {
                var p = n
                  , q = a
                  , r = d
                  , t = e
                  , u = f;
                if (0 === p.indexOf("GTM-"))
                    Uv(p, void 0, !1, {
                        source: 1,
                        fromContainerExecution: !0
                    });
                else {
                    var v = Hx("js", Bb());
                    Uv(p, void 0, !0, {
                        source: 1,
                        fromContainerExecution: !0
                    });
                    var w = {
                        originatingEntity: t,
                        inheritParentConfig: u
                    };
                    T(82) || Lx(v, q, w);
                    Lx(Ix(p, r), q, w)
                }
            }
        }
        return h
    }
      , xA = function() {
        var a = ii.zones;
        a || (a = ii.zones = new BA);
        return a
    }
      , CA = {
        zone: 1,
        cn: 1,
        css: 1,
        ew: 1,
        eq: 1,
        ge: 1,
        gt: 1,
        lc: 1,
        le: 1,
        lt: 1,
        re: 1,
        sw: 1,
        um: 1
    }
      , zA = {
        cl: ["ecl"],
        ecl: ["cl"],
        ehl: ["hl"],
        gaawc: ["googtag"],
        hl: ["ehl"]
    }
      , BA = function() {
        this.m = {};
        this.F = {};
        this.H = 0
    };
    aa = BA.prototype;
    aa.isActive = function(a, b) {
        for (var c, d = 0; d < a.length && !(c = this.m[a[d]]); d++)
            ;
        if (!c)
            return !0;
        if (!this.isActive([c.Ih], b))
            return !1;
        for (var e = 0; e < c.Te.length; e++)
            if (this.F[c.Te[e]].wd(b))
                return !0;
        return !1
    }
    ;
    aa.getIsAllowedFn = function(a, b) {
        if (!this.isActive(a, b))
            return function() {
                return !1
            }
            ;
        for (var c, d = 0; d < a.length && !(c = this.m[a[d]]); d++)
            ;
        if (!c)
            return function() {
                return !0
            }
            ;
        for (var e = [], f = 0; f < c.Te.length; f++) {
            var g = this.F[c.Te[f]];
            g.wd(b) && e.push(g)
        }
        if (!e.length)
            return function() {
                return !1
            }
            ;
        var h = this.getIsAllowedFn([c.Ih], b);
        return function(m, n) {
            n = n || [];
            if (!h(m, n))
                return !1;
            for (var p = 0; p < e.length; ++p)
                if (e[p].Zl(m, n))
                    return !0;
            return !1
        }
    }
    ;
    aa.unregisterChild = function(a) {
        for (var b = 0; b < a.length; b++)
            delete this.m[a[b]]
    }
    ;
    aa.createZone = function(a, b) {
        var c = String(++this.H);
        this.F[c] = new DA(a,b);
        return c
    }
    ;
    aa.updateZone = function(a, b, c) {
        var d = this.F[a];
        d && d.H(b, c)
    }
    ;
    aa.registerChild = function(a, b, c) {
        var d = this.m[a];
        if (!d && ii[a] || !d && Tj(a) || d && d.Ih !== b)
            return !1;
        if (d)
            return d.Te.push(c),
            !1;
        this.m[a] = {
            Ih: b,
            Te: [c]
        };
        return !0
    }
    ;
    var DA = function(a, b) {
        this.F = null;
        this.m = [{
            eventId: a,
            wd: !0
        }];
        if (b) {
            this.F = {};
            for (var c = 0; c < b.length; c++)
                this.F[b[c]] = !0
        }
    };
    DA.prototype.H = function(a, b) {
        var c = this.m[this.m.length - 1];
        a <= c.eventId || c.wd !== b && this.m.push({
            eventId: a,
            wd: b
        })
    }
    ;
    DA.prototype.wd = function(a) {
        for (var b = this.m.length - 1; 0 <= b; b--)
            if (this.m[b].eventId <= a)
                return this.m[b].wd;
        return !1
    }
    ;
    DA.prototype.Zl = function(a, b) {
        b = b || [];
        if (!this.F || CA[a] || this.F[a])
            return !0;
        for (var c = 0; c < b.length; ++c)
            if (this.F[b[c]])
                return !0;
        return !1
    }
    ;
    function EA(a) {
        var b = ii.zones;
        return b ? b.getIsAllowedFn(xj(), a) : function() {
            return !0
        }
    }
    function FA() {
        Iv(Ej(), function(a) {
            var b = a.originalEventData["gtm.uniqueEventId"]
              , c = ii.zones;
            return c ? c.isActive(xj(), b) : !0
        });
        Gv(Ej(), function(a) {
            var b = a.entityId
              , c = a.securityGroups;
            return EA(Number(a.originalEventData["gtm.uniqueEventId"]))(b, c)
        })
    }
    ;var GA = function(a, b) {
        this.tagId = a;
        this.ue = b
    };
    function HA(a, b) {
        var c = this, d;
        var e = function(v) {
            Gv(v, function(w) {
                for (var y = Hv().getExternalRestrictions(0, Ej()), x = na(y), B = x.next(); !B.done; B = x.next()) {
                    var A = B.value;
                    if (!A(w))
                        return !1
                }
                return !0
            }, !0);
            Iv(v, function(w) {
                for (var y = Hv().getExternalRestrictions(1, Ej()), x = na(y), B = x.next(); !B.done; B = x.next()) {
                    var A = B.value;
                    if (!A(w))
                        return !1
                }
                return !0
            }, !0);
            h && h(new GA(a,v))
        };
        K(this.getName(), ["tagId:!string", "options:?PixieMap"], arguments);
        var f = J(b, this.J, 1) || {}
          , g = f.firstPartyUrl
          , h = f.onLoad
          , m = !0 === f.loadByDestination
          , n = !0 === f.isGtmEvent
          , p = !0 === f.siloed;
        Bz([function() {
            return M(c, "load_google_tags", a, g)
        }
        ]);
        if (m) {
            if (Uj(a))
                return
        } else if (Tj(a))
            return;
        var q = 6
          , r = Fz(this);
        n && (q = 7);
        "__zone" === r.hc() && (q = 1);
        var t = {
            source: q,
            fromContainerExecution: !0,
            siloed: p
        };
        if (m)
            Vv(a, g, t, e);
        else {
            var u = 0 === a.indexOf("GTM-");
            Uv(a, g, !u, t, e)
        }
        h && "__zone" === r.hc() && AA(Number.MIN_SAFE_INTEGER, [a], null, {}, vA(Fz(this)));
        d = p ? zj(a) : a;
        return d
    }
    HA.K = "internal.loadGoogleTag";
    function IA(a) {
        return new Tc("",function(b) {
            var c = this.evaluate(b);
            if (c instanceof Tc)
                return new Tc("",function() {
                    var d = za.apply(0, arguments)
                      , e = this
                      , f = k(Fz(this), null);
                    f.eventId = a.eventId;
                    f.priorityId = a.priorityId;
                    f.originalEventData = a.originalEventData;
                    var g = d.map(function(m) {
                        return e.evaluate(m)
                    })
                      , h = Ma(this.J);
                    h.m = f;
                    return c.fb.apply(c, [h].concat(qa(g)))
                }
                )
        }
        )
    }
    ;function JA(a, b, c) {
        var d = this;
    }
    JA.K = "internal.addGoogleTagRestriction";
    var KA = {}
      , LA = [];
    function SA(a, b) {}
    SA.K = "internal.addHistoryChangeListener";
    function TA(a, b, c) {}
    TA.U = "addWindowEventListener";
    function UA(a, b) {
        K(this.getName(), ["toPath:!string", "fromPath:!string"], arguments);
        M(this, "access_globals", "write", a);
        M(this, "access_globals", "read", b);
        var c = a.split(".")
          , d = b.split(".")
          , e = [G, H]
          , f = Ib(c, e)
          , g = Ib(d, e);
        if (void 0 === f || void 0 === g)
            return !1;
        f[c[c.length - 1]] = g[d[d.length - 1]];
        return !0
    }
    UA.U = "aliasInWindow";
    function VA(a, b, c) {}
    VA.K = "internal.appendRemoteConfigParameter";
    function WA() {
        var a = 2;
        return a
    }
    ;function XA(a) {
        var b;
        K(this.getName(), ["path:!string"], [a]);
        M(this, "access_globals", "execute", a);
        for (var c = a.split("."), d = G, e = d[c[0]], f = 1; e && f < c.length; f++)
            if (d = e,
            e = e[c[f]],
            d === G || d === H)
                return;
        if ("function" !== Va(e))
            return;
        for (var g = WA(), h = [], m = 1; m < arguments.length; m++)
            h.push(J(arguments[m], this.J, g));
        var n = (0,
        this.J.M)(e, d, h);
        b = ad(n, this.J, g);
        void 0 === b && void 0 !== n && O(45);
        return b
    }
    XA.U = "callInWindow";
    function YA(a) {}
    YA.U = "callLater";
    function ZA(a) {}
    ZA.K = "callOnDomReady";
    function $A(a) {}
    $A.K = "callOnWindowLoad";
    function aB(a, b) {
        var c;
        return c
    }
    aB.K = "internal.computeGtmParameter";
    function bB(a) {
        var b;
        return b
    }
    bB.K = "internal.copyFromCrossContainerData";
    function cB(a, b) {
        var c;
        K(this.getName(), ["key:!string", "dataLayerVersion:?number"], arguments),
        M(this, "read_data_layer", a),
        c = 2 !== (b || 2) ? Hi(a, 1) : Ji(a, [G, H]);
        var d = ad(c, this.J, WA());
        void 0 === d && void 0 !== c && O(45);
        return d
    }
    cB.U = "copyFromDataLayer";
    function dB(a) {
        var b = void 0;
        return b
    }
    dB.K = "internal.copyFromDataLayerCache";
    function eB(a) {
        var b;
        K(this.getName(), ["path:!string"], arguments);
        M(this, "access_globals", "read", a);
        var c = a.split(".")
          , d = Ib(c, [G, H]);
        if (!d)
            return;
        var e = d[c[c.length - 1]];
        b = ad(e, this.J, WA());
        void 0 === b && void 0 !== e && O(45);
        return b
    }
    eB.U = "copyFromWindow";
    function fB(a) {
        var b = void 0;
        return ad(b, this.J, WA())
    }
    fB.K = "internal.copyKeyFromWindow";
    function gB(a, b) {
        var c;
        return c
    }
    gB.K = "internal.copyPreHit";
    function hB(a, b) {
        var c = null
          , d = WA();
        K(this.getName(), ["functionPath:!string", "arrayPath:!string"], arguments);
        M(this, "access_globals", "readwrite", a);
        M(this, "access_globals", "readwrite", b);
        var e = [G, H]
          , f = a.split(".")
          , g = Ib(f, e)
          , h = f[f.length - 1];
        if (void 0 === g)
            throw Error("Path " + a + " does not exist.");
        var m = g[h];
        if (m && !pb(m))
            return null;
        if (m)
            return ad(m, this.J, d);
        var n;
        m = function() {
            if (!pb(n.push))
                throw Error("Object at " + b + " in window is not an array.");
            n.push.call(n, arguments)
        }
        ;
        g[h] = m;
        var p = b.split(".")
          , q = Ib(p, e)
          , r = p[p.length - 1];
        if (void 0 === q)
            throw Error("Path " + p + " does not exist.");
        n = q[r];
        void 0 === n && (n = [],
        q[r] = n);
        c = function() {
            m.apply(m, Array.prototype.slice.call(arguments, 0))
        }
        ;
        return ad(c, this.J, d)
    }
    hB.U = "createArgumentsQueue";
    function iB(a) {
        return ad(function(c) {
            var d = mw();
            if ("function" === typeof c)
                d(function() {
                    c(function(f, g, h) {
                        var m = mw()
                          , n = m && m.getByName && m.getByName(f);
                        return yk(G.gaplugins.Linker, n).decorate(g, h)
                    })
                });
            else if (Array.isArray(c)) {
                var e = String(c[0]).split(".");
                b[1 === e.length ? e[0] : e[1]] && d.apply(null, c)
            } else if ("isLoaded" === c)
                return !!d.loaded
        }, this.J, 1)
    }
    iB.K = "internal.createGaCommandQueue";
    function jB(a) {
        K(this.getName(), ["path:!string"], arguments);
        M(this, "access_globals", "readwrite", a);
        var b = a.split(".")
          , c = Ib(b, [G, H])
          , d = b[b.length - 1];
        if (!c)
            throw Error("Path " + a + " does not exist.");
        var e = c[d];
        void 0 === e && (e = [],
        c[d] = e);
        return ad(function() {
            if (!pb(e.push))
                throw Error("Object at " + a + " in window is not an array.");
            e.push.apply(e, Array.prototype.slice.call(arguments, 0))
        }, this.J, WA())
    }
    jB.U = "createQueue";
    function kB(a, b) {
        var c = null;
        return c
    }
    kB.K = "internal.createRegex";
    function lB() {
        var a = {};
        return a
    }
    ;function mB(a) {}
    mB.K = "internal.declareConsentState";
    function nB(a) {
        var b = "";
        return b
    }
    nB.K = "internal.decodeUrlHtmlEntities";
    function oB(a, b, c) {
        var d;
        return d
    }
    oB.K = "internal.decorateUrlWithGaCookies";
    function pB(a) {
        var b;
        return b
    }
    pB.K = "internal.detectUserProvidedData";
    function tB(a, b) {
        return b
    }
    tB.K = "internal.enableAutoEventOnClick";
    function CB(a, b) {
        return b
    }
    CB.K = "internal.enableAutoEventOnElementVisibility";
    function DB() {}
    DB.K = "internal.enableAutoEventOnError";
    var EB = {}
      , FB = []
      , GB = {}
      , HB = 0
      , IB = 0;
    function OB(a, b) {
        var c = this;
        return b
    }
    OB.K = "internal.enableAutoEventOnFormInteraction";
    function TB(a, b) {
        var c = this;
        return b
    }
    TB.K = "internal.enableAutoEventOnFormSubmit";
    function YB() {
        var a = this;
    }
    YB.K = "internal.enableAutoEventOnGaSend";
    var ZB = {}
      , $B = [];
    function gC(a, b) {
        var c = this;
        return b
    }
    gC.K = "internal.enableAutoEventOnHistoryChange";
    var hC = ["http://", "https://", "javascript:", "file://"];
    function lC(a, b) {
        var c = this;
        return b
    }
    lC.K = "internal.enableAutoEventOnLinkClick";
    var mC, nC;
    function yC(a, b) {
        var c = this;
        return b
    }
    yC.K = "internal.enableAutoEventOnScroll";
    function zC(a) {
        return function() {
            if (a.Hc && a.Jc >= a.Hc)
                a.ic && G.clearInterval(a.ic);
            else {
                a.Jc++;
                var b = Cb();
                ty({
                    event: a.eventName,
                    "gtm.timerId": a.ic,
                    "gtm.timerEventNumber": a.Jc,
                    "gtm.timerInterval": a.interval,
                    "gtm.timerLimit": a.Hc,
                    "gtm.timerStartTime": a.Se,
                    "gtm.timerCurrentTime": b,
                    "gtm.timerElapsedTime": b - a.Se,
                    "gtm.triggers": a.Wh
                })
            }
        }
    }
    function AC(a, b) {
        return b
    }
    AC.K = "internal.enableAutoEventOnTimer";
    var gc = la(["data-gtm-yt-inspected-"]), CC = ["www.youtube.com", "www.youtube-nocookie.com"], DC, EC = !1;
    function OC(a, b) {
        var c = this;
        return b
    }
    OC.K = "internal.enableAutoEventOnYouTubeActivity";
    var PC;
    function QC(a) {
        var b = !1;
        return b
    }
    QC.K = "internal.evaluateMatchingRules";
    var RC = function(a) {
        switch (a) {
        case "page_view":
            return [ar, pu, Kt, Yt, iu, ju, bu];
        case "call_conversion":
            return [pu];
        case "conversion":
            return [fr, Qt, Ft, Tt, Gt, Ht, It, Jt, Kt, Yt, Zt, au, cu, mu, nu, $t, iu, ju, Ut, du, eu, gu, Rt, Vt, ku, gr, Wt, hu, Lt, bu, St, ou, Xt, fu, Pt, Ot, lu];
        case "landing_page":
            return [fr, Qt, Ft, Yt, hr, iu, ju, Ut, Rt, gr, Wt, Lt, bu, St, ou, lu];
        case "remarketing":
            return [fr, Qt, Ft, Tt, Gt, Ht, It, Jt, Kt, Yt, Zt, cu, $t, iu, ju, Ut, du, Rt, gr, Wt, hu, Lt, bu, St, ou, Pt, lu];
        case "user_data_lead":
            return [fr, Qt, Ft, Gt, Kt, Yt, $t, iu, ju, hr, Ut, gu, Rt, gr, Wt, hu, Lt, bu, St, ou, lu];
        case "user_data_web":
            return [fr, Qt, Ft, Gt, Kt, Yt, $t, iu, ju, hr, Ut, gu, Rt, gr, Wt, hu, Lt, bu, St, ou, lu];
        default:
            return [fr, Qt, Ft, Tt, Gt, Ht, It, Jt, Kt, Yt, Zt, au, cu, mu, nu, $t, iu, ju, Ut, du, eu, gu, Rt, Vt, ku, gr, Wt, hu, Lt, bu, St, ou, Xt, fu, Pt, Ot, lu]
        }
    }
      , SC = function(a, b, c, d) {
        var e = new Cq(b,c,d);
        e.metadata.hit_type = a;
        e.metadata.speculative = !0;
        e.metadata.event_start_timestamp_ms = Cb();
        e.metadata.speculative_in_message = d.eventMetadata.speculative;
        return e
    }
      , TC = function(a, b, c, d) {
        function e(r, t) {
            for (var u = na(h), v = u.next(); !v.done; v = u.next()) {
                var w = v.value;
                w.isAborted = !1;
                w.metadata.speculative = !0;
                w.metadata.consent_updated = !0;
                w.metadata.event_start_timestamp_ms = Cb();
                w.metadata.consent_event_id = r;
                w.metadata.consent_priority_id = t
            }
        }
        function f(r) {
            for (var t = 0; t < h.length; t++) {
                var u = h[t];
                if (!r || r(u.metadata.hit_type))
                    if (!u.metadata.consent_updated || "page_view" === u.metadata.hit_type || W(q)) {
                        for (var v = h[t], w = RC(v.metadata.hit_type), y = 0; y < w.length && (w[y](v),
                        !v.isAborted); y++)
                            ;
                        u.metadata.speculative || u.isAborted || Ev(u)
                    }
            }
        }
        var g = d.isGtmEvent && "" === a ? {
            id: "",
            prefix: "",
            ka: "",
            ma: []
        } : cm(a, d.isGtmEvent);
        if (g) {
            var h = [];
            if (d.eventMetadata.hit_type_override) {
                var m = d.eventMetadata.hit_type_override;
                Array.isArray(m) || (m = [m]);
                for (var n = 0; n < m.length; n++) {
                    var p = SC(m[n], g, b, d);
                    p.metadata.speculative = !1;
                    h.push(p)
                }
            } else
                b === P.g.fa && (T(14) ? h.push(SC("page_view", g, b, d)) : h.push(SC("landing_page", g, b, d))),
                h.push(SC("conversion", g, b, d)),
                h.push(SC("user_data_lead", g, b, d)),
                h.push(SC("user_data_web", g, b, d)),
                h.push(SC("remarketing", g, b, d));
            var q = [P.g.R, P.g.P];
            Xl(function() {
                f();
                T(15) && (W([P.g.Aa]) || Wl(function(r) {
                    e(r.consentEventId, r.consentPriorityId);
                    f(function(t) {
                        return "remarketing" === t
                    })
                }, [P.g.Aa]));
                W(q) || Wl(function(r) {
                    e(r.consentEventId, r.consentPriorityId);
                    f()
                }, q)
            }, q)
        }
    };
    var UC = function(a) {
        var b, c, d = a.metadata.send_as_iframe, e = a.D[P.g.og];
        W([P.g.R, P.g.P]) ? d ? (b = Ai.F ? Bi() + "/activityi/" + e + ";" : "https://" + e + ".fls.doubleclick.net/activityi;",
        c = 3) : (b = pj("https://ad.doubleclick.net") + "/activity;",
        c = 1) : (b = "" + pj("https://ade.googlesyndication.com") + "/ddm/activity/",
        c = 2);
        return {
            baseUrl: b,
            endpoint: c,
            Pm: d
        }
    }
      , VC = function(a) {
        var b = a.D[P.g.ia];
        if (!Array.isArray(b))
            return "";
        for (var c = [], d = function(h, m, n) {
            void 0 !== n && "" !== n && c.push(h + m + ":" + encodeURIComponent(String(n)))
        }, e = 0; e < b.length; e++) {
            var f = b[e]
              , g = e + 1;
            d("i", g, f.id);
            d("p", g, f.price);
            d("q", g, f[P.g.ld]);
            d("c", g, f[P.g.xc]);
            d("l", g, f[P.g.Pa]);
            d("a", g, f.accountId)
        }
        return c.join("|")
    }
      , WC = {}
      , XC = (WC[P.g.mc] = "gcu",
    WC[P.g.jb] = "gclgb",
    WC[P.g.Sa] = "gclaw",
    WC[P.g.Cb] = "auiddc",
    WC[P.g.Sb] = "ps",
    WC[P.g.Ze] = "pscdl",
    WC[P.g.gg] = "gcldc",
    WC[P.g.ob] = "edid",
    WC[P.g.Li] = "cat",
    WC[P.g.Mi] = "type",
    WC[P.g.og] = "src",
    WC[P.g.Ni] = "pcor",
    WC[P.g.Oi] = "num",
    WC[P.g.Pi] = "tran",
    WC[P.g.Qi] = "u",
    WC[P.g.Yd] = "gac",
    WC[P.g.zc] = "gacgb",
    WC[P.g.Ac] = "gdpr",
    WC[P.g.rb] = "gdid",
    WC[P.g.Fb] = "frm",
    WC[P.g.ae] = "gtm_up",
    WC[P.g.ld] = "qty",
    WC[P.g.Cc] = "gdpr_consent",
    WC[P.g.Ca] = "ord",
    WC[P.g.qf] = "uaa",
    WC[P.g.rf] = "uab",
    WC[P.g.tf] = "uafvl",
    WC[P.g.uf] = "uamb",
    WC[P.g.vf] = "uam",
    WC[P.g.wf] = "uap",
    WC[P.g.xf] = "uapv",
    WC[P.g.yf] = "uaw",
    WC[P.g.qa] = "cost",
    WC[P.g.Mb] = "npa",
    WC[P.g.ya] = null,
    WC[P.g.Zc] = null,
    WC[P.g.ia] = null,
    WC)
      , YC = function(a, b) {
        var c = []
          , d = {}
          , e = function(r, t, u) {
            var v = u ? String(t) : encodeURIComponent(String(t));
            d[r] = v
        }
          , f = Xa(a.D[P.g.Zc]) ? a.D[P.g.Zc] : {};
        z(a.D, function(r, t) {
            var u = XC[r];
            if (u) {
                var v = !0 === $f[u];
                if (void 0 === t || !v && "" === t)
                    return;
                e(u, t)
            }
            void 0 === u && e(r, t)
        });
        e("gtm", Un({
            za: a.metadata.source_canonical_id
        }));
        zn() && e("gcs", An());
        e("gcd", En(a.o));
        Qn() && e("dma_cps", Fn());
        e("dma", Pn());
        cn(ln()) && e("tcfd", Rn());
        Ai.m && e("tag_exp", Ai.m);
        var g = VC(a);
        g && e("prd", g, !0);
        e("epver", "2");
        var h = a.D[P.g.ya];
        h && a.metadata.redact_click_ids && (h = ij(String(h)));
        z(f, function(r, t) {
            if (null != t)
                if ("~oref" === r)
                    h = t;
                else {
                    var u = encodeURIComponent(r);
                    null != d[u] && O(141);
                    e(u, t)
                }
        });
        var m = W(P.g.P)
          , n = a.metadata.user_data;
        if (n && m) {
            var p = Ah(n);
            p && c.push(p.then(function(r) {
                return e("em", r.Sj)
            }))
        }
        var q = function() {
            h && e("~oref", h);
            b(d)
        };
        if (c.length)
            try {
                Promise.all(c).then(function() {
                    q()
                });
                return
            } catch (r) {}
        q()
    }
      , ZC = function(a) {
        "page_view" === a.metadata.hit_type ? su(a) : YC(a, function(b) {
            var c = a.metadata.parsed_target
              , d = UC(a)
              , e = d.baseUrl
              , f = d.Pm
              , g = [];
            z(b, function(p, q) {
                g.push(p + "=" + q)
            });
            var h = e + g.join(";") + "?";
            f ? yc(h, a.o.onSuccess) : zc(h, a.o.onSuccess, a.o.onFailure);
            if (a.metadata.attribution_reporting_experiment) {
                var m = "" + pj("https://ad.doubleclick.net") + "/activity;register_conversion=1;" + g.join(";") + "?";
                zc(m, void 0, void 0, {
                    attributionsrc: ""
                })
            }
            if (a.metadata.send_fledge_experiment) {
                var n = zt() + "/td/fls/rul/activityi;fledge=1;" + g.join(";") + "?";
                wt(n, Jj(c.target.id))
            }
        })
    };
    var $C = function() {
        return [P.g.R, P.g.P]
    }
      , bD = function(a) {
        var b = cm(a);
        if (b && (1 === b.ma.length || 3 === b.ma.length)) {
            var c = b.ma[fm[4]] || ""
              , d = b.ma[fm[5]]
              , e = ""
              , f = "unknown";
            if (d) {
                var g = d.split("+");
                if (2 !== g.length)
                    return;
                e = g[0];
                f = aD[g[1].toLowerCase()]
            }
            if (f)
                return {
                    target: b,
                    il: c,
                    jl: e,
                    rl: f
                }
        }
    }
      , cD = function(a) {
        Dr(a);
    }
      , dD = function(a) {
        var b = Lb(tm(a.o, P.g.la, 1), ".")
          , c = Lb(tm(a.o, P.g.la, 2), ".");
        a.D[P.g.rb] = b;
        a.D[P.g.ob] = c
    }
      , eD = function(a) {
        if (!a.metadata.consent_updated) {
            var b = U(a.o, P.g.Hi);
            if (Xa(b) && b.exclusion_parameters && b.engines)
                if (Sn()) {} else {
                    var c = !1 !== U(a.o, P.g.wa)
                      , d = Zq(a)
                      , e = function() {
                        if (W($C())) {
                            var f = {
                                config: b,
                                gtm: Un({
                                    za: a.metadata.source_canonical_id
                                })
                            };
                            c && ($o(d),
                            f.auiddc = Yo[ap(d.prefix)]);
                            void 0 === G.__dc_ns_processor && (G.__dc_ns_processor = []);
                            G.__dc_ns_processor.push(f);
                            wc("https://www.googletagmanager.com/dclk/ns/v1.js")
                        }
                    };
                    W($C()) ? e() : Nl(e, $C())
                }
        }
    }
      , hD = function(a, b, c, d) {
        function e() {
            for (var p = na(g), q = p.next(); !q.done; q = p.next()) {
                var r = q.value;
                if (!r.metadata.consent_updated || "page_view" === r.metadata.hit_type || W($C())) {
                    for (var t = na("page_view" === r.metadata.hit_type ? fD : gD), u = t.next(); !u.done; u = t.next()) {
                        var v = u.value;
                        v(r);
                        if (r.isAborted)
                            break
                    }
                    r.metadata.speculative || r.isAborted || ZC(r)
                }
            }
        }
        var f = bD(a);
        if (f) {
            var g = []
              , h = new Cq(f.target,b,d);
            h.metadata.parsed_target = f;
            h.metadata.counting_method = f.rl;
            g.push(h);
            if (T(14) && b === P.g.fa) {
                var m = new Cq(f.target,b,d);
                m.metadata.hit_type = "page_view";
                m.metadata.speculative = !0;
                g.push(m)
            }
            var n = $C();
            Xl(function() {
                e();
                W(n) || Wl(function(p) {
                    for (var q = p.consentEventId, r = p.consentPriorityId, t = na(g), u = t.next(); !u.done; u = t.next()) {
                        var v = u.value;
                        v.metadata.consent_updated = !0;
                        v.metadata.consent_event_id = q;
                        v.metadata.consent_priority_id = r
                    }
                    e(q, r)
                }, n)
            }, n)
        } else
            I(d.onFailure)
    }
      , gD = [fr, function(a) {
        a.metadata.conversion_linker_enabled = !1 !== U(a.o, P.g.wa);
        var b = !0 === U(a.o, P.g.We)
          , c = W($C());
        if (Sn() && b) {
            b = !1
        }
        a.metadata.send_as_iframe = b && c;
        var d = U(a.o, P.g.ja);
        a.metadata.redact_ads_data = void 0 != d && !1 !== d;
        a.metadata.redact_click_ids = a.metadata.redact_ads_data && !W($C());
        a.metadata.cookie_options = Zq(a)
    }
    , function(a) {
        if (!a.metadata.consent_updated) {
            var b = a.o.isGtmEvent ? U(a.o, "oref") : ej(hj(G.location.href));
            a.D[P.g.ya] = b
        }
    }
    , function(a) {
        if (a.eventName === P.g.Ra && !a.o.isGtmEvent) {
            if (!a.metadata.consent_updated) {
                var b = {
                    callback: U(a.o, P.g.Eb),
                    Rj: U(a.o, U(a.o, P.g.qb)),
                    lk: U(a.o, P.g.qb)
                };
                er(b, a.metadata.cookie_options, a.metadata.redact_ads_data, wq)
            }
            a.isAborted = !0
        }
    }
    , function(a) {
        if (a.eventName === P.g.fa && !a.o.isGtmEvent) {
            if (!a.metadata.consent_updated && !T(14)) {
                var b = a.metadata.conversion_linker_enabled
                  , c = a.metadata.cookie_options
                  , d = a.metadata.redact_ads_data;
                br({
                    vd: b,
                    zd: U(a.o, P.g.xa) || {},
                    Fd: U(a.o, P.g.Va),
                    za: a.metadata.source_canonical_id,
                    allowAdPersonalizationSignals: yn(a.o),
                    Bd: d,
                    kk: U(a.o, P.g.Da)
                }, c);
                eD(a);
                var e = a.metadata.parsed_target.target
                  , f = Lb(tm(a.o, P.g.la, 2), ".")
                  , g = Lb(tm(a.o, P.g.la, 1), ".")
                  , h = T(66) ? cl(!0) : void 0;
                nr({
                    bh: !0,
                    fc: b ? c : void 0,
                    jh: f,
                    o: a.o,
                    rh: g,
                    Lf: b,
                    Bd: d,
                    targetId: 1 < e.ma.length ? e.id : "",
                    uh: h
                })
            }
            a.isAborted = !0
        }
    }
    , function(a) {
        var b = a.metadata.parsed_target
          , c = {}
          , d = U(a.o, P.g.Zc);
        Xa(d) && z(d, function(e, f) {
            null != f && (c[e] = f)
        });
        a.D[P.g.og] = b.target.ma[fm[3]];
        a.D[P.g.Mi] = b.il;
        a.D[P.g.Li] = b.jl;
        a.D[P.g.Zc] = c
    }
    , function(a) {
        var b = a.metadata.counting_method;
        switch (b) {
        case "standard":
            a.D[P.g.Ca] = tb(1E11, 1E13);
            return;
        case "unique":
            a.D[P.g.Ca] = "1";
            a.D[P.g.Oi] = tb(1E11, 1E13);
            return;
        case "per_session":
            var c = U(a.o, P.g.tb);
            a.D[P.g.Ca] = c;
            return
        }
        var d = "transactions" === b ? "1" : U(a.o, P.g.ld);
        a.D[P.g.ld] = d;
        a.copyToHitData(P.g.qa);
        a.copyToHitData(P.g.Ca)
    }
    , function(a) {
        a.o.isGtmEvent && (a.copyToHitData(P.g.Qi),
        a.copyToHitData(P.g.Pi),
        a.copyToHitData(P.g.pg))
    }
    , function(a) {
        a.metadata.consent_updated && (a.D[P.g.mc] = "1")
    }
    , function(a) {
        var b = sn();
        b && (a.D[P.g.Ac] = b);
        var c = qn();
        c && (a.D[P.g.Cc] = c)
    }
    , function(a) {
        "1" === Mo(!1)._up && (a.D[P.g.ae] = "1")
    }
    , function(a) {
        yn(a.o) ? a.D[P.g.Mb] = "0" : a.D[P.g.Mb] = "1"
    }
    , function(a) {
        if (a.metadata.conversion_linker_enabled) {
            var b = W($C())
              , c = a.metadata.cookie_options
              , d = a.metadata.redact_ads_data
              , e = wq(c.prefix, d)
              , f = !1;
            $o(c);
            var g = b ? Yo[ap(c.prefix)] : void 0;
            e && e.length && (a.D[P.g.gg] = e.join("."),
            f = !0);
            if (a.metadata.send_as_iframe) {
                var h = "_gcl" !== Gp(c.prefix), m;
                if (!(m = f)) {
                    var n = c.prefix;
                    m = !(jj("gclaw") || jj("gac") || 0 < (Qp().aw || []).length ? 0 : 0 < (Qp().gb || []).length || T(51) && void 0 !== Qp().gbraid || kq(n, !0))
                }
                if (m) {
                    var p = vq(c.prefix, d);
                    p && p.length && (a.D[P.g.Sa] = p.join("."),
                    O(59));
                    var q, r = jj("gac");
                    (q = r ? !W(qq()) && d ? "0" : decodeURIComponent(r) : pq(Ap(zp()) ? kp() : {})) && (h || (a.D[P.g.Yd] = q))
                } else {
                    var t;
                    a: {
                        var u = c.prefix
                          , v = jj("gclgb");
                        if (v)
                            t = v.split(".");
                        else {
                            var w = Gp(u);
                            if ("_gcl" === w) {
                                var y = !W(qq()) && d
                                  , x = Qp()
                                  , B = [];
                                x.wbraid && B.push(x.wbraid);
                                T(51) && x.gbraid && B.push(x.gbraid);
                                if (0 < B.length) {
                                    t = y ? ["0"] : B;
                                    break a
                                }
                            }
                            t = Ep({
                                prefix: w
                            })
                        }
                    }
                    var A = t;
                    A.length && (a.D[P.g.jb] = A.join("."));
                    if (!h) {
                        var D, E = jj("gacgb");
                        (D = E ? !W(qq()) && d ? "0" : decodeURIComponent(E) : pq(Ap(zp()) ? kp("_gac_gb", !0) : {})) && (a.D[P.g.zc] = D)
                    }
                }
            }
            g && (a.D[P.g.Cb] = g)
        }
    }
    , function(a) {
        var b = a.metadata.counting_method;
        if ("transactions" === b || "items_sold" === b) {
            var c = a.o.isGtmEvent
              , d = U(a.o, P.g.ia);
            if (Array.isArray(d)) {
                for (var e = 0; e < d.length; e++) {
                    var f = d[e];
                    Xa(f) && !c && (f[P.g.xc] = U(a.o, P.g.xc),
                    f[P.g.Pa] = U(a.o, P.g.Pa),
                    f.accountId = void 0)
                }
                a.D[P.g.ia] = d
            }
        }
    }
    , function(a) {
        var b = U(a.o, P.g.Yc)
          , c = {};
        Xa(b) && z(b, function(g, h) {
            l(h) && iD.test(g) && (c[g] = h)
        });
        for (var d = sm(a.o), e = 0; e < d.length; e++) {
            var f = d[e];
            iD.test(f) && (c[f] = f)
        }
        z(c, function(g, h) {
            a.D[g] = U(a.o, h)
        })
    }
    , dD, function(a) {
        var b;
        if (b = W($C()))
            a: {
                if (!jD && !tt("attribution-reporting")) {
                    if (!al('')) {
                        b = !1;
                        break a
                    }
                    jD = !0
                }
                b = tt("attribution-reporting") ? !0 : !1
            }
        var c = b;
        if (a.metadata.attribution_reporting_experiment = c)
            a.D[P.g.Sb] = "1",
            a.D[P.g.Ni] = tb()
    }
    , function(a) {
        if (a.o.isGtmEvent) {
            var b = U(a.o, P.g.Ga);
            Xa(b) && (a.metadata.user_data = b)
        }
    }
    , function(a) {
        if (!mt(G))
            O(87);
        else if (void 0 !== ot) {
            O(85);
            var b = kt();
            b ? st(b, a) : O(86)
        }
    }
    , function(a) {
        T(37) && !1 !== U(a.o, P.g.Ea) && W($C()) && yn(a.o) && vt() && (a.metadata.send_fledge_experiment = !0)
    }
    , function(a) {
        if (Dq(a, "ccd_add_1p_data", !1) && W(P.g.P)) {
            var b = a.o.F[P.g.fe];
            if (Pi(b)) {
                var c = U(a.o, P.g.Ga);
                null === c ? a.metadata.user_data_from_code = null : (b.enable_code && Xa(c) && (a.metadata.user_data_from_code = c),
                Xa(b.selectors) && (a.metadata.user_data_from_manual = Oi(b.selectors)))
            }
        }
    }
    , gr, hr, cD]
      , fD = [ar, dD, eD, cD]
      , aD = {
        "": "unknown",
        standard: "standard",
        unique: "unique",
        per_session: "per_session",
        transactions: "transactions",
        items_sold: "items_sold"
    }
      , iD = /^u([1-9]\d?|100)$/
      , jD = !1;
    var xD = function() {
        var a = !0;
        tn(7) && tn(9) && tn(10) || (a = !1);
        return a
    };
    var BD = function(a, b) {
        if (!b.isGtmEvent) {
            var c = U(b, P.g.qb)
              , d = U(b, P.g.Eb)
              , e = U(b, c);
            if (void 0 === e) {
                var f = void 0;
                yD.hasOwnProperty(c) ? f = yD[c] : zD.hasOwnProperty(c) && (f = zD[c]);
                1 === f && (f = AD(c));
                l(f) ? mw()(function() {
                    var g = mw().getByName(a).get(f);
                    d(g)
                }) : d(void 0)
            } else
                d(e)
        }
    }
      , CD = function(a, b) {
        var c = a[P.g.Hb]
          , d = b + "."
          , e = a[P.g.Z] || ""
          , f = void 0 === c ? !!a.use_anchor : "fragment" === c
          , g = !!a[P.g.sb];
        e = String(e).replace(/\s+/g, "").split(",");
        var h = mw();
        h(d + "require", "linker");
        h(d + "linker:autoLink", e, f, g)
    }
      , GD = function(a, b, c) {
        if (!c.isGtmEvent || !DD[a]) {
            var d = !W(P.g.W)
              , e = function(f) {
                var g, h, m = mw(), n = ED(b, "", c), p, q = n.createOnlyFields._useUp;
                if (c.isGtmEvent || FD(b, n.createOnlyFields)) {
                    c.isGtmEvent && (g = "gtm" + yi(),
                    h = n.createOnlyFields,
                    n.gtmTrackerName && (h.name = g));
                    m(function() {
                        var t = m.getByName(b);
                        t && (p = t.get("clientId"));
                        c.isGtmEvent || m.remove(b)
                    });
                    m("create", a, c.isGtmEvent ? h : n.createOnlyFields);
                    d && W(P.g.W) && (d = !1,
                    m(function() {
                        var t = mw().getByName(c.isGtmEvent ? g : b);
                        !t || t.get("clientId") == p && q || (c.isGtmEvent ? (n.fieldsToSet["&gcu"] = "1",
                        n.fieldsToSet["&sst.gcut"] = ci[f]) : (n.fieldsToSend["&gcu"] = "1",
                        n.fieldsToSend["&sst.gcut"] = ci[f]),
                        t.set(n.fieldsToSet),
                        c.isGtmEvent ? t.send("pageview") : t.send("pageview", n.fieldsToSend))
                    }));
                    c.isGtmEvent && m(function() {
                        m.remove(g)
                    })
                }
            };
            Wl(function() {
                return e(P.g.W)
            }, P.g.W);
            Wl(function() {
                return e(P.g.R)
            }, P.g.R);
            Wl(function() {
                return e(P.g.P)
            }, P.g.P);
            c.isGtmEvent && (DD[a] = !0)
        }
    }
      , HD = function(a, b) {
        nj() && b && (a[P.g.pb] = b)
    }
      , QD = function(a, b, c) {
        function d() {
            var N = U(c, P.g.Yc);
            h(function() {
                if (!c.isGtmEvent && Xa(N)) {
                    var Q = u.fieldsToSend, V = m().getByName(n), ca;
                    for (ca in N)
                        if (void 0 != N[ca] && /^(dimension|metric)\d+$/.test(ca)) {
                            var Z = V.get(AD(N[ca]));
                            ID(Q, ca, Z)
                        }
                }
            })
        }
        function e() {
            if (u.displayfeatures) {
                var N = "_dc_gtm_" + f.replace(/[^A-Za-z0-9-]/g, "");
                p("require", "displayfeatures", void 0, {
                    cookieName: N
                })
            }
        }
        var f = a, g, h = c.isGtmEvent ? nw(U(c, "gaFunctionName")) : nw();
        if (pb(h)) {
            var m = mw, n;
            c.isGtmEvent ? n = U(c, "name") || U(c, "gtmTrackerName") : n = "gtag_" + f.split("-").join("_");
            var p = function(N) {
                var Q = [].slice.call(arguments, 0);
                Q[0] = n ? n + "." + Q[0] : "" + Q[0];
                h.apply(window, Q)
            }
              , q = function(N) {
                var Q = function(ka, ha) {
                    for (var ja = 0; ha && ja < ha.length; ja++)
                        p(ka, ha[ja])
                }
                  , V = c.isGtmEvent
                  , ca = V ? JD(u) : KD(b, c);
                if (ca) {
                    var Z = {};
                    HD(Z, N);
                    p("require", "ec", "ec.js", Z);
                    V && ca.eh && p("set", "&cu", ca.eh);
                    var R = ca.action;
                    if (V || "impressions" === R)
                        if (Q("ec:addImpression", ca.Pj),
                        !V)
                            return;
                    if ("promo_click" === R || "promo_view" === R || V && ca.Pe) {
                        var oa = ca.Pe;
                        Q("ec:addPromo", oa);
                        if (oa && 0 < oa.length && "promo_click" === R) {
                            V ? p("ec:setAction", R, ca.ub) : p("ec:setAction", R);
                            return
                        }
                        if (!V)
                            return
                    }
                    "promo_view" !== R && "impressions" !== R && (Q("ec:addProduct", ca.Mc),
                    p("ec:setAction", R, ca.ub))
                }
            }
              , r = function(N) {
                if (N) {
                    var Q = {};
                    if (Xa(N))
                        for (var V in LD)
                            LD.hasOwnProperty(V) && MD(LD[V], V, N[V], Q);
                    HD(Q, x);
                    p("require", "linkid", Q)
                }
            }
              , t = function() {
                if (Sn()) {} else {
                    var N = U(c, P.g.Si);
                    N && (p("require", N, {
                        dataLayer: hi.Ya
                    }),
                    p("require", "render"))
                }
            }
              , u = ED(n, b, c)
              , v = function(N, Q, V) {
                V && (Q = "" + Q);
                u.fieldsToSend[N] = Q
            };
            !c.isGtmEvent && FD(n, u.createOnlyFields) && (h(function() {
                m() && m().remove(n)
            }),
            ND[n] = !1);
            h("create", f, u.createOnlyFields);
            var w = c.isGtmEvent && u.fieldsToSet[P.g.pb];
            if (!c.isGtmEvent && u.createOnlyFields[P.g.pb] || w) {
                var y = mj() ? lj(c.isGtmEvent ? u.fieldsToSet[P.g.pb] : u.createOnlyFields[P.g.pb], "/analytics.js") : void 0;
                y && (g = y)
            }
            var x = c.isGtmEvent ? u.fieldsToSet[P.g.pb] : u.createOnlyFields[P.g.pb];
            if (x) {
                var B = c.isGtmEvent ? u.fieldsToSet[P.g.Xd] : u.createOnlyFields[P.g.Xd];
                B && !ND[n] && (ND[n] = !0,
                h(qw(n, B)))
            }
            c.isGtmEvent ? u.enableRecaptcha && p("require", "recaptcha", "recaptcha.js") : (d(),
            r(u.linkAttribution));
            var A = u[P.g.xa];
            A && A[P.g.Z] && CD(A, n);
            p("set", u.fieldsToSet);
            if (c.isGtmEvent) {
                if (u.enableLinkId) {
                    var D = {};
                    HD(D, x);
                    p("require", "linkid", "linkid.js", D)
                }
                GD(f, n, c)
            }
            if (b === P.g.Qb)
                if (c.isGtmEvent) {
                    e();
                    if (u.remarketingLists) {
                        var E = "_dc_gtm_" + f.replace(/[^A-Za-z0-9-]/g, "");
                        p("require", "adfeatures", {
                            cookieName: E
                        })
                    }
                    q(x);
                    p("send", "pageview");
                    u.createOnlyFields._useUp && ow(n + ".")
                } else
                    t(),
                    p("send", "pageview", u.fieldsToSend);
            else
                b === P.g.fa ? (t(),
                Ar(f, c),
                U(c, P.g.Va) && (cq(["aw", "dc"]),
                ow(n + ".")),
                eq(["aw", "dc"]),
                0 != u.sendPageView && p("send", "pageview", u.fieldsToSend),
                GD(f, n, c)) : b === P.g.Ra ? BD(n, c) : "screen_view" === b ? p("send", "screenview", u.fieldsToSend) : "timing_complete" === b ? (u.fieldsToSend.hitType = "timing",
                v("timingCategory", u.eventCategory, !0),
                c.isGtmEvent ? v("timingVar", u.timingVar, !0) : v("timingVar", u.name, !0),
                v("timingValue", xb(u.value)),
                void 0 !== u.eventLabel && v("timingLabel", u.eventLabel, !0),
                p("send", u.fieldsToSend)) : "exception" === b ? p("send", "exception", u.fieldsToSend) : "" === b && c.isGtmEvent || ("track_social" === b && c.isGtmEvent ? (u.fieldsToSend.hitType = "social",
                v("socialNetwork", u.socialNetwork, !0),
                v("socialAction", u.socialAction, !0),
                v("socialTarget", u.socialTarget, !0)) : ((c.isGtmEvent || OD[b]) && q(x),
                c.isGtmEvent && e(),
                u.fieldsToSend.hitType = "event",
                v("eventCategory", u.eventCategory, !0),
                v("eventAction", u.eventAction || b, !0),
                void 0 !== u.eventLabel && v("eventLabel", u.eventLabel, !0),
                void 0 !== u.value && v("eventValue", xb(u.value))),
                p("send", u.fieldsToSend));
            var C = g && !c.eventMetadata.suppress_script_load;
            if (!PD && (!c.isGtmEvent || C)) {
                g = g || "https://www.google-analytics.com/analytics.js";
                PD = !0;
                var F = function() {
                    c.onFailure()
                }
                  , L = function() {
                    m().loaded || F()
                };
                Sn() ? I(L) : wc(g, L, F)
            }
        } else
            I(c.onFailure)
    }
      , RD = function(a, b, c, d) {
        Xl(function() {
            QD(a, b, d)
        }, [P.g.W, P.g.R])
    }
      , TD = function(a) {
        function b(e) {
            function f(h, m) {
                for (var n = 0; n < m.length; n++) {
                    var p = m[n];
                    if (e[p]) {
                        g[h] = e[p];
                        break
                    }
                }
            }
            var g = k(e);
            f("id", ["id", "item_id", "promotion_id"]);
            f("name", ["name", "item_name", "promotion_name"]);
            f("brand", ["brand", "item_brand"]);
            f("variant", ["variant", "item_variant"]);
            f("list", ["list_name", "item_list_name"]);
            f("position", ["list_position", "creative_slot", "index"]);
            (function() {
                if (e.category)
                    g.category = e.category;
                else {
                    for (var h = "", m = 0; m < SD.length; m++)
                        void 0 !== e[SD[m]] && (h && (h += "/"),
                        h += e[SD[m]]);
                    h && (g.category = h)
                }
            }
            )();
            f("listPosition", ["list_position"]);
            f("creative", ["creative_name"]);
            f("list", ["list_name"]);
            f("position", ["list_position", "creative_slot"]);
            return g
        }
        for (var c = [], d = 0; a && d < a.length; d++)
            a[d] && Xa(a[d]) && c.push(b(a[d]));
        return c.length ? c : void 0
    }
      , UD = function(a) {
        return W(a)
    }
      , VD = !1;
    var PD, ND = {}, DD = {}, WD = {}, XD = Object.freeze((WD.page_hostname = 1,
    WD[P.g.oa] = 1,
    WD[P.g.kb] = 1,
    WD[P.g.Ta] = 1,
    WD[P.g.Ua] = 1,
    WD[P.g.ab] = 1,
    WD[P.g.vc] = 1,
    WD[P.g.Db] = 1,
    WD[P.g.Oa] = 1,
    WD[P.g.wc] = 1,
    WD[P.g.ya] = 1,
    WD[P.g.kd] = 1,
    WD[P.g.Fa] = 1,
    WD[P.g.Ib] = 1,
    WD)), YD = {}, yD = Object.freeze((YD.client_storage = "storage",
    YD.sample_rate = 1,
    YD.site_speed_sample_rate = 1,
    YD.store_gac = 1,
    YD.use_amp_client_id = 1,
    YD[P.g.lb] = 1,
    YD[P.g.wa] = "storeGac",
    YD[P.g.Ta] = 1,
    YD[P.g.Ua] = 1,
    YD[P.g.ab] = 1,
    YD[P.g.vc] = 1,
    YD[P.g.Db] = 1,
    YD[P.g.wc] = 1,
    YD)), ZD = {}, $D = Object.freeze((ZD._cs = 1,
    ZD._useUp = 1,
    ZD.allowAnchor = 1,
    ZD.allowLinker = 1,
    ZD.alwaysSendReferrer = 1,
    ZD.clientId = 1,
    ZD.cookieDomain = 1,
    ZD.cookieExpires = 1,
    ZD.cookieFlags = 1,
    ZD.cookieName = 1,
    ZD.cookiePath = 1,
    ZD.cookieUpdate = 1,
    ZD.legacyCookieDomain = 1,
    ZD.legacyHistoryImport = 1,
    ZD.name = 1,
    ZD.sampleRate = 1,
    ZD.siteSpeedSampleRate = 1,
    ZD.storage = 1,
    ZD.storeGac = 1,
    ZD.useAmpClientId = 1,
    ZD._cd2l = 1,
    ZD)), aE = Object.freeze({
        anonymize_ip: 1
    }), bE = {}, zD = Object.freeze((bE.campaign = {
        content: "campaignContent",
        id: "campaignId",
        medium: "campaignMedium",
        name: "campaignName",
        source: "campaignSource",
        term: "campaignKeyword"
    },
    bE.app_id = 1,
    bE.app_installer_id = 1,
    bE.app_name = 1,
    bE.app_version = 1,
    bE.description = "exDescription",
    bE.fatal = "exFatal",
    bE.language = 1,
    bE.page_hostname = "hostname",
    bE.transport_type = "transport",
    bE[P.g.Ba] = "currencyCode",
    bE[P.g.xg] = 1,
    bE[P.g.ya] = "location",
    bE[P.g.kd] = "page",
    bE[P.g.Fa] = "referrer",
    bE[P.g.Ib] = "title",
    bE[P.g.kf] = 1,
    bE[P.g.Da] = 1,
    bE)), cE = {}, dE = Object.freeze((cE.content_id = 1,
    cE.event_action = 1,
    cE.event_category = 1,
    cE.event_label = 1,
    cE.link_attribution = 1,
    cE.name = 1,
    cE[P.g.xa] = 1,
    cE[P.g.wg] = 1,
    cE[P.g.Ka] = 1,
    cE[P.g.qa] = 1,
    cE)), eE = Object.freeze({
        displayfeatures: 1,
        enableLinkId: 1,
        enableRecaptcha: 1,
        eventAction: 1,
        eventCategory: 1,
        eventLabel: 1,
        gaFunctionName: 1,
        gtmEcommerceData: 1,
        gtmTrackerName: 1,
        linker: 1,
        remarketingLists: 1,
        socialAction: 1,
        socialNetwork: 1,
        socialTarget: 1,
        timingVar: 1,
        value: 1
    }), SD = Object.freeze(["item_category", "item_category2", "item_category3", "item_category4", "item_category5"]), fE = {}, LD = Object.freeze((fE.levels = 1,
    fE[P.g.Ua] = "duration",
    fE[P.g.vc] = 1,
    fE)), gE = {}, hE = Object.freeze((gE.anonymize_ip = 1,
    gE.fatal = 1,
    gE.send_page_view = 1,
    gE.store_gac = 1,
    gE.use_amp_client_id = 1,
    gE[P.g.wa] = 1,
    gE[P.g.xg] = 1,
    gE)), MD = function(a, b, c, d) {
        if (void 0 !== c)
            if (hE[b] && (c = yb(c)),
            "anonymize_ip" !== b || c || (c = void 0),
            1 === a)
                d[AD(b)] = c;
            else if (l(a))
                d[a] = c;
            else
                for (var e in a)
                    a.hasOwnProperty(e) && void 0 !== c[e] && (d[a[e]] = c[e])
    }, AD = function(a) {
        return a && l(a) ? a.replace(/(_[a-z])/g, function(b) {
            return b[1].toUpperCase()
        }) : a
    }, iE = {}, OD = Object.freeze((iE.checkout_progress = 1,
    iE.select_content = 1,
    iE.set_checkout_option = 1,
    iE[P.g.nc] = 1,
    iE[P.g.oc] = 1,
    iE[P.g.Pb] = 1,
    iE[P.g.qc] = 1,
    iE[P.g.hb] = 1,
    iE[P.g.Bb] = 1,
    iE[P.g.ib] = 1,
    iE[P.g.Ja] = 1,
    iE[P.g.sc] = 1,
    iE[P.g.Na] = 1,
    iE)), jE = {}, kE = Object.freeze((jE.checkout_progress = 1,
    jE.set_checkout_option = 1,
    jE[P.g.Xf] = 1,
    jE[P.g.Yf] = 1,
    jE[P.g.nc] = 1,
    jE[P.g.oc] = 1,
    jE[P.g.Zf] = 1,
    jE[P.g.Pb] = 1,
    jE[P.g.Ja] = 1,
    jE[P.g.sc] = 1,
    jE[P.g.cg] = 1,
    jE)), lE = {}, mE = Object.freeze((lE.generate_lead = 1,
    lE.login = 1,
    lE.search = 1,
    lE.select_content = 1,
    lE.share = 1,
    lE.sign_up = 1,
    lE.view_search_results = 1,
    lE[P.g.qc] = 1,
    lE[P.g.hb] = 1,
    lE[P.g.Bb] = 1,
    lE[P.g.ib] = 1,
    lE[P.g.Na] = 1,
    lE)), nE = function(a) {
        var b = "general";
        kE[a] ? b = "ecommerce" : mE[a] ? b = "engagement" : "exception" === a && (b = "error");
        return b
    }, oE = {}, pE = Object.freeze((oE.view_search_results = 1,
    oE[P.g.hb] = 1,
    oE[P.g.ib] = 1,
    oE[P.g.Na] = 1,
    oE)), ID = function(a, b, c) {
        a.hasOwnProperty(b) || (a[b] = c)
    }, qE = function(a) {
        if (Array.isArray(a)) {
            for (var b = [], c = 0; c < a.length; c++) {
                var d = a[c];
                if (void 0 != d) {
                    var e = d.id
                      , f = d.variant;
                    void 0 != e && void 0 != f && b.push(String(e) + "." + String(f))
                }
            }
            return 0 < b.length ? b.join("!") : void 0
        }
    }, ED = function(a, b, c) {
        var d = function(N) {
            return U(c, N)
        }
          , e = {}
          , f = {}
          , g = {}
          , h = {}
          , m = qE(d(P.g.Ji));
        !c.isGtmEvent && m && ID(f, "exp", m);
        g["&gtm"] = Un({
            za: c.eventMetadata.source_canonical_id,
            Hf: !0
        });
        c.isGtmEvent || (g._no_slc = !0);
        Jl() && (h._cs = UD);
        var n = d(P.g.Yc);
        if (!c.isGtmEvent && Xa(n))
            for (var p in n)
                if (n.hasOwnProperty(p) && /^(dimension|metric)\d+$/.test(p) && void 0 != n[p]) {
                    var q = d(String(n[p]));
                    void 0 !== q && ID(f, p, q)
                }
        for (var r = !c.isGtmEvent, t = sm(c), u = 0; u < t.length; ++u) {
            var v = t[u];
            if (c.isGtmEvent) {
                var w = d(v);
                eE.hasOwnProperty(v) ? e[v] = w : $D.hasOwnProperty(v) ? h[v] = w : g[v] = w
            } else {
                var y = void 0;
                y = v !== P.g.la ? d(v) : tm(c, v);
                if (dE.hasOwnProperty(v))
                    MD(dE[v], v, y, e);
                else if (aE.hasOwnProperty(v))
                    MD(aE[v], v, y, g);
                else if (zD.hasOwnProperty(v))
                    MD(zD[v], v, y, f);
                else if (yD.hasOwnProperty(v))
                    MD(yD[v], v, y, h);
                else if (/^(dimension|metric|content_group)\d+$/.test(v))
                    MD(1, v, y, f);
                else if (v === P.g.la) {
                    if (!VD) {
                        var x = Lb(y);
                        x && (f["&did"] = x)
                    }
                    var B = void 0
                      , A = void 0;
                    b === P.g.fa ? B = Lb(tm(c, v), ".") : (B = Lb(tm(c, v, 1), "."),
                    A = Lb(tm(c, v, 2), "."));
                    B && (f["&gdid"] = B);
                    A && (f["&edid"] = A)
                } else
                    v === P.g.Oa && 0 > t.indexOf(P.g.vc) && (h.cookieName = y + "_ga");
                T(87) && XD[v] && (c.H.hasOwnProperty(v) || b === P.g.fa && c.m.hasOwnProperty(v)) && (r = !1)
            }
        }
        T(87) && r && (f["&jsscut"] = "1");
        !1 !== d(P.g.Xe) && !1 !== d(P.g.kb) && xD() || (g.allowAdFeatures = !1);
        g.allowAdPersonalizationSignals = yn(c);
        !c.isGtmEvent && d(P.g.Va) && (h._useUp = !0);
        if (c.isGtmEvent) {
            h.name = h.name || e.gtmTrackerName;
            var D = g.hitCallback;
            g.hitCallback = function() {
                pb(D) && D();
                c.onSuccess()
            }
        } else {
            ID(h, "cookieDomain", "auto");
            ID(g, "forceSSL", !0);
            ID(e, "eventCategory", nE(b));
            pE[b] && ID(f, "nonInteraction", !0);
            "login" === b || "sign_up" === b || "share" === b ? ID(e, "eventLabel", d(P.g.wg)) : "search" === b || "view_search_results" === b ? ID(e, "eventLabel", d(P.g.Xi)) : "select_content" === b && ID(e, "eventLabel", d(P.g.Di));
            var E = e[P.g.xa] || {}
              , C = E[P.g.Bc];
            C || 0 != C && E[P.g.Z] ? h.allowLinker = !0 : !1 === C && ID(h, "useAmpClientId", !1);
            f.hitCallback = c.onSuccess;
            h.name = a
        }
        zn() && (g["&gcs"] = An());
        g["&gcd"] = En(c);
        Jl() && (W(P.g.W) || (h.storage = "none"),
        W([P.g.R, P.g.P]) || (g.allowAdFeatures = !1,
        h.storeGac = !1));
        Qn() && (g["&dma_cps"] = Fn());
        g["&dma"] = Pn();
        cn(ln()) && (g["&tcfd"] = Rn());
        Ai.m && (g["&tag_exp"] = Ai.m);
        var F = oj(c) || d(P.g.pb)
          , L = d(P.g.Xd);
        F && (c.isGtmEvent || (h[P.g.pb] = F),
        h._cd2l = !0);
        L && !c.isGtmEvent && (h[P.g.Xd] = L);
        e.fieldsToSend = f;
        e.fieldsToSet = g;
        e.createOnlyFields = h;
        return e
    }, JD = function(a) {
        var b = a.gtmEcommerceData;
        if (!b)
            return null;
        var c = {};
        b.currencyCode && (c.eh = b.currencyCode);
        if (b.impressions) {
            c.action = "impressions";
            var d = b.impressions;
            c.Pj = "impressions" === b.translateIfKeyEquals ? TD(d) : d
        }
        if (b.promoView) {
            c.action = "promo_view";
            var e = b.promoView.promotions;
            c.Pe = "promoView" === b.translateIfKeyEquals ? TD(e) : e
        }
        if (b.promoClick) {
            c.action = "promo_click";
            var f = b.promoClick.promotions;
            c.Pe = "promoClick" === b.translateIfKeyEquals ? TD(f) : f;
            c.ub = b.promoClick.actionField;
            return c
        }
        for (var g in b)
            if (void 0 !== b[g] && "translateIfKeyEquals" !== g && "impressions" !== g && "promoView" !== g && "promoClick" !== g && "currencyCode" !== g) {
                c.action = g;
                var h = b[g].products;
                c.Mc = "products" === b.translateIfKeyEquals ? TD(h) : h;
                c.ub = b[g].actionField;
                break
            }
        return Object.keys(c).length ? c : null
    }, KD = function(a, b) {
        function c(u) {
            return {
                id: d(P.g.Ca),
                affiliation: d(P.g.ig),
                revenue: d(P.g.qa),
                tax: d(P.g.cf),
                shipping: d(P.g.dd),
                coupon: d(P.g.jg),
                list: d(P.g.bf) || d(P.g.bd) || u
            }
        }
        for (var d = function(u) {
            return U(b, u)
        }, e = d(P.g.ia), f, g = 0; e && g < e.length && !(f = e[g][P.g.bf] || e[g][P.g.bd]); g++)
            ;
        var h = d(P.g.Yc);
        if (Xa(h))
            for (var m = 0; e && m < e.length; ++m) {
                var n = e[m], p;
                for (p in h)
                    h.hasOwnProperty(p) && /^(dimension|metric)\d+$/.test(p) && void 0 != h[p] && ID(n, p, n[h[p]])
            }
        var q = null
          , r = d(P.g.Ii);
        if (a === P.g.Ja || a === P.g.sc)
            q = {
                action: a,
                ub: c(),
                Mc: TD(e)
            };
        else if (a === P.g.nc)
            q = {
                action: "add",
                ub: c(),
                Mc: TD(e)
            };
        else if (a === P.g.oc)
            q = {
                action: "remove",
                ub: c(),
                Mc: TD(e)
            };
        else if (a === P.g.Na)
            q = {
                action: "detail",
                ub: c(f),
                Mc: TD(e)
            };
        else if (a === P.g.hb)
            q = {
                action: "impressions",
                Pj: TD(e)
            };
        else if (a === P.g.ib)
            q = {
                action: "promo_view",
                Pe: TD(r) || TD(e)
            };
        else if ("select_content" === a && r && 0 < r.length || a === P.g.Bb)
            q = {
                action: "promo_click",
                Pe: TD(r) || TD(e)
            };
        else if ("select_content" === a || a === P.g.qc)
            q = {
                action: "click",
                ub: {
                    list: d(P.g.bf) || d(P.g.bd) || f
                },
                Mc: TD(e)
            };
        else if (a === P.g.Pb || "checkout_progress" === a) {
            var t = {
                step: a === P.g.Pb ? 1 : d(P.g.af),
                option: d(P.g.Qd)
            };
            q = {
                action: "checkout",
                Mc: TD(e),
                ub: k(c(), t)
            }
        } else
            "set_checkout_option" === a && (q = {
                action: "checkout_option",
                ub: {
                    step: d(P.g.af),
                    option: d(P.g.Qd)
                }
            });
        q && (q.eh = d(P.g.Ba));
        return q
    }, rE = {}, FD = function(a, b) {
        var c = rE[a];
        rE[a] = k(b);
        if (!c)
            return !1;
        for (var d in b)
            if (b.hasOwnProperty(d) && b[d] !== c[d])
                return !0;
        for (var e in c)
            if (c.hasOwnProperty(e) && c[e] !== b[e])
                return !0;
        return !1
    };
    function sE(a, b, c, d) {}
    sE.K = "internal.executeEventProcessor";
    function tE(a) {
        var b;
        return ad(b, this.J, 1)
    }
    tE.K = "internal.executeJavascriptString";
    function uE(a) {
        var b;
        return b
    }
    ;var vE = null;
    function wE() {
        var a = new cb;
        M(this, "read_container_data"),
        T(34) && vE ? a = vE : (a.set("containerId", 'GTM-M86QHGF'),
        a.set("version", '81'),
        a.set("environmentName", ''),
        a.set("debugMode", Of),
        a.set("previewMode", Rf),
        a.set("environmentMode", Qf),
        a.set("firstPartyServing", mj()),
        a.set("containerUrl", qc),
        a.Lb(),
        T(34) && (vE = a));
        return a
    }
    wE.U = "getContainerVersion";
    function xE(a, b) {
        b = void 0 === b ? !0 : b;
        var c;
        K(this.getName(), ["name:!string", "decode:?boolean"], arguments),
        M(this, "get_cookies", a),
        c = ad(ao(a, void 0, !!b), this.J);
        return c
    }
    xE.U = "getCookieValues";
    function yE() {
        return pl()
    }
    yE.K = "internal.getCountryCode";
    function zE() {
        var a = [];
        return ad(a)
    }
    zE.K = "internal.getDestinationIds";
    function AE(a, b) {
        var c = null;
        return c
    }
    AE.K = "internal.getElementAttribute";
    function BE(a) {
        var b = null;
        return b
    }
    BE.K = "internal.getElementById";
    function CE(a) {
        var b = "";
        return b
    }
    CE.K = "internal.getElementInnerText";
    function DE(a, b) {
        var c = null;
        return c
    }
    DE.K = "internal.getElementProperty";
    function EE(a) {
        var b;
        return b
    }
    EE.K = "internal.getElementValue";
    function FE(a) {
        var b = 0;
        return b
    }
    FE.K = "internal.getElementVisibilityRatio";
    function GE(a) {
        var b = null;
        return b
    }
    GE.K = "internal.getElementsByCssSelector";
    function HE(a) {
        var b;
        K(this.getName(), ["keyPath:!string"], arguments);
        M(this, "read_event_data", a);
        var c;
        a: {
            var d = a
              , e = Fz(this).originalEventData;
            if (e) {
                for (var f = e, g = {}, h = {}, m = {}, n = [], p = d.split("\\\\"), q = 0; q < p.length; q++) {
                    for (var r = p[q].split("\\."), t = 0; t < r.length; t++) {
                        for (var u = r[t].split("."), v = 0; v < u.length; v++)
                            n.push(u[v]),
                            v !== u.length - 1 && n.push(m);
                        t !== r.length - 1 && n.push(h)
                    }
                    q !== p.length - 1 && n.push(g)
                }
                for (var w = [], y = "", x = na(n), B = x.next(); !B.done; B = x.next()) {
                    var A = B.value;
                    A === m ? (w.push(y),
                    y = "") : y = A === g ? y + "\\" : A === h ? y + "." : y + A
                }
                y && w.push(y);
                for (var D = na(w), E = D.next(); !E.done; E = D.next()) {
                    if (null == f) {
                        c = void 0;
                        break a
                    }
                    f = f[E.value]
                }
                c = f
            } else
                c = void 0
        }
        b = ad(c, this.J, 1);
        return b
    }
    HE.K = "internal.getEventData";
    var IE = {};
    IE.enableAWFledge = T(18);
    IE.enableAdsConversionValidation = T(10);
    IE.enableAutoPiiOnPhoneAndAddress = T(17);
    IE.enableCachedEcommerceData = T(25);
    IE.enableCcdPreAutoPiiDetection = T(26);
    IE.enableCloudRecommentationsErrorLogging = T(28);
    IE.enableCloudRecommentationsSchemaIngestion = T(29);
    IE.enableCloudRetailInjectPurchaseMetadata = T(31);
    IE.enableCloudRetailLogging = T(30);
    IE.enableCloudRetailPageCategories = T(32);
    IE.enableConsentDisclosureActivity = T(33);
    IE.enableDCFledge = T(37);
    IE.enableDecodeUri = T(46);
    IE.enableDeferAllEnhancedMeasurement = T(38);
    IE.enableEuidAutoMode = T(40);
    IE.enableFormSkipValidation = T(43);
    IE.enableGaRegionActivityPerformanceFix = T(50);
    IE.enableSharedUserId = T(70);
    IE.enableSharedUserIdFromUserProperty = T(71);
    IE.enableUrlDecodeEventUsage = T(75);
    IE.enableZoneConfigInChildContainers = T(77);
    IE.ignoreServerMacroInGoogleSignal = T(80);
    IE.renameOnoToNonGaiaRemarketing = T(83);
    IE.useEnableAutoEventOnFormApis = T(89);
    IE.autoPiiEligible = tl();
    function JE() {
        return ad(IE)
    }
    JE.K = "internal.getFlags";
    function KE() {
        return new Yc(fz)
    }
    KE.K = "internal.getHtmlId";
    function LE(a, b) {
        var c;
        return c
    }
    LE.K = "internal.getProductSettingsParameter";
    function ME(a, b) {
        var c;
        return c
    }
    ME.U = "getQueryParameters";
    function NE(a, b) {
        var c;
        return c
    }
    NE.U = "getReferrerQueryParameters";
    function OE(a) {
        var b = "";
        return b
    }
    OE.U = "getReferrerUrl";
    function PE() {
        return ol["1"] || ""
    }
    PE.K = "internal.getRegionCode";
    function QE(a, b) {
        var c;
        return c
    }
    QE.K = "internal.getRemoteConfigParameter";
    function RE(a) {
        var b = "";
        return b
    }
    RE.U = "getUrl";
    function SE() {
        M(this, "get_user_agent");
        return oc.userAgent
    }
    SE.U = "getUserAgent";
    function ZE() {
        return G.gaGlobal = G.gaGlobal || {}
    }
    var $E = function() {
        var a = ZE();
        a.hid = a.hid || tb();
        return a.hid
    }
      , aF = function(a, b) {
        var c = ZE();
        if (void 0 == c.vid || b && !c.from_cookie)
            c.vid = a,
            c.from_cookie = b
    };
    var IF = function(a) {
        this.F = a;
        this.H = "";
        this.m = this.F
    }
      , JF = function(a, b) {
        a.m = b;
        return a
    }
      , KF = function(a, b) {
        a.M = b;
        return a
    };
    function LF(a) {
        var b = a.search;
        return a.protocol + "//" + a.hostname + a.pathname + (b ? b + "&richsstsse" : "?richsstsse")
    }
    function MF(a, b, c) {
        if (a) {
            var d = a || [];
            if (Array.isArray(d))
                for (var e = Xa(b) ? b : {}, f = na(d), g = f.next(); !g.done; g = f.next())
                    c(g.value, e)
        }
    }
    ;var bG = window
      , cG = document
      , dG = function(a) {
        var b = bG._gaUserPrefs;
        if (b && b.ioo && b.ioo() || cG.documentElement.hasAttribute("data-google-analytics-opt-out") || a && !0 === bG["ga-disable-" + a])
            return !0;
        try {
            var c = bG.external;
            if (c && c._gaUserPrefs && "oo" == c._gaUserPrefs)
                return !0
        } catch (p) {}
        for (var d = [], e = String(cG.cookie).split(";"), f = 0; f < e.length; f++) {
            var g = e[f].split("=")
              , h = g[0].replace(/^\s*|\s*$/g, "");
            if (h && "AMP_TOKEN" == h) {
                var m = g.slice(1).join("=").replace(/^\s*|\s*$/g, "");
                m && (m = decodeURIComponent(m));
                d.push(m)
            }
        }
        for (var n = 0; n < d.length; n++)
            if ("$OPT_OUT" == d[n])
                return !0;
        return cG.getElementById("__gaOptOutExtension") ? !0 : !1
    };
    function oG(a) {
        z(a, function(c) {
            "_" === c.charAt(0) && delete a[c]
        });
        var b = a[P.g.cb] || {};
        z(b, function(c) {
            "_" === c.charAt(0) && delete b[c]
        })
    }
    ;var wG = function(a, b) {};
    function vG(a, b) {
        var c = function() {};
        return c
    }
    function xG(a, b, c) {}
    ;var yG = vG;
    var zG = function(a, b, c) {
        for (var d = 0; d < b.length; d++)
            a.hasOwnProperty(b[d]) && (a[String(b[d])] = c(a[String(b[d])]))
    };
    function AG(a, b, c) {
        var d = this;
        K(this.getName(), ["tagId:!string", "configuration:?PixieMap", "messageContext:?PixieMap"], arguments);
        var e = b ? J(b) : {};
        Bz([function() {
            return M(d, "configure_google_tags", a, e)
        }
        ]);
        var f = c ? J(c) : {}
          , g = Fz(this);
        f.originatingEntity = vA(g);
        Lx(Ix(a, e), g.eventId, f);
    }
    AG.K = "internal.gtagConfig";
    function BG() {
        var a = {};
        return a
    }
    ;var CG = function(a, b) {
        function c(f, g) {
            for (var h in f)
                if (f.hasOwnProperty(h)) {
                    var m = g ? g + "." + h : h;
                    Xa(f[h]) && -1 === e.indexOf(f[h]) ? (e.push(f[h]),
                    c(f[h], m)) : d.push(m)
                }
            e.pop()
        }
        var d = []
          , e = [a];
        c(a, b);
        return d
    };
    function DG(a, b) {
        K(this.getName(), ["keyOrObject:!*", "value:?*"], arguments);
        var c = null
          , d = J(a);
        if (Xa(d)) {
            for (var e = CG(d, ""), f = 0; f < e.length; f++)
                M(this, "write_data_layer", e[f]);
            c = Gx(d)
        } else if ("string" === typeof d) {
            var g = J(b);
            if (Xa(g))
                for (var h = CG(g, d), m = 0; m < h.length; m++)
                    M(this, "write_data_layer", h[m]);
            else
                M(this, "write_data_layer", d);
            c = Gx(d, g)
        }
        if (c) {
            var n = Fz(this);
            Lx(c, n.eventId, wA(n));
            return ad(c)
        }
    }
    DG.U = "gtagSet";
    function EG(a, b) {}
    EG.U = "injectHiddenIframe";
    function FG(a, b, c, d, e) {}
    FG.K = "internal.injectHtml";
    var JG = {};
    var KG = function(a, b, c, d, e, f) {
        f ? e[f] ? (e[f][0].push(c),
        e[f][1].push(d)) : (e[f] = [[c], [d]],
        wc(a, function() {
            for (var g = e[f][0], h = 0; h < g.length; h++)
                I(g[h]);
            g.push = function(m) {
                I(m);
                return 0
            }
        }, function() {
            for (var g = e[f][1], h = 0; h < g.length; h++)
                I(g[h]);
            e[f] = null
        }, b)) : wc(a, c, d, b)
    };
    function LG(a, b, c, d) {
        if (!Sn()) {
            K(this.getName(), ["url:!string", "onSuccess:?Fn", "onFailure:?Fn", "cacheToken:?string"], arguments);
            M(this, "inject_script", a);
            var e = this.J;
            KG(a, void 0, function() {
                b && b.fb(e)
            }, function() {
                c && c.fb(e)
            }, JG, d)
        }
    }
    var MG = {
        dl: 1,
        id: 1
    }
      , NG = {};
    function OG(a, b, c, d) {}
    LG.U = "injectScript";
    OG.K = "internal.injectScript";
    function PG(a) {
        var b = !0;
        return b
    }
    PG.U = "isConsentGranted";
    function QG() {
        return rl()
    }
    QG.K = "internal.isDmaRegion";
    function RG(a) {
        var b = !1;
        return b
    }
    RG.K = "internal.isEntityInfrastructure";
    function SG() {
        var a = Xg(function(b) {
            Fz(this).log("error", b)
        });
        a.U = "JSON";
        return a
    }
    ;function TG(a) {
        var b = void 0;
        return ad(b)
    }
    TG.K = "internal.legacyParseUrl";
    function UG() {
        return !1
    }
    var VG = {
        getItem: function(a) {
            var b = null;
            return b
        },
        setItem: function(a, b) {
            return !1
        },
        removeItem: function(a) {}
    };
    function WG() {
        try {
            M(this, "logging")
        } catch (c) {
            return
        }
        if (!console)
            return;
        for (var a = Array.prototype.slice.call(arguments, 0), b = 0; b < a.length; b++)
            a[b] = J(a[b], this.J);
        console.log.apply(console, a);
    }
    WG.U = "logToConsole";
    function XG(a, b) {}
    XG.K = "internal.mergeRemoteConfig";
    function YG(a, b, c) {
        c = void 0 === c ? !0 : c;
        var d = [];
        return ad(d)
    }
    YG.K = "internal.parseCookieValuesFromString";
    function ZG(a) {
        var b = void 0;
        return b
    }
    ZG.U = "parseUrl";
    function $G(a) {}
    $G.K = "internal.processAsNewEvent";
    function aH(a, b, c) {
        var d;
        return d
    }
    aH.K = "internal.pushToDataLayer";
    function bH(a) {
        var b = !1;
        return b
    }
    bH.U = "queryPermission";
    function cH() {
        var a = "";
        return a
    }
    cH.U = "readCharacterSet";
    function dH() {
        return hi.Ya
    }
    dH.K = "internal.readDataLayerName";
    function eH() {
        var a = "";
        return a
    }
    eH.U = "readTitle";
    function fH(a, b) {
        var c = this;
    }
    fH.K = "internal.registerCcdCallback";
    function gH(a) {
        return !0
    }
    gH.K = "internal.registerDestination";
    var hH = ["config", "event", "get", "set"];
    function iH(a, b, c) {}
    iH.K = "internal.registerGtagCommandListener";
    function jH(a, b) {
        var c = !1;
        return c
    }
    jH.K = "internal.removeDataLayerEventListener";
    function kH(a, b) {}
    kH.K = "internal.removeFormData";
    function lH() {}
    lH.U = "resetDataLayer";
    function mH(a, b, c, d) {}
    mH.K = "internal.sendGtagEvent";
    function nH(a, b, c) {}
    nH.U = "sendPixel";
    function oH(a, b) {}
    oH.K = "internal.setAnchorHref";
    function pH(a, b, c, d) {
        var e = this;
        d = void 0 === d ? !0 : d;
        var f = !1;
        return f
    }
    pH.U = "setCookie";
    function qH(a) {}
    qH.K = "internal.setCorePlatformServices";
    function rH(a, b) {}
    rH.K = "internal.setDataLayerValue";
    function sH(a) {
        K(this.getName(), ["consentSettings:!PixieMap"], arguments);
        for (var b = a.Zb(), c = b.length(), d = 0; d < c; d++) {
            var e = b.get(d);
            e !== P.g.kc && e !== P.g.Ue && M(this, "access_consent", e, "write")
        }
        var f = Fz(this)
          , g = f.eventId
          , h = wA(f)
          , m = Hx("consent", "default", J(a));
        Lx(m, g, h);
    }
    sH.U = "setDefaultConsentState";
    function tH(a, b) {}
    tH.K = "internal.setDelegatedConsentType";
    function uH(a, b) {}
    uH.K = "internal.setFormAction";
    function vH(a, b, c) {}
    vH.K = "internal.setInCrossContainerData";
    function wH(a, b, c) {
        K(this.getName(), ["path:!string", "value:?*", "overrideExisting:?boolean"], arguments);
        M(this, "access_globals", "readwrite", a);
        var d = a.split(".")
          , e = Ib(d, [G, H])
          , f = d.pop();
        if (e && (void 0 === e[f] || c))
            return e[f] = J(b, this.J, WA()),
            !0;
        return !1
    }
    wH.U = "setInWindow";
    function xH(a, b, c) {}
    xH.K = "internal.setProductSettingsParameter";
    function yH(a, b, c) {}
    yH.K = "internal.setRemoteConfigParameter";
    function zH(a, b, c, d) {
        var e = this;
        var f = function(u, v) {
            var w = new cb;
            w.set("name", u);
            w.set("message", v);
            return w
        }
          , g = function(u, v) {
            var w = new Uint8Array(u);
            if (2 === v) {
                for (var y = "", x = 0; x < w.length; x++) {
                    var B = w[x].toString(16);
                    y += 1 === B.length ? "0" + B : B
                }
                return y
            }
            for (var A = Array(w.length), D = 0; D < w.length; D++)
                A[D] = w[D];
            var E = A.map(function(C) {
                return String.fromCharCode(C)
            }).join("");
            return G.btoa(E)
        };
        K(this.getName(), ["input:!string", "onSuccess:!Fn", "onFailure:?Fn"], arguments);
        var h = "hex" === (d instanceof cb ? J(d) : {}).outputEncoding ? 2 : 1;
        c = c || new Tc("emptyFn",function() {}
        );
        for (var m = G.msCrypto, n = G.crypto, p = et(a), q = new Uint8Array(p.length), r = 0; r < p.length; r++)
            q[r] = p[r];
        if (n && n.subtle)
            n.subtle.digest("SHA-256", q).then(function(u) {
                return void b.invoke(e.J, g(u, h))
            }, function(u) {
                c.invoke(e.J, f(u.name, u.message))
            });
        else if (m && m.subtle) {
            var t = m.subtle.digest("SHA-256", q);
            t.oncomplete = function(u) {
                return void b.invoke(e.J, g(u.target.result, h))
            }
            ;
            t.onerror = function(u) {
                return void c.invoke(e.J, f(u.target.result.name, u.target.result.message))
            }
        } else
            c.invoke(this.J, f("BrowserNotSupported", "This method is not supported in this browser."));
    }
    zH.U = "sha256";
    function AH(a, b, c) {}
    AH.K = "internal.sortRemoteConfigParameters";
    var BH = {}
      , CH = {};
    BH.getItem = function(a) {
        var b = null;
        return b
    }
    ;
    BH.setItem = function(a, b) {}
    ;
    BH.removeItem = function(a) {}
    ;
    BH.clear = function() {}
    ;
    BH.U = "templateStorage";
    function DH(a, b) {
        var c = !1;
        return c
    }
    DH.K = "internal.testRegex";
    function EH(a) {
        var b;
        return b
    }
    ;function FH(a) {
        var b;
        return b
    }
    FH.K = "internal.unsiloId";
    function GH(a) {
        K(this.getName(), ["consentSettings:!PixieMap"], arguments);
        var b = J(a), c;
        for (c in b)
            b.hasOwnProperty(c) && M(this, "access_consent", c, "write");
        var d = Fz(this);
        Lx(Hx("consent", "update", b), d.eventId, wA(d));
    }
    GH.U = "updateConsentState";
    var HH;
    function IH(a, b, c) {
        HH = HH || new hh;
        HH.add(a, b, c)
    }
    function JH(a, b) {
        var c = HH = HH || new hh;
        if (c.F.hasOwnProperty(a))
            throw "Attempting to add a private function which already exists: " + a + ".";
        if (c.m.hasOwnProperty(a))
            throw "Attempting to add a private function with an existing API name: " + a + ".";
        c.F[a] = pb(b) ? Dg(a, b) : Eg(a, b)
    }
    function KH() {
        return function(a) {
            var b;
            var c = HH;
            if (c.m.hasOwnProperty(a))
                b = c.get(a, this);
            else {
                var d;
                if (d = c.F.hasOwnProperty(a)) {
                    var e = !1
                      , f = this.J.m;
                    if (f) {
                        var g = f.hc();
                        if (g) {
                            0 !== g.indexOf("__cvt_") && (e = !0);
                        }
                    } else
                        e = !0;
                    d = e
                }
                if (d) {
                    var h = c.F.hasOwnProperty(a) ? c.F[a] : void 0;
                    b = h
                } else
                    throw Error(a + " is not a valid API name.");
            }
            return b
        }
    }
    ;var LH = function() {
        var a = function(c) {
            return JH(c.K, c)
        }
          , b = function(c) {
            return IH(c.U, c)
        };
        b(zz);
        b(Gz);
        b(UA);
        b(XA);
        b(YA);
        b(cB);
        b(eB);
        b(hB);
        b(jB);
        b(wE);
        b(xE);
        b(ME);
        b(NE);
        b(OE);
        b(RE);
        b(DG);
        b(EG);
        b(LG);
        b(PG);
        b(WG);
        b(ZG);
        b(bH);
        b(cH);
        b(eH);
        b(nH);
        b(pH);
        b(sH);
        b(wH);
        b(zH);
        b(BH);
        b(GH);
        b(SG());
        IH("Math", Jg());
        IH("Object", fh);
        IH("TestHelper", jh());
        IH("assertApi", Fg);
        IH("assertThat", Gg);
        IH("decodeUri", Kg);
        IH("decodeUriComponent", Lg);
        IH("encodeUri", Mg);
        IH("encodeUriComponent", Ng);
        IH("fail", Tg);
        IH("generateRandom", Ug);
        IH("getTimestamp", Vg);
        IH("getTimestampMillis", Vg);
        IH("getType", Wg);
        IH("makeInteger", Yg);
        IH("makeNumber", Zg);
        IH("makeString", $g);
        IH("makeTableMap", ah);
        IH("mock", dh);
        IH("fromBase64", uE, !("atob"in G));
        IH("localStorage", VG, !UG());
        IH("toBase64", EH, !("btoa"in G));
        a(Cz);
        a(Xz);
        a(iA);
        a(pA);
        a(uA);
        a(JA);
        a(SA);
        a(VA);
        a(ZA);
        a($A);
        a(bB);
        a(dB);
        a(fB);
        a(gB);
        a(iB);
        a(kB);
        a(mB);
        a(nB);
        a(oB);
        a(pB);
        a(tB);
        a(CB);
        a(DB);
        a(OB);
        a(TB);
        a(YB);
        a(gC);
        a(lC);
        a(yC);
        a(AC);
        a(OC);
        a(Og);
        a(QC);
        a(sE);
        a(tE);
        a(yE);
        a(zE);
        a(AE);
        a(BE);
        a(CE);
        a(DE);
        a(EE);
        a(FE);
        a(GE);
        a(HE);
        a(JE);
        a(KE);
        a(LE);
        a(PE);
        a(QE);
        a(AG);
        a(FG);
        a(OG);
        a(QG);
        a(RG);
        a(TG);
        a(HA);
        a(XG);
        a(YG);
        a($G);
        a(aH);
        a(dH);
        a(fH);
        a(gH);
        a(iH);
        a(jH);
        a(kH);
        a(mH);
        a(oH);
        a(qH);
        a(rH);
        a(tH);
        a(uH);
        a(vH);
        a(xH);
        a(yH);
        a(AH);
        a(DH);
        a(FH);
        JH("internal.CrossContainerSchema", lB());
        JH("internal.GtagSchema", BG());
        IH("mockObject", eh);
        return KH()
    };
    var xz;
    function MH() {
        xz.m.m.M = function(a, b, c) {
            ii.SANDBOXED_JS_SEMAPHORE = ii.SANDBOXED_JS_SEMAPHORE || 0;
            ii.SANDBOXED_JS_SEMAPHORE++;
            try {
                return a.apply(b, c)
            } finally {
                ii.SANDBOXED_JS_SEMAPHORE--
            }
        }
    }
    function NH(a) {
        a && z(a, function(b, c) {
            for (var d = 0; d < c.length; d++) {
                var e = c[d].replace(/^_*/, "");
                xi[e] = xi[e] || [];
                xi[e].push(b)
            }
        })
    }
    ;var OH = encodeURI
      , X = encodeURIComponent
      , PH = Array.isArray
      , QH = function(a, b, c) {
        zc(a, b, c)
    }
      , RH = function(a, b) {
        if (!a)
            return !1;
        var c = dj(hj(a), "host");
        if (!c)
            return !1;
        for (var d = 0; b && d < b.length; d++) {
            var e = b[d] && b[d].toLowerCase();
            if (e) {
                var f = c.length - e.length;
                0 < f && "." != e.charAt(0) && (f--,
                e = "." + e);
                if (0 <= f && c.indexOf(e, f) == f)
                    return !0
            }
        }
        return !1
    }
      , SH = function(a, b, c) {
        for (var d = {}, e = !1, f = 0; a && f < a.length; f++)
            a[f] && a[f].hasOwnProperty(b) && a[f].hasOwnProperty(c) && (d[a[f][b]] = a[f][c],
            e = !0);
        return e ? d : null
    };
    var nI = G.clearTimeout
      , oI = G.setTimeout
      , pI = function(a, b, c) {
        if (Sn()) {
            b && I(b)
        } else
            return wc(a, b, c)
    }
      , qI = function() {
        return G.location.href
    }
      , rI = function(a) {
        return dj(hj(a), "fragment")
    }
      , sI = function(a) {
        return ej(hj(a))
    }
      , tI = function(a, b) {
        return Hi(a, b || 2)
    }
      , uI = function(a, b, c) {
        return b ? uy(a, b, c) : ty(a)
    }
      , vI = function(a, b) {
        G[a] = b
    }
      , wI = function(a, b, c) {
        b && (void 0 === G[a] || c && !G[a]) && (G[a] = b);
        return G[a]
    }
      , xI = function(a, b) {
        if (Sn()) {
            b && I(b)
        } else
            yc(a, b)
    }
      , yI = function(a) {
        return !!Iz(a, "init", !1)
    }
      , zI = function(a) {
        Jz(a, "init", !0)
    };

    var AI = {};
    var Y = {
        securityGroups: {}
    };

    Y.securityGroups.sdl = ["google"],
    function() {
        function a() {
            return !!(Object.keys(p("horiz.pix")).length || Object.keys(p("horiz.pct")).length || Object.keys(p("vert.pix")).length || Object.keys(p("vert.pct")).length)
        }
        function b(A) {
            for (var D = [], E = A.split(","), C = 0; C < E.length; C++) {
                var F = Number(E[C]);
                if (isNaN(F))
                    return [];
                r.test(E[C]) || D.push(F)
            }
            return D
        }
        function c() {
            var A = 0
              , D = 0;
            return function() {
                var E = Kr()
                  , C = E.height;
                A = Math.max(y.scrollLeft + E.width, A);
                D = Math.max(y.scrollTop + C, D);
                return {
                    fh: A,
                    gh: D
                }
            }
        }
        function d() {
            v = wI("self");
            w = v.document;
            y = w.scrollingElement || w.body && w.body.parentNode;
            B = c()
        }
        function e(A, D, E, C) {
            var F = p(D), L = {}, N;
            for (N in F)
                if (L = {
                    Ed: L.Ed
                },
                L.Ed = N,
                F.hasOwnProperty(L.Ed)) {
                    var Q = Number(L.Ed);
                    A < Q || (uI({
                        event: "gtm.scrollDepth",
                        "gtm.scrollThreshold": Q,
                        "gtm.scrollUnits": E.toLowerCase(),
                        "gtm.scrollDirection": C,
                        "gtm.triggers": F[L.Ed].join(",")
                    }),
                    Mz("sdl", D, function(V) {
                        return function(ca) {
                            delete ca[V.Ed];
                            return ca
                        }
                    }(L), {}))
                }
        }
        function f() {
            var A = B()
              , D = A.fh
              , E = A.gh
              , C = D / y.scrollWidth * 100
              , F = E / y.scrollHeight * 100;
            e(D, "horiz.pix", t.Cf, u.gj);
            e(C, "horiz.pct", t.Bf, u.gj);
            e(E, "vert.pix", t.Cf, u.Dj);
            e(F, "vert.pct", t.Bf, u.Dj);
            Jz("sdl", "pending", !1)
        }
        function g(A, D) {
            yI("sdl") && !a() && (D ? Bc(v, "scrollend", A) : Bc(v, "scroll", A),
            Bc(v, "resize", A),
            Jz("sdl", "init", !1))
        }
        function h() {
            var A = 250
              , D = !1;
            w.scrollingElement && w.documentElement && v.addEventListener && (A = 50,
            D = !0);
            var E = 0
              , C = !1
              , F = function() {
                C ? E = oI(F, A) : (E = 0,
                f(),
                g(L));
                C = !1
            }
              , L = function() {
                D && B();
                E ? C = !0 : (E = oI(F, A),
                Jz("sdl", "pending", !0))
            };
            return L
        }
        function m() {
            var A = function() {
                f();
                g(A, !0)
            };
            return A
        }
        function n(A, D, E) {
            if (D) {
                var C = b(String(A));
                Mz("sdl", E, function(F) {
                    for (var L = 0; L < C.length; L++) {
                        var N = String(C[L]);
                        F.hasOwnProperty(N) || (F[N] = []);
                        F[N].push(D)
                    }
                    return F
                }, {})
            }
        }
        function p(A) {
            return Iz("sdl", A, {})
        }
        function q(A) {
            I(A.vtp_gtmOnSuccess);
            var D = A.vtp_uniqueTriggerId
              , E = A.vtp_horizontalThresholdsPixels
              , C = A.vtp_horizontalThresholdsPercent
              , F = A.vtp_verticalThresholdUnits
              , L = A.vtp_verticalThresholdsPixels
              , N = A.vtp_verticalThresholdsPercent;
            switch (A.vtp_horizontalThresholdUnits) {
            case t.Cf:
                n(E, D, "horiz.pix");
                break;
            case t.Bf:
                n(C, D, "horiz.pct")
            }
            switch (F) {
            case t.Cf:
                n(L, D, "vert.pix");
                break;
            case t.Bf:
                n(N, D, "vert.pct")
            }
            yI("sdl") ? Iz("sdl", "pending") || (x || (d(),
            x = !0),
            I(function() {
                return f()
            })) : (d(),
            x = !0,
            y && (zI("sdl"),
            Jz("sdl", "pending", !0),
            I(function() {
                f();
                if (a()) {
                    var Q = h();
                    "onscrollend"in v ? (Q = m(),
                    Ac(v, "scrollend", Q)) : Ac(v, "scroll", Q);
                    Ac(v, "resize", Q)
                } else
                    Jz("sdl", "init", !1)
            })))
        }
        var r = /^\s*$/, t = {
            Bf: "PERCENT",
            Cf: "PIXELS"
        }, u = {
            Dj: "vertical",
            gj: "horizontal"
        }, v, w, y, x = !1, B;
        (function(A) {
            Y.__sdl = A;
            Y.__sdl.C = "sdl";
            Y.__sdl.isVendorTemplate = !0;
            Y.__sdl.priorityOverride = 0;
            Y.__sdl.isInfrastructure = !1;
            Y.__sdl.runInSiloedMode = !1
        }
        )(function(A) {
            A.vtp_triggerStartOption ? q(A) : ly(function() {
                q(A)
            })
        })
    }();
    Y.securityGroups.jsm = ["customScripts"],
    Y.__jsm = function(a) {
        if (void 0 !== a.vtp_javascript) {
            var b = a.vtp_javascript;
            try {
                var c = wI("google_tag_manager");
                return c && c.e && c.e(b)
            } catch (d) {}
        }
    }
    ,
    Y.__jsm.C = "jsm",
    Y.__jsm.isVendorTemplate = !0,
    Y.__jsm.priorityOverride = 0,
    Y.__jsm.isInfrastructure = !1,
    Y.__jsm.runInSiloedMode = !1;
    Y.securityGroups.c = ["google"],
    Y.__c = function(a) {
        return a.vtp_value
    }
    ,
    Y.__c.C = "c",
    Y.__c.isVendorTemplate = !0,
    Y.__c.priorityOverride = 0,
    Y.__c.isInfrastructure = !0,
    Y.__c.runInSiloedMode = !0;
    Y.securityGroups.d = ["google"],
    Y.__d = function(a) {
        var b = null
          , c = null
          , d = a.vtp_attributeName;
        if ("CSS" == a.vtp_selectorType)
            try {
                var e = nh(a.vtp_elementSelector);
                e && 0 < e.length && (b = e[0])
            } catch (f) {
                b = null
            }
        else
            b = H.getElementById(a.vtp_elementId);
        b && (d ? c = function() {
            if (b instanceof HTMLInputElement) {
                var f = b;
                if ("value" === d)
                    return f.value;
                if ("checked" === d && ("radio" === f.type || "checkbox" === f.type))
                    return f.checked
            }
            return Cc(b, d)
        }() : c = Dc(b));
        return Ab(String(b && c))
    }
    ,
    Y.__d.C = "d",
    Y.__d.isVendorTemplate = !0,
    Y.__d.priorityOverride = 0,
    Y.__d.isInfrastructure = !0,
    Y.__d.runInSiloedMode = !1;
    Y.securityGroups.f = ["google"],
    Y.__f = function(a) {
        var b = tI("gtm.referrer", 1) || H.referrer;
        return b ? a.vtp_component && "URL" != a.vtp_component ? dj(hj(String(b)), a.vtp_component, a.vtp_stripWww, a.vtp_defaultPages, a.vtp_queryKey) : sI(String(b)) : String(b)
    }
    ,
    Y.__f.C = "f",
    Y.__f.isVendorTemplate = !0,
    Y.__f.priorityOverride = 0,
    Y.__f.isInfrastructure = !0,
    Y.__f.runInSiloedMode = !1;
    Y.securityGroups.cl = ["google"],
    function() {
        function a(b) {
            var c = b.target;
            if (c) {
                var d = Nz(c, "gtm.click");
                uI(d)
            }
        }
        (function(b) {
            Y.__cl = b;
            Y.__cl.C = "cl";
            Y.__cl.isVendorTemplate = !0;
            Y.__cl.priorityOverride = 0;
            Y.__cl.isInfrastructure = !1;
            Y.__cl.runInSiloedMode = !1
        }
        )(function(b) {
            if (!yI("cl")) {
                var c = wI("document");
                Ac(c, "click", a, !0);
                zI("cl")
            }
            I(b.vtp_gtmOnSuccess)
        })
    }();
    Y.securityGroups.j = ["google"],
    Y.__j = function(a) {
        for (var b = String(a.vtp_name).split("."), c = wI(b.shift()), d = 0; d < b.length; d++)
            c = c && c[b[d]];
        return c
    }
    ,
    Y.__j.C = "j",
    Y.__j.isVendorTemplate = !0,
    Y.__j.priorityOverride = 0,
    Y.__j.isInfrastructure = !0,
    Y.__j.runInSiloedMode = !1;
    Y.securityGroups.k = ["google"],
    Y.__k = function(a) {
        var b = a.vtp_name
          , c = tI("gtm.cookie", 1)
          , d = !!a.vtp_decodeCookie;
        return ao(b, c, void 0 === d ? !0 : !!d)[0]
    }
    ,
    Y.__k.C = "k",
    Y.__k.isVendorTemplate = !0,
    Y.__k.priorityOverride = 0,
    Y.__k.isInfrastructure = !0,
    Y.__k.runInSiloedMode = !1;
    Y.securityGroups.fls = [],
    Y.__fls = function(a) {
        var b = [];
        if (a.vtp_enableProductReporting)
            switch (a.vtp_dataSource) {
            case "DATA_LAYER":
                b = tI("ecommerce.purchase.products");
                break;
            case "JSON":
                b = a.vtp_productData;
                break;
            case "STRING":
                for (var c = (a.vtp_productData || "").split("|"), d = 0; d < c.length; d++) {
                    var e = c[d].split(":");
                    e[1] = e[1] && X(e[1]) || "";
                    c[d] = e.join(":");
                    var f = {
                        i: "id",
                        p: "price",
                        q: "quantity",
                        c: "country",
                        l: "language",
                        a: "accountId"
                    }
                      , g = e[0][0]
                      , h = Number(e[0].slice(1)) - 1
                      , m = b[h] || {};
                    f.hasOwnProperty(g) && (m[f[g]] = e[1]);
                    b[h] = m
                }
            }
        var n = !a.hasOwnProperty("vtp_enableConversionLinker") || !!a.vtp_enableConversionLinker
          , p = SH(a.vtp_customVariable || [], "key", "value") || {}
          , q = {}
          , r = (q[P.g.ja] = tI(P.g.ja),
        q[P.g.We] = !a.vtp_useImageTag,
        q[P.g.ia] = b,
        q[P.g.Za] = a.vtp_conversionCookiePrefix || void 0,
        q[P.g.wa] = n,
        q[P.g.ld] = a.vtp_quantity,
        q[P.g.Ca] = a.vtp_orderId,
        q[P.g.qa] = a.vtp_revenue,
        q[P.g.pg] = a.vtp_matchIdVariable,
        q.oref = a.vtp_useImageTag ? void 0 : a.vtp_url,
        q.tran = a.vtp_transactionVariable,
        q.u = a.vtp_userVariable,
        q[P.g.Ga] = a.vtp_userDataVariable,
        q);
        T(37) && (r[P.g.Ea] = tI(P.g.Ea),
        r[P.g.oa] = tI(P.g.oa));
        for (var t in p)
            p.hasOwnProperty(t) && (r[t] = p[t]);
        var u = "DC-" + a.vtp_advertiserId
          , v = u + "/" + a.vtp_groupTag + "/" + (a.vtp_activityTag + "+" + ("ITEM_SOLD" === a.vtp_countingMethod ? "items_sold" : "transactions"));
        Vv(u, void 0, {
            source: 7,
            fromContainerExecution: !0,
            siloed: !0
        });
        var w = {
            noGtmEvent: !0,
            isGtmEvent: !0,
            onSuccess: a.vtp_gtmOnSuccess,
            onFailure: a.vtp_gtmOnFailure
        };
        Lx(Jx(zj(v), "", r), a.vtp_gtmEventId, w)
    }
    ,
    Y.__fls.C = "fls",
    Y.__fls.isVendorTemplate = !0,
    Y.__fls.priorityOverride = 0,
    Y.__fls.isInfrastructure = !1,
    Y.__fls.runInSiloedMode = !1;
    Y.securityGroups.access_globals = ["google"],
    function() {
        function a(b, c, d) {
            var e = {
                key: d,
                read: !1,
                write: !1,
                execute: !1
            };
            switch (c) {
            case "read":
                e.read = !0;
                break;
            case "write":
                e.write = !0;
                break;
            case "readwrite":
                e.read = e.write = !0;
                break;
            case "execute":
                e.execute = !0;
                break;
            default:
                throw Error("Invalid " + b + " request " + c);
            }
            return e
        }
        (function(b) {
            Y.__access_globals = b;
            Y.__access_globals.C = "access_globals";
            Y.__access_globals.isVendorTemplate = !0;
            Y.__access_globals.priorityOverride = 0;
            Y.__access_globals.isInfrastructure = !1;
            Y.__access_globals.runInSiloedMode = !1
        }
        )(function(b) {
            for (var c = b.vtp_keys || [], d = b.vtp_createPermissionError, e = [], f = [], g = [], h = 0; h < c.length; h++) {
                var m = c[h]
                  , n = m.key;
                m.read && e.push(n);
                m.write && f.push(n);
                m.execute && g.push(n)
            }
            return {
                assert: function(p, q, r) {
                    if (!l(r))
                        throw d(p, {}, "Key must be a string.");
                    if ("read" === q) {
                        if (-1 < e.indexOf(r))
                            return
                    } else if ("write" === q) {
                        if (-1 < f.indexOf(r))
                            return
                    } else if ("readwrite" === q) {
                        if (-1 < f.indexOf(r) && -1 < e.indexOf(r))
                            return
                    } else if ("execute" === q) {
                        if (-1 < g.indexOf(r))
                            return
                    } else
                        throw d(p, {}, "Operation must be either 'read', 'write', or 'execute', was " + q);
                    throw d(p, {}, "Prohibited " + q + " on global variable: " + r + ".");
                },
                O: a
            }
        })
    }();
    Y.securityGroups.u = ["google"],
    function() {
        var a = function(b) {
            return {
                toString: function() {
                    return b
                }
            }
        };
        (function(b) {
            Y.__u = b;
            Y.__u.C = "u";
            Y.__u.isVendorTemplate = !0;
            Y.__u.priorityOverride = 0;
            Y.__u.isInfrastructure = !0;
            Y.__u.runInSiloedMode = !1
        }
        )(function(b) {
            var c;
            c = (c = b.vtp_customUrlSource ? b.vtp_customUrlSource : tI("gtm.url", 1)) || qI();
            var d = b[a("vtp_component")];
            if (!d || "URL" == d)
                return sI(String(c));
            var e = hj(String(c)), f;
            if ("QUERY" === d)
                a: {
                    var g = b[a("vtp_multiQueryKeys").toString()], h = b[a("vtp_queryKey").toString()] || "", m = b[a("vtp_ignoreEmptyQueryParam").toString()], n;
                    n = g ? Array.isArray(h) ? h : String(h).replace(/\s+/g, "").split(",") : [String(h)];
                    for (var p = 0; p < n.length; p++) {
                        var q = dj(e, "QUERY", void 0, void 0, n[p]);
                        if (void 0 != q && (!m || "" !== q)) {
                            f = q;
                            break a
                        }
                    }
                    f = void 0
                }
            else
                f = dj(e, d, "HOST" == d ? b[a("vtp_stripWww")] : void 0, "PATH" == d ? b[a("vtp_defaultPages")] : void 0);
            return f
        })
    }();
    Y.securityGroups.v = ["google"],
    Y.__v = function(a) {
        var b = a.vtp_name;
        if (!b || !b.replace)
            return !1;
        var c = tI(b.replace(/\\\./g, "."), a.vtp_dataLayerVersion || 1);
        return void 0 !== c ? c : a.vtp_defaultValue
    }
    ,
    Y.__v.C = "v",
    Y.__v.isVendorTemplate = !0,
    Y.__v.priorityOverride = 0,
    Y.__v.isInfrastructure = !0,
    Y.__v.runInSiloedMode = !1;

    Y.securityGroups.read_event_data = ["google"],
    function() {
        function a(b, c) {
            return {
                key: c
            }
        }
        (function(b) {
            Y.__read_event_data = b;
            Y.__read_event_data.C = "read_event_data";
            Y.__read_event_data.isVendorTemplate = !0;
            Y.__read_event_data.priorityOverride = 0;
            Y.__read_event_data.isInfrastructure = !1;
            Y.__read_event_data.runInSiloedMode = !1
        }
        )(function(b) {
            var c = b.vtp_eventDataAccess
              , d = b.vtp_keyPatterns || []
              , e = b.vtp_createPermissionError;
            return {
                assert: function(f, g) {
                    if (null != g && !l(g))
                        throw e(f, {
                            key: g
                        }, "Key must be a string.");
                    if ("any" !== c) {
                        try {
                            if ("specific" === c && null != g && fg(g, d))
                                return
                        } catch (h) {
                            throw e(f, {
                                key: g
                            }, "Invalid key filter.");
                        }
                        throw e(f, {
                            key: g
                        }, "Prohibited read from event data.");
                    }
                },
                O: a
            }
        })
    }();
    Y.securityGroups.gclidw = ["google"],
    function() {
        var a = ["aw", "dc", "gf", "ha", "gb"];
        (function(b) {
            Y.__gclidw = b;
            Y.__gclidw.C = "gclidw";
            Y.__gclidw.isVendorTemplate = !0;
            Y.__gclidw.priorityOverride = 100;
            Y.__gclidw.isInfrastructure = !1;
            Y.__gclidw.runInSiloedMode = !1
        }
        )(function(b) {
            var c, d, e, f;
            b.vtp_enableCookieOverrides && (e = b.vtp_cookiePrefix,
            c = b.vtp_path,
            d = b.vtp_domain,
            f = b.vtp_cookieFlags);
            var g = tI(P.g.ja);
            g = void 0 != g && !1 !== g;
            if (T(14)) {
                var h = {}
                  , m = (h[P.g.Oa] = e,
                h[P.g.Db] = c,
                h[P.g.Ta] = d,
                h[P.g.ab] = f,
                h[P.g.ja] = g,
                h);
                b.vtp_enableUrlPassthrough && (m[P.g.Va] = !0);
                if (b.vtp_enableCrossDomain && b.vtp_linkerDomains) {
                    var n = {};
                    m[P.g.xa] = (n[P.g.Bc] = b.vtp_acceptIncoming,
                    n[P.g.Z] = b.vtp_linkerDomains.toString().replace(/\s+/g, "").split(","),
                    n[P.g.Hb] = b.vtp_urlPosition,
                    n[P.g.sb] = b.vtp_formDecoration,
                    n)
                }
                var p = Gm(Fm(Em(Dm(wm(new vm(b.vtp_gtmEventId,b.vtp_gtmPriorityId), m), b.vtp_gtmOnSuccess), b.vtp_gtmOnFailure), !0));
                p.eventMetadata.hit_type_override = "page_view";
                TC("", P.g.fa, Date.now(), p)
            } else {
                I(b.vtp_gtmOnSuccess);
                var q = {
                    prefix: e,
                    path: c,
                    domain: d,
                    flags: f
                };
                if (!b.vtp_enableCrossDomain || !1 !== b.vtp_acceptIncoming)
                    if (b.vtp_enableCrossDomain || Vo())
                        Up(a, q),
                        hp(q);
                Rp(q);
                $p(["aw", "dc"], q);
                xq(q, void 0, void 0, g);
                if (b.vtp_enableCrossDomain && b.vtp_linkerDomains) {
                    var r = b.vtp_linkerDomains.toString().replace(/\s+/g, "").split(",");
                    Yp(a, r, b.vtp_urlPosition, !!b.vtp_formDecoration, q.prefix);
                    ip(ap(q.prefix), r, b.vtp_urlPosition, !!b.vtp_formDecoration, q);
                    ip("FPAU", r, b.vtp_urlPosition, !!b.vtp_formDecoration, q)
                }
                !mj() && T(67) && Zs(void 0, Math.round(Cb()));
                nr({
                    o: Gm(new vm(b.vtp_gtmEventId,b.vtp_gtmPriorityId)),
                    bh: !1,
                    Bd: g,
                    fc: q,
                    Lf: !0
                });
                b.vtp_enableUrlPassthrough && cq(["aw", "dc", "gb"]);
                eq(["aw", "dc", "gb"])
            }
        })
    }();

    Y.securityGroups.read_data_layer = ["google"],
    function() {
        function a(b, c) {
            return {
                key: c
            }
        }
        (function(b) {
            Y.__read_data_layer = b;
            Y.__read_data_layer.C = "read_data_layer";
            Y.__read_data_layer.isVendorTemplate = !0;
            Y.__read_data_layer.priorityOverride = 0;
            Y.__read_data_layer.isInfrastructure = !1;
            Y.__read_data_layer.runInSiloedMode = !1
        }
        )(function(b) {
            var c = b.vtp_allowedKeys || "specific"
              , d = b.vtp_keyPatterns || []
              , e = b.vtp_createPermissionError;
            return {
                assert: function(f, g) {
                    if (!l(g))
                        throw e(f, {}, "Keys must be strings.");
                    if ("any" !== c) {
                        try {
                            if (fg(g, d))
                                return
                        } catch (h) {
                            throw e(f, {}, "Invalid key filter.");
                        }
                        throw e(f, {}, "Prohibited read from data layer variable: " + g + ".");
                    }
                },
                O: a
            }
        })
    }();
    Y.securityGroups.hl = ["google"],
    function() {
        function a(f) {
            return f.target && f.target.location && f.target.location.href ? f.target.location.href : qI()
        }
        function b(f, g) {
            Ac(f, "hashchange", function(h) {
                var m = a(h);
                g({
                    source: "hashchange",
                    state: null,
                    url: sI(m),
                    X: rI(m)
                })
            })
        }
        function c(f, g) {
            Ac(f, "popstate", function(h) {
                var m = a(h);
                g({
                    source: "popstate",
                    state: h.state,
                    url: sI(m),
                    X: rI(m)
                })
            })
        }
        function d(f, g, h) {
            var m = g.history
              , n = m[f];
            if (pb(n))
                try {
                    m[f] = function(p, q, r) {
                        n.apply(m, [].slice.call(arguments, 0));
                        h({
                            source: f,
                            state: p,
                            url: sI(qI()),
                            X: rI(qI())
                        })
                    }
                } catch (p) {}
        }
        function e() {
            var f = {
                source: null,
                state: wI("history").state || null,
                url: sI(qI()),
                X: rI(qI())
            };
            return function(g) {
                var h = f
                  , m = {};
                m[h.source] = !0;
                m[g.source] = !0;
                if (!m.popstate || !m.hashchange || h.X != g.X) {
                    var n = {
                        event: "gtm.historyChange",
                        "gtm.historyChangeSource": g.source,
                        "gtm.oldUrlFragment": f.X,
                        "gtm.newUrlFragment": g.X,
                        "gtm.oldHistoryState": f.state,
                        "gtm.newHistoryState": g.state,
                        "gtm.oldUrl": f.url,
                        "gtm.newUrl": g.url
                    };
                    f = g;
                    uI(n)
                }
            }
        }
        (function(f) {
            Y.__hl = f;
            Y.__hl.C = "hl";
            Y.__hl.isVendorTemplate = !0;
            Y.__hl.priorityOverride = 0;
            Y.__hl.isInfrastructure = !1;
            Y.__hl.runInSiloedMode = !1
        }
        )(function(f) {
            var g = wI("self");
            if (!yI("hl")) {
                var h = e();
                b(g, h);
                c(g, h);
                d("pushState", g, h);
                d("replaceState", g, h);
                zI("hl")
            }
            I(f.vtp_gtmOnSuccess)
        })
    }();

    Y.securityGroups.gaawe = ["google"],
    function() {
        function a(f, g, h) {
            for (var m = 0; m < g.length; m++)
                f.hasOwnProperty(g[m]) && (f[g[m]] = h(f[g[m]]))
        }
        function b(f, g, h) {
            var m = {}, n = function(u, v) {
                m[u] = m[u] || v
            }, p = function(u, v, w) {
                w = void 0 === w ? !1 : w;
                c.push(6);
                if (u) {
                    m.items = m.items || [];
                    for (var y = {}, x = 0; x < u.length; y = {
                        Me: void 0
                    },
                    x++)
                        y.Me = {},
                        z(u[x], function(A) {
                            return function(D, E) {
                                w && "id" === D ? A.Me.promotion_id = E : w && "name" === D ? A.Me.promotion_name = E : A.Me[D] = E
                            }
                        }(y)),
                        m.items.push(y.Me)
                }
                if (v)
                    for (var B in v)
                        d.hasOwnProperty(B) ? n(d[B], v[B]) : n(B, v[B])
            }, q;
            "dataLayer" === f.vtp_getEcommerceDataFrom ? (q = f.vtp_gtmCachedValues.eventModel) || (q = f.vtp_gtmCachedValues.ecommerce) : (q = f.vtp_ecommerceMacroData,
            Xa(q) && q.ecommerce && !q.items && (q = q.ecommerce));
            if (Xa(q)) {
                var r = !1, t;
                for (t in q)
                    q.hasOwnProperty(t) && (r || (c.push(5),
                    r = !0),
                    "currencyCode" === t ? n("currency", q.currencyCode) : "impressions" === t && g === P.g.hb ? p(q.impressions, null) : "promoClick" === t && g === P.g.Bb ? p(q.promoClick.promotions, q.promoClick.actionField, !0) : "promoView" === t && g === P.g.ib ? p(q.promoView.promotions, q.promoView.actionField, !0) : e.hasOwnProperty(t) ? g === e[t] && p(q[t].products, q[t].actionField) : m[t] = q[t]);
                k(m, h)
            }
        }
        var c = []
          , d = {
            id: "transaction_id",
            revenue: "value",
            list: "item_list_name"
        }
          , e = {
            click: "select_item",
            detail: "view_item",
            add: "add_to_cart",
            remove: "remove_from_cart",
            checkout: "begin_checkout",
            checkout_option: "checkout_option",
            purchase: "purchase",
            refund: "refund"
        };
        (function(f) {
            Y.__gaawe = f;
            Y.__gaawe.C = "gaawe";
            Y.__gaawe.isVendorTemplate = !0;
            Y.__gaawe.priorityOverride = 0;
            Y.__gaawe.isInfrastructure = !1;
            Y.__gaawe.runInSiloedMode = !1
        }
        )(function(f) {
            var g;
            g = f.vtp_migratedToV2 ? String(f.vtp_measurementIdOverride) : String(f.vtp_measurementIdOverride || f.vtp_measurementId);
            if (l(g) && 0 === g.indexOf("G-")) {
                var h = String(f.vtp_eventName)
                  , m = {};
                c = [];
                f.vtp_sendEcommerceData && (Xh.hasOwnProperty(h) || "checkout_option" === h) && b(f, h, m);
                var n = f.vtp_eventSettingsVariable;
                if (n)
                    for (var p in n)
                        n.hasOwnProperty(p) && (m[p] = n[p]);
                if (f.vtp_eventSettingsTable) {
                    var q = SH(f.vtp_eventSettingsTable, "parameter", "parameterValue"), r;
                    for (r in q)
                        m[r] = q[r]
                }
                var t = SH(f.vtp_eventParameters, "name", "value"), u;
                for (u in t)
                    t.hasOwnProperty(u) && (m[u] = t[u]);
                var v = f.vtp_userDataVariable;
                v && (m[P.g.Ga] = v);
                if (m.hasOwnProperty(P.g.cb) || f.vtp_userProperties) {
                    var w = m[P.g.cb] || {};
                    k(SH(f.vtp_userProperties, "name", "value"), w);
                    m[P.g.cb] = w
                }
                var y = {
                    originatingEntity: cw(1, f.vtp_gtmEntityIndex, f.vtp_gtmEntityName)
                };
                if (0 < c.length) {
                    var x = {};
                    y.eventMetadata = (x.event_usage = c,
                    x)
                }
                a(m, Yh, function(A) {
                    return yb(A)
                });
                a(m, $h, function(A) {
                    return Number(A)
                });
                var B = f.vtp_gtmEventId;
                y.noGtmEvent = !0;
                Lx(Jx(g, h, m), B, y);
                I(f.vtp_gtmOnSuccess)
            } else
                I(f.vtp_gtmOnFailure)
        })
    }();

    Y.securityGroups.load_google_tags = ["google"],
    function() {
        function a(b, c, d) {
            return {
                tagId: c,
                firstPartyUrl: d
            }
        }
        (function(b) {
            Y.__load_google_tags = b;
            Y.__load_google_tags.C = "load_google_tags";
            Y.__load_google_tags.isVendorTemplate = !0;
            Y.__load_google_tags.priorityOverride = 0;
            Y.__load_google_tags.isInfrastructure = !1;
            Y.__load_google_tags.runInSiloedMode = !1
        }
        )(function(b) {
            var c = b.vtp_allowedTagIds || "specific"
              , d = b.vtp_allowFirstPartyUrls || !1
              , e = b.vtp_allowedFirstPartyUrls || "specific"
              , f = b.vtp_urls || []
              , g = b.vtp_tagIds || []
              , h = b.vtp_createPermissionError;
            return {
                assert: function(m, n, p) {
                    (function(q) {
                        if (!l(q))
                            throw h(m, {}, "Tag ID must be a string.");
                        if ("any" !== c && ("specific" !== c || -1 === g.indexOf(q)))
                            throw h(m, {}, "Prohibited Tag ID: " + q + ".");
                    }
                    )(n);
                    (function(q) {
                        if (void 0 !== q) {
                            if (!l(q))
                                throw h(m, {}, "First party URL must be a string.");
                            if (d) {
                                if ("any" === e)
                                    return;
                                if ("specific" === e)
                                    try {
                                        if (wg(hj(q), f))
                                            return
                                    } catch (r) {
                                        throw h(m, {}, "Invalid first party URL filter.");
                                    }
                            }
                            throw h(m, {}, "Prohibited first party URL: " + q);
                        }
                    }
                    )(p)
                },
                O: a
            }
        })
    }();
    Y.securityGroups.read_container_data = ["google"],
    Y.__read_container_data = function() {
        return {
            assert: function() {},
            O: function() {
                return {}
            }
        }
    }
    ,
    Y.__read_container_data.C = "read_container_data",
    Y.__read_container_data.isVendorTemplate = !0,
    Y.__read_container_data.priorityOverride = 0,
    Y.__read_container_data.isInfrastructure = !1,
    Y.__read_container_data.runInSiloedMode = !1;

    Y.securityGroups.sp = ["google"],
    Y.__sp = function(a) {
        var b, c = {};
        "DATA_LAYER" == a.vtp_customParamsFormat && Xa(a.vtp_dataLayerVariable) ? c = k(a.vtp_dataLayerVariable) : "USER_SPECIFIED" == a.vtp_customParamsFormat && (c = SH(a.vtp_customParams, "key", "value"));
        b = c;
        b[P.g.Ye] = !0;
        var d = !a.hasOwnProperty("vtp_enableConversionLinker") || !!a.vtp_enableConversionLinker;
        b[P.g.Za] = a.vtp_conversionCookiePrefix;
        b[P.g.wa] = d;
        b[P.g.ja] = tI(P.g.ja);
        a.vtp_enableDynamicRemarketing && (a.vtp_eventValue && (b[P.g.qa] = a.vtp_eventValue),
        a.vtp_eventItems && (b[P.g.ia] = a.vtp_eventItems));
        a.vtp_rdp && (b[P.g.Vb] = !0);
        a.vtp_userId && (b[P.g.Da] = a.vtp_userId);
        b[P.g.Ea] = tI(P.g.Ea),
        b[P.g.oa] = tI(P.g.oa),
        b[P.g.Rb] = tI(P.g.Rb),
        b[P.g.Ka] = tI(P.g.Ka);
        var e = "AW-" + a.vtp_conversionId
          , f = e + (a.vtp_conversionLabel ? "/" + a.vtp_conversionLabel : "");
        Vv(e, void 0, {
            source: 7,
            fromContainerExecution: !0,
            siloed: !0
        });
        var g = {}
          , h = {
            eventMetadata: (g.hit_type_override = "remarketing",
            g),
            noGtmEvent: !0,
            isGtmEvent: !0,
            onSuccess: a.vtp_gtmOnSuccess,
            onFailure: a.vtp_gtmOnFailure
        };
        Lx(Jx(zj(f), a.vtp_eventName || "", b), a.vtp_gtmEventId, h)
    }
    ,
    Y.__sp.C = "sp",
    Y.__sp.isVendorTemplate = !0,
    Y.__sp.priorityOverride = 0,
    Y.__sp.isInfrastructure = !1,
    Y.__sp.runInSiloedMode = !1;

    Y.securityGroups.ua = ["google"],
    function() {
        function a(n, p) {
            for (var q in n)
                if (!h[q] && n.hasOwnProperty(q)) {
                    var r = g[q] ? yb(n[q]) : n[q];
                    "anonymizeIp" != q || r || (r = void 0);
                    p[q] = r
                }
        }
        function b(n) {
            var p = {};
            n.vtp_gaSettings && k(SH(n.vtp_gaSettings.vtp_fieldsToSet, "fieldName", "value"), p);
            k(SH(n.vtp_fieldsToSet, "fieldName", "value"), p);
            yb(p.urlPassthrough) && (p._useUp = !0);
            n.vtp_transportUrl && (p._x_19 = n.vtp_transportUrl);
            return p
        }
        function c(n, p) {
            return void 0 === p ? p : n(p)
        }
        function d(n, p, q) {
            var r = function(N, Q, V) {
                for (var ca in N)
                    if (t.hasOwnProperty(ca)) {
                        var Z = V[Q] || {};
                        Z.actionField = Z.actionField || {};
                        Z.actionField[t[ca]] = N[ca];
                        V[Q] = Z
                    }
            }, t = {
                transaction_id: "id",
                affiliation: "affiliation",
                value: "revenue",
                tax: "tax",
                shipping: "shipping",
                coupon: "coupon",
                item_list_name: "list"
            }, u = {}, v = (u[P.g.qc] = "click",
            u[P.g.Na] = "detail",
            u[P.g.nc] = "add",
            u[P.g.oc] = "remove",
            u[P.g.Pb] = "checkout",
            u[P.g.Ja] = "purchase",
            u[P.g.sc] = "refund",
            u), w;
            if (n.vtp_useEcommerceDataLayer) {
                var y = !1;
                n.vtp_useGA4SchemaForEcommerce && (w = n.vtp_gtmCachedValues.eventModel,
                y = !!w);
                y || (w = tI("ecommerce", 1))
            } else
                n.vtp_ecommerceMacroData && (w = n.vtp_ecommerceMacroData.ecommerce,
                !w && n.vtp_useGA4SchemaForEcommerce && (w = n.vtp_ecommerceMacroData));
            if (!Xa(w))
                return;
            w = Object(w);
            var x = {}
              , B = w.currencyCode;
            n.vtp_useGA4SchemaForEcommerce && (B = B || w.currency);
            var A = Db(p, "currencyCode", B);
            A && (x.currencyCode = A);
            w.impressions && (x.impressions = w.impressions);
            w.promoView && (x.promoView = w.promoView);
            if (n.vtp_useGA4SchemaForEcommerce) {
                if (q === P.g.hb && !w.impressions)
                    w.items && (x.impressions = w.items,
                    x.translateIfKeyEquals = "impressions");
                else if (q === P.g.ib && !w.promoView)
                    w.promoView = {},
                    w.items && (x.promoView = {},
                    x.promoView.promotions = w.items,
                    x.translateIfKeyEquals = "promoView");
                else if (q === P.g.Bb && !w.promoClick)
                    w.promoClick = {},
                    w.items && (x.promoClick = {},
                    x.promoClick.promotions = w.items,
                    x.translateIfKeyEquals = "promoClick",
                    r(w, "promoClick", x));
                else if (v.hasOwnProperty(q)) {
                    var D = v[q];
                    !w[D] && w.items && (x[D] = {},
                    x[D].products = w.items,
                    x.translateIfKeyEquals = "products",
                    r(w, D, x))
                }
                var E = x.translateIfKeyEquals;
                if ("promoClick" === E || "products" === E)
                    return x
            }
            if (w.promoClick)
                return x.promoClick = w.promoClick,
                x;
            for (var C = "detail checkout checkout_option click add remove purchase refund".split(" "), F = 0; F < C.length; F++) {
                var L = w[C[F]];
                if (L)
                    return x[C[F]] = L,
                    x
            }
            n.vtp_useGA4SchemaForEcommerce && v.hasOwnProperty(q) && r(w, v[q], x);
            return x;
        }
        function e(n, p) {
            if (!f && (!mj() || !p._x_19 || n.vtp_useDebugVersion || n.vtp_useInternalVersion)) {
                var q = n.vtp_useDebugVersion ? "u/analytics_debug.js" : "analytics.js";
                n.vtp_useInternalVersion && !n.vtp_useDebugVersion && (q = "internal/" + q);
                f = !0;
                var r = n.vtp_gtmOnFailure
                  , t = mj() ? lj(p._x_19, "/analytics.js") : void 0
                  , u = or("https:", "http:", "//www.google-analytics.com/" + q, p && !!p.forceSSL);
                pI("analytics.js" === q && t ? t : u, function() {
                    var v = mw();
                    v && v.loaded || r();
                }, r)
            }
        }
        var f, g = {
            allowAnchor: !0,
            allowLinker: !0,
            alwaysSendReferrer: !0,
            anonymizeIp: !0,
            cookieUpdate: !0,
            exFatal: !0,
            forceSSL: !0,
            javaEnabled: !0,
            legacyHistoryImport: !0,
            nonInteraction: !0,
            useAmpClientId: !0,
            useBeacon: !0,
            storeGac: !0,
            allowAdFeatures: !0,
            allowAdPersonalizationSignals: !0,
            _cd2l: !0
        }, h = {
            urlPassthrough: !0
        }, m = function(n) {
            function p() {
                if (n.vtp_doubleClick || "DISPLAY_FEATURES" == n.vtp_advertisingFeaturesType)
                    w.displayfeatures = !0
            }
            var q = {}
              , r = {}
              , t = {};
            if (n.vtp_gaSettings) {
                var u = n.vtp_gaSettings;
                k(SH(u.vtp_contentGroup, "index", "group"), q);
                k(SH(u.vtp_dimension, "index", "dimension"), r);
                k(SH(u.vtp_metric, "index", "metric"), t);
                var v = k(u);
                v.vtp_fieldsToSet = void 0;
                v.vtp_contentGroup = void 0;
                v.vtp_dimension = void 0;
                v.vtp_metric = void 0;
                n = k(n, v)
            }
            k(SH(n.vtp_contentGroup, "index", "group"), q);
            k(SH(n.vtp_dimension, "index", "dimension"), r);
            k(SH(n.vtp_metric, "index", "metric"), t);
            var w = b(n)
              , y = String(n.vtp_trackingId || "")
              , x = ""
              , B = ""
              , A = "";
            n.vtp_setTrackerName && "string" == typeof n.vtp_trackerName ? "" !== n.vtp_trackerName && (A = n.vtp_trackerName,
            B = A + ".") : (A = "gtm" + yi(),
            B = A + ".");
            var D = function(ka, ha) {
                for (var ja in ha)
                    ha.hasOwnProperty(ja) && (w[ka + ja] = ha[ja])
            };
            D("contentGroup", q);
            D("dimension", r);
            D("metric", t);
            n.vtp_enableEcommerce && (x = n.vtp_gtmCachedValues.event,
            w.gtmEcommerceData = d(n, w, x));
            if ("TRACK_EVENT" === n.vtp_trackType)
                x = "track_event",
                p(),
                w.eventCategory = String(n.vtp_eventCategory),
                w.eventAction = String(n.vtp_eventAction),
                w.eventLabel = c(String, n.vtp_eventLabel),
                w.value = c(xb, n.vtp_eventValue);
            else if ("TRACK_PAGEVIEW" == n.vtp_trackType) {
                if (x = P.g.Qb,
                p(),
                "DISPLAY_FEATURES_WITH_REMARKETING_LISTS" == n.vtp_advertisingFeaturesType && (w.remarketingLists = !0),
                n.vtp_autoLinkDomains) {
                    var E = {};
                    E[P.g.Z] = n.vtp_autoLinkDomains;
                    E.use_anchor = n.vtp_useHashAutoLink;
                    E[P.g.sb] = n.vtp_decorateFormsAutoLink;
                    w[P.g.xa] = E
                }
            } else
                "TRACK_SOCIAL" === n.vtp_trackType ? (x = "track_social",
                w.socialNetwork = String(n.vtp_socialNetwork),
                w.socialAction = String(n.vtp_socialAction),
                w.socialTarget = String(n.vtp_socialActionTarget)) : "TRACK_TIMING" == n.vtp_trackType && (x = "timing_complete",
                w.eventCategory = String(n.vtp_timingCategory),
                w.timingVar = String(n.vtp_timingVar),
                w.value = xb(n.vtp_timingValue),
                w.eventLabel = c(String, n.vtp_timingLabel));
            n.vtp_enableRecaptcha && (w.enableRecaptcha = !0);
            n.vtp_enableLinkId && (w.enableLinkId = !0);
            var C = {};
            a(w, C);
            w.name || (C.gtmTrackerName = A);
            C.gaFunctionName = n.vtp_functionName;
            void 0 !== n.vtp_nonInteraction && (C.nonInteraction = n.vtp_nonInteraction);
            var F = Gm(Fm(Em(Dm(wm(new vm(n.vtp_gtmEventId,n.vtp_gtmPriorityId), C), n.vtp_gtmOnSuccess), n.vtp_gtmOnFailure), !0));
            n.vtp_useDebugVersion && n.vtp_useInternalVersion && (F.eventMetadata.suppress_script_load = !0);
            RD(y, x, Date.now(), F);
            var L = nw(n.vtp_functionName);
            if (pb(L)) {
                var N = function(ka) {
                    var ha = [].slice.call(arguments, 0);
                    ha[0] = B + ha[0];
                    L.apply(window, ha)
                };
                if ("TRACK_TRANSACTION" == n.vtp_trackType) {} else if ("DECORATE_LINK" == n.vtp_trackType) {} else if ("DECORATE_FORM" == n.vtp_trackType) {} else if ("TRACK_DATA" == n.vtp_trackType) {}
                e(n, w)
            } else
                I(n.vtp_gtmOnFailure)
        };
        Y.__ua = m;
        Y.__ua.C = "ua";
        Y.__ua.isVendorTemplate = !0;
        Y.__ua.priorityOverride = 0;
        Y.__ua.isInfrastructure = !1;
        Y.__ua.runInSiloedMode = !1
    }();
    Y.securityGroups.access_consent = ["google"],
    function() {
        function a(b, c, d) {
            var e = {
                consentType: c,
                read: !1,
                write: !1
            };
            switch (d) {
            case "read":
                e.read = !0;
                break;
            case "write":
                e.write = !0;
                break;
            default:
                throw Error("Invalid " + b + " request " + d);
            }
            return e
        }
        (function(b) {
            Y.__access_consent = b;
            Y.__access_consent.C = "access_consent";
            Y.__access_consent.isVendorTemplate = !0;
            Y.__access_consent.priorityOverride = 0;
            Y.__access_consent.isInfrastructure = !1;
            Y.__access_consent.runInSiloedMode = !1
        }
        )(function(b) {
            for (var c = b.vtp_consentTypes || [], d = b.vtp_createPermissionError, e = [], f = [], g = 0; g < c.length; g++) {
                var h = c[g]
                  , m = h.consentType;
                h.read && e.push(m);
                h.write && f.push(m)
            }
            return {
                assert: function(n, p, q) {
                    if (!l(p))
                        throw d(n, {}, "Consent type must be a string.");
                    if ("read" === q) {
                        if (-1 < e.indexOf(p))
                            return
                    } else if ("write" === q) {
                        if (-1 < f.indexOf(p))
                            return
                    } else
                        throw d(n, {}, "Access type must be either 'read', or 'write', was " + q);
                    throw d(n, {}, "Prohibited " + q + " on consent type: " + p + ".");
                },
                O: a
            }
        })
    }();
    Y.securityGroups.inject_script = ["google"],
    function() {
        function a(b, c) {
            return {
                url: c
            }
        }
        (function(b) {
            Y.__inject_script = b;
            Y.__inject_script.C = "inject_script";
            Y.__inject_script.isVendorTemplate = !0;
            Y.__inject_script.priorityOverride = 0;
            Y.__inject_script.isInfrastructure = !1;
            Y.__inject_script.runInSiloedMode = !1
        }
        )(function(b) {
            var c = b.vtp_urls || []
              , d = b.vtp_createPermissionError;
            return {
                assert: function(e, f) {
                    if (!l(f))
                        throw d(e, {}, "Script URL must be a string.");
                    try {
                        if (wg(hj(f), c))
                            return
                    } catch (g) {
                        throw d(e, {}, "Invalid script URL filter.");
                    }
                    throw d(e, {}, "Prohibited script URL: " + f);
                },
                O: a
            }
        })
    }();

    Y.securityGroups.gas = ["google"],
    Y.__gas = function(a) {
        var b = k(a)
          , c = b;
        c[Ce.ra] = null;
        c[Ce.Pg] = null;
        var d = b = c;
        d.vtp_fieldsToSet = d.vtp_fieldsToSet || [];
        var e = d.vtp_cookieDomain;
        void 0 !== e && (d.vtp_fieldsToSet.push({
            fieldName: "cookieDomain",
            value: e
        }),
        delete d.vtp_cookieDomain);
        return b
    }
    ,
    Y.__gas.C = "gas",
    Y.__gas.isVendorTemplate = !0,
    Y.__gas.priorityOverride = 0,
    Y.__gas.isInfrastructure = !1,
    Y.__gas.runInSiloedMode = !1;

    Y.securityGroups.awct = ["google"],
    function() {
        function a(b, c, d) {
            return function(e, f, g) {
                c[e] = "DATA_LAYER" === d ? tI(g) : b[f]
            }
        }
        (function(b) {
            Y.__awct = b;
            Y.__awct.C = "awct";
            Y.__awct.isVendorTemplate = !0;
            Y.__awct.priorityOverride = 0;
            Y.__awct.isInfrastructure = !1;
            Y.__awct.runInSiloedMode = !1
        }
        )(function(b) {
            var c = !b.hasOwnProperty("vtp_enableConversionLinker") || !!b.vtp_enableConversionLinker
              , d = !!b.vtp_enableEnhancedConversions || !!b.vtp_enableEnhancedConversion
              , e = SH(b.vtp_customVariables, "varName", "value") || {}
              , f = {}
              , g = (f[P.g.qa] = b.vtp_conversionValue || 0,
            f[P.g.Ba] = b.vtp_currencyCode,
            f[P.g.Ca] = b.vtp_orderId,
            f[P.g.Za] = b.vtp_conversionCookiePrefix,
            f[P.g.wa] = c,
            f[P.g.Jd] = d,
            f[P.g.ja] = tI(P.g.ja),
            f[P.g.la] = tI("developer_id"),
            f);
            g[P.g.Ea] = tI(P.g.Ea),
            g[P.g.oa] = tI(P.g.oa),
            g[P.g.Rb] = tI(P.g.Rb),
            g[P.g.Ka] = tI(P.g.Ka);
            b.vtp_rdp && (g[P.g.Vb] = !0);
            if (b.vtp_enableCustomParams)
                for (var h in e)
                    ei.hasOwnProperty(h) || (g[h] = e[h]);
            if (b.vtp_enableProductReporting) {
                var m = a(b, g, b.vtp_productReportingDataSource);
                m(P.g.Nd, "vtp_awMerchantId", "aw_merchant_id");
                m(P.g.Ld, "vtp_awFeedCountry", "aw_feed_country");
                m(P.g.Md, "vtp_awFeedLanguage", "aw_feed_language");
                m(P.g.Kd, "vtp_discount", "discount");
                m(P.g.ia, "vtp_items", "items")
            }
            b.vtp_enableShippingData && (g[P.g.od] = b.vtp_deliveryPostalCode,
            g[P.g.Ud] = b.vtp_estimatedDeliveryDate,
            g[P.g.xc] = b.vtp_deliveryCountry,
            g[P.g.dd] = b.vtp_shippingFee);
            b.vtp_transportUrl && (g[P.g.Kb] = b.vtp_transportUrl);
            if (b.vtp_enableNewCustomerReporting) {
                var n = a(b, g, b.vtp_newCustomerReportingDataSource);
                n(P.g.jd, "vtp_awNewCustomer", "new_customer");
                n(P.g.Od, "vtp_awCustomerLTV", "customer_lifetime_value")
            }
            var p;
            a: {
                if (b.vtp_enableEnhancedConversion) {
                    var q = b.vtp_cssProvidedEnhancedConversionValue || b.vtp_enhancedConversionObject;
                    if (q) {
                        p = {
                            enhanced_conversions_mode: "manual",
                            enhanced_conversions_manual_var: q
                        };
                        break a
                    }
                }
                p = void 0
            }
            var r = p;
            if (r) {
                var t = {};
                g[P.g.Td] = (t[b.vtp_conversionLabel] = r,
                t)
            }
            var u = "AW-" + b.vtp_conversionId
              , v = u + "/" + b.vtp_conversionLabel;
            Vv(u, b.vtp_transportUrl, {
                source: 7,
                fromContainerExecution: !0,
                siloed: !0
            });
            var w = {}
              , y = {
                eventMetadata: (w.hit_type_override = "conversion",
                w),
                noGtmEvent: !0,
                isGtmEvent: !0,
                onSuccess: b.vtp_gtmOnSuccess,
                onFailure: b.vtp_gtmOnFailure
            };
            Lx(Jx(zj(v), P.g.Ja, g), b.vtp_gtmEventId, y)
        })
    }();

    Y.securityGroups.write_data_layer = ["google"],
    function() {
        function a(b, c) {
            return {
                key: c
            }
        }
        (function(b) {
            Y.__write_data_layer = b;
            Y.__write_data_layer.C = "write_data_layer";
            Y.__write_data_layer.isVendorTemplate = !0;
            Y.__write_data_layer.priorityOverride = 0;
            Y.__write_data_layer.isInfrastructure = !1;
            Y.__write_data_layer.runInSiloedMode = !1
        }
        )(function(b) {
            var c = b.vtp_keyPatterns || []
              , d = b.vtp_createPermissionError;
            return {
                assert: function(e, f) {
                    if (!l(f))
                        throw d(e, {}, "Keys must be strings.");
                    try {
                        if (fg(f, c))
                            return
                    } catch (g) {
                        throw d(e, {}, "Invalid key filter.");
                    }
                    throw d(e, {}, "Prohibited write to data layer variable: " + f + ".");
                },
                O: a
            }
        })
    }();
    Y.securityGroups.logging = ["google"],
    function() {
        function a() {
            return {}
        }
        (function(b) {
            Y.__logging = b;
            Y.__logging.C = "logging";
            Y.__logging.isVendorTemplate = !0;
            Y.__logging.priorityOverride = 0;
            Y.__logging.isInfrastructure = !1;
            Y.__logging.runInSiloedMode = !1
        }
        )(function(b) {
            var c = b.vtp_environments || "debug"
              , d = b.vtp_createPermissionError;
            return {
                assert: function(e) {
                    var f;
                    if (f = "all" !== c && !0) {
                        var g = !1;
                        f = !g
                    }
                    if (f)
                        throw d(e, {}, "Logging is not enabled in all environments");
                },
                O: a
            }
        })
    }();

    Y.securityGroups.configure_google_tags = ["google"],
    function() {
        function a(b, c, d) {
            return {
                tagId: c,
                configuration: d
            }
        }
        (function(b) {
            Y.__configure_google_tags = b;
            Y.__configure_google_tags.C = "configure_google_tags";
            Y.__configure_google_tags.isVendorTemplate = !0;
            Y.__configure_google_tags.priorityOverride = 0;
            Y.__configure_google_tags.isInfrastructure = !1;
            Y.__configure_google_tags.runInSiloedMode = !1
        }
        )(function(b) {
            var c = b.vtp_allowedTagIds || "specific"
              , d = b.vtp_tagIds || []
              , e = b.vtp_createPermissionError;
            return {
                assert: function(f, g) {
                    if (!l(g))
                        throw e(f, {}, "Tag ID must be a string.");
                    if ("any" !== c && ("specific" !== c || -1 === d.indexOf(g)))
                        throw e(f, {}, "Prohibited configuration for Tag ID: " + g + ".");
                },
                O: a
            }
        })
    }();

    Y.securityGroups.html = ["customScripts"],
    function() {
        function a(d, e, f, g) {
            return function() {
                try {
                    if (0 < e.length) {
                        var h = e.shift()
                          , m = a(d, e, f, g);
                        if ("SCRIPT" == String(h.nodeName).toUpperCase() && "text/gtmscript" == h.type) {
                            var n = H.createElement("script");
                            n.async = !1;
                            n.type = "text/javascript";
                            n.id = h.id;
                            n.text = h.text || h.textContent || h.innerHTML || "";
                            h.charset && (n.charset = h.charset);
                            var p = h.getAttribute("data-gtmsrc");
                            p && (n.src = p,
                            sc(n, m));
                            d.insertBefore(n, null);
                            p || m()
                        } else if (h.innerHTML && 0 <= h.innerHTML.toLowerCase().indexOf("<script")) {
                            for (var q = []; h.firstChild; )
                                q.push(h.removeChild(h.firstChild));
                            d.insertBefore(h, null);
                            a(h, q, m, g)()
                        } else
                            d.insertBefore(h, null),
                            m()
                    } else
                        f()
                } catch (r) {
                    I(g)
                }
            }
        }
        function b(d) {
            if (H.body) {
                var e = d.vtp_gtmOnFailure
                  , f = kz(d.vtp_html, d.vtp_gtmOnSuccess, e)
                  , g = f.Nj
                  , h = f.onSuccess;
                if (d.vtp_useIframe) {} else
                    d.vtp_supportDocumentWrite ? c(g, h, e) : a(H.body, Ec(g), h, e)()
            } else
                oI(function() {
                    b(d)
                }, 200)
        }
        var c = function(d, e, f) {
            aw(function() {
                var g = google_tag_manager_external.postscribe.getPostscribe()
                  , h = {
                    done: e
                }
                  , m = H.createElement("div");
                m.style.display = "none";
                m.style.visibility = "hidden";
                H.body.appendChild(m);
                try {
                    g(m, d, h)
                } catch (n) {
                    I(f)
                }
            })
        };
        Y.__html = b;
        Y.__html.C = "html";
        Y.__html.isVendorTemplate = !0;
        Y.__html.priorityOverride = 0;
        Y.__html.isInfrastructure = !1;
        Y.__html.runInSiloedMode = !1
    }();

    Y.securityGroups.get_cookies = ["google"],
    function() {
        function a(b, c) {
            return {
                name: c
            }
        }
        (function(b) {
            Y.__get_cookies = b;
            Y.__get_cookies.C = "get_cookies";
            Y.__get_cookies.isVendorTemplate = !0;
            Y.__get_cookies.priorityOverride = 0;
            Y.__get_cookies.isInfrastructure = !1;
            Y.__get_cookies.runInSiloedMode = !1
        }
        )(function(b) {
            var c = b.vtp_cookieAccess || "specific"
              , d = b.vtp_cookieNames || []
              , e = b.vtp_createPermissionError;
            return {
                assert: function(f, g) {
                    if (!l(g))
                        throw e(f, {}, "Cookie name must be a string.");
                    if ("any" !== c && !("specific" === c && 0 <= d.indexOf(g)))
                        throw e(f, {}, 'Access to cookie "' + g + '" is prohibited.');
                },
                O: a
            }
        })
    }();
    var BI = {};
    BI.onHtmlSuccess = lz(!0),
    BI.onHtmlFailure = lz(!1);
    BI.dataLayer = Ii;
    BI.callback = function(a) {
        wi.hasOwnProperty(a) && pb(wi[a]) && wi[a]();
        delete wi[a]
    }
    ;
    BI.bootstrap = 0;
    BI._spx = !1;
    function CI() {
        ii[Cj()] = ii[Cj()] || BI;
        Sj();
        Wj() || z(Xj(), function(d, e) {
            Vv(d, e.transportUrl, e.context);
            O(92)
        });
        Fb(xi, Y.securityGroups);
        var a = Gj(Hj()), b, c = null == a ? void 0 : null == (b = a.context) ? void 0 : b.source;
        2 !== c && 4 !== c && 3 !== c || O(142);
        hz(),
        hf({
            dm: function(d) {
                return d === fz
            },
            vl: function(d) {
                return new iz(d)
            },
            fm: function(d) {
                for (var e = !1, f = !1, g = 2; g < d.length; g++)
                    e = e || 8 === d[g],
                    f = f || 16 === d[g];
                return e && f
            },
            Dm: function(d) {
                var e;
                if (d === fz)
                    e = d;
                else {
                    var f = yi();
                    gz[f] = d;
                    e = 'google_tag_manager["rm"]["' + Ej() + '"](' + f + ")"
                }
                return e
            }
        });
        kf = Bf
    }
    (function(a) {
        function b() {
            n = H.documentElement.getAttribute("data-tag-assistant-present");
            Ey(n) && (m = h.dj)
        }
        function c() {
            m && qc ? g(m) : a()
        }
        if (!G["__TAGGY_INSTALLED"]) {
            var d = !1;
            if (H.referrer) {
                var e = hj(H.referrer);
                d = "cct.google" === cj(e, "host")
            }
            if (!d) {
                var f = ao("googTaggyReferrer");
                d = !(!f.length || !f[0].length)
            }
            d && (G["__TAGGY_INSTALLED"] = !0,
            wc("https://cct.google/taggy/agent.js"))
        }
        var g = function(u) {
            var v = "GTM"
              , w = "GTM";
            ni && (v = "OGT",
            w = "GTAG");
            var y = G["google.tagmanager.debugui2.queue"];
            y || (y = [],
            G["google.tagmanager.debugui2.queue"] = y,
            wc("https://" + hi.Hd + "/debug/bootstrap?id=" + Hf.ctid + "&src=" + w + "&cond=" + u + "&gtm=" + Un()));
            var x = {
                messageType: "CONTAINER_STARTING",
                data: {
                    scriptSource: qc,
                    containerProduct: v,
                    debug: !1,
                    id: Hf.ctid,
                    targetRef: {
                        ctid: Hf.ctid,
                        isDestination: vj.je
                    },
                    aliases: yj(),
                    destinations: Bj()
                }
            };
            x.data.resume = function() {
                a()
            }
            ;
            hi.sk && (x.data.initialPublish = !0);
            y.push(x)
        }
          , h = {
            Mk: 1,
            fj: 2,
            tj: 3,
            ji: 4,
            dj: 5
        };
        h[h.Mk] = "GTM_DEBUG_LEGACY_PARAM";
        h[h.fj] = "GTM_DEBUG_PARAM";
        h[h.tj] = "REFERRER";
        h[h.ji] = "COOKIE";
        h[h.dj] = "EXTENSION_PARAM";
        var m = void 0
          , n = void 0
          , p = dj(G.location, "query", !1, void 0, "gtm_debug");
        Ey(p) && (m = h.fj);
        if (!m && H.referrer) {
            var q = hj(H.referrer);
            "tagassistant.google.com" === cj(q, "host") && (m = h.tj)
        }
        if (!m) {
            var r = ao("__TAG_ASSISTANT");
            r.length && r[0].length && (m = h.ji)
        }
        m || b();
        if (!m && Fy(n)) {
            var t = !1;
            Ac(H, "TADebugSignal", function() {
                t || (t = !0,
                b(),
                c())
            }, !1);
            G.setTimeout(function() {
                t || (t = !0,
                b(),
                c())
            }, 200)
        } else
            c()
    }
    )(function() {
        try {
            Qj();
            if (T(55)) {}
            Bl().F();
            rn();
            $l();
            var a = Ej();
            if (sj().canonical[a]) {
                var b = ii.zones;
                b && b.unregisterChild(xj());
                Hv().removeExternalRestrictions(Ej());
            } else {
                pt();
                Ai.m = "";
                Ai.F = Ai.M;
                Ai.H = "";
                Ai.da = "ad_storage|analytics_storage|ad_user_data|ad_personalization";
                Ai.T = "ad_storage|analytics_storage|ad_user_data";
                Ai.Wa = "";
                Sv();
                for (var c = data.resource || {}, d = c.macros || [], e = 0; e < d.length; e++)
                    $e.push(d[e]);
                for (var f = c.tags || [], g = 0; g < f.length; g++)
                    cf.push(f[g]);
                for (var h = c.predicates || [], m = 0; m < h.length; m++)
                    bf.push(h[m]);
                for (var n = c.rules || [], p = 0; p < n.length; p++) {
                    for (var q = n[p], r = {}, t = 0; t < q.length; t++) {
                        var u = q[t][0];
                        r[u] = Array.prototype.slice.call(q[t], 1);
                        "if" !== u && "unless" !== u || jf(r[u])
                    }
                    af.push(r)
                }
                ef = Y;
                ff = nz;
                Df = new Kf;
                var v = data.sandboxed_scripts
                  , w = data.security_groups;
                a: {
                    var y = data.runtime || []
                      , x = data.runtime_lines;
                    xz = new we;
                    MH();
                    Ze = wz();
                    var B = xz
                      , A = LH()
                      , D = new Tc("require",A);
                    D.Lb();
                    B.m.m.set("require", D);
                    for (var E = [], C = 0; C < y.length; C++) {
                        var F = y[C];
                        if (!Array.isArray(F) || 3 > F.length) {
                            if (0 === F.length)
                                continue;
                            break a
                        }
                        x && x[C] && x[C].length && uf(F, x[C]);
                        try {
                            xz.execute(F),
                            T(63) && jk && 50 === F[0] && E.push(F[1])
                        } catch (Ja) {}
                    }
                    T(63) && (lf = E)
                }
                if (v && v.length)
                    for (var L = ["sandboxedScripts"], N = 0; N < v.length; N++) {
                        var Q = v[N].replace(/^_*/, "");
                        xi[Q] = L
                    }
                NH(w);
                CI();
                if (!ri)
                    for (var V = rl() ? Ci(Ai.T) : Ci(Ai.da), ca = 0; ca < Ol.length; ca++) {
                        var Z = Ol[ca]
                          , R = Z
                          , oa = V[Z] ? "granted" : "denied";
                        wl().implicit(R, oa)
                    }
                Dy();
                Wv = !1;
                Xv = 0;
                if ("interactive" === H.readyState && !H.createEventObject || "complete" === H.readyState)
                    Zv();
                else {
                    Ac(H, "DOMContentLoaded", Zv);
                    Ac(H, "readystatechange", Zv);
                    if (H.createEventObject && H.documentElement.doScroll) {
                        var ka = !0;
                        try {
                            ka = !G.frameElement
                        } catch (Ja) {}
                        ka && $v()
                    }
                    Ac(G, "load", Zv)
                }
                iy = !1;
                "complete" === H.readyState ? ky() : Ac(G, "load", ky);
                jk && (dk(xk),
                T(23) && ek(xk),
                G.setInterval(wk, 864E5));
                dk(qz);
                dk($w);
                dk(vu);
                dk(Jm);
                dk(kx);
                ek(pm);
                dk(dt);
                ek(il);
                T(63) && (dk(ex),
                dk(fx),
                dk(gx));
                jk && T(52) && (dk(rz),
                dk(tz));
                Jy();
                ek(ml);
                T(81) && ek(Fx);
                T(62) && ek(Hy);
                google_tag_manager_external.postscribe.installPostscribe();
                dz();
                nl(1);
                FA();
                vi = Cb();
                BI.bootstrap = vi;
                if (T(55)) {}
            }
        } catch (Ja) {
            if (nl(4),
            jk) {
                var ja = qk(!1, !0, !0);
                zc(ja)
            }
        }
    });

}
)()
