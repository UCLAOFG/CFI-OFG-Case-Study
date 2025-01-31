import pandas as pd
import pathlib

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()

df = pd.read_excel(
    DATA_PATH.joinpath("Legacy_modeled_Qualtrics_Data.xlsx"), sheet_name="Sheet1"
)
# df2=pd.read_excel(DATA_PATH.joinpath('2024.02.28_Updated Transp. Index 2023 FC.xlsx'),sheet_name='Full Dataset_Board',nrows=500)
df["GICS.Sector"] = df["GICS.Sector"].astype(object)

dfnz2 = pd.read_excel(
    DATA_PATH.joinpath(
        "2024.04.04-NZ for Descriptive Testing_not full QC w sectors.xlsx"
    ),
    sheet_name="Dissertation Net Zero & Governa",
    nrows=496,
)
