# -*- coding: utf-8 -*-
"""
Created on 2021/08/04
@author: Ivan Y.W.Chiu
"""

from src.anomaly_maker import SimpleOneThingMeanMismatchMaker, SimpleOneThingMeanKShiftMaker
import pandas as pd
import numpy as np
from typing import Tuple



class SimpleOneThingMeanMismatchDetector(SimpleOneThingMeanMismatchMaker):
    def __init__(self, df: pd.DataFrame, col: str, criteria: float=0.33, item: str="") -> None:
        super().__init__(df, col, mismatch_ratio=0, item=item)
        self.criteria = criteria

    def display(self) -> None:
        return

    def detect(self) -> Tuple[list, np.ndarray]:
        gb_df = self.df.groupby(by=[self.col])["Value"].agg({"Mean": "mean", "Count": "count"})
        gb_df["Off_Target"] = gb_df["Mean"] - 0
        gb_df["Ratio"] = gb_df["Off_Target"]/self.tolerance
        mismatch_index = gb_df[gb_df['Ratio'] >= self.criteria].index.tolist()
        mismatch_ratio = gb_df.loc[mismatch_index]['Ratio'].values
        return mismatch_index, mismatch_ratio

