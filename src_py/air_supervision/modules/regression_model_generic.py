from abc import ABC, abstractmethod

import hat.aio
import hat.event.server.common

from enum import Enum


class RETURN_TYPE(Enum):
    PREDICT = 1
    FIT = 2
    CREATE = 3


class GenericModel(ABC):

    def get_default_setting(self):
        return {'name': 'PrecisionDEF', 'value': -1}

    def set_default_setting(self, name, value):
        d = {'name': name, 'value': value}
        self.fit(**d)

    def __init__(self, module, name="undefined"):
        self.module = module

        self._id = None
        self.name = name
        self.created = False

    def set_id(self, model_id):
        self._id = model_id
        self.created = True

    async def _register_event(self, event_type, data, return_type):

        events = await self.module._engine.register(
            self.module._source,
            [hat.event.server.common.RegisterEvent(
                event_type=event_type,
                source_timestamp=None,
                payload=hat.event.server.common.EventPayload(
                    type=hat.event.server.common.EventPayloadType.JSON,
                    data=data))])
        self.module._request_ids[events[0].event_id._asdict()['instance']] = (return_type, self.name)

    # @abstractmethod
    async def fit(self, **kwargs):

        if self._id:
            train_data = self._get_dataset()

            event_type = ('aimm', 'fit', self._id)
            if 'name' in kwargs:
                data = {'args': [train_data, None], 'kwargs': {'additional': kwargs['value']}}
            else:
                data = {'args': [train_data, None], 'kwargs': {}}
            await self._register_event(event_type, data, RETURN_TYPE.FIT)

    async def _create_instance(self, model_name):

        event_type = ('aimm', 'create_instance')
        data = {'model_type': model_name, 'args': [], 'kwargs': {}}
        await self._register_event(event_type, data, RETURN_TYPE.CREATE)

    async def predict(self, model_input):

        event_type = ('aimm', 'predict', self._id)
        data = {'args': [model_input.tolist()], 'kwargs': {}}
        await self._register_event(event_type, data, RETURN_TYPE.PREDICT)

    def _get_dataset(self):
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

                value = (float(value) - 32) * 5 / 9

                train_data.append([
                    value,
                    timestamp.hour,
                    int((timestamp.hour >= 7) & (timestamp.hour <= 22)),
                    timestamp.weekday(),
                    int(timestamp.weekday() < 5)
                ])
        return train_data

