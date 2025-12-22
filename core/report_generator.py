import json
from datetime import datetime

class ReportGenerator:
    """Generates structured analysis reports"""
    
    def __init__(self, session_id, filename):
        """Initialize report generator"""
        self.session_id = session_id
        self.filename = filename
        self.report = {
            'session_id': session_id,
            'filename': filename,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sections': {}
        }
    
    def add_dataset_overview(self, profile):
        """Add dataset overview section"""
        basic_info = profile.get('basic_info', {})
        quality = profile.get('data_quality', {})
        col_types = profile.get('column_types', {})
        
        self.report['sections']['dataset_overview'] = {
            'title': 'Dataset Overview',
            'content': {
                'filename': self.filename,
                'total_rows': basic_info.get('total_rows', 0),
                'total_columns': basic_info.get('total_columns', 0),
                'numeric_columns': len(col_types.get('numeric', [])),
                'categorical_columns': len(col_types.get('categorical', [])),
                'quality_score': quality.get('overall_quality_score', 0),
                'completeness': quality.get('completeness_score', 0)
            }
        }
    
    def add_data_quality(self, cleaning_summary):
        """Add data quality section"""
        self.report['sections']['data_quality'] = {
            'title': 'Data Quality & Cleaning',
            'content': {
                'original_rows': cleaning_summary.get('original_rows', 0),
                'cleaned_rows': cleaning_summary.get('cleaned_rows', 0),
                'cleaning_operations': cleaning_summary.get('report', [])
            }
        }
    
    def add_statistics(self, profile):
        """Add statistics section"""
        numeric_stats = profile.get('numeric_stats', {})
        categorical_stats = profile.get('categorical_stats', {})
        
        self.report['sections']['statistics'] = {
            'title': 'Key Statistics',
            'content': {
                'numeric_variables': numeric_stats,
                'categorical_variables': categorical_stats
            }
        }
    
    def add_visualizations(self, charts):
        """Add visualizations section"""
        self.report['sections']['visualizations'] = {
            'title': 'Visualizations',
            'content': {
                'total_charts': len(charts),
                'charts': charts
            }
        }
    
    def add_insights(self, insights_text):
        """Add AI-generated insights"""
        self.report['sections']['insights'] = {
            'title': 'AI-Generated Insights',
            'content': insights_text
        }
    
    def add_executive_summary(self, summary_text):
        """Add executive summary"""
        self.report['sections']['executive_summary'] = {
            'title': 'Executive Summary',
            'content': summary_text
        }
    
    def add_recommendations(self, recommendations_text):
        """Add recommendations"""
        self.report['sections']['recommendations'] = {
            'title': 'Recommendations',
            'content': recommendations_text
        }
    
    def generate_json(self):
        """Generate report as JSON"""
        return json.dumps(self.report, indent=2)
    
    def generate_html_summary(self):
        """Generate HTML summary for display"""
        html = f"""
        <div class="report-summary">
            <h2>Analysis Report</h2>
            <p><strong>File:</strong> {self.filename}</p>
            <p><strong>Generated:</strong> {self.report['generated_at']}</p>
            <p><strong>Sections:</strong> {len(self.report['sections'])}</p>
        </div>
        """
        return html
    
    def get_report(self):
        """Get complete report"""
        return self.report