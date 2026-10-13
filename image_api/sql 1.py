# import pyodbc
import pandas as pd
import sqlite3
from sqlite3 import Error



def getQueryResult(server,database,uid,pwd, tsql):
    cnxn = sqlite3.connect(server)

    c = cnxn.cursor()
    query=c.execute(tsql)
    
    cols = [column[0] for column in query.description]
    res= pd.DataFrame.from_records(data = query.fetchall(), columns = cols) #
    
    #res = pd.read_sql_query(tsql, cnxn)
        
        
    # rows = c.fetchall()
    # for r1,row1 in enumerate(rows):
    #     rstr_ = ''
    #     # print(row1)
    #     for r, row in enumerate(row1):
    #         # print(row)
    #         if (r == 0):
    #             rstr_ = str(row)
    return res

def runTSQLOnly(server, database, uid, pwd, tsql):
    cnxn = sqlite3.connect(server)
    cursor = cnxn.cursor()

    cursor.execute(tsql)
    cnxn.commit()
    cursor.close()
    cnxn.close()
    
    
#getQueryResult(server,database,uid,pwd, tsql)



# MS SQL FUNCTIONS
# def createTableFromFileHeader (filepathname,separator,server,database,uid,pwd,tablename):
#     read_file = open(filepathname, "r")
#     lines = read_file.readlines()
#     header_text=[]
#     create_table_query=''
#     for x, lines in enumerate(lines):
#         if(x==0):
#             header_text=lines.split(separator)
#         if(x>0):
#             break
#     for j,head in enumerate(header_text):
#         if(j<header_text.__len__()-1):
#             create_table_query=create_table_query+head.replace('\n','')+' varchar(200) null, '
#         else :
#             create_table_query=create_table_query+head.replace('\n','')+' varchar(200) null '
#     create_table_query='Create Table '+tablename+' (' + create_table_query +' )'
#     #print(create_table_query)
#     drop_table="if object_id ('dbo."+tablename+"') is not null drop table "+tablename+";"
#     runTSQLOnly(server, database, uid, pwd, drop_table)
#     runTSQLOnly(server, database, uid, pwd, create_table_query)
#     print ('Table Created')
    
    


# def bulkInsert(filepathname,separator,server,database,uid,pwd,tablename):
#     insertQuery ='BULK INSERT '+database+'.dbo.'+tablename+' FROM '+"'"+filepathname.replace('/','\\')+"' "+ "WITH (FIRSTROW = 2,FIELDTERMINATOR='"+separator+"',ROWTERMINATOR='\\n');"
#     runTSQLOnly(server, database, uid, pwd, insertQuery)
#     print('DataUploaded')

# def createTable_bulkInsert(filepathname, separator, server, database, uid, pwd, tablename):
#     createTableFromFileHeader(filepathname, separator, server, database, uid, pwd, tablename)
#     bulkInsert(filepathname, separator, server, database, uid, pwd, tablename)
#     print('Process completed')



###########################################################################################
# filepathname='C:/Users/esurmon/Desktop/Temp/RCA_EVENT_SUMMARY'
# separator='|'
# server='LOCALHOST'
# database='BLUEGRASS'
# uid='sa'
# pwd='surajit@123'
# tsql='SELECT * FROM SITEDBBLG'
# tablename='testtable'
###########################################################################################
# createTableFromFileHeader (filepathname,separator,server,database,uid,pwd,tablename)
# bulkInsert (filepathname,separator,server,database,uid,pwd,tablename)
# createTable_bulkInsert(filepathname, separator, server, database, uid, pwd, tablename)
