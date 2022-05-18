import pandas
import numpy
import hat.aio
import hat.event.server.common

from src_py.air_supervision.modules.regression_model_generic import GenericModel


class SVM(GenericModel):
    def __init__(self, module, name):
        super().__init__(module, name)

    def set_id(self, model_id):
        super().set_id(model_id)

    def get_default_setting(self):
        # super().get_default_setting()
        return {'name': 'SVGDefault', 'value': -2}

    def set_default_setting(self, name, value):
        super().set_default_setting(name, value)

    async def fit(self):
        await super().fit()

    async def create_instance(self):
        await super()._create_instance('air_supervision.aimm.regression_models.' + self.name)

    async def predict(self, event):
        await super().predict(event)


class Cluster(GenericModel):
    def __init__(self, module, name):
        super().__init__(module, name)

    def set_id(self, model_id):
        super().set_id(model_id)

    def get_default_setting(self):
        # super().get_default_setting()
        return {'name': 'ClusterDefault', 'value': -2}

    def set_default_setting(self, name, value):
        super().set_default_setting(name, value)

    async def fit(self):
        await super().fit()

    async def create_instance(self):
        await super()._create_instance('air_supervision.aimm.regression_models.' + self.name)

    async def predict(self, event):
        await super().predict(event)


class Forest(GenericModel):
    def __init__(self, module, name):
        super().__init__(module, name)

    def set_id(self, model_id):
        super().set_id(model_id)

    def get_default_setting(self):
        # super().get_default_setting()
        return {'name': 'ForestDefault', 'value': -2}

    def set_default_setting(self, name, value):
        super().set_default_setting(name, value)

    async def fit(self):
        await super().fit()

    async def create_instance(self):
        await super()._create_instance('air_supervision.aimm.regression_models.' + self.name)

    async def predict(self, event):
        await super().predict(event)

