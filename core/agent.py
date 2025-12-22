import json
from datetime import datetime

import pandas as pd

from core.storage import Storage
from core.llm_client import LLMClient
from core.report_generator import ReportGenerator


class Agent:
    """
    Autonomous Data Analyst Agent
    Controls the full analysis workflow
    """

    def __init__(self, session_id):
        self.session_id = session_id
        self.storage = Storage()
        self.llm = LLMClient()

        session_info = self.storage.get_session(session_id)
        self.filename = session_info["filename"]
        self.filepath = session_info["filepath"]

    def run_analysis(self):
        """
        Main execution pipeline
        """
        try:
            # -------------------------------------------------
            # STEP 1: Load REAL dataset
            # -------------------------------------------------
            df = self.storage.load_dataframe(self.filepath)
            if df is None or df.empty:
                raise ValueError("Dataset could not be loaded or is empty")

            # -------------------------------------------------
            # STEP 2: REAL dataset profiling (NO MOCK DATA)
            # -------------------------------------------------
            numeric_cols = df.select_dtypes(include="number").columns.tolist()
            categorical_cols = df.select_dtypes(exclude="number").columns.tolist()

            total_rows, total_columns = df.shape
            total_cells = total_rows * total_columns
            missing_cells = int(df.isnull().sum().sum())

            completeness_score = round(
                (1 - (missing_cells / total_cells)) * 100, 2
            ) if total_cells > 0 else 0

            profile = {
                "basic_info": {
                    "total_rows": total_rows,
                    "total_columns": total_columns
                },
                "column_types": {
                    "numeric": numeric_cols,
                    "categorical": categorical_cols
                },
                "data_quality": {
                    "missing_values_per_column": df.isnull().sum().to_dict(),
                    "completeness_score": completeness_score
                }
            }

            # -------------------------------------------------
            # STEP 3: Charts (placeholder for now)
            # -------------------------------------------------
            charts = []  # Real charts can be added later

            # -------------------------------------------------
            # STEP 4: AI Insights (FACT-GROUNDED)
            # -------------------------------------------------
            context = f"Dataset name: {self.filename}"
            data_summary = json.dumps(profile, indent=2)

            insights = self.llm.generate_insights(
                context=context,
                data_summary=data_summary
            )

            # -------------------------------------------------
            # STEP 5: Build structured report
            # -------------------------------------------------
            report_generator = ReportGenerator(
                session_id=self.session_id,
                filename=self.filename
            )

            report_generator.add_dataset_overview(profile)
            report_generator.add_statistics(profile)
            report_generator.add_visualizations(charts)
            report_generator.add_insights(insights)
            report_generator.add_executive_summary(insights)

            report = report_generator.get_report()

            # -------------------------------------------------
            # STEP 6: Persist results
            # -------------------------------------------------
            self.storage.save_analysis_result(
                self.session_id, "profile", json.dumps(profile)
            )
            self.storage.save_analysis_result(
                self.session_id, "charts", json.dumps(charts)
            )
            self.storage.save_analysis_result(
                self.session_id, "insights", insights
            )
            self.storage.save_analysis_result(
                self.session_id, "report", json.dumps(report)
            )

            # -------------------------------------------------
            # STEP 7: Mark session completed
            # -------------------------------------------------
            self.storage.update_session_status(self.session_id, "completed")

            return True

        except Exception as e:
            print("Agent error:", e)
            return False
