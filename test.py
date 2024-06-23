import os
import fsspec

import pandas as pd
import xarray as xr

from datetime import datetime

filepath = 'https://power-analysis-ready-datastore.s3.us-west-2.amazonaws.com/power_901_annual_radiation_utc.zarr'
filepath_mapped = fsspec.get_mapper(filepath)
ds = xr.open_zarr(filepath_mapped, consolidated=True)

ds_time_series = ds.ALLSKY_SFC_LW_DWN.sel(time=pd.date_range(datetime(2019, 12, 31), datetime(2020, 12, 31), freq='1Y')).load()
output = r'' # if none the location of the script is where the files will be outputted.
ds_time_series = ds_time_series.to_dataframe()
ds_time_series.to_csv(os.path.join(output, "region.csv"))
