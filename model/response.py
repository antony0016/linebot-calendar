import json


class PostbackRequest:

    def __init__(self, model='', method='', data=dict, raw_data: str = ''):
        self.model = model
        self.method = method
        self.data = data
        if raw_data != '':
            self.loads(raw_data.replace('+', ' '))

    def dumps(self, data=None) -> str:
        if data is not None:
            self.data = data
        return json.dumps(self.__dict__)

    def loads(self, raw_data: str):
        data = json.loads(raw_data)
        self.model = data['model']
        self.method = data['method']
        self.data = data['data']
