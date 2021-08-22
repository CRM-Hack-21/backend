import uuid
from hashlib import sha256
import os
def get_database():
    from pymongo import MongoClient
    import pymongo
    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = os.getenv('CONNECTION_STRING')


    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    from pymongo import MongoClient
    client = MongoClient(CONNECTION_STRING)
    return client


async def init_db(client, dick,model_auth,flag_err):
    companies_collection = client.my_db.get_collection('companies')
    dick['password'] = sha256(dick['password'].encode('utf-8')).hexdigest()
    result = companies_collection.insert_one(dick)
    rslt = await init_auth(client, dick, model_auth)

    # Create the database for our example (we will use the same database throughout the tutorial
    print(result)
    if result:
        return {'uuid': rslt}
    else:
        flag_err['error'] = 'Login or password incorrect'
        return flag_err


async def get_user_data(client, email, password,model_auth, flag_err):
    companies_collection = client.my_db.get_collection('companies')
    result = companies_collection.find_one({'mail': email})

    hashed_password = sha256(password.encode('utf-8')).hexdigest()
    flag_err['error'] = 'err'

    if result['password'] == hashed_password:
        uuid = await init_auth(client, result, model_auth)
        return {'uuid':uuid}
    else:
        flag_err['error'] = 'Login or password incorrect'
        return flag_err


async def init_auth(client, comp_col, model):
    auth_collection = client.my_db.get_collection('id')
    model['comp_id'] = comp_col['_id']
    model['_id'] = str(uuid.uuid4())
    auth_collection.insert_one(model)
    return model['_id']


async def check_auf(client, header):

    auth_collection = client.my_db.get_collection('id')
    res = auth_collection.find_one({'_id': header})

    return res


async def add_vk(client, header, token):

    col = await check_auf(client, header)

    err_flag = dict(error='Session is invalid')
    if col is None:
        print("errrrrooooorooroororororoo")
        return err_flag


    comp_collection = client.my_db.get_collection('companies')
    comp_collection.update_one({'_id': col['comp_id']}, {'$set': {'vk_token': token}})

    return { "msg": "ok" }
async def add_good(client, market_lot):
    goods_collection = client.my_db.get_collection('goods')
   # tmp = auth_collection.find_one({'_id': comp_dic['comp_id']})
    res=goods_collection.insert_one(market_lot)
    flag_err = dict(error='No error')

    if res is None:
        flag_err['error'] = 'Login or password incorrect'
        return flag_err
    else:
        return res

async def db_get_id(client,market_lot,Session):
    auth_collection = client.my_db.get_collection('id')
    result = market_lot.find_one({'_id': Session})
    return result

async def check_goods(client, header):

    auth_collection = client.my_db.get_collection('goods')
    res = auth_collection.find_one({'_id': header})

    return res
async def good_get_array(client,id ):
    print(id)
    auth_collection = client.my_db.get_collection('goods')
    #or elements in auth_collection.find_one
    result = list()
    for item in auth_collection.find({'sellers_id': id}):
        result.append(item)
   # print(result['main_photo_id'])
    return result
async def good_get(client,id ):
    print(id)
    auth_collection = client.my_db.get_collection('goods')
    result = auth_collection.find_one({'_id': id})
    print(result['main_photo_id'])
    return result
async def seller_id_get(client,id):
    auth_collection = client.my_db.get_collection('companies')
    result = auth_collection.find_one({'_id': id})
    return result