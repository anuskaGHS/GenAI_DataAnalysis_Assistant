import pandas as pd
import numpy as np

class DataCleaner:
    """Handles data cleaning operations"""
    
    def __init__(self, df):
        """Initialize with a DataFrame"""
        self.df = df.copy()
        self.original_df = df.copy()
        self.cleaning_report = []
    
    def clean(self):
        """Execute full cleaning pipeline"""
        # Step 1: Handle duplicates
        self._remove_duplicates()
        
        # Step 2: Fix data types
        self._fix_data_types()
        
        # Step 3: Handle missing values
        self._handle_missing_values()
        
        # Step 4: Remove completely empty rows/columns
        self._remove_empty()
        
        # Step 5: Detect outliers (just report, don't remove)
        self._detect_outliers()
        
        return self.df, self.cleaning_report
    
    def _remove_duplicates(self):
        """Remove duplicate rows"""
        initial_count = len(self.df)
        self.df = self.df.drop_duplicates()
        duplicates_removed = initial_count - len(self.df)
        
        if duplicates_removed > 0:
            self.cleaning_report.append(
                f"✓ Removed {duplicates_removed} duplicate rows"
            )
        else:
            self.cleaning_report.append("✓ No duplicate rows found")
    
    def _fix_data_types(self):
        """Attempt to fix data types"""
        type_changes = []
        
        for col in self.df.columns:
            # Try to convert to numeric if possible
            if self.df[col].dtype == 'object':
                try:
                    # Try converting to numeric
                    numeric_col = pd.to_numeric(self.df[col], errors='coerce')
                    
                    # If more than 70% converts successfully, use it
                    non_null_count = numeric_col.notna().sum()
                    total_count = len(self.df)
                    
                    if non_null_count / total_count > 0.7:
                        self.df[col] = numeric_col
                        type_changes.append(f"{col}: text → numeric")
                except:
                    pass
        
        if type_changes:
            self.cleaning_report.append(
                f"✓ Fixed data types: {', '.join(type_changes)}"
            )
        else:
            self.cleaning_report.append("✓ Data types are appropriate")
    
    def _handle_missing_values(self):
        """Handle missing values intelligently"""
        missing_info = []
        
        for col in self.df.columns:
            missing_count = self.df[col].isna().sum()
            
            if missing_count > 0:
                missing_pct = (missing_count / len(self.df)) * 100
                
                # If more than 50% missing, just note it
                if missing_pct > 50:
                    missing_info.append(
                        f"{col}: {missing_count} missing ({missing_pct:.1f}%) - kept as-is"
                    )
                else:
                    # Fill based on data type
                    if self.df[col].dtype in ['int64', 'float64']:
                        # Numeric: fill with median
                        median_val = self.df[col].median()
                        self.df[col] = self.df[col].fillna(median_val)
                        missing_info.append(
                            f"{col}: filled {missing_count} with median ({median_val:.2f})"
                        )
                    else:
                        # Categorical: fill with mode or 'Unknown'
                        if self.df[col].mode().empty:
                            self.df[col] = self.df[col].fillna('Unknown')
                            missing_info.append(
                                f"{col}: filled {missing_count} with 'Unknown'"
                            )
                        else:
                            mode_val = self.df[col].mode()[0]
                            self.df[col] = self.df[col].fillna(mode_val)
                            missing_info.append(
                                f"{col}: filled {missing_count} with mode ('{mode_val}')"
                            )
        
        if missing_info:
            self.cleaning_report.append(
                f"✓ Handled missing values:\n  " + "\n  ".join(missing_info)
            )
        else:
            self.cleaning_report.append("✓ No missing values found")
    
    def _remove_empty(self):
        """Remove completely empty rows and columns"""
        # Remove empty rows
        initial_rows = len(self.df)
        self.df = self.df.dropna(how='all')
        empty_rows = initial_rows - len(self.df)
        
        # Remove empty columns
        initial_cols = len(self.df.columns)
        self.df = self.df.dropna(axis=1, how='all')
        empty_cols = initial_cols - len(self.df.columns)
        
        if empty_rows > 0 or empty_cols > 0:
            self.cleaning_report.append(
                f"✓ Removed {empty_rows} empty rows and {empty_cols} empty columns"
            )
    
    def _detect_outliers(self):
        """Detect outliers using IQR method (report only)"""
        outlier_info = []
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            # Define outlier bounds
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # Count outliers
            outliers = ((self.df[col] < lower_bound) | (self.df[col] > upper_bound)).sum()
            
            if outliers > 0:
                outlier_pct = (outliers / len(self.df)) * 100
                outlier_info.append(
                    f"{col}: {outliers} potential outliers ({outlier_pct:.1f}%)"
                )
        
        if outlier_info:
            self.cleaning_report.append(
                f"⚠ Outliers detected (not removed):\n  " + "\n  ".join(outlier_info)
            )
        else:
            self.cleaning_report.append("✓ No significant outliers detected")
    
    def get_cleaning_summary(self):
        """Get a summary of cleaning operations"""
        summary = {
            'original_rows': len(self.original_df),
            'original_cols': len(self.original_df.columns),
            'cleaned_rows': len(self.df),
            'cleaned_cols': len(self.df.columns),
            'report': self.cleaning_report
        }
        return summary