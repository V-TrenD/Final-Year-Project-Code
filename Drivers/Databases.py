'''

@author: Vussy Dube
'''
import sqlite3
import struct


def _getUPPay(account):
    converts = 'CHEQUE', 'CREDIT', 'SAVINGS', 'TOKENS'
    for key in converts:
        temp = long(eval(account['UP_PAY'][key]))
        temp = bytearray(struct.pack("L", temp))
        temp.reverse()
        tempf = struct.unpack('f', temp)[0]
        account['UP_PAY'][key] = tempf
    return account

def toAccountPacket(d):
    print "toAccountPacket -> ",d
    converts = 'CHEQUE', 'CREDIT', 'SAVINGS', 'TOKENS'
    for key in converts:
        temp = long(eval(d['UP_PAY'][key]))
        temp = bytearray(struct.pack("L", temp)) 
        print ([ "0x%02x" % b for b in temp ])
        tempf = struct.unpack('f', temp)[0]
        temp.reverse()
        print key, tempf,struct.unpack('f', temp)[0]
        temp.reverse()
        d['UP_PAY'][key] = temp
    return d

def packageForSave(uppay):
    for key in uppay:
        result = "0x"
        binary = bytearray(struct.pack("f", uppay[key]))
        for b in binary:
            result += "%02X"%b
        uppay[key] = result
        
    return {'UP_PAY':uppay}

def to_hex_str(data):
    print data
    result = "0x"
    for x in data:
        if type(x) is str:
            result += "%02X"%ord(x)
        else:
            result += "%02X"%x
    return result

def getRawAccount(d):
    """Returns a raw representation of the state of the given account
    Makes it easier to transmit a full accounts data
    Format
        UPPAY <VALID> <CHEQUE> <CREDIT> <SAVINGS> <TOKENS>
        EXAMPLE 
            UPPAY 0x1E 0x0000FA43 0x0000c842 0x00007a44 0x00007a43
    """
    rawSTR = 'UPPAY'
    if 'VALID' in d:
        rawSTR += ' %c' % d['VALID']
    else:
        rawSTR += ' \x0F'
    print d['CHEQUE']
    rawSTR += d['CHEQUE']
    rawSTR += d['CREDIT']
    rawSTR += d['SAVINGS']
    rawSTR += d['TOKENS']
    return rawSTR

class Database:
    __table_name__ = None
    __columns__ = None
    __types__ = None

    def __init__(self, name="testBase.db"):
        if not isinstance(str, type(name)):
            self.db = sqlite3.connect(name)  # create a database with the given name
            self.db.text_factory = str
            try:  # try to open the Database
                sqlite3.connect(name)  #
            except:  #
                print "Database already Open"  #
        else:
            self.db = name
        self.cursor = self.db.cursor()

    def createTable(self, tbName="myTable", colNames=["ID"], colTypes=["SERIAL"], primary="ID"):
        s = "CREATE TABLE IF NOT EXISTS %s (\n" % tbName
        for col in range(len(colNames) - 1):
            s += '\t%s\t%s,\n' % (colNames[col], colTypes[col])
        s += " \t%s\t%s );" % (colNames[-1], colTypes[-1])
        # s += "\tPRIMARY KEY (%s) );" % primary
        print s
        try:
            return self.cursor.execute(s)
        except:
            print "Dropping Table"
            self.cursor.execute(" DROP TABLE %s" % tbName)
            return self.cursor.execute(s)

    def getTables(self):
        c = self.db.execute("SELECT name FROM sqlite_master WHERE type='table';")
        res = []
        for i in c:
            if "sqlite_sequence" not in i:
                res.append(i[0])
        return res

    def __getTable(self, tbName):
        print "TODO dataBase.getTable(%s)" % tbName
        
    def getTable(self):
        self.__getTable(self.__table_name__)

    def getAllin(self, tbName):
        self.cursor.execute("SELECT * FROM %s" % tbName)
        print "SELECT * FROM %s" % tbName
        return self.cursor.fetchall()

    def __insert__(self, tbName, col , values):
        s = "INSERT INTO %s\n" % tbName
        s += "%s \nVALUES\n %s;" % (tuple(col), tuple(values))
        s = "INSERT INTO %s %s VALUES (%s)" % \
              (tbName, tuple(col), (len(values) - 1) * '?,' + '?')
        print s
        self.cursor.execute(s, values)
        self.db.commit()
        return self.cursor.lastrowid

    def insert(self, *__args):
        print __args
        if len(__args) == 3:
            self.__insert__(__args[0], __args[1], __args[2])

    def close(self):
        self.db.close()

    def drop(self, tbname=__table_name__):
        print "Dropping table ", tbname
        self.db.execute("DROP TABLE %s" % tbname)

class ACCOUNTDATABASE(Database):
    __table_name__ = "PAYMENTS"
    __columns__ = "ID", "CARDID", "CARDKEY", "USERID", "USERINFO", "ACCOUNTTYPE", "BALANCE", "AVBALANCE", "APPLICATIONINFO" 
#     "ID",  #                1| Primary KEY            | INT*
#     "CARDID",  #            2| PYSICAL CARD ID        | CHAR[12]*
#     "CARDKEY",  #           3| CARDAPPLICATION KEY    | CHAR[16]*
#     "USERID",  #            4| USERID                 | INT*
#     "USERINFO",  #          5| USER Name and Surname  | TEXT
#     "ACCOUNTTYPE",  #       6| The Type of account    | INT
#     "BALANCE",  #           7| How Much is left in the| DECIMAL(10,2)
#     "AVBALANCE",  #         8| How much Can be used   | DECIMAL(10,2)
#     "APPLICATIONINFO"  #    9| Other Info             | TEXT
    __types__ = "INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL", "VARCHAR(12) NOT NULL", "VARCHAR(16)", "INT NOT NULL", "TEXT", "INT", "DECIMAL(10,2)", "DECIMAL(10,2)", "TEXT" 
#     "INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL",  #      1| Primary KEY
#     "VARCHAR(12) NOT NULL",  #                            2| PYSICAL CARD ID
#     "VARCHAR(16)",  #                                     3| CARDAPPLICATION KEY
#     "INT NOT NULL",  #                                    4| USERID
#     "TEXT",  #                                            5| USER Name and Surname
#     "INT",  #                                             6| The Type of account
#     "DECIMAL(10,2)",  #                                   7| How Much is left in the
#     "DECIMAL(10,2)",  #                                   8| How much Can be used
#     "TEXT"  #                                             9| Other Info
    def __init__(self, name='testBase.db'):
        Database.__init__(self, name)
        if self.__table_name__ not in self.getTables():
            self.createTable(self.__table_name__, self.__columns__, self.__types__)

    def drop(self, tbname=__table_name__):
        Database.drop(self, self.__table_name__)
        
    def getALL(self):
        return self.getAllin(self.__table_name__)
    
    def getAccounts(self, USER_ID):
        """Returns the accounts associated with the given ID and APP ID
        +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        Accounts Structure
        APP_NAME
            ATTRIBUTE1
            ATTRIBUTE2
            ATTRIBUTE3
        +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        UP_PAY
            VALID - Bitmap <3:0> [CHECKSUM |CHEQUE | CREDIT | SAVINGS | TOKENS]
            CHEQUE - FLOAT [0xFFFFFFFFF] 4 Bytes
            CREDIT - FLOAT [0xFFFFFFFFF] 4 Bytes
            SAVINGS - FLOAT [0xFFFFFFFFF] 4 Bytes
            TOKENS - FLOAT [0xFFFFFFFFF] 4 Bytes
        """
        c = self.cursor.execute("""SELECT * FROM PAYMENTS WHERE ID=?;""",[USER_ID])
        data = self.toDic(c.fetchone())
        result = data["APPLICATIONINFO"]
        # {'UP_PAY':{'VALID':0x05,'CHEQUE':0x00000000,'CREDIT':0x00000000,'SAVINGS':0x00000000,'TOKENS':0x00000000}}
        return result
    
    def getUPPay(self, USER_ID):
        c = self.cursor.execute("""SELECT * FROM PAYMENTS WHERE ID=?;""",[USER_ID])
        data = self.toDic(c.fetchone())
        result = data["APPLICATIONINFO"]
        result = _getUPPay(eval(result))
        # {'UP_PAY':{'VALID':0x05,'CHEQUE':0x00000000,'CREDIT':0x00000000,'SAVINGS':0x00000000,'TOKENS':0x00000000}}
        return result['UP_PAY']
    
    def fetAccount(self, userID, accountID):
        accounts = "UP_PAY", "OTHER"
        appLIST = toAccountPacket(eval(self.getAccounts(userID)))
        return getRawAccount(appLIST[accounts[accountID]])
    
    def checkCard(self, id=0x00):
        print "Checking CARD ID",id
        CARDIDNAME = ''
        r = range(0, 12)
        r.reverse()
        for i in r:
            CARDIDNAME+= "%c"%(((id & (0xFF << 8*i)) >> 8*i) & 0xFF)
        print r
        #CARDIDNAME = 'UPBANK\x00\x00L0V3'
        print CARDIDNAME
        c =  self.cursor.execute("""SELECT * FROM PAYMENTS WHERE CARDID=?;""",[CARDIDNAME])
        return self.toDic(c.fetchone())
        
    
    def toDic(self, data):
        result = {}
        for key in range(len(self.__columns__)):
            if data != None:
                result[self.__columns__[key]] = data[key]
            else:
                result[self.__columns__[key]] = None
        return result
    
    def app(self, UID, app):
        if app == "UP_PAY":
            return self.getUPPay(UID)
        
    
    def transfer_card_to_account(self, app,account, value, UID, CID, cardAccount):
        application = self.app(UID, app)
        if type(CID) is str:
            CID = eval(to_hex_str(CID))
        card = self.checkCard(CID)
        card_application =self.app(card['ID'], app)
        if application == None:
            print "No Such Application"
            return False, "No Such App"
        else:
            print "Application is", application
            if account in application and cardAccount in card_application:
                if card['ID'] == UID and account == cardAccount:
                    return True, "Self Transfer"
                print 'Account\t', application
                print 'Card\t', card_application
                card_application[account] -= value
                application[account] += value
                print 'Transfer', UID, '->',card['ID'],"[", CID,"]"
                print 'Account\t', application
                print 'Card\t', card_application
                self.cursor.execute("UPDATE PAYMENTS set APPLICATIONINFO=? WHERE ID=%d"%card['ID'], (str(packageForSave(card_application)), ))
                self.cursor.execute("UPDATE PAYMENTS set APPLICATIONINFO=? WHERE ID=%d"%UID, (str(packageForSave(application)), ))
                self.db.commit()
                return True, "Transfer Complete"
            else:
                print "No Such Account"
                return False, "No Such Account"
       
        
    
"""
CARD IDs are as follows
LOVE    76, 48, 86, 51- Highest specs and accounts
HATE    72, 64, 84, 51- Lowest specs and accounts
TIME    84, 124, 77, 51- Mid specs All accounts
FEAR    70, 51, 64, 82- Mid specs less accounts
R@ge    82, 64, 71, 51- Mid specs some accounts
"""
db = ACCOUNTDATABASE('type2.db')
print ACCOUNTDATABASE.__columns__
print ACCOUNTDATABASE.__types__
# db.insert(ACCOUNTDATABASE.__table_name__,
#           ACCOUNTDATABASE.__columns__,
#           (
#             "00001",  #             1| Primary KEY            | INT*
#             'UPBANK\0\0L0V3',  # [85, 80, 66, 65, 78, 75,  #    PROVIDER ID
#              # 0x00, 0x01,  # Region and CARD TYPE, ACCOUNT TYPE, 
#             # 76, 48, 86, 51  # CARD ID 
#             # ],  #                  2| PYSICAL CARD ID        | CHAR[12]*
#             "\xA1\x9A\x70\x86\xD4\x0F\x05\x45\xD8\xA1\x9D\xC9\x57\x69\xA0\xF8",  # [-95, -102, 112, -122, -44, 15, 5, 69, -40, -95, -99, -55, 87, 105, -96, -8],  #           3| CARDAPPLICATION KEY    | CHAR[16]*
#             "%d" % 0x76488651,  #          4| USERID                 | INT*
#             "Vusumuzi Dube",  #     5| USER Name and Surname  | TEXT
#             "%d" % 0,  #                   6| The Type of account    | INT
#             "%f" % 86858385778590.73,  #   7| How Much is left in the| DECIMAL(10,2)
#             "%f" % (86858385778590.73 * .75),  # 8| How much Can be used   | DECIMAL(10,2)
#             "No Info"  #    9| Other Info             | TEXT
#     ))

#db.cursor.execute("UPDATE PAYMENTS set APPLICATIONINFO=? WHERE ID=1",("{'UP_PAY':{'CHEQUE':'0x0000fa43','CREDIT':'0x0000c842','SAVINGS':'0x00007a44','TOKENS':'0x00007a43'}}",))
#db.db.commit()
#db.transfer_card_to_account("UP_PAY", "CHEQUE", 0, 1, 'UPBANK\x00\x00R@G3', 'CHEQUE')


c = db.getALL()
for x in c:
    print x
# ac = db.getUPPay(c[0][0])
# card = db.checkCard(eval(to_hex_str('UPBANK\x00\x00R@G3')))
# cc = db.getUPPay(card['ID'])
# print "Account\t", ac
# print "Card\t",cc
# cc['CREDIT'] -= 50
# ac['CREDIT'] += 50
# print 'Transfer Credit', 'CARD -> ACCOUNT'
# print "Account\t", ac
# print "Card\t",cc
# savestr = str(packageForSave(ac))
# print savestr
# db.cursor.execute("UPDATE PAYMENTS set APPLICATIONINFO=? WHERE ID=%d"%c[0][0], (savestr, ))
# savestr = str(packageForSave(cc))
# print savestr
#db.cursor.execute("UPDATE PAYMENTS set APPLICATIONINFO=? WHERE ID=%d"%card['ID'], (savestr, ))
#db.db.commit()



class CardDatabase(Database):
    __table_name__ = "CARDS"
    __columns__ = "ID", "CARDID", "CARDKEY", "USERID", "USERINFO", "ACCOUNTTYPE", "BALANCE", "AVBALANCE", "APPLICATIONINFO" 
#     "ID",  #                1| Primary KEY            | INT*
#     "CARDID",  #            2| PYSICAL CARD ID        | CHAR[12]*
#     "CARDKEY",  #           3| CARDAPPLICATION KEY    | CHAR[16]*
#     "USERID",  #            4| USERID                 | INT*
#     "USERINFO",  #          5| USER Name and Surname  | TEXT
#     "ACCOUNTTYPE",  #       6| The Type of account    | INT
#     "BALANCE",  #           7| How Much is left in the| DECIMAL(10,2)
#     "AVBALANCE",  #         8| How much Can be used   | DECIMAL(10,2)
#     "APPLICATIONINFO"  #    9| Other Info             | TEXT
    __types__ = "INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL", "VARCHAR(12) NOT NULL", "VARCHAR(16)", "INT NOT NULL", "TEXT", "INT", "DECIMAL(10,2)", "DECIMAL(10,2)", "TEXT" 
#     "INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL",  #      1| Primary KEY
#     "VARCHAR(12) NOT NULL",  #                            2| PYSICAL CARD ID
#     "VARCHAR(16)",  #                                     3| CARDAPPLICATION KEY
#     "INT NOT NULL",  #                                    4| USERID
#     "TEXT",  #                                            5| USER Name and Surname
#     "INT",  #                                             6| The Type of account
#     "DECIMAL(10,2)",  #                                   7| How Much is left in the
#     "DECIMAL(10,2)",  #                                   8| How much Can be used
#     "TEXT"  #                                             9| Other Info
    def __init__(self, name='testBase.db'):
        Database.__init__(self, name)
        if self.__table_name__ not in self.getTables():
            self.createTable(self.__table_name__, self.__columns__, self.__types__)

    def drop(self, tbname=__table_name__):
        Database.drop(self, self.__table_name__)
        
    def getALL(self):
        return self.getAllin(self.__table_name__)
