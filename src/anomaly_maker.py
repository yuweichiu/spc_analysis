# -*- coding: utf-8 -*-
"""
Created on 2021/08/04
@author: Ivan Y.W.Chiu
"""

import pandas as pd
from typing import Tuple
import random
import math


class DataInfo:
    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df
        self.len = len(self.df)
        self.chart_type = self.get_chart_type(df)
        self.ucl, self.lcl = self.get_cl(df)
        self.tolerance = self.get_tolerance(df, self.chart_type, self.ucl, self.lcl)

    def get_chart_type(self, df:pd.DataFrame) -> str:
        chart_type = self.df['Chart_Type'].tolist()[-1]
        return chart_type

    def get_cl(self, df:pd.DataFrame) -> Tuple[float, float]:
        ucl, lcl = df['UCL'].values[-1], df['LCL'].values[-1]
        return ucl, lcl

    def get_tolerance(self, df: pd.DataFrame, chart_type: str, ucl: float, lcl: float) -> float:
        if chart_type == 'MEAN':
            return (ucl-lcl)/2
        else:
            mean = df['Value'].mean()
            return ucl - mean



class SimpleOneThingMeanMismatchMaker(DataInfo):
    def __init__(self, df: pd.DataFrame, col:str, mismatch_ratio:float, item: str="") -> None:
        super().__init__(df)
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


    def gen(self) -> pd.DataFrame:
        selected_row_index = self.df[self.df[self.col] == self.item].index
        selected_value = self.df['Value'].loc[selected_row_index]
        selected_value = selected_value + self.tolerance*self.mismatch_ratio
        self.df['Value'].loc[selected_row_index] = selected_value
        return self.df


class SimpleOneThingMeanKShiftMaker(SimpleOneThingMeanMismatchMaker):
    def __init__(self, df: pd.DataFrame, col: str, mismatch_ratio: float, item: str="") -> None:
        super().__init__(df, col, mismatch_ratio, item=item)

    def sampling_shift_starting_index(self, df: pd.DataFrame) -> int:
        max_index_of_df = len(df) - 1
        ratio_of_shifted_data = math.floor(max_index_of_df * random.randint(40, 80)/100)
        index_start = random.randint(ratio_of_shifted_data, max_index_of_df)
        return index_start

    def gen(self) -> pd.DataFrame:
        df = self.df[self.df[self.col] == self.item]
        self.index_start = self.sampling_shift_starting_index(df)
        selected_row_index = df.index
        selected_value = self.df['Value'].loc[selected_row_index].values
        selected_value[self.index_start: ] = selected_value[self.index_start: ] + self.tolerance*self.mismatch_ratio
        self.df['Value'].loc[selected_row_index] = selected_value
        return self.df


class OneThingProgressivlyTrendingMaker:
    def __init__(self) -> None:
        pass

