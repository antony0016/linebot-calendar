import json


class PostbackRequest:

    def __init__(self, model='', method='', data=None, raw_data: str = ''):
        if data is None:
            data = {}
        self.model = model
        self.method = method
        self.data = data
        # decode line postback data to dict
        if raw_data != '':
            self.loads(raw_data.replace('+', ' '))

    def dumps(self, model=None, method=None, data=None) -> str:
        if data is not None:
            self.data = data
        if model is not None:
            self.model = model
        if method is not None:
            self.method = method
        return json.dumps(self.__dict__)

    def loads(self, raw_data: str):
        data = json.loads(raw_data)
        self.model = data['model']
        self.method = data['method']
        self.data = data['data']
