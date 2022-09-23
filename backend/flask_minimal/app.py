from ast import arg
from tracemalloc import start
from flask import Flask
from flask_restful import Resource, Api, reqparse
import datetime
from connDB import ConnDB
import sys
app = Flask(__name__)
api = Api(app)
conndb = ConnDB()

class myApiTool():
    @staticmethod
    def eval_datetime(time: str):
        try:
            return datetime.datetime.fromisoformat(time)
        except Exception as e:
            print(f"{time} is not isofromat time", file=sys.stderr)
            return None


class WordsFreq(Resource, myApiTool):
    def __init__(self):
        super().__init__()
        self.input_args = reqparse.RequestParser()
        self.input_args.add_argument("start_time", type=str, help="require start_time", location='json', required=True)
        self.input_args.add_argument("end_time", type=str, help="require end_time", location='json', required=True)
        self.input_args.add_argument("screen_name", type=str, help="require screen_time", location='json', required=True)
        self.input_args.add_argument("choice", type=list, help="require choice", location='json')

    def get(self):
        args = self.input_args.parse_args()
        res = conndb.get_freq(args['start_time'], args['end_time'], args['screen_name'], args['choice'])
        return res, res['status']

    def post(self):
        args = self.input_args.parse_args()
        return args


api.add_resource(WordsFreq, "/api/wf/")

if __name__ == '__main__':
    app.run(debug=True)