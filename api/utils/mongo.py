import hashlib,re
from django.conf import settings
import pymongo, datetime
import pandas as pd
import numpy as np


class MongoDB:
    collections = {
        "buff_csgo": {
            "id": "id",
            "item_id": "item_id",
            "name": "name",
            "price": "quick_price",
            "sell_num": "sell_num",
            "sell_min_price": "sell_min_price",
            "buy_max_price": "buy_max_price",
            "buy_num": "buy_num",
            "icon_url": "goods_info.icon_url",
            "category": "goods_info.info.tags.category.localized_name",
            "exterior": "goods_info.info.tags.exterior.localized_name",
            "quality": "goods_info.info.tags.quality.localized_name",
            "rarity": "goods_info.info.tags.rarity.localized_name",
            "type": "goods_info.info.tags.type.localized_name",
            "today": "today",
            "update_time": "update_time",
            "href": "https://buff.163.com/goods/",
        },
        "uuyp_csgo": {
            "id": "Id",
            "item_id": "item_id",
            "name": "CommodityName",
            "price": "Price",
            "sell_num": "OnSaleCount",
            "lease_deposit": "LeaseDeposit",
            "long_lease_price": "LongLeaseUnitPrice",
            "lease_price": "LeaseUnitPrice",
            "lease_num": "OnLeaseCount",
            "rent": "Rent",
            "icon_url": "IconUrl",
            "exterior": "Exterior",
            "quality": "Quality",
            "rarity": "Rarity",
            "type": "TypeName",
            "today": "today",
            "update_time": "update_time",
            "href": "https://www.youpin898.com/goodInfo?id=",
        },
        "steam_csgo": {
            "id": "hash_name",
            "item_id": "item_id",
            "name": "name",
            "price": "sell_price",
            "sell_num": "sell_listings",
            "sell_min_price": "sale_price",
            "icon_url": "asset_description.icon_url",
            "type": "asset_description.type",
            "today": "today",
            "update_time": "update_time",
            "href": "https://steamcommunity.com/market/listings/730/",
        },
        "c5_csgo": {
            "id": "id",
            "item_id": "item_id",
            "name": "itemName",
            "price": "cnyPrice",
            "sell_num": "quantity",
            "sell_min_price": "cnyPrice",
            "icon_url": "imageUrl",
            "exterior": "itemInfo.exteriorName",
            "quality": "itemInfo.qualityName",
            "rarity": "itemInfo.rarityName",
            "type": "itemInfo.typeName",
            "today": "today",
            "update_time": "update_time",
            "href": "https://www.c5game.com/csgo/",
        },
        "igxe_csgo": {
            "id": "id",
            "item_id": "item_id",
            "name": "market_name",
            "price": "reference_price",
            "sell_num": "sale_count",
            "sell_min_price": "ags_manual_min_price",
            "buy_max_price": "purchase_max_price",
            "buy_num": "purchase_count",
            "lease_deposit": "lease_sale_count",
            "long_lease_price": "lease_min_price",
            "lease_num": "lease_min_short_price",
            "icon_url": "icon_url",
            "exterior": "exterior_name",
            "quality": "quality_name",
            "rarity": "rarity_name",
            "type": "title",
            "today": "today",
            "update_time": "update_time",
            "href": "https://www.igxe.cn/product/730/",
        },
    }

    def __init__(
        self,
        database=settings.MONGODB_DB,
        host=settings.MONGODB_HOST,
        port=settings.MONGODB_PORT,
        username=settings.MONGODB_USER,
        password=settings.MONGODB_PSW,
        authSource=settings.MONGODB_AUTHSOURCE,
    ):
        self.client = pymongo.MongoClient(
            host=host,
            port=port,
            username=username,
            password=password,
            authSource=authSource,
        )
        self.database = self.client[database]
        self.write_list = []

    def get_item(self, col, item_id):

        res = self.database[col].find({"item_id": item_id})
        if len(list(res.clone())):
            return res[0]
        else:
            return {}

    def get_items(self, col, item_ids: list):
        time = datetime.datetime.today().date()
        pipeline=[{"$match":{"item_id": {"$in": item_ids}}},
            {
                "$lookup": {
                    "from": col + "_archive",
                    "pipeline": [
                        {"$match": {"archive_time": str(time)}},
                        {"$project": {"_id": 0}},
                        # 可以在这里添加更多的筛选条件
                    ],
                    "localField": "item_id",
                    "foreignField": "item_id",
                    "as": "today",
                },
            },
            {"$unwind": "$today"},
            {"$project": {"_id": 0}},
            {
                "$project": {
                    **{k: f"${v}" for k, v in self.collections.get(col).items()},
                    **{
                        "href": {
                            "$concat": [
                                self.collections.get(col, {}).get("href"),
                                {"$toString": "$id"},
                            ]
                        },
                        "buy_max_price": {
                            "$convert": {
                                "input": f"${self.collections.get(col,{}).get('buy_max_price')}",  # 你要转换的字段名
                                "to": "double",  # 目标类型为双精度浮点数
                                "onError": 0,  # 如果转换错误，则返回默认值0
                            }
                        },
                        "sell_min_price": {
                            "$convert": {
                                "input": f"${self.collections.get(col,{}).get('sell_min_price')}",  # 你要转换的字段名
                                "to": "double",  # 目标类型为双精度浮点数
                                "onError": 0,  # 如果转换错误，则返回默认值0
                            }
                        },
                        "price": {
                            "$convert": {
                                "input": f"${self.collections.get(col,{}).get('price')}",  # 你要转换的字段名
                                "to": "double",  # 目标类型为双精度浮点数
                                "onError": 0,  # 如果转换错误，则返回默认值0
                            }
                        },
                        "today_price": {
                            "$convert": {
                                "input": "$today.price",  # 你要转换的字段名
                                "to": "double",  # 目标类型为双精度浮点数
                                "onError": 0,  # 如果转换错误，则返回默认值0
                            }
                        },
                    },
                }
            },
            {
                "$project": {
                    **{k: 1 for k, v in self.collections.get(col).items()},
                    **{
                        "difference": {
                            "$subtract": ["$buy_max_price", "$sell_min_price"]
                        },
                    },
                    **{
                        "price_rate": {
                            "$cond": {
                                "if": {"$ne": ["$today_price", 0]},
                                "then": {
                                    "$round": [
                                        {
                                            "$divide": [
                                                {
                                                    "$subtract": [
                                                        "$price",
                                                        "$today_price",
                                                    ]
                                                },
                                                "$today_price",
                                            ]
                                        },
                                        4,
                                    ]
                                },
                                "else": 0,
                            }
                        }
                    },
                }
            }]
        results = self.database[col].aggregate(pipeline)
        result_dict = {result["item_id"]: result for result in results}

        # 添加未查到的item_id的空文档
        for item_id in item_ids:
            if item_id not in result_dict:
                result_dict[item_id] = {}  # 添加空文档

        # 按原始item_ids顺序返回结果
        return [result_dict[item_id] for item_id in item_ids]
    def get_item_archive(self, col, item_id:str,days=1):
        today_time=datetime.datetime.today()
        last_day_time=today_time-datetime.timedelta(days=days)
        res=[]
        for i in  self.database[col+'_archive'].find({"item_id": item_id, 'archive_time': {'$gt': str(last_day_time.date()),'$lte': str(today_time.date())}}).sort("archive_time", 1):
            i.pop('_id')
            res.append(i)
        return res
    def get_items_archive(self, col,days=1):
        today_time=datetime.date.today()
        last_day_time=datetime.date.today()-datetime.timedelta(days=days)
        res = (i.pop('ObjectId') for i in self.database[col].find({'archive_time': {'$gt': str(last_day_time.date()),'$lte': str(today_time.date())}}).sort("archive_time", 1))

        return res
    def get_leaks(
        self,
        col,
        pagesize=10,
        page=1,
        sort=0,
        exterior=None,
        name=None,
        quality=None,
        type=None,
        rarity=None,
        price_gte=None,
        price_lte=None,
    ):
        if sort == 0:
            sort_dict = {"difference": -1}
        elif sort == 1:
            sort_dict = {"difference": 1}

        time = datetime.datetime.today().date()
        match = [
            {
                "$expr": {
                    "$gt": [
                        {
                            "$toDouble": f"${self.collections.get(col).get('buy_max_price')}"
                        },
                        {
                            "$toDouble": f"${self.collections.get(col).get('sell_min_price')}"
                        },
                    ]
                }
            }
        ]
        if col == "steam_csgo":
            if exterior:
                match.append(
                    {
                        self.collections.get(col).get("name"): {
                            "$regex": f".*{exterior}.*"
                        }
                    }
                )
            match.append(
                {self.collections.get(col).get("name"): {"$regex": ".*"+re.escape(name)+".*"}}
            )
            if quality:

                match.append(
                    {
                        self.collections.get(col).get("type"): {
                            "$regex": f".*{quality}.*"
                        }
                    }
                )
            if rarity:
                match.append(
                    {self.collections.get(col).get("type"): {"$regex": f".*{rarity}.*"}}
                )
            if type:
                match.append(
                    {self.collections.get(col).get("type"): {"$regex": f".*{type}.*"}}
                )
        else:
            if exterior:
                match.append(
                    {
                        self.collections.get(col).get("exterior"): {
                            "$regex": f".*{exterior}.*"
                        }
                    }
                )
            match.append(
                {self.collections.get(col).get("name"): {"$regex": ".*"+re.escape(name)+".*"}}
            )
            if quality:
                if quality == "普通" and col == "uuyp_csgo":
                    match.append({self.collections.get(col).get("quality"): None})
                elif quality == "普通" and col == "c5_csgo":
                    match.append({self.collections.get(col).get("quality"): ""})
                else:
                    match.append(
                        {
                            self.collections.get(col).get("quality"): {
                                "$regex": f".*{quality}.*"
                            }
                        }
                    )
            if rarity:

                match.append(
                    {
                        self.collections.get(col).get("rarity"): {
                            "$regex": f".*{rarity}.*"
                        }
                    }
                )
            if type:
                match.append(
                    {self.collections.get(col).get("type"): {"$regex": f".*{type}.*"}}
                )
        if price_gte != None:
            match.append(
                {
                    "$expr": {
                        "$gte": [
                            {"$toDouble": f"${self.collections.get(col).get('price')}"},
                            price_gte,
                        ]
                    }
                }
            )
        if price_lte != None:
            match.append(
                {
                    "$expr": {
                        "$lte": [
                            {"$toDouble": f"${self.collections.get(col).get('price')}"},
                            price_lte,
                        ]
                    }
                }
            )
        pipeline = [
            {"$match": {"$and": match}},
            {
                "$lookup": {
                    "from": col + "_archive",
                    "pipeline": [
                        {"$match": {"archive_time": str(time)}},
                        {"$project": {"_id": 0}},
                        # 可以在这里添加更多的筛选条件
                    ],
                    "localField": "item_id",
                    "foreignField": "item_id",
                    "as": "today",
                },
            },
            {"$unwind": "$today"},
            {"$project": {"_id": 0}},
            {
                "$project": {
                    **{k: f"${v}" for k, v in self.collections.get(col).items()},
                    **{
                        "href": {
                            "$concat": [
                                self.collections.get(col, {}).get("href"),
                                {"$toString": "$id"},
                            ]
                        },
                        "buy_max_price": {
                            "$convert": {
                                "input": f"${self.collections.get(col,{}).get('buy_max_price')}",  # 你要转换的字段名
                                "to": "double",  # 目标类型为双精度浮点数
                                "onError": 0,  # 如果转换错误，则返回默认值0
                            }
                        },
                        "sell_min_price": {
                            "$convert": {
                                "input": f"${self.collections.get(col,{}).get('sell_min_price')}",  # 你要转换的字段名
                                "to": "double",  # 目标类型为双精度浮点数
                                "onError": 0,  # 如果转换错误，则返回默认值0
                            }
                        },
                        "price": {
                            "$convert": {
                                "input": f"${self.collections.get(col,{}).get('price')}",  # 你要转换的字段名
                                "to": "double",  # 目标类型为双精度浮点数
                                "onError": 0,  # 如果转换错误，则返回默认值0
                            }
                        },
                        "today_price": {
                            "$convert": {
                                "input": "$today.price",  # 你要转换的字段名
                                "to": "double",  # 目标类型为双精度浮点数
                                "onError": 0,  # 如果转换错误，则返回默认值0
                            }
                        },
                    },
                }
            },
            {
                "$project": {
                    **{k: 1 for k, v in self.collections.get(col).items()},
                    **{
                        "difference": {
                            "$subtract": ["$buy_max_price", "$sell_min_price"]
                        },
                    },
                    **{
                        "price_rate": {
                            "$cond": {
                                "if": {"$ne": ["$today_price", 0]},
                                "then": {
                                    "$round": [
                                        {
                                            "$divide": [
                                                {
                                                    "$subtract": [
                                                        "$price",
                                                        "$today_price",
                                                    ]
                                                },
                                                "$today_price",
                                            ]
                                        },
                                        4,
                                    ]
                                },
                                "else": 0,
                            }
                        }
                    },
                }
            },
            {"$sort": sort_dict},
            {"$skip": (page - 1) * pagesize},
            {"$limit": pagesize},
        ]
        pipeline2 = [
            {"$match": {"$and": match}},
            {"$group": {"_id": None, "total": {"$sum": 1}}},
        ]
        data = list(self.database[col].aggregate(pipeline))
        try:
            total = list(self.database[col].aggregate(pipeline2))[0].get("total", 0)
        except:
            total = 0
        return data, total

    def get_pages(
        self,
        col,
        pagesize=10,
        page=1,
        sort=0,
        exterior=None,
        name=None,
        quality=None,
        type=None,
        rarity=None,
        price_gte=None,
        price_lte=None,
    ):
        if sort == 0:
            sort_dict = {"update_time": -1}
        elif sort == 1:
            sort_dict = {"price_rate": 1}
        elif sort == -1:
            sort_dict = {"price_rate": -1}
        elif sort == -2:
            sort_dict = {"update_time": -1}
        elif sort == 2:
            sort_dict = {"update_time": 1}
        time = datetime.datetime.today().date()
        match = []
        if col == "steam_csgo":
            if exterior:
                match.append(
                    {
                        self.collections.get(col).get("name"): {
                            "$regex": f".*{exterior}.*"
                        }
                    }
                )
            match.append(
                {self.collections.get(col).get("name"): {"$regex": ".*"+re.escape(name)+".*"}}
            )
            if quality:

                match.append(
                    {
                        self.collections.get(col).get("type"): {
                            "$regex": f".*{quality}.*"
                        }
                    }
                )
            if rarity:
                match.append(
                    {self.collections.get(col).get("type"): {"$regex": f".*{rarity}.*"}}
                )
            if type:
                match.append(
                    {self.collections.get(col).get("type"): {"$regex": f".*{type}.*"}}
                )
        else:
            if exterior:
                match.append(
                    {
                        self.collections.get(col).get("exterior"): {
                            "$regex": f".*{exterior}.*"
                        }
                    }
                )
            match.append(
                {self.collections.get(col).get("name"): {"$regex": ".*"+re.escape(name)+".*"}}
            )
            if quality:
                if quality == "普通" and col == "uuyp_csgo":
                    match.append({self.collections.get(col).get("quality"): None})
                elif quality == "普通" and col == "c5_csgo":
                    match.append({self.collections.get(col).get("quality"): ""})
                else:
                    match.append(
                        {
                            self.collections.get(col).get("quality"): {
                                "$regex": f".*{quality}.*"
                            }
                        }
                    )
            if rarity:

                match.append(
                    {
                        self.collections.get(col).get("rarity"): {
                            "$regex": f".*{rarity}.*"
                        }
                    }
                )
            if type:
                match.append(
                    {self.collections.get(col).get("type"): {"$regex": f".*{type}.*"}}
                )
        if price_gte != None:
            match.append(
                {
                    "$expr": {
                        "$gte": [
                            {"$toDouble": f"${self.collections.get(col).get('price')}"},
                            price_gte,
                        ]
                    }
                }
            )
        if price_lte != None:
            match.append(
                {
                    "$expr": {
                        "$lte": [
                            {"$toDouble": f"${self.collections.get(col).get('price')}"},
                            price_lte,
                        ]
                    }
                }
            )
        pipeline = [
            {"$match": {"$and": match}},
            {
                "$lookup": {
                    "from": col + "_archive",
                    "pipeline": [
                        {"$match": {"archive_time": str(time)}},
                        {"$project": {"_id": 0}},
                        # 可以在这里添加更多的筛选条件
                    ],
                    "localField": "item_id",
                    "foreignField": "item_id",
                    "as": "today",
                },
            },
            {"$unwind": "$today"},
            {"$project": {"_id": 0}},
            {
                "$project": {
                    **{k: f"${v}" for k, v in self.collections.get(col).items()},
                    **{
                        "price": {
                            "$convert": {
                                "input": f"${self.collections.get(col,{}).get('price')}",  # 你要转换的字段名
                                "to": "double",  # 目标类型为双精度浮点数
                                "onError": 0,  # 如果转换错误，则返回默认值0
                            }
                        },
                        "today_price": {
                            "$convert": {
                                "input": "$today.price",  # 你要转换的字段名
                                "to": "double",  # 目标类型为双精度浮点数
                                "onError": 0,  # 如果转换错误，则返回默认值0
                            }
                        },
                    },
                }
            },
            {
                "$project": {
                    **{k: 1 for k, v in self.collections.get(col).items()},
                    **{
                        "href": {
                            "$concat": [
                                self.collections.get(col, {}).get("href"),
                                {"$toString": "$id"},
                            ]
                        },
                        "price_rate": {
                            "$cond": {
                                "if": {"$ne": ["$today_price", 0]},
                                "then": {
                                    "$round": [
                                        {
                                            "$divide": [
                                                {
                                                    "$subtract": [
                                                        "$price",
                                                        "$today_price",
                                                    ]
                                                },
                                                "$today_price",
                                            ]
                                        },
                                        4,
                                    ]
                                },
                                "else": 0,
                            }
                        },
                    },
                }
            },
            {"$sort": sort_dict},
            {"$skip": (page - 1) * pagesize},
            {"$limit": pagesize},
        ]
        pipeline2 = [
            {"$match": {"$and": match}},
            {"$group": {"_id": None, "total": {"$sum": 1}}},
        ]
        data = list(self.database[col].aggregate(pipeline))
        try:
            total = list(self.database[col].aggregate(pipeline2))[0].get("total", 0)
        except:
            total = 0
        return data, total
    def get_pages_all(
        self,
        col,
        sort=0,
        exterior=None,
        name=None,
        quality=None,
        type=None,
        rarity=None,
        price_gte=None,
        price_lte=None,
        page=None,
        pagesize=None,
    ):
        if sort == 0:
            sort_dict = {"update_time": -1}
        elif sort == 1:
            sort_dict = {"price_rate": 1}
        elif sort == -1:
            sort_dict = {"price_rate": -1}
        elif sort == -2:
            sort_dict = {"update_time": -1}
        elif sort == 2:
            sort_dict = {"update_time": 1}
        time = datetime.datetime.today().date()
        match = []
        if col == "steam_csgo":
            if exterior:
                match.append(
                    {
                        self.collections.get(col).get("name"): {
                            "$regex": f".*{exterior}.*"
                        }
                    }
                )
            match.append(
                {self.collections.get(col).get("name"): {"$regex": ".*"+re.escape(name)+".*"}}
            )
            if quality:

                match.append(
                    {
                        self.collections.get(col).get("type"): {
                            "$regex": f".*{quality}.*"
                        }
                    }
                )
            if rarity:
                match.append(
                    {self.collections.get(col).get("type"): {"$regex": f".*{rarity}.*"}}
                )
            if type:
                match.append(
                    {self.collections.get(col).get("type"): {"$regex": f".*{type}.*"}}
                )
        else:
            if exterior:
                match.append(
                    {
                        self.collections.get(col).get("exterior"): {
                            "$regex": f".*{exterior}.*"
                        }
                    }
                )
            match.append(
                {self.collections.get(col).get("name"): {"$regex": ".*"+re.escape(name)+".*"}}
            )
            if quality:
                if quality == "普通" and col == "uuyp_csgo":
                    match.append({self.collections.get(col).get("quality"): None})
                elif quality == "普通" and col == "c5_csgo":
                    match.append({self.collections.get(col).get("quality"): ""})
                else:
                    match.append(
                        {
                            self.collections.get(col).get("quality"): {
                                "$regex": f".*{quality}.*"
                            }
                        }
                    )
            if rarity:

                match.append(
                    {
                        self.collections.get(col).get("rarity"): {
                            "$regex": f".*{rarity}.*"
                        }
                    }
                )
            if type:
                match.append(
                    {self.collections.get(col).get("type"): {"$regex": f".*{type}.*"}}
                )
        if price_gte != None:
            match.append(
                {
                    "$expr": {
                        "$gte": [
                            {"$toDouble": f"${self.collections.get(col).get('price')}"},
                            price_gte,
                        ]
                    }
                }
            )
        if price_lte != None:
            match.append(
                {
                    "$expr": {
                        "$lte": [
                            {"$toDouble": f"${self.collections.get(col).get('price')}"},
                            price_lte,
                        ]
                    }
                }
            )
        pipeline = [
            {"$match": {"$and": match}},
            {
                "$lookup": {
                    "from": col + "_archive",
                    "pipeline": [
                        {"$match": {"archive_time": str(time)}},
                        {"$project": {"_id": 0}},
                        # 可以在这里添加更多的筛选条件
                    ],
                    "localField": "item_id",
                    "foreignField": "item_id",
                    "as": "today",
                },
            },
            {"$unwind": "$today"},
            {"$project": {"_id": 0}},
            {
                "$project": {
                    **{k: f"${v}" for k, v in self.collections.get(col).items()},
                    **{
                        "price": {
                            "$convert": {
                                "input": f"${self.collections.get(col,{}).get('price')}",  # 你要转换的字段名
                                "to": "double",  # 目标类型为双精度浮点数
                                "onError": 0,  # 如果转换错误，则返回默认值0
                            }
                        },
                        "today_price": {
                            "$convert": {
                                "input": "$today.price",  # 你要转换的字段名
                                "to": "double",  # 目标类型为双精度浮点数
                                "onError": 0,  # 如果转换错误，则返回默认值0
                            }
                        },
                    },
                }
            },
            {
                "$project": {
                    **{k: 1 for k, v in self.collections.get(col).items()},
                    **{
                        "href": {
                            "$concat": [
                                self.collections.get(col, {}).get("href"),
                                {"$toString": "$id"},
                            ]
                        },
                        "price_rate": {
                            "$cond": {
                                "if": {"$ne": ["$today_price", 0]},
                                "then": {
                                    "$round": [
                                        {
                                            "$divide": [
                                                {
                                                    "$subtract": [
                                                        "$price",
                                                        "$today_price",
                                                    ]
                                                },
                                                "$today_price",
                                            ]
                                        },
                                        4,
                                    ]
                                },
                                "else": 0,
                            }
                        },
                    },
                }
            },
            {"$sort": sort_dict},
        ]

        data = list(self.database[col].aggregate(pipeline))

        return data

    def getDetail(self, item_id):
        time = datetime.datetime.today().date()
        cols = ["steam_csgo", "uuyp_csgo", "c5_csgo", "igxe_csgo"]
        pipeline = [
            {"$match": {"item_id": item_id}},
            {
                "$lookup": {
                    "from": "buff_csgo" + "_archive",
                    "pipeline": [
                        {"$match": {"archive_time": str(time)}},
                        {"$project": {"_id": 0}},
                    ],
                    "localField": "item_id",
                    "foreignField": "item_id",
                    "as": "today",
                },
            },
            {"$project": {"_id": 0}},
            {"$unwind": "$today"},
            {
                "$project": {
                    **{
                        k: f"${v}" for k, v in self.collections.get("buff_csgo").items()
                    },
                    **{
                        "price": {
                            "$convert": {
                                "input": f"${self.collections.get('buff_csgo',{}).get('price')}",  # 你要转换的字段名
                                "to": "double",  # 目标类型为双精度浮点数
                                "onError": 0,  # 如果转换错误，则返回默认值0
                            }
                        },
                        "today_price": {
                            "$convert": {
                                "input": "$today.price",  # 你要转换的字段名
                                "to": "double",  # 目标类型为双精度浮点数
                                "onError": 0,  # 如果转换错误，则返回默认值0
                            }
                        },
                    },
                }
            },
            {
                "$project": {
                    **{k: 1 for k, v in self.collections.get("buff_csgo").items()},
                    **{
                        "href": {
                            "$concat": [
                                self.collections.get("buff_csgo", {}).get("href"),
                                {"$toString": "$id"},
                            ]
                        },
                        "price_rate": {
                            "$cond": {
                                "if": {"$ne": ["$today_price", 0]},
                                "then": {
                                    "$round": [
                                        {
                                            "$divide": [
                                                {
                                                    "$subtract": [
                                                        "$price",
                                                        "$today_price",
                                                    ]
                                                },
                                                "$today_price",
                                            ]
                                        },
                                        4,
                                    ]
                                },
                                "else": 0,
                            }
                        },
                    },
                }
            },
        ]
        for col in cols:
            pipeline.append(
                {
                    "$lookup": {
                        "from": col,
                        "localField": "item_id",
                        "let": {"item_id": "$item_id"},
                        "pipeline": [
                            {"$match": {"$expr": {"$eq": ["$item_id", "$$item_id"]}}},
                            {"$project": {"_id": 0}},
                            {
                                "$lookup": {
                                    "from": col + "_archive",
                                    "pipeline": [
                                        {"$match": {"archive_time": str(time)}},
                                        {"$project": {"_id": 0}},
                                        # 可以在这里添加更多的筛选条件
                                    ],
                                    "localField": "item_id",
                                    "foreignField": "item_id",
                                    "as": "today",
                                },
                            },
                            {"$unwind": "$today"},
                            {
                                "$project": {
                                    **{
                                        k: f"${v}"
                                        for k, v in self.collections.get(
                                            col, {}
                                        ).items()
                                    },
                                    **{
                                        
                                        "price": {
                                            "$convert": {
                                                "input": f"${self.collections.get(col,{}).get('price')}",  # 你要转换的字段名
                                                "to": "double",  # 目标类型为双精度浮点数
                                                "onError": 0,  # 如果转换错误，则返回默认值0
                                            }
                                        },
                                        "today_price": {
                                            "$convert": {
                                                "input": "$today.price",  # 你要转换的字段名
                                                "to": "double",  # 目标类型为双精度浮点数
                                                "onError": 0,  # 如果转换错误，则返回默认值0
                                            }
                                        },
                                    },
                                }
                            },
                            {
                                "$project": {
                                    **{
                                        k: 1
                                        for k, v in self.collections.get(
                                            col, {}
                                        ).items()
                                    },
                                    **{
                                        "href": {
                                            "$concat": [
                                                self.collections.get(col, {}).get(
                                                    "href"
                                                ),
                                                {"$toString": "$id"},
                                            ]
                                        },
                                        "today_price": 1,
                                        "price_rate": {
                                            "$cond": {
                                                "if": {"$ne": ["$today_price", 0]},
                                                "then": {
                                                    "$round": [
                                                        {
                                                            "$divide": [
                                                                {
                                                                    "$subtract": [
                                                                        "$price",
                                                                        "$today_price",
                                                                    ]
                                                                },
                                                                "$today_price",
                                                            ]
                                                        },
                                                        4,
                                                    ]
                                                },
                                                "else": 0,
                                            }
                                        },
                                    },
                                }
                            },
                        ],
                        "foreignField": "item_id",
                        "as": col,
                    }
                }
            )
        return tuple(self.database["buff_csgo"].aggregate(pipeline))[0]

    def insert_item(self, col, item):

        res = self.database[col].insert_one(item)
        return res.acknowledged

    def delete_item(self, col, item_id):
        res = self.database[col].delete_one({"item_id": item_id})
        return res.acknowledged

    def update_item(self, col, item_id, item, upsert=False):
        res = self.database[col].update_one({"item_id": item_id}, item, upsert=upsert)
        return res.acknowledged

    def get_all_items(self, col, rule=None):
        if rule is None:
            rule = {}
        return self.database[col].find(rule)

    def get_sorted_items(self, col, sort, rule=None, limit=0):
        if rule is None:
            rule = {}
        return self.database[col].find(rule).sort(sort, pymongo.ASCENDING).limit(limit)

    def close(self):
        self.client.close()

    def get_size(self, col):
        return self.database[col].estimated_document_count()
