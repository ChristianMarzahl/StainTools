from __future__ import division

import numpy as np

from staintools.stain_extractors.ruifrok_johnston_stain_extractor import RuifrokJohnstonStainExtractor
from staintools.stain_extractors.macenko_stain_extractor import MacenkoStainExtractor
from staintools.stain_extractors.vahadane_stain_extractor import VahadaneStainExtractor
from staintools.utils.misc_utils import convert_OD_to_RGB


class StainNormalizer(object):

    def __init__(self, method):
        if method.lower() == 'rj':
            self.extractor = RuifrokJohnstonStainExtractor
        elif method.lower() == 'macenko':
            self.extractor = MacenkoStainExtractor
        elif method.lower() == 'vahadane':
            self.extractor = VahadaneStainExtractor
        else:
            raise Exception('Method not recognized.')

    def fit(self, target):
        """
        Fit to a target image.

        :param target: Image RGB uint8.
        :return:
        """
        self.stain_matrix_target = self.extractor.get_stain_matrix(target)
        self.target_concentrations = self.extractor.get_concentrations(target, self.stain_matrix_target)
        self.maxC_target = np.percentile(self.target_concentrations, 99, axis=0).reshape((1, 2))
        self.stain_matrix_target_RGB = convert_OD_to_RGB(self.stain_matrix_target)  # useful to visualize.

    def transform(self, I):
        """
        Transform an image.

        :param I: Image RGB uint8.
        :return:
        """
        stain_matrix_source = self.extractor.get_stain_matrix(I)
        source_concentrations = self.extractor.get_concentrations(I, stain_matrix_source)
        assert stain_matrix_source.min() >= 0, "Stain matrix has negative values."
        assert source_concentrations.min() >= 0, "Concentration matrix has negative values."
        maxC_source = np.percentile(source_concentrations, 99, axis=0).reshape((1, 2))
        source_concentrations *= (self.maxC_target / maxC_source)
        tmp = 255 * np.exp(-1 * np.dot(source_concentrations, self.stain_matrix_target))
        return tmp.reshape(I.shape).astype(np.uint8)

    def get_hematoxylin(self, I):
        """
        Hematoxylin channel extraction.

        :param I: Image RGB uint8.
        :return:
        """
        h, w, c = I.shape
        stain_matrix_source = self.extractor.get_stain_matrix(I)
        source_concentrations = self.extractor.get_concentrations(I, stain_matrix_source)
        H = source_concentrations[:, 0].reshape(h, w)
        H = np.exp(-1 * H)
        return H
