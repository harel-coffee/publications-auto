"""
Create a database of imbalanced binary class datasets.
"""

# Author: Georgios Douzas <gdouzas@icloud.com>
#         Joao Fonseca <jpmrfonseca@gmail.com>
# License: MIT

from re import sub
from collections import Counter
from itertools import product
from urllib.parse import urljoin
from string import ascii_lowercase
from zipfile import ZipFile
from io import BytesIO, StringIO

import requests
import numpy as np
import pandas as pd
from sklearn.utils import check_X_y
from imblearn.datasets import make_imbalance

from .base import Datasets

UCI_URL = 'https://archive.ics.uci.edu/ml/machine-learning-databases/'
KEEL_URL = 'http://sci2s.ugr.es/keel/keel-dataset/datasets/imbalanced/'
FETCH_URLS = {
    'breast_tissue': urljoin(UCI_URL, '00192/BreastTissue.xls'),
    'ecoli': urljoin(UCI_URL, 'ecoli/ecoli.data'),
    'eucalyptus': 'https://www.openml.org/data/get_csv/3625/dataset_194_eucalyptus.arff',
    'glass': urljoin(UCI_URL, 'glass/glass.data'),
    'haberman': urljoin(UCI_URL, 'haberman/haberman.data'),
    'heart': urljoin(UCI_URL, 'statlog/heart/heart.dat'),
    'iris': urljoin(UCI_URL, 'iris/bezdekIris.data'),
    'libras': urljoin(UCI_URL, 'libras/movement_libras.data'),
    'liver': urljoin(UCI_URL, 'liver-disorders/bupa.data'),
    'pima': 'https://gist.githubusercontent.com/ktisha/c21e73a1bd1700294ef790c56c8aec1f/raw'
    '/819b69b5736821ccee93d05b51de0510bea00294/pima-indians-diabetes.csv',
    'vehicle': urljoin(UCI_URL, 'statlog/vehicle/'),
    'wine': urljoin(UCI_URL, 'wine/wine.data'),
    'new_thyroid_1': urljoin(
        urljoin(KEEL_URL, 'imb_IRlowerThan9/'), 'new-thyroid1.zip'
    ),
    'new_thyroid_2': urljoin(
        urljoin(KEEL_URL, 'imb_IRlowerThan9/'), 'new-thyroid2.zip'
    ),
    'cleveland': urljoin(
        urljoin(KEEL_URL, 'imb_IRhigherThan9p2/'), 'cleveland-0_vs_4.zip'
    ),
    'dermatology': urljoin(
        urljoin(KEEL_URL, 'imb_IRhigherThan9p3/'), 'dermatology-6.zip'
    ),
    'led': urljoin(
        urljoin(KEEL_URL, 'imb_IRhigherThan9p2/'), 'led7digit-0-2-4-5-6-7-8-9_vs_1.zip'
    ),
    'page_blocks_1_3': urljoin(
        urljoin(KEEL_URL, 'imb_IRhigherThan9p1/'), 'page-blocks-1-3_vs_4.zip'
    ),
    'vowel': urljoin(urljoin(KEEL_URL, 'imb_IRhigherThan9p1/'), 'vowel0.zip'),
    'yeast_1': urljoin(urljoin(KEEL_URL, 'imb_IRlowerThan9/'), 'yeast1.zip'),
}


class ImbalancedBinaryDatasets(Datasets):
    """Class to download, transform and save binary class imbalanced
    datasets."""

    MULTIPLICATION_FACTORS = [2, 3]
    RANDOM_STATE = 0

    @staticmethod
    def _calculate_ratio(multiplication_factor, y):
        """Calculate ratio based on IRs multiplication factor."""
        ratio = Counter(y).copy()
        ratio[1] = int(ratio[1] / multiplication_factor)
        return ratio

    def _make_imbalance(self, data, multiplication_factor):
        """Undersample the minority class."""
        X_columns = [col for col in data.columns if col != 'target']
        X, y = check_X_y(data.loc[:, X_columns], data['target'])
        if multiplication_factor > 1.0:
            sampling_strategy = self._calculate_ratio(multiplication_factor, y)
            X, y = make_imbalance(
                X,
                y,
                sampling_strategy=sampling_strategy,
                random_state=self.RANDOM_STATE,
            )
        columns = [str(num) for num in range(data.shape[1] - 1)] + ['target']
        data = pd.DataFrame(np.column_stack((X, y)), columns=columns)
        data['target'] = data['target'].astype(int)
        return data

    def download(self):
        """Download the datasets and append undersampled versions of them."""
        super(ImbalancedBinaryDatasets, self).download()
        undersampled_datasets = []
        for (name, data), factor in list(
            product(self.content_, self.MULTIPLICATION_FACTORS)
        ):
            ratio = self._calculate_ratio(factor, data.target)
            if ratio[1] >= 15:
                data = self._make_imbalance(data, factor)
                undersampled_datasets.append((f'{name} ({factor})', data))
        self.content_ += undersampled_datasets
        return self

    def fetch_breast_tissue(self):
        """Download and transform the Breast Tissue Data Set.
        The minority class is identified as the `car` and `fad`
        labels and the majority class as the rest of the labels.

        http://archive.ics.uci.edu/ml/datasets/breast+tissue
        """
        data = pd.read_excel(FETCH_URLS['breast_tissue'], sheet_name='Data')
        data = data.drop(columns='Case #').rename(columns={'Class': 'target'})
        data['target'] = data['target'].isin(['car', 'fad']).astype(int)
        return data

    def fetch_ecoli(self):
        """Download and transform the Ecoli Data Set.
        The minority class is identified as the `pp` label
        and the majority class as the rest of the labels.

        https://archive.ics.uci.edu/ml/datasets/ecoli
        """
        data = pd.read_csv(FETCH_URLS['ecoli'], header=None, delim_whitespace=True)
        data = data.drop(columns=0).rename(columns={8: 'target'})
        data['target'] = data['target'].isin(['pp']).astype(int)
        return data

    def fetch_eucalyptus(self):
        """Download and transform the Eucalyptus Data Set.
        The minority class is identified as the `best` label
        and the majority class as the rest of the labels.

        https://www.openml.org/d/188
        """
        data = pd.read_csv(FETCH_URLS['eucalyptus'])
        data = data.iloc[:, -9:].rename(columns={'Utility': 'target'})
        data = data[data != '?'].dropna()
        data['target'] = data['target'].isin(['best']).astype(int)
        return data

    def fetch_glass(self):
        """Download and transform the Glass Identification Data Set.
        The minority class is identified as the `1` label
        and the majority class as the rest of the labels.

        https://archive.ics.uci.edu/ml/datasets/glass+identification
        """
        data = pd.read_csv(FETCH_URLS['glass'], header=None)
        data = data.drop(columns=0).rename(columns={10: 'target'})
        data['target'] = data['target'].isin([1]).astype(int)
        return data

    def fetch_haberman(self):
        """Download and transform the Haberman's Survival Data Set.
        The minority class is identified as the `1` label
        and the majority class as the `0` label.

        https://archive.ics.uci.edu/ml/datasets/Haberman's+Survival
        """
        data = pd.read_csv(FETCH_URLS['haberman'], header=None)
        data.rename(columns={3: 'target'}, inplace=True)
        data['target'] = data['target'].isin([2]).astype(int)
        return data

    def fetch_heart(self):
        """Download and transform the Heart Data Set.
        The minority class is identified as the `2` label
        and the majority class as the `1` label.

        http://archive.ics.uci.edu/ml/datasets/statlog+(heart)
        """
        data = pd.read_csv(FETCH_URLS['heart'], header=None, delim_whitespace=True)
        data.rename(columns={13: 'target'}, inplace=True)
        data['target'] = data['target'].isin([2]).astype(int)
        return data

    def fetch_iris(self):
        """Download and transform the Iris Data Set.
        The minority class is identified as the `1` label
        and the majority class as the rest of the labels.

        https://archive.ics.uci.edu/ml/datasets/iris
        """
        data = pd.read_csv(FETCH_URLS['iris'], header=None)
        data.rename(columns={4: 'target'}, inplace=True)
        data['target'] = data['target'].isin(['Iris-setosa']).astype(int)
        return data

    def fetch_libras(self):
        """Download and transform the Libras Movement Data Set.
        The minority class is identified as the `1` label
        and the majority class as the rest of the labels.

        https://archive.ics.uci.edu/ml/datasets/Libras+Movement
        """
        data = pd.read_csv(FETCH_URLS['libras'], header=None)
        data.rename(columns={90: 'target'}, inplace=True)
        data['target'] = data['target'].isin([1]).astype(int)
        return data

    def fetch_liver(self):
        """Download and transform the Liver Disorders Data Set.
        The minority class is identified as the `1` label
        and the majority class as the '2' label.

        https://archive.ics.uci.edu/ml/datasets/liver+disorders
        """
        data = pd.read_csv(FETCH_URLS['liver'], header=None)
        data.rename(columns={6: 'target'}, inplace=True)
        data['target'] = data['target'].isin([1]).astype(int)
        return data

    def fetch_pima(self):
        """Download and transform the Pima Indians Diabetes Data Set.
        The minority class is identified as the `1` label
        and the majority class as the '0' label.

        https://www.kaggle.com/uciml/pima-indians-diabetes-database
        """
        data = pd.read_csv(FETCH_URLS['pima'], header=None, skiprows=9)
        data.rename(columns={8: 'target'}, inplace=True)
        return data

    def fetch_vehicle(self):
        """Download and transform the Vehicle Silhouettes Data Set.
        The minority class is identified as the `1` label
        and the majority class as the rest of the labels.

        https://archive.ics.uci.edu/ml/datasets/Statlog+(Vehicle+Silhouettes)
        """
        data = []
        for letter in ascii_lowercase[0:9]:
            partial_data = pd.read_csv(
                urljoin(FETCH_URLS['vehicle'], 'xa%s.dat' % letter),
                header=None,
                delim_whitespace=True,
            )
            partial_data = partial_data.rename(columns={18: 'target'})
            partial_data['target'] = partial_data['target'].isin(['van']).astype(int)
            data.append(partial_data)
        return pd.concat(data)

    def fetch_wine(self):
        """Download and transform the Wine Data Set.
        The minority class is identified as the `2` label
        and the majority class as the rest of the labels.

        https://archive.ics.uci.edu/ml/datasets/wine
        """
        data = pd.read_csv(FETCH_URLS['wine'], header=None)
        data.rename(columns={0: 'target'}, inplace=True)
        data['target'] = data['target'].isin([2]).astype(int)
        return data

    def fetch_new_thyroid_1(self):
        """Download and transform the Thyroid 1 Disease Data Set.
        The minority class is identified as the `positive`
        label and the majority class as the `negative` label.

        http://sci2s.ugr.es/keel/dataset.php?cod=145
        """
        zipped_data = requests.get(FETCH_URLS['new_thyroid_1']).content
        unzipped_data = (
            ZipFile(BytesIO(zipped_data)).read('new-thyroid1.dat').decode('utf-8')
        )
        data = pd.read_csv(
            StringIO(sub(r'@.+\n+', '', unzipped_data)),
            header=None,
            sep=', ',
            engine='python',
        )
        data.rename(columns={5: 'target'}, inplace=True)
        data['target'] = data['target'].isin(['positive']).astype(int)
        return data

    def fetch_new_thyroid_2(self):
        """Download and transform the Thyroid 2 Disease Data Set.
        The minority class is identified as the `positive`
        label and the majority class as the `negative` label.

        http://sci2s.ugr.es/keel/dataset.php?cod=146
        """
        zipped_data = requests.get(FETCH_URLS['new_thyroid_2']).content
        unzipped_data = (
            ZipFile(BytesIO(zipped_data)).read('newthyroid2.dat').decode('utf-8')
        )
        data = pd.read_csv(
            StringIO(sub(r'@.+\n+', '', unzipped_data)),
            header=None,
            sep=', ',
            engine='python',
        )
        data.rename(columns={5: 'target'}, inplace=True)
        data['target'] = data['target'].isin(['positive']).astype(int)
        return data

    def fetch_cleveland(self):
        """Download and transform the Heart Disease Cleveland Data Set.
        The minority class is identified as the `positive` label and
        the majority class as the `negative` label.

        http://sci2s.ugr.es/keel/dataset.php?cod=980
        """
        zipped_data = requests.get(FETCH_URLS['cleveland']).content
        unzipped_data = (
            ZipFile(BytesIO(zipped_data)).read('cleveland-0_vs_4.dat').decode('utf-8')
        )
        data = pd.read_csv(StringIO(sub(r'@.+\n+', '', unzipped_data)), header=None)
        data.rename(columns={13: 'target'}, inplace=True)
        data['target'] = data['target'].isin(['positive']).astype(int)
        return data

    def fetch_dermatology(self):
        """Download and transform the Dermatology Data Set.
        The minority class is identified as the `positive` label and
        the majority class as the `negative` label.

        http://sci2s.ugr.es/keel/dataset.php?cod=1330
        """
        data = pd.read_csv(FETCH_URLS['dermatology'], header=None)
        data = data.drop(columns=33).rename(columns={34: 'target'})
        data['target'] = data['target'].isin([1]).astype(int)
        return data

    def fetch_led(self):
        """Download and transform the LED Display Domain Data Set.
        The minority class is identified as the `positive` label and
        the majority class as the `negative` label.

        http://sci2s.ugr.es/keel/dataset.php?cod=998
        """
        zipped_data = requests.get(FETCH_URLS['led']).content
        unzipped_data = (
            ZipFile(BytesIO(zipped_data))
            .read('led7digit-0-2-4-5-6-7-8-9_vs_1.dat')
            .decode('utf-8')
        )
        data = pd.read_csv(StringIO(sub(r'@.+\n+', '', unzipped_data)), header=None)
        data.rename(columns={7: 'target'}, inplace=True)
        data['target'] = data['target'].isin(['positive']).astype(int)
        return data

    def fetch_page_blocks_1_3(self):
        """Download and transform the Page Blocks 1-3 Data Set.
        The minority class is identified as the `positive` label and
        the majority class as the `negative` label.

        http://sci2s.ugr.es/keel/dataset.php?cod=124
        """
        zipped_data = requests.get(FETCH_URLS['page_blocks_1_3']).content
        unzipped_data = (
            ZipFile(BytesIO(zipped_data))
            .read('page-blocks-1-3_vs_4.dat')
            .decode('utf-8')
        )
        data = pd.read_csv(StringIO(sub(r'@.+\n+', '', unzipped_data)), header=None)
        data.rename(columns={10: 'target'}, inplace=True)
        data['target'] = data['target'].isin(['positive']).astype(int)
        return data

    def fetch_vowel(self):
        """Download and transform the Vowel Recognition Data Set.
        The minority class is identified as the `positive` label and
        the majority class as the `negative` label.

        http://sci2s.ugr.es/keel/dataset.php?cod=127
        """
        zipped_data = requests.get(FETCH_URLS['vowel']).content
        unzipped_data = ZipFile(BytesIO(zipped_data)).read('vowel0.dat').decode('utf-8')
        data = pd.read_csv(StringIO(sub(r'@.+\n+', '', unzipped_data)), header=None)
        data.rename(columns={13: 'target'}, inplace=True)
        data['target'] = data['target'].isin([' positive']).astype(int)
        return data

    def fetch_yeast_1(self):
        """Download and transform the Yeast 1 Data Set.
        The minority class is identified as the `positive` label and
        the majority class as the `negative` label.

        http://sci2s.ugr.es/keel/dataset.php?cod=153
        """
        zipped_data = requests.get(FETCH_URLS['yeast_1']).content
        unzipped_data = ZipFile(BytesIO(zipped_data)).read('yeast1.dat').decode('utf-8')
        data = pd.read_csv(StringIO(sub(r'@.+\n+', '', unzipped_data)), header=None)
        data.rename(columns={8: 'target'}, inplace=True)
        data['target'] = data['target'].isin([' positive']).astype(int)
        return data
