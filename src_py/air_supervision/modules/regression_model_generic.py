from abc import ABC, abstractmethod
import pandas
import numpy
import hat.aio
import hat.event.server.common
import pandas as pd
import numpy as np
from enum import Enum

from sklearn import preprocessing
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

class RETURN_TYPE(Enum):
    PREDICT = 1
    FIT = 2
    CREATE = 3


class GenericModel(ABC):

    def __init__(self, module):
        self.module = module

        self._id = None
        self.name = 'UNDEFINED'
        self.created = False

    def set_id(self, model_id):
        self._id = model_id
        self.created = True

    # @abstractmethod
    async def fit(self):

        if self._id:

            df = pandas.read_csv('../../dataset/ambient_temperature_system_failure.csv')
            df['timestamp'] = pd.to_datetime(df['timestamp'])

            df['hours'] = df['timestamp'].dt.hour
            df['daylight'] = ((df['hours'] >= 7) & (df['hours'] <= 22)).astype(int)
            df['DayOfTheWeek'] = df['timestamp'].dt.dayofweek
            df['WeekDay'] = (df['DayOfTheWeek'] < 5).astype(int)

            df['time_epoch'] = (df['timestamp'].astype(np.int64) / 100000000000).astype(np.int64)

            # creation of 4 distinct categories that seem useful (week end/day week & night/day)
            df['categories'] = df['WeekDay'] * 2 + df['daylight']


            # Take useful feature and standardize them
            data = df[['value', 'hours', 'daylight', 'DayOfTheWeek', 'WeekDay']]
            # breakpoint()

            new_data = []

            for index, row in df.iterrows():
                # print(row['value'], row['c2'])
                new_data.append([row['value'],row['hours'],row['daylight'],row['DayOfTheWeek'], row['WeekDay']])

            events = await self.module._engine.register(
                self.module._source,
                [_register_event(('aimm', 'fit', self._id),
                                 {
                                     'args': [new_data, None],
                                     'kwargs': {

                                     }
                                 }
                                 )])
            self.module._request_ids[events[0].event_id._asdict()['instance']] = (RETURN_TYPE.FIT, self.name)

    async def _create_instance(self, model_name):

        return_id = await self.module._engine.register(
            self.module._source,
            [_register_event(('aimm', 'create_instance'),
                             {
                                 'model_type': model_name,
                                 'args': [],
                                 'kwargs': {}
                             }
                             )])

        self.module._request_ids[return_id[0].event_id._asdict()['instance']] = (RETURN_TYPE.CREATE, self.name)

    async def predict(self, model_input):
        new_data = []
        for index, row in model_input.iterrows():
            # print(row['value'], row['c2'])
            new_data.append([row['value'], row['hours'], row['daylight'], row['DayOfTheWeek'], row['WeekDay']])

        events = await self.module._engine.register(
            self.module._source,
            [_register_event(('aimm', 'predict', self._id),
                             {'args': [new_data],
                              'kwargs': {
                              }
                              }
                             )])

        self.module._request_ids[events[0].event_id._asdict()['instance']] = (RETURN_TYPE.PREDICT, self.name)


def _register_event(event_type, payload, source_timestamp=None):
    return hat.event.server.common.RegisterEvent(
        event_type=event_type,
        source_timestamp=source_timestamp,
        payload=hat.event.server.common.EventPayload(
            type=hat.event.server.common.EventPayloadType.JSON,
            data=payload))
