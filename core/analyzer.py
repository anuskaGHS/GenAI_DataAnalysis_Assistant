import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import os
import config

class DataAnalyzer:
    """Performs statistical analysis and generates charts"""
    
    def __init__(self, df, session_id):
        """Initialize with DataFrame and session ID"""
        self.df = df
        self.session_id = session_id
        self.charts = []
        
        # Create charts directory
        self.charts_dir = os.path.join(config.UPLOAD_FOLDER, 'charts', session_id)
        os.makedirs(self.charts_dir, exist_ok=True)
        
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (config.CHART_WIDTH, config.CHART_HEIGHT)
    
    def analyze(self):
        """Run complete analysis pipeline"""
        # Get column types
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = self.df.select_dtypes(include=['object']).columns.tolist()
        
        # Generate charts based on data types
        chart_count = 0
        
        # 1. Numeric distributions
        for col in numeric_cols[:3]:  # Limit to first 3
            if chart_count >= config.MAX_CHARTS:
                break
            self._create_histogram(col)
            chart_count += 1
        
        # 2. Categorical distributions
        for col in categorical_cols[:2]:  # Limit to first 2
            if chart_count >= config.MAX_CHARTS:
                break
            if self.df[col].nunique() <= 15:  # Only if reasonable number of categories
                self._create_bar_chart(col)
                chart_count += 1
        
        # 3. Correlation heatmap (if multiple numeric columns)
        if len(numeric_cols) >= 2 and chart_count < config.MAX_CHARTS:
            self._create_correlation_heatmap(numeric_cols)
            chart_count += 1
        
        # 4. Box plots for numeric columns
        if len(numeric_cols) >= 1 and chart_count < config.MAX_CHARTS:
            self._create_boxplot(numeric_cols[:3])
            chart_count += 1
        
        return self.charts
    
    def _create_histogram(self, column):
        """Create histogram for numeric column"""
        try:
            plt.figure(figsize=(config.CHART_WIDTH, config.CHART_HEIGHT))
            
            # Plot histogram
            plt.hist(self.df[column].dropna(), bins=30, color='skyblue', edgecolor='black', alpha=0.7)
            plt.xlabel(column, fontsize=12)
            plt.ylabel('Frequency', fontsize=12)
            plt.title(f'Distribution of {column}', fontsize=14, fontweight='bold')
            plt.grid(axis='y', alpha=0.3)
            
            # Add mean line
            mean_val = self.df[column].mean()
            plt.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_val:.2f}')
            plt.legend()
            
            # Save
            filename = f'hist_{column.replace(" ", "_")}.png'
            filepath = os.path.join(self.charts_dir, filename)
            plt.tight_layout()
            plt.savefig(filepath, dpi=config.CHART_DPI, bbox_inches='tight')
            plt.close()
            
            self.charts.append({
                'type': 'histogram',
                'title': f'Distribution of {column}',
                'filename': filename,
                'filepath': filepath,
                'description': f'Histogram showing the distribution of {column} values'
            })
        except Exception as e:
            print(f"Error creating histogram for {column}: {e}")
    
    def _create_bar_chart(self, column):
        """Create bar chart for categorical column"""
        try:
            plt.figure(figsize=(config.CHART_WIDTH, config.CHART_HEIGHT))
            
            # Get value counts
            value_counts = self.df[column].value_counts().head(10)  # Top 10
            
            # Plot bar chart
            value_counts.plot(kind='bar', color='coral', edgecolor='black')
            plt.xlabel(column, fontsize=12)
            plt.ylabel('Count', fontsize=12)
            plt.title(f'Top Categories in {column}', fontsize=14, fontweight='bold')
            plt.xticks(rotation=45, ha='right')
            plt.grid(axis='y', alpha=0.3)
            
            # Save
            filename = f'bar_{column.replace(" ", "_")}.png'
            filepath = os.path.join(self.charts_dir, filename)
            plt.tight_layout()
            plt.savefig(filepath, dpi=config.CHART_DPI, bbox_inches='tight')
            plt.close()
            
            self.charts.append({
                'type': 'bar_chart',
                'title': f'Top Categories in {column}',
                'filename': filename,
                'filepath': filepath,
                'description': f'Bar chart showing the frequency of categories in {column}'
            })
        except Exception as e:
            print(f"Error creating bar chart for {column}: {e}")
    
    def _create_correlation_heatmap(self, numeric_cols):
        """Create correlation heatmap for numeric columns"""
        try:
            plt.figure(figsize=(config.CHART_WIDTH, config.CHART_HEIGHT))
            
            # Calculate correlation
            corr_matrix = self.df[numeric_cols].corr()
            
            # Plot heatmap
            sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', 
                       center=0, square=True, linewidths=1, cbar_kws={"shrink": 0.8})
            plt.title('Correlation Heatmap', fontsize=14, fontweight='bold')
            
            # Save
            filename = 'correlation_heatmap.png'
            filepath = os.path.join(self.charts_dir, filename)
            plt.tight_layout()
            plt.savefig(filepath, dpi=config.CHART_DPI, bbox_inches='tight')
            plt.close()
            
            self.charts.append({
                'type': 'heatmap',
                'title': 'Correlation Heatmap',
                'filename': filename,
                'filepath': filepath,
                'description': 'Heatmap showing correlations between numeric variables'
            })
        except Exception as e:
            print(f"Error creating correlation heatmap: {e}")
    
    def _create_boxplot(self, numeric_cols):
        """Create box plot for numeric columns"""
        try:
            plt.figure(figsize=(config.CHART_WIDTH, config.CHART_HEIGHT))
            
            # Prepare data
            data_to_plot = [self.df[col].dropna() for col in numeric_cols]
            
            # Plot boxplot
            bp = plt.boxplot(data_to_plot, labels=numeric_cols, patch_artist=True)
            
            # Color the boxes
            for patch in bp['boxes']:
                patch.set_facecolor('lightblue')
            
            plt.ylabel('Values', fontsize=12)
            plt.title('Box Plot - Distribution Comparison', fontsize=14, fontweight='bold')
            plt.xticks(rotation=45, ha='right')
            plt.grid(axis='y', alpha=0.3)
            
            # Save
            filename = 'boxplot_comparison.png'
            filepath = os.path.join(self.charts_dir, filename)
            plt.tight_layout()
            plt.savefig(filepath, dpi=config.CHART_DPI, bbox_inches='tight')
            plt.close()
            
            self.charts.append({
                'type': 'boxplot',
                'title': 'Box Plot - Distribution Comparison',
                'filename': filename,
                'filepath': filepath,
                'description': 'Box plot comparing distributions of numeric variables'
            })
        except Exception as e:
            print(f"Error creating boxplot: {e}")
    
    def get_charts_info(self):
        """Return information about generated charts"""
        return self.charts