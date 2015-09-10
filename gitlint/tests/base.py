from unittest import TestCase

import os


class BaseTestCase(TestCase):
    # In case of assert failures, print the full error message
    maxDiff = None

    @staticmethod
    def get_sample_path(filename=""):
        samples_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "samples")
        return os.path.join(samples_dir, filename)

    @staticmethod
    def get_sample(filename=""):
        sample_path = BaseTestCase.get_sample_path(filename)
        sample = open(sample_path).read()
        return sample
