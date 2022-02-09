define change_direction == 'increase' or 'decrease'

decide initial time series data region

decide initial change point
(取 'cumulative sum of (ts_int - mean) 之最大/最小處' 與 'ts_int 之總數量-1' 之小者)

在最大限制回圈內
計算change point 前後兩段數據的平均值及兩平均的平均，
來獲得 ts_int 的 cumulative sum
並以此cusum之最大/最小值重新判定change point
