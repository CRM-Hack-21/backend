# -*- coding: utf-8 -*-
import uuid

import requests
import vk_api
import time
import json

from pymongo import MongoClient

import XML as moduleXml
from fastapi import FastAPI, Header
from typing import Optional
from pydantic import BaseModel
from urllib import request
from fastapi.middleware.cors import CORSMiddleware
from mongo_db import init_db, init_auth, get_database, get_user_data, add_vk, add_good,db_get_id,check_auf, good_get, seller_id_get, good_get_array
from mongo_db import init_auth
XML = moduleXml.XML("settings")
VK = vk_api.VkApi(token=XML.parsingFile("token"))

done = False

groupsId = []
groupsShortName = ""
for child in XML.parsingFile("groups", False):
   groupsShortName += child.text + ","

for group in VK.method("groups.getById", {"group_id": "206619249"}):
    groupsId.append(group["id"] * -1)
    a = VK.method('photos.getMarketUploadServer', {"group_id": "206619249"})
app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
comp_dic = dict(name='name', mail='mail', password='password', vk_token='vk_token')
auth_dic = dict(_id='id', comp_id='id_comp')
good_dic = dict(name='name', description='none', category_id='0', main_photo_id='sad_photo', price=0, old_price=0, url='url',sellers_id='idsel')
good_rec_dic = dict(name='name', main_photo_id='sad_photo', price=0)
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    category_id: str
    main_photo: str
    price: float
    old_price: float
    url: str
#    tax: Optional[float] = None

class Reg(BaseModel):
    name: str
    mail: str
    password: str
   # vk_token: str

class Auth(BaseModel):
    mail: str
    password: str
    _uuid: str

class Token(BaseModel):
    vk_token: str
class Good(BaseModel):
    id: str


global mongo_db

client = get_database()

flag_err = dict(error='no error')
@app.get("/get_good_array")
async def get_goods_array(good: str):
    good_ = await good_get_array(client, good)
    return good_
@app.get("/get_good")
async def get_good(good: str):
    good_ = await good_get(client, good)
    good_rec_dic['name'] = good_['name']
    good_rec_dic['main_photo_id'] = good_['main_photo_id']
    good_rec_dic['price'] = good_['price']
    seller = await seller_id_get(client, good_['sellers_id'])
    good_rec_dic['seller_name'] = seller['name']
    return good_rec_dic

@app.post("/register")
async def reg(reg: Reg):
    comp_dic['name'] = reg.name
    comp_dic['mail'] = reg.mail
    comp_dic['password'] = reg.password
    return await init_db(client, comp_dic, auth_dic, flag_err)


@app.post("/vk_token")
async def vk_token(token: Token, Session: Optional[str] = Header(None)):
    print(token.vk_token)
    print(Session)
    return await add_vk(client, Session, token.vk_token)


@app.post("/login")
async def login(auth: Auth):
    auth_dic['mail'] = auth.mail
    auth_dic['password'] = auth.password
    return await get_user_data(client, auth_dic['mail'], auth_dic['password'], auth_dic, flag_err)


@app.post("/product")
async def create_item(item: Item, Session: Optional[str] = Header(None)):
    #return item


    user = await check_auf(client, Session)
    if user is None:
        return {'error': 'Access denied'}

    url=a["upload_url"]

    with request.urlopen(item.main_photo) as response:
        img = response.read()
        # name_img = os.path.basename(path_img)

        files = {'file': ("img1.png", img, 'multipart/form-data', {'Expires': '0'})}
        with requests.Session() as s:
            r = s.post(url, files=files)
            tmp=r.json()
            tmp["group_id"]= "206619249"
            print(r.status_code)
            print(r.json())
            e=VK.method('photos.saveMarketPhoto',tmp)
            print(e)
            print(type(e))

            e[0]['name'] = item.name
            e[0]['description'] = item.description
            e[0]['category_id'] = item.category_id

            good_id = str(uuid.uuid4())

            e[0]['main_photo_id'] = e[0]['id']
            e[0]['price'] = item.price
            e[0]['old_price'] = item.old_price

            good_dic['name'] = item.name
            good_dic['description'] = item.description
            good_dic['category_id'] = item.category_id

            good_dic['main_photo_id'] = e[0]['sizes'][0]['url']
            good_dic['price'] = item.price
            good_dic['old_price'] = item.old_price
            good_dic['sellers_id'] = user['comp_id']
            good_dic['_id'] = good_id
            # tmpp = await db_get_id(client,item,Session)

            good_dic['url'] = f'https://crm-platform-frontend.pages.dev/b2c/product/{good_id}'
            tmpp = await add_good(client, good_dic)
            e[0]['url'] = f'https://crm-platform-frontend.pages.dev/b2c/product/{good_id}'
######  end of  frontend  part
######  marketplace vk the lot
            VK.method('market.add', e[0])
