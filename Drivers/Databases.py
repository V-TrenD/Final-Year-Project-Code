'''

@author: Vussy Dube
'''
import sqlite3


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
    
"""
CARD IDs are as follows
LOVE    76, 48, 86, 51- Highest specs and accounts
HATE    72, 64, 84, 51- Lowest specs and accounts
TIME    84, 124, 77, 51- Mid specs All accounts
FEAR    70, 51, 64, 82- Mid specs less accounts
R@ge    82, 64, 71, 51- Mid specs some accounts
"""
db = ACCOUNTDATABASE()
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
c = db.getALL()
print c

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
