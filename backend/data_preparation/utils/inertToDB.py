from pymongo import MongoClient
from datetime import datetime

client = MongoClient('mongodb://localhost:27017/')
db = client.TweetMiningTest
col = db.RawTweets
d = datetime.now()


