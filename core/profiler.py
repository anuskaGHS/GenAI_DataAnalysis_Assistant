import pandas as pd
import numpy as np

class DataProfiler:
    """Profiles and understands dataset structure"""
    
    def __init__(self, df):
        """Initialize with a DataFrame"""
        self.df = df
        self.profile = {}
    
    def generate_profile(self):
        """Generate complete dataset profile"""
        # Basic information
        self.profile['basic_info'] = self._get_basic_info()
        
        # Column types
        self.profile['column_types'] = self._classify_columns()
        
        # Statistics for numeric columns
        self.profile['numeric_stats'] = self._get_numeric_stats()
        
        # Statistics for categorical columns
        self.profile['categorical_stats'] = self._get_categorical_stats()
        
        # Data quality metrics
        self.profile['data_quality'] = self._assess_data_quality()
        
        return self.profile
    
    def _get_basic_info(self):
        """Get basic dataset information"""
        return {
            'total_rows': len(self.df),
            'total_columns': len(self.df.columns),
            'total_cells': len(self.df) * len(self.df.columns),
            'memory_usage': self.df.memory_usage(deep=True).sum(),
            'column_names': list(self.df.columns)
        }
    
    def _classify_columns(self):
        """Classify columns by type"""
        numeric_cols = []
        categorical_cols = []
        datetime_cols = []
        
        for col in self.df.columns:
            # Check if numeric
            if self.df[col].dtype in ['int64', 'float64']:
                # Further check if it's actually categorical (few unique values)
                unique_count = self.df[col].nunique()
                if unique_count < 10 and unique_count < len(self.df) * 0.05:
                    categorical_cols.append(col)
                else:
                    numeric_cols.append(col)
            
            # Check if datetime
            elif self.df[col].dtype == 'datetime64[ns]':
                datetime_cols.append(col)
            
            # Otherwise, it's categorical
            else:
                categorical_cols.append(col)
        
        return {
            'numeric': numeric_cols,
            'categorical': categorical_cols,
            'datetime': datetime_cols
        }
    
    def _get_numeric_stats(self):
        """Get statistics for numeric columns"""
        numeric_cols = self.profile.get('column_types', {}).get('numeric', [])
        
        if not numeric_cols:
            return {}
        
        stats = {}
        for col in numeric_cols:
            stats[col] = {
                'count': int(self.df[col].count()),
                'mean': float(self.df[col].mean()),
                'median': float(self.df[col].median()),
                'std': float(self.df[col].std()),
                'min': float(self.df[col].min()),
                'max': float(self.df[col].max()),
                'q25': float(self.df[col].quantile(0.25)),
                'q75': float(self.df[col].quantile(0.75)),
                'missing': int(self.df[col].isna().sum()),
                'missing_pct': float((self.df[col].isna().sum() / len(self.df)) * 100)
            }
        
        return stats
    
    def _get_categorical_stats(self):
        """Get statistics for categorical columns"""
        categorical_cols = self.profile.get('column_types', {}).get('categorical', [])
        
        if not categorical_cols:
            return {}
        
        stats = {}
        for col in categorical_cols:
            unique_values = self.df[col].nunique()
            value_counts = self.df[col].value_counts()
            
            # Get top 5 most common values
            top_values = []
            for val, count in value_counts.head(5).items():
                top_values.append({
                    'value': str(val),
                    'count': int(count),
                    'percentage': float((count / len(self.df)) * 100)
                })
            
            stats[col] = {
                'unique_count': int(unique_values),
                'missing': int(self.df[col].isna().sum()),
                'missing_pct': float((self.df[col].isna().sum() / len(self.df)) * 100),
                'most_common': top_values,
                'mode': str(self.df[col].mode()[0]) if not self.df[col].mode().empty else 'N/A'
            }
        
        return stats
    
    def _assess_data_quality(self):
        """Assess overall data quality"""
        total_cells = len(self.df) * len(self.df.columns)
        missing_cells = self.df.isna().sum().sum()
        missing_pct = (missing_cells / total_cells) * 100
        
        # Calculate completeness score (0-100)
        completeness_score = 100 - missing_pct
        
        # Check for duplicate rows
        duplicate_rows = self.df.duplicated().sum()
        duplicate_pct = (duplicate_rows / len(self.df)) * 100
        
        # Overall quality score (simple heuristic)
        quality_score = completeness_score * 0.7 + (100 - duplicate_pct) * 0.3
        
        return {
            'completeness_score': float(completeness_score),
            'total_missing_cells': int(missing_cells),
            'missing_percentage': float(missing_pct),
            'duplicate_rows': int(duplicate_rows),
            'duplicate_percentage': float(duplicate_pct),
            'overall_quality_score': float(quality_score)
        }
    
    def get_summary_text(self):
        """Get human-readable summary"""
        basic = self.profile.get('basic_info', {})
        quality = self.profile.get('data_quality', {})
        col_types = self.profile.get('column_types', {})
        
        summary = f"""
Dataset Profile Summary:
- Total Rows: {basic.get('total_rows', 0):,}
- Total Columns: {basic.get('total_columns', 0)}
- Numeric Columns: {len(col_types.get('numeric', []))}
- Categorical Columns: {len(col_types.get('categorical', []))}
- Data Quality Score: {quality.get('overall_quality_score', 0):.1f}/100
- Completeness: {quality.get('completeness_score', 0):.1f}%
"""
        return summary.strip()