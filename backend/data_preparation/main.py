import os
import sys
from pathlib import Path

curPath = Path(os.path.abspath(os.path.dirname(__file__)))
print(str(curPath.parent.absolute()))
sys.path.append(str(curPath.parent.absolute()))

from data_preparation.BaseEngine import BaseEngine
from data_preparation.data_processing.TweetProcessingEngine import TweetProcessingEngine
from data_preparation.data_collection.TweetCollectionEngine import TweetCollectionEngine


def begin_tweet_pre_processing(argv):
    tpe = TweetProcessingEngine()
    if argv[1] == 'all':
        """python3 main.py begin_tweet_pre_processing all"""
        userid_list = tpe.get_distinct_users_on_db()
        for u in userid_list:
            tpe.begin_process(u)
    else:
        """python3 main.py begin_tweet_pre_processing [user_id]"""
        userid = int(argv[1])
        input(f"Are you sure to begin_tweet_pre_processing for this user-> {userid}")
        tpe.begin_process(userid)


def update_tweets_batch(argv):
    input("This function is defined in the script x 1/3")
    input("This function is defined in the script x 2/3")
    input("This function is defined in the scriptx  3/3")
    be = BaseEngine()
    update_list = ['KimKardashian', 'selenagomez', 'UQ_News', 'jacobcollier', 'cz_binance', 'BillGates',
                   'neymarjr', 'realmadrid', 'BrunoMars', 'RickandMorty', 'BTS_twt', 'NASA']
    for i in update_list:
        _id = be.get_user_id(i)
        print(f"Updating {i}, id: {_id}")
        update_tweets(['', _id, 'ignore_2x_confirm'])

def update_tweets(argv):
    """ if userid not exist, program will crawl and save it to db"""

    tce = TweetCollectionEngine()
    if argv[1] == 'all':
        """python3 main.py update_tweets all"""
        userid_list = tce.get_distinct_users_on_db()
        for u in userid_list:
            tce.insert_new_tweets_by_user(u)
    else:

        userid = argv[1]
        if argv[2] is not None and argv[2] != 'ignore_2x_confirm':
            input(f'Your Request userid is {userid}, are you sure to continue?')
        tce.insert_new_tweets_by_user(int(userid))


def update_user_profiles(argv):
    tce = TweetCollectionEngine()
    tce.update_users()


def get_user_id(argv):
    be = BaseEngine()
    print(be.get_user_id(argv[1]))


def main(argv):
    if argv[0] == "begin_tweet_pre_processing":
        begin_tweet_pre_processing(argv)

    elif argv[0] == "update_tweets":
        update_tweets(argv)

    elif argv[0] == 'update_user_profiles':
        update_user_profiles(argv)

    elif argv[0] == "get_user_id":
        get_user_id(argv)

    elif argv[0] == "buildall":
        print("Updating Tweets")
        update_tweets(['', 'all'])
        print("Processing")
        begin_tweet_pre_processing(['', 'all'])
        print("Updating User Profiles")
        update_user_profiles([])

    elif argv[0] == 'update_tweets_batch':
        update_tweets_batch(argv)


if __name__ == '__main__':
    main(sys.argv[1:])
