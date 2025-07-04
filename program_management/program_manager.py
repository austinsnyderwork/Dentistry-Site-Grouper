import logging
import pandas as pd

from analysis import AnalysisClass
from utils.enums import ProgramColumns, WorksiteEnums, ProviderEnums
from environment import EnvironmentLoader

logging.basicConfig(level=logging.INFO)


def apply_filter_dataframe(row, rows: list, valid_worksite_ids_by_year: dict):
    year = row[ProgramColumns.YEAR.value]
    worksite_id = row[WorksiteEnums.Attributes.WORKSITE_ID.value]

    if worksite_id in valid_worksite_ids_by_year[year]:
        rows.append(row)


def dataframe_contains_columns(df: pd.DataFrame, columns):
    return all([column in df.columns for column in columns])


class ProgramManager:

    def __init__(self, worksites_path: str, year_end_path: str):
        self.worksites_df = pd.read_csv(worksites_path)
        self.worksites_df.columns = [col.lower().replace(' ', '') for col in self.worksites_df.columns]

        self.year_end_df = pd.read_csv(year_end_path)
        self.year_end_df.columns = [col.lower().replace(' ', '') for col in self.year_end_df.columns]

    def analyze(self, analysis_class: AnalysisClass):
        env_loader = EnvironmentLoader(worksites_df=self.worksites_df,
                                       year_end_df=self.year_end_df,
                                       required_cols=analysis_class.required_columns)
        env = env_loader.load_environment()

        years = list(self.year_end_df[ProgramColumns.YEAR.value].unique())

        df = analysis_class.analyze_environment(env=env,
                                                years=years)

        source_hcp_ids = set(self.year_end_df[ProviderEnums.Attributes.HCP_ID.value])
        output_hcp_ids = set(df[ProviderEnums.Attributes.HCP_ID.value])

        source_worksite_ids = set(self.year_end_df[WorksiteEnums.Attributes.WORKSITE_ID.value])
        output_worksite_ids = set(df[WorksiteEnums.Attributes.WORKSITE_ID.value])

        missing_provider_ids = {
            hcp_id for hcp_id in source_hcp_ids if hcp_id not in output_hcp_ids
        }
        if missing_provider_ids:
            logging.error(f"Missing HcpId's from output: {missing_provider_ids}")

        missing_worksite_ids = {
            worksite_id for worksite_id in source_worksite_ids if worksite_id not in output_worksite_ids
        }
        if missing_worksite_ids:
            logging.error(f"Missing WorksiteId's from output: {missing_worksite_ids}")

        return df
