import data_preparation.config as config
from data_preparation.BaseEngine import BaseEngine
import datetime
import time
from data_preparation.data_processing.WordFrequencyEngine import WordFrequencyEngine
from emoji import EMOJI_DATA
import re
from pprint import pprint

from data_preparation.my_logging import logger


class TweetProcessingEngine(BaseEngine):

    def __init__(self):
        super().__init__()
        self.freqEngine = WordFrequencyEngine()

    def freq_life_time(self, userid):
        now = datetime.datetime.now()
        past = datetime.datetime(1888, 1, 1, 1, 1, 1)
        _project = {'text': 1}
        t_list = list(self.get_tweets_by_user_on_db(userid=userid, start_time=past, end_time=now, projection=_project))
        # combine them to strings
        target_s = ""
        for i in t_list:
            target_s += i['text']

        return WordFrequencyEngine.rough_tokenization(target_s)

    def begin_process(self, userid):
        col_processed = self.get_col_processed()
        col_raw_tweets = self.get_col_raw_tweets()

        project = {'id': 1, "_id": 0}
        all_id_from_cal_raw = list(col_raw_tweets.find({"author_id": userid}, projection=project))
        all_id_from_processed = list(col_processed.find({"author_id": userid}, projection=project))
        l_cal_raw = [x['id'] for x in all_id_from_cal_raw]
        l_processed = [x['id'] for x in all_id_from_processed]
        need_process = list(set(l_cal_raw) - set(l_processed))

        total = len(need_process)
        count = 0
        for i in need_process:
            s_time = time.time()
            val = list(col_raw_tweets.find({"id": i}, projection={'id': 1, 'text': 1, '_id': -1, 'created_at': 1}))
            text = val[0]['text']
            token = self.freqEngine.spacy_tokenization(text)
            # remove emoji, get list of number of url
            url_regex = r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*"
            num_regex = r"^(?!-0?(\.0+)?$)-?(0|[1-9]\d*)?(\.\d+)?(?<=\d)$"

            new_token = []
            url_l = []
            num_l = []
            for i in token:

                url_match = re.search(url_regex, i)
                num_match = re.search(num_regex, i)
                if i not in EMOJI_DATA and i[0] != '@':
                    if not url_match:
                        if not num_match:
                            special_char = False
                            for j in i:
                                if j not in config.LOWER_CASE_CHAR:
                                    special_char = True

                            if not special_char:
                                new_token.append(i)
                        else:
                            num_l.append(i)
                    else:
                        url_l.append(i)
            token = new_token

            at_l, hash_l, emoji_l = self.freqEngine.get_at_n_hash(text)
            e_time = time.time()
            # logger.debug(f" Processing time cost = {e_time - s_time}")

            _d = {'id': val[0]['id'],
                  'author_id': userid,
                  'created_at': val[0]['created_at'],
                  'words_list': token,
                  'at': at_l,
                  "emoji": emoji_l,
                  'hash': hash_l,
                  'num': num_l,
                  "url": url_l
                  }

            # pprint(_d)
            col_processed.insert_one(_d)
            count += 1
            print(f"Userid: {userid} TimeCost: {round(e_time- s_time, 4)} s (Progress: {count}/{total})")

    def test_portal(self, userid, method):
        now = datetime.datetime.now()
        past = datetime.datetime(1888, 1, 1, 1, 1, 1)
        _project = {'text': 1}
        t_list = list(self.get_tweets_by_user_on_db(userid=userid, start_time=past, end_time=now, projection=_project))
        # combine them to strings
        target_s = ""
        for i in t_list:
            target_s += i['text']

        return method(target_s)

    def cal_freq(self, userid: int, start_time: datetime.datetime, end_time: datetime.datetime, choice: list):
        print(f"st{start_time}")
        # fetch data
        res = list(
            self.get_col_processed().find({'author_id': userid, "created_at": {'$gte': start_time, "$lt": end_time}},
                                          projection={'_id': 0, 'id': 1, 'words_list': 1, 'at': 1, 'emoji': 1,
                                                      'hash': 1}))
        s_time = time.time()
        _d = {}

        if "word" in choice:
            freq_l = self._cal_freq(res, attr_name='words_list')
            freq_l = sorted(freq_l.items(), key=lambda item: item[1], reverse=True)
            _d["word"] = freq_l
        if "at" in choice:

            freq_l = self._cal_freq(res, attr_name='at')
            freq_l = sorted(freq_l.items(), key=lambda item: item[1], reverse=True)
            _d['at'] = freq_l
        if "emoji" in choice:
            freq_l = self._cal_freq(res, attr_name='emoji')
            freq_l = sorted(freq_l.items(), key=lambda item: item[1], reverse=True)
            _d["emoji"] = freq_l
        if "hash" in choice:
            freq_l = self._cal_freq(res, attr_name='hash')
            freq_l = sorted(freq_l.items(), key=lambda item: item[1], reverse=True)
            _d["hash"] = freq_l

        e_time = time.time()
        print(f"timecost = {e_time - s_time}\n len(res)={len(res)}")
        # print(_d)
        return _d



    @staticmethod
    def _cal_freq(token_words, attr_name):
        """
        :param token_words:  e.g. [["hello", "baby", "hello"]]
        :param attr_name:  e.g. words_list, hash, emoji
        :return:
        """
        freq_l = {}
        for i in token_words:
            for w in i[attr_name]:
                if w in freq_l:
                    freq_l[w] += 1
                else:
                    freq_l[w] = 1
        return freq_l
