import sys
import os 
import time
import thread
import quickfix as fix
import quickfix44 as fix44
from datetime import datetime
import cPickle as p

class MinInc(fix.DoubleField):
    def __init__(self, data = None):
        if data == None:
            fix.DoubleField.__init__(self, 6350)
        else:
            fix.DoubleField.__init__(self, 6350, data)
class MinBr(fix.DoubleField):
    def __init__(self, data = None):
        if data == None:
            fix.DoubleField.__init__(self, 6351)
        else:
            fix.DoubleField.__init__(self, 6351, data)
class YTM(fix.DoubleField):
    def __init__(self, data = None):
        if data == None:
            fix.DoubleField.__init__(self, 6360)
        else:
            fix.DoubleField.__init__(self, 6360, data)
class YTW(fix.DoubleField):
    def __init__(self, data = None):
        if data == None:
            fix.DoubleField.__init__(self, 6361)
        else:
            fix.DoubleField.__init__(self, 6361, data)

class SECURITY():
    def __init__(self):
        self.Symbol="EURUSD_SPOT"
        self.MDEntryID=""
        self.MDUpdateAction=""
        self.MDEntryType=""
        self.MDEntryPx=0
        self.MDEntrySize=0
        self.MinQty=0
        self.MinInc=0 #
        self.MinBR=0 #
        self.YTM=0 #
        self.YTW=0 #
    def __str__(self):
	return '''
	Symbol is %s,
	MDEntryID is %s,
	MDUpdateAction is %s,
	MDEntryType is %s,
	MDEntryPx is %f,
	MDEntrySize is %f,
	MinQty is %f,
	MinInc is %f,
	MinBr is %f,
	YTM is %f,
	YTW is %f
	''' % (self.Symbol, self.MDEntryID, self.MDUpdateAction, self.MDEntryType, 
	       self.MDEntryPx, self.MDEntrySize, self.MinQty, self.MinInc, self.MinBR,
	       self.YTM, self.YTW)

class Application (fix.Application):
    global securities 
    securities = {"":SECURITY()}
    securities.clear()

    def onCreate (self, sessionID):
        self.sessionID = sessionID
        print ("Application created - session: " + sessionID.toString ())

    def onLogon (self, sessionID):
        print "Logon", sessionID

    def onLogout (self, sessionID):
        print "Logout", sessionID 

    def toAdmin (self, message, sessionID):
        pass 

    def fromAdmin (self, message, sessionID):
        pass
       
    def fromApp (self, message, sessionID):
        self.onMessage(message, sessionID)
        print "IN", message        
    
    def toApp (self, message, sessionID):
        print "OUT", message
	
    def run(self):
	print '''
	input 1 to fill the snapshot,
	input 2 to quit
    input 3 to request market data
	'''
	while True:
         input = raw_input()
         if input == '1':
             self.fillSnapShot()
         elif input == '3':
             self.queryOnMD()
         elif input == '2':
             break
         else:
             continue

    def fillSnapShot(self):
	home_path = '/home/roman/Downloads/fix_ntpro/snapshotfrompython.txt'
	f = file(home_path, "w")
	f.write('''symbol, entryid, updateaction, entrytype, price, size, minqty, mininc, minbr, ytm, ytw\n''')
	lst = list()
	for name, security in securities.items():	    
	    lst.append(security)
	lst.sort(key = lambda security:security.Symbol)
	for security in lst:	    
	    str='''%s,%s,%s,%s,%f,%f,%f,%f,%f,%f,%f\n''' % (security.Symbol, 
	       security.MDEntryID, security.MDUpdateAction, security.MDEntryType, 
	       security.MDEntryPx, security.MDEntrySize, security.MinQty, security.MinInc, security.MinBR,
	       security.YTM, security.YTW)
	    f.write(str)
	    #p.dump(address, f)
	f.close()
	if len(lst)>0:
	    print "Write the snapshot to the file ", home_path, "succesfully" 
	    
	
    def onMessage(self, message, sessionID):
        print "OnMessage %s" % message    
        msgType = fix.MsgType ()
        message.getHeader ().getField (msgType)
        if (msgType.getValue () == "X"):
	    print "MarketDataIncrementalRefresh %s" % message
	    noMDEntries = fix.NoMDEntries()
            message.getField(noMDEntries)
	    if (noMDEntries.getValue()!=1):
		print "NoMDEntries in MarketDataIncrementalRefresh is not 1!"
		return
	    group = fix44.MarketDataIncrementalRefresh.NoMDEntries()
	    message.getGroup(1, group);

	    entryID = fix.MDEntryID() 
	    group.getField(entryID)      
	    action = fix.MDUpdateAction()
	    group.getField(action);  
	    actionvalue = action.getValue() #0=New, 1=Update, 2=Delete)
	    if (actionvalue=='2'): #delete
		if entryID.getValue() in securities:
		    del securities[entryID.getValue()]
		return			    
	    security = SECURITY()
	    security.MDEntryID = entryID.getValue()
	    security.MDUpdateAction = action.getValue()
	    symbol = fix.Symbol()
	    if(group.isSetField(symbol)):
		group.getField(symbol)
		security.Symbol = symbol.getValue()
	    entryType = fix.MDEntryType()
	    if(group.isSetField(entryType)):
		group.getField(entryType)    
		security.MDEntryType = entryType.getValue()
	    price = fix.MDEntryPx ()
	    if(group.isSetField(price)):
		group.getField(price)
		security.MDEntryPx = price.getValue()
	    size = fix.MDEntrySize()
	    if(group.isSetField(size)):
		group.getField(size) 
		security.MDEntrySize = size.getValue()
	    qty = fix.MinQty ()
	    if(group.isSetField(qty)):
		group.getField(qty)
		security.MinQty	= qty.getValue()
	    inc = MinInc ()
	    if(message.isSetField(inc)):
		message.getField(inc)
		security.MinInc	= inc.getValue()
	    br = MinBr ()
	    if(message.isSetField(br)):
		message.getField(br)
		security.MinBR	= br.getValue()
	    ytm = YTM ()
	    if(message.isSetField(ytm)):
		message.getField(ytm)
		security.YTM = ytm.getValue()
	    ytw = YTW ()
	    if(message.isSetField(ytw)):
		message.getField(ytw)
		security.YTW = ytw.getValue();
	    print security
	    securities[entryID.getValue()] = security              

    def queryEnterOrder (self):
        print ("\nTradeCaptureReport (AE)\n")
        trade = fix.Message ()
        trade.getHeader ().setField (fix.BeginString (fix.BeginString_FIX44))
        trade.getHeader ().setField (fix.MsgType (fix.MsgType_TradeCaptureReport))

        trade.setField (fix.TradeReportTransType (fix.TradeReportTransType_NEW))       # 487
        trade.setField (fix.TradeReportID (self.genTradeReportID ()))                  # 571
        trade.setField (fix.TrdSubType (4))                        # 829
        trade.setField (fix.SecondaryTrdType (2))                  # 855
        trade.setField (fix.Symbol ("EURUSD"))                   # 55
        trade.setField (fix.LastQty (22))                          # 32
        trade.setField (fix.LastPx (21.12))                        # 31
        trade.setField (fix.TradeDate ((datetime.now ().strftime ("%Y%m%d"))))                      # 75
        trade.setField (fix.TransactTime ((datetime.now ().strftime ("%Y%m%d-%H:%M:%S.%f"))[:-3]))  # 60
        trade.setField (fix.PreviouslyReported (False))            # 570

        group = fix44.TradeCaptureReport ().NoSides ()

        group.setField (fix.Side (fix.Side_SELL))                  # 54
        group.setField (fix.OrderID (self.genOrderID ()))          # 37
        group.setField (fix.NoPartyIDs (1))                        # 453
        group.setField (fix.PartyIDSource (fix.PartyIDSource_PROPRIETARY_CUSTOM_CODE)) # 447
        group.setField (fix.PartyID ("CLEARING"))                  # 448
        group.setField (fix.PartyRole (fix.PartyRole_CLEARING_ACCOUNT))                # 452
        trade.addGroup (group)

        group.setField (fix.Side (fix.Side_BUY))                   # 54
        group.setField (fix.OrderID (self.genOrderID ()))          # 37
        group.setField (fix.NoPartyIDs (1))                        # 453
        group.setField (fix.PartyIDSource (fix.PartyIDSource_PROPRIETARY_CUSTOM_CODE)) # 447
        group.setField (fix.PartyID ("CLEARING"))                  # 448
        group.setField (fix.PartyRole (fix.PartyRole_CLEARING_ACCOUNT))                # 452
        trade.addGroup (group)

        fix.Session.sendToTarget (trade, self.sessionID)

    def queryOnMD(self):
        print("Sending message to server")
        message = fix.Message()
        header = message.getHeader();
        #header.setField(fix.BeginString("FIX.4.4"))
        #header.setField(fix.BodyLength(100))
        #header.setField(fix.MsgSeqNum(250))
        #header.setField(fix.SendingTime(datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.%f")))
        #header.setField(fix.SenderCompID("ALFN00_00_MD"))
        #header.setField(fix.TargetCompID("NTPROUAT"))
        header.setField(fix.MsgType("V"))
        message.setField(fix.MDReqID("EURUSD_FULL"))
        message.setField(fix.SubscriptionRequestType('1'))
        message.setField(fix.MarketDepth(0))
        message.setField(fix.MDUpdateType(1))
        message.setField(fix.NoRelatedSym(1))
        message.setField(fix.Symbol("EUR/USD"))
        message.setField(fix.NoMDEntryTypes(2))
        message.setValue(fix.MDEntryType('0'))
        message.addValue(fix.MDEntryType('1'))
        #message.setField(fix.CheckSum(240))
        #message.setField(fix.Text("Getting Market data"))

        fix.Session.sendToTarget (message, self.sessionID)

