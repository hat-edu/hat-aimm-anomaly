from abc import ABC, abstractmethod
import pandas
import numpy
import hat.aio
import hat.event.server.common
import pandas as pd
import numpy as np
from enum import Enum


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
            import csv
            from datetime import datetime

            train_data = []

            with open("../../dataset/ambient_temperature_system_failure.csv", "r") as f:
                reader = csv.reader(f, delimiter="\t")
                for i, line in enumerate(reader):
                    if not i:
                        continue
                    timestamp = datetime.strptime(line[0].split(',')[0], '%Y-%m-%d %H:%M:%S')
                    value = float(line[0].split(',')[1])

                    train_data.append([
                        value,
                        timestamp.hour,
                        int((timestamp.hour >= 7) & (timestamp.hour <= 22)),
                        timestamp.weekday(),
                        int(timestamp.weekday() < 5)
                    ])


            events = await self.module._engine.register(
                self.module._source,
                [_register_event(('aimm', 'fit', self._id),
                                 {
                                     'args': [train_data, None],
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



        events = await self.module._engine.register(
            self.module._source,
            [_register_event(('aimm', 'predict', self._id),
                             {'args': [model_input.tolist()],
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
