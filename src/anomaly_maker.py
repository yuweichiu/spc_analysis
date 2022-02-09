# -*- coding: utf-8 -*-
"""
Created on 2021/08/04
@author: Ivan Y.W.Chiu
"""

from operator import index
import pandas as pd
import numpy as np
from typing import Tuple
import random
import math



def sampling_shift_starting_index(df: pd.DataFrame) -> int:
    max_index_of_df = len(df) - 1
    ratio_of_shifted_data = math.floor(max_index_of_df * random.randint(40, 80)/100)
    start_id = random.randint(ratio_of_shifted_data, max_index_of_df)
    end_id = max_index_of_df
    print(start_id, end_id)
    return start_id, end_id


class DataInfo:
    def __init__(self, df: pd.DataFrame) -> None:
        """A basic class for getting the basic info in spc data.

        Args:
            df (pd.DataFrame): spc data.
        """
        self.df = df.copy()
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
        """Generate a spc data that has value mean mismatch on the 'item' of 'col'.

        Args:
            df (pd.DataFrame): Raw spc data.
            col (str): The column you want to be mismatch.
            mismatch_ratio (float): Mismatch quantity will be the value + the tolerance * the ratio.
            item (str, optional): The item in the 'col' you want to be mismatch. Defaults to "", will choose it randomly.
        """
        super().__init__(df)
        self.col = col
        self.mismatch_ratio = mismatch_ratio
        self.item = item
        if self.col != 'global':
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
    def __init__(self, df: pd.DataFrame, col: str, kshift_ratio: float, item: str="") -> None:
        """Make a k-shift in the data.

        Args:
            df (pd.DataFrame): Raw SPC data.
            col (str): The column you want to have k-shift.
            kshift_ratio (float): K-shift quantity will be the value + the tolerance * the ratio.
            item (str, optional): The item in the 'col' you want to be mismatch. Defaults to "", will choose it randomly.
        """
        super().__init__(df, col, kshift_ratio, item=item)
        self.kshift_ratio = kshift_ratio

    def gen(self) -> pd.DataFrame:
        if self.col != 'global':
            df = self.df[self.df[self.col] == self.item]
        else:
            df = self.df.copy()
        self.index_start, _ = sampling_shift_starting_index(df)
        selected_row_index = df.index
        selected_value = self.df['Value'].loc[selected_row_index].values
        selected_value[self.index_start: ] = selected_value[self.index_start: ] + self.tolerance*self.kshift_ratio
        self.df['Value'].loc[selected_row_index] = selected_value
        return self.df


class OneThingProgressivlyTrendingMaker(DataInfo):
    def __init__(self, df: pd.DataFrame, col:str, start_id: int, end_id: int, final_ratio: float, item: str="", trend_type: str="x1") -> None:
        """Generate a y=ax  or y=a(x^2 ) trending according to start_id, end_id, and final_ratio.

        Args:
            df (pd.DataFrame): [description]
            col (str): [description]
            start_id (int): [description]
            end_id (int): [description]
            final_ratio (float): 
            item (str, optional): [description]. Defaults to "".
            trend_type (str, optional): [description]. Defaults to "x1".
        """
        super().__init__(df)

        self.start_id = start_id
        self.end_id = end_id
        self.final_ratio = final_ratio
        self.trend_type = trend_type


    def gen(self):
        if self.col != 'global':
            df = self.df[self.df[self.col] == self.item]
        else:
            df = self.df.copy()

        selected_row_index = df.index
        value_col = df['Value'].values
        index_col = np.arange(0, len(value_col))
        sigma_0 = value_col[0: self.start_id + 1].std()

        if self.trend_type == 'x1':
            a = (self.final_ratio * sigma_0) / (self.end_id - self.start_id)
            value_col = np.where(
                (index_col >= self.start_id) & (index_col < self.end_id), 
                value_col + a * (value_col - self.start_id),
                value_col
                )

        elif self.trend_type == 'x2':
            a = (self.final_ratio * sigma_0) / (self.end_id**2 - self.start_id**2)
            value_col = np.where(
                (index_col >= self.start_id) & (index_col < self.end_id),
                value_col + a * (value_col - self.start_id)**2,
                value_col
            )
        else:
            raise ValueError("trend_type should be 'x1' or 'x2, {} was given.".format(self.trend_type))

        self.df['Value'].loc[selected_row_index] = value_col
        return self.df
            




