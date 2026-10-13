from sqlalchemy.orm import Session

import models, schemas

import pandas as pd



def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


################################################################################################################################
def get_master_poly(db: Session, item: schemas.MasterPolygonCreate, objectId: int):
    db_item = models.MasterPolygon(**item.dict(), objectId=objectId)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item



################################################################################################################################

'''
#######################################################################################################################

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



#MS SQL FUNCTIONS
def createTableFromFileHeader (filepathname,separator,server,database,uid,pwd,tablename):
    read_file = open(filepathname, "r")
    lines = read_file.readlines()
    header_text=[]
    create_table_query=''
    for x, lines in enumerate(lines):
        if(x==0):
            header_text=lines.split(separator)
        if(x>0):
            break
    for j,head in enumerate(header_text):
        if(j<header_text.__len__()-1):
            create_table_query=create_table_query+head.replace('\n','')+' varchar(200) null, '
        else :
            create_table_query=create_table_query+head.replace('\n','')+' varchar(200) null '
    create_table_query='Create Table '+tablename+' (' + create_table_query +' )'
    #print(create_table_query)
    drop_table="if object_id ('dbo."+tablename+"') is not null drop table "+tablename+";"
    runTSQLOnly(server, database, uid, pwd, drop_table)
    runTSQLOnly(server, database, uid, pwd, create_table_query)
    print ('Table Created')
    
    


def bulkInsert(filepathname,separator,server,database,uid,pwd,tablename):
    insertQuery ='BULK INSERT '+database+'.dbo.'+tablename+' FROM '+"'"+filepathname.replace('/','\\')+"' "+ "WITH (FIRSTROW = 2,FIELDTERMINATOR='"+separator+"',ROWTERMINATOR='\\n');"
    runTSQLOnly(server, database, uid, pwd, insertQuery)
    print('DataUploaded')

def createTable_bulkInsert(filepathname, separator, server, database, uid, pwd, tablename):
    createTableFromFileHeader(filepathname, separator, server, database, uid, pwd, tablename)
    bulkInsert(filepathname, separator, server, database, uid, pwd, tablename)
    print('Process completed')



##########################################################################################
filepathname='C:/Users/esurmon/Desktop/Temp/RCA_EVENT_SUMMARY'
separator='|'
server='LOCALHOST'
database='BLUEGRASS'
uid='sa'
pwd='surajit@123'
tsql='SELECT * FROM SITEDBBLG'
tablename='testtable'
##########################################################################################
createTableFromFileHeader (filepathname,separator,server,database,uid,pwd,tablename)
bulkInsert (filepathname,separator,server,database,uid,pwd,tablename)
createTable_bulkInsert(filepathname, separator, server, database, uid, pwd, tablename)













def get_resource(r):
    resourceSets = json.loads(r.text)
    try:
        for resource in resourceSets['resourceSets']:
            return [rsc for rsc in resource['resources']]
    except KeyError:
        try:
            resourcesSets = resourceSets['Response']['ResourceSets']
            resourceSet = resourcesSets['ResourceSet']
            if isinstance(resourceSet, dict):
                return resourceSet['Resources']
            elif isinstance(resourceSet, list):
                return [rsc for rsc in resourceSet['Resources']]
        except KeyError:
            print(KeyError)

def get_elevation(lat, lon):
    key = 'Ap2jFsGK3XZxoJYoaoE8pMLEk2B4x8OqgkolcqfDPwN-24_V9Vd__m5YOCyXPXch'
    point_query = f"{lat},{lon}"
    api_query = f'http://dev.virtualearth.net/REST/v1/Elevation/List?points={point_query}&heights=sealevel&key={key}'
    
    r = requests.get(api_query)
    if r.status_code != 200:
        raise r.raise_for_status()

    resource = get_resource(r)
    elevation = resource[0]['elevations'][0]

    return elevation
'''