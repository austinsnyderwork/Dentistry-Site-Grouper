import pandas as pd

from utils.enums import ProgramColumns


def _get_years_from_dataframe(df: pd.DataFrame):
    if ProgramColumns.YEAR.value not in df.columns:
        raise ValueError(f"Must include the column '{ProgramColumns.YEAR.value} in the input dataframe.")

    years = df[ProgramColumns.YEAR.value].unique().tolist()
    years = sorted(years)
    return years


def _split_by_year(df: pd.DataFrame):
    df_years = _get_years_from_dataframe(df=df)

    dfs = {year: df.query(f"{ProgramColumns.YEAR.value} == {year}") for year in df_years}

    return dfs


class YearEndDataFrames:

    def __init__(self, year_end_df):
        self.year_end_dfs = _split_by_year(year_end_df)

    @property
    def years(self):
        return list(self.year_end_dfs.keys())

    def get_dataframe(self, year):
        if year not in self.year_end_dfs:
            raise ValueError(f"Requested dataframe year '{year}' not in year-end years {list(self.year_end_dfs.keys())}.")

        return self.year_end_dfs[year]


