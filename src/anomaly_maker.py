# -*- coding: utf-8 -*-
"""
Created on 2021/08/04
@author: Ivan Y.W.Chiu
"""

import pandas as pd
from typing import Tuple
import random


class SimpleOneThingMeanMismatchMaker:
    def __init__(self, df: pd.DataFrame, col:str, mismatch_ratio:float, item: str="") -> None:
        self.df = df
        self.col = col
        self.mismatch_ratio = mismatch_ratio
        self.item = item
        self.select_item()

    def select_item(self) -> None:
        unique_item = self.df[self.col].unique().tolist()
        unique_count = len(unique_item)

        if self.item == "":
            mismatch_item_index = random.randint(0, unique_count-1)
            self.item = unique_item[mismatch_item_index]
        else:
            if self.item not in unique_item:
                raise ValueError("Item {} is found in the column {}.".format(self.item, self.col))

    def get_cl(self, df:pd.DataFrame) -> Tuple[float, float]:
        ucl, lcl = df['UCL'].values[-1], df['LCL'].values[-1]
        return ucl, lcl

    def cal_tolerance(self, df: pd.DataFrame, chart_type: str, ucl: float, lcl: float) -> float:
        if chart_type == 'MEAN':
            return (ucl-lcl)/2
        else:
            mean = df['Value'].mean()
            return ucl - mean

    def gen(self) -> pd.DataFrame:
        ucl, lcl = self.get_cl(self.df)
        chart_type = self.df['Chart_Type'].tolist()[-1]
        tolerance = self.cal_tolerance(self.df, chart_type, ucl, lcl)

        selected_row_index = self.df[self.df[self.col] == self.item].index
        selected_value = self.df['Value'].loc[selected_row_index]
        selected_value = selected_value + tolerance*self.mismatch_ratio
        self.df['Value'].loc[selected_row_index] = selected_value
        return self.df


class OneThingProgressivlyTrendingMaker:
    def __init__(self) -> None:
        pass

class SimpleOneThingMeanKShiftMaker:
    def __init__(self) -> None:
        pass