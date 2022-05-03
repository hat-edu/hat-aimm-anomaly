from sklearn import multioutput, svm, exceptions
import aimm.plugins
import numpy as np
import pickle


import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn import preprocessing
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans


@aimm.plugins.model
class Cluster(aimm.plugins.Model):

    def __init__(self):
        pass

    def fit(self, x, y):

        data = x[['value', 'hours', 'daylight', 'DayOfTheWeek', 'WeekDay']]

        outliers_fraction = 0.01

        min_max_scaler = preprocessing.StandardScaler()
        np_scaled = min_max_scaler.fit_transform(data)
        data = pd.DataFrame(np_scaled)
        # reduce to 2 importants features
        pca = PCA(n_components=2)
        data = pca.fit_transform(data)
        # standardize these 2 new features
        min_max_scaler = preprocessing.StandardScaler()
        np_scaled = min_max_scaler.fit_transform(data)
        data = pd.DataFrame(np_scaled)

        # calculate with different number of centroids to see the loss plot (elbow method)
        n_cluster = range(1, 20)
        kmeans = [KMeans(n_clusters=i).fit(data) for i in n_cluster]
        scores = [kmeans[i].score(data) for i in range(len(kmeans))]

        # Not clear for me, I choose 15 centroids arbitrarily and add these data to the central dataframe
        x['cluster'] = kmeans[14].predict(data)
        x['principal_feature1'] = data[0]
        x['principal_feature2'] = data[1]

        # return Series of distance between each point and his distance with the closest centroid
        def getDistanceByPoint(data, model):
            distance = pd.Series()
            for i in range(0, len(data)):
                Xa = np.array(data.loc[i])
                Xb = model.cluster_centers_[model.labels_[i] - 1]
                distance.at[i] = np.linalg.norm(Xa - Xb)
            return distance

        # get the distance between each point and its nearest centroid. The biggest distances are considered as anomaly
        distance = getDistanceByPoint(data, kmeans[14])
        number_of_outliers = int(outliers_fraction * len(distance))
        threshold = distance.nlargest(number_of_outliers).min()
        # anomaly21 contain the anomaly result of method 2.1 Cluster (0:normal, 1:anomaly)
        x['anomaly21'] = (distance >= threshold).astype(int)

        a = x.loc[x['anomaly21'] == 1, ['time_epoch', 'value']]  # anomaly

        return a


    def predict(self, x):
        try:
            x = np.array(x).reshape(1, -1)
            return self._model.predict(x).reshape(-1).tolist()
        except exceptions.NotFittedError:
            return []

    def serialize(self):
        return pickle.dumps(self)

    @classmethod
    def deserialize(self, b):
        return pickle.loads(b)


@aimm.plugins.model
class Forest(aimm.plugins.Model):

    def __init__(self):
        outliers_fraction = 0.01
        self.model = IsolationForest(contamination=outliers_fraction)

    def fit(self, x, y):
        pd.DataFrame(data=x, columns=['value', 'hours', 'daylight', 'DayOfTheWeek', 'WeekDay'])

        min_max_scaler = preprocessing.StandardScaler()
        np_scaled = min_max_scaler.fit_transform(x)
        data = pd.DataFrame(np_scaled)
        # train isolation forest
        self.model.fit(data)
        return self

    def predict(self, X):
        rez = pd.Series(self.model.predict(X)).map({1: 0, -1: 1})
        return rez.values.tolist()

    def serialize(self):
        return pickle.dumps(self)

    @classmethod
    def deserialize(cls, b):
        return pickle.loads(b)


@aimm.plugins.model
class constant(aimm.plugins.Model):

    def __init__(self):
        # self._linear = LinearRegression()
        pass

    def fit(self, X, y):
        self._linear = self._linear.fit(X, y)
        return self

    def predict(self, X):
        # return self._linear.predict(X)

        return [800] * len(X)


    def serialize(self):
        return pickle.dumps(self)

    @classmethod
    def deserialize(cls, b):
        return pickle.loads(b)
