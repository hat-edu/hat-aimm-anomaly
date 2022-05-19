import pandas
import numpy
import hat.aio
import hat.event.server.common

from src_py.air_supervision.modules.model_controller_generic import GenericModel

supported_models = ['Forest', 'SVM', 'Cluster']


class SVM(GenericModel):
    def __init__(self, module, name):
        super().__init__(module, name)

        self.hyperparameters = {
            'contamination': 0.3,
            'svm1': 1,
            'svm2': 'R'
        }


class Cluster(GenericModel):
    def __init__(self, module, name):
        super().__init__(module, name)

        self.hyperparameters = {
            'contamination': 0.3,
            'cluster1': 1,
            'cluster2': 'R'
        }



class Forest(GenericModel):
    def __init__(self, module, name):
        super().__init__(module, name)

        self.hyperparameters = {
            'contamination': 0.3,
            'other_test_p': 1,
            'third' : 'R'
        }




