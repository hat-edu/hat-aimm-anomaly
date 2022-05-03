from hat import util
import hat.aio
import hat.event.server.common
from aimm.client import repl
from enum import Enum
import pandas as pd
import sys
import os
from datetime import datetime

sys.path.insert(0, '../../')
import importlib
# from src_py.air_supervision.modules.SVR import MultiOutputSVR, constant
from src_py.air_supervision.modules.regression_model_generic import RETURN_TYPE

import logging

mlog = logging.getLogger(__name__)
json_schema_id = None
json_schema_repo = None
_source_id = 0


async def create(conf, engine):
    module = ReadingsModule()
    # module.model_control = ModelControl()

    global _source_id
    module._source = hat.event.server.common.Source(
        type=hat.event.server.common.SourceType.MODULE,
        name=__name__,
        id=_source_id)
    _source_id += 1

    module._subscription = hat.event.server.common.Subscription([
        ('aimm', '*'),
        ('gui', 'system', 'timeseries', 'reading'),
        ('backValue', 'backValue', '*')])
    module._async_group = hat.aio.Group()
    module._engine = engine

    module._model_ids = {}

    module._current_model_name = None

    module._column_names = ['timestamp', 'value', 'hours', 'daylight', 'DayOfTheWeek', 'WeekDay']
    module._readings_pd = pd.DataFrame(columns=module._column_names)
    module._readings_done = None
    module._readings = []

    module._data_tracker = 0

    module._request_id = None

    module._MODELS = {}

    module._request_ids = {}

    return module


class ReadingsModule(hat.event.server.common.Module):

    @property
    def async_group(self):
        return self._async_group

    @property
    def subscription(self):
        return self._subscription

    async def create_session(self):
        return ReadingsSession(self._engine, self,
                               self._async_group.create_subgroup())

    def send_message(self, event, type_name):

        async def send_log_message():
            await self._engine.register(
                self._source,
                [_register_event(('gui', 'log', type_name), event.payload.data)])

        try:
            self._async_group.spawn(send_log_message)
        except:
            pass
    def process_state(self, event):
        if not event.payload.data['models'] or not self._MODELS:
            return

        for model_id, model_name in event.payload.data['models'].items():
            model_name = model_name.rsplit('.', 1)[-1]
            for m_name, model_inst in self._MODELS.items():
                if model_name == m_name:
                    model_inst.set_id(model_id)

        self.send_message(event, 'model_state')

    def process_action(self, event):
        if (request_instance := event.payload.data.get('request_id')['instance']) in self._request_ids \
                and event.payload.data.get('status') == 'DONE':

            request_type, model_name = self._request_ids[request_instance]
            del self._request_ids[request_instance]

            if request_type == RETURN_TYPE.CREATE:
                try:
                    self._async_group.spawn(self._MODELS[model_name].fit)
                except:
                    pass

            if request_type == RETURN_TYPE.FIT:
                self._current_model_name = model_name
                pass

            if request_type == RETURN_TYPE.PREDICT:
                tss = self._readings_done['timestamp'].tolist()
                vals = self._readings_done['value'].tolist()

                rez = [
                    self._process_event(
                        ('gui', 'system', 'timeseries', 'forecast'), {
                            'timestamp': t,
                            'is_anomaly': r,
                            'value': v
                        })
                    for r, t, v in zip(event.payload.data['result'], tss, vals)]

                return rez

    def process_aimm(self, event):

        if event.event_type[1] == 'state':
            return self.process_state(event)

        elif event.event_type[1] == 'action':
            return self.process_action(event)

    def process_reading(self, event):

        d = datetime.strptime(event.payload.data['timestamp'], '%Y-%m-%d %H:%M:%S')

        self._readings_pd.loc[len(self._readings_pd.index)] = [
            event.payload.data['timestamp'],
            event.payload.data['value'],
            d.hour,
            int((d.hour >= 7) & (d.hour <= 22)),
            d.weekday(),
            int(d.weekday() < 5)
        ]

        self._data_tracker += 1
        if self._data_tracker % 5 == 0:
            if self._current_model_name:
                try:
                    self._async_group.spawn(self._MODELS[self._current_model_name].predict,
                                            self._readings_pd.drop('timestamp', axis=1))
                except:
                    pass

                self._readings_done = self._readings_pd.copy()
                self._readings_pd = self._readings_pd[0:0]

    def process_return(self, event):

        model_n = 'constant'
        if 'model' in event.payload.data:
            model_n = event.payload.data['model']

        # IGNORED ON FIRST RUN
        for model_name, model_inst in self._MODELS.items():
            if model_n == model_name:
                self._current_model_name = model_name
                return

        MyClass = getattr(importlib.import_module("src_py.air_supervision.modules.regression_models"), model_n)

        self._MODELS[model_n] = MyClass(self)

        try:
            self._async_group.spawn(self._MODELS[model_n].create_instance)
        except:
            pass

    def _process_event(self, event_type, payload, source_timestamp=None):
        return self._engine.create_process_event(
            self._source,
            _register_event(event_type, payload, source_timestamp))


class ReadingsSession(hat.event.server.common.ModuleSession):

    def __init__(self, engine, module, group):
        self._engine = engine
        self._module = module
        self._async_group = group

    @property
    def async_group(self):
        return self._async_group

    async def process(self, changes):
        new_events = []

        for event in changes:

            result = {
                'aimm': self._module.process_aimm,
                'gui': self._module.process_reading,
                'backValue': self._module.process_return

            }[event.event_type[0]](event)

            if result:
                new_events.extend(result)

        return new_events


def _register_event(event_type, payload, source_timestamp=None):
    return hat.event.server.common.RegisterEvent(
        event_type=event_type,
        source_timestamp=source_timestamp,
        payload=hat.event.server.common.EventPayload(
            type=hat.event.server.common.EventPayloadType.JSON,
            data=payload))
