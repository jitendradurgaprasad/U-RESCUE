"""
sampler.py

Sampling utilities for U Rescue.
"""

import pandas as pd


class Sampler:

    @staticmethod
    def random_sample(dataframe, n):

        return dataframe.sample(n=n, random_state=42)

    @staticmethod
    def full_dataset(dataframe):

        return dataframe.copy()