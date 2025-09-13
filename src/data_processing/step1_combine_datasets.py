#!/usr/bin/env python3
"""
Step 1: Combine and analyze all misogyny detection datasets
"""

import pandas as pd
import numpy as np
from datasets import load_dataset
import json
from typing import Dict, List, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatasetCombiner:
    def __init__(self):
        self.combined_data = []
        self.dataset_stats = {}
        
    def load_local_datasets(self):
        """Load all local CSV/TSV datasets"""
        logger.info("Loading local datasets...")
        
        datasets = {
            'manual_tag': 'ManualTag_Misogyny.csv',
            'dev_set': 'dev.csv',
            'gab_hate': 'GabHateCorpus_annotations.tsv',
            'labeled_data': 'labeled_data.csv',
            'final_labels': 'final_labels.csv'
        }
        
        for name, filename in datasets.items():
            try:
                if filename.endswith('.tsv'):
                    df = pd.read_csv(filename, sep='\t', encoding='latin-1')
                else:
                    df = pd.read_csv(filename, encoding='latin-1')
                
                self.dataset_stats[name] = {
                    'rows': len(df),
                    'columns': list(df.columns),
                    'sample_data': df.head(2).to_dict('records')
                }
                
                logger.info(f"✅ Loaded {name}: {len(df)} rows, {len(df.columns)} columns")
                
                # Store the dataframe for processing
                setattr(self, f'{name}_df', df)
                
            except Exception as e:
                logger.error(f"❌ Failed to load {filename}: {str(e)}")
    
    def load_huggingface_dataset(self):
        """Load the Hugging Face misogyny dataset"""
        logger.info("Loading Hugging Face dataset...")
        
        try:
            # Load the dataset
            ds = load_dataset("weibac/misogynistic-statements-classification-en")
            
            # Convert to pandas for easier processing
            train_df = pd.DataFrame(ds['train'])
            test_df = pd.DataFrame(ds['test'])
            
            self.dataset_stats['huggingface'] = {
                'train_rows': len(train_df),
                'test_rows': len(test_df),
                'columns': list(train_df.columns),
                'sample_data': train_df.head(2).to_dict('records')
            }
            
            # Store dataframes
            self.hf_train_df = train_df
            self.hf_test_df = test_df
            
            logger.info(f"✅ Loaded Hugging Face dataset: {len(train_df)} train, {len(test_df)} test rows")
            
        except Exception as e:
            logger.error(f"❌ Failed to load Hugging Face dataset: {str(e)}")
    
    def analyze_data_quality(self):
        """Analyze the quality and characteristics of each dataset"""
        logger.info("Analyzing data quality...")
        
        quality_report = {}
        
        for dataset_name, stats in self.dataset_stats.items():
            logger.info(f"\n📊 Analyzing {dataset_name}:")
            
            if dataset_name == 'manual_tag':
                df = getattr(self, 'manual_tag_df', None)
                if df is not None:
                    misogyny_count = df['is_misogyny'].sum() if 'is_misogyny' in df.columns else 0
                    total_count = len(df)
                    quality_report[dataset_name] = {
                        'total_samples': total_count,
                        'misogyny_samples': misogyny_count,
                        'non_misogyny_samples': total_count - misogyny_count,
                        'misogyny_ratio': misogyny_count / total_count if total_count > 0 else 0,
                        'avg_text_length': df['Definition'].str.len().mean() if 'Definition' in df.columns else 0
                    }
            
            elif dataset_name == 'dev_set':
                df = getattr(self, 'dev_set_df', None)
                if df is not None:
                    sexist_count = len(df[df['label_sexist'] == 'sexist'])
                    total_count = len(df)
                    quality_report[dataset_name] = {
                        'total_samples': total_count,
                        'sexist_samples': sexist_count,
                        'non_sexist_samples': total_count - sexist_count,
                        'sexist_ratio': sexist_count / total_count if total_count > 0 else 0,
                        'avg_text_length': df['text'].str.len().mean() if 'text' in df.columns else 0,
                        'categories': df['label_category'].value_counts().to_dict() if 'label_category' in df.columns else {}
                    }
            
            elif dataset_name == 'huggingface':
                train_df = getattr(self, 'hf_train_df', None)
                test_df = getattr(self, 'hf_test_df', None)
                if train_df is not None:
                    # Assuming the HF dataset has labels
                    label_col = [col for col in train_df.columns if 'label' in col.lower() or 'class' in col.lower()]
                    if label_col:
                        label_col = label_col[0]
                        misogyny_count = (train_df[label_col] == 1).sum() if label_col in train_df.columns else 0
                        total_count = len(train_df)
                        quality_report[dataset_name] = {
                            'train_samples': total_count,
                            'test_samples': len(test_df) if test_df is not None else 0,
                            'misogyny_samples': misogyny_count,
                            'non_misogyny_samples': total_count - misogyny_count,
                            'misogyny_ratio': misogyny_count / total_count if total_count > 0 else 0,
                            'avg_text_length': train_df.iloc[:, 0].str.len().mean() if len(train_df.columns) > 0 else 0
                        }
        
        return quality_report
    
    def combine_datasets(self):
        """Combine all datasets into a unified format"""
        logger.info("Combining datasets into unified format...")
        
        combined_records = []
        
        # Process manual tag dataset
        if hasattr(self, 'manual_tag_df'):
            df = self.manual_tag_df
            for _, row in df.iterrows():
                combined_records.append({
                    'text': row.get('Definition', ''),
                    'label': row.get('is_misogyny', 0),
                    'source': 'manual_tag',
                    'category': 'misogyny' if row.get('is_misogyny', 0) == 1 else 'non_misogyny'
                })
        
        # Process dev set dataset
        if hasattr(self, 'dev_set_df'):
            df = self.dev_set_df
            for _, row in df.iterrows():
                combined_records.append({
                    'text': row.get('text', ''),
                    'label': 1 if row.get('label_sexist') == 'sexist' else 0,
                    'source': 'dev_set',
                    'category': row.get('label_category', 'none'),
                    'subcategory': row.get('label_vector', 'none')
                })
        
        # Process Hugging Face dataset
        if hasattr(self, 'hf_train_df'):
            df = self.hf_train_df
            label_col = [col for col in df.columns if 'label' in col.lower() or 'class' in col.lower()]
            text_col = [col for col in df.columns if col not in label_col and df[col].dtype == 'object']
            
            if label_col and text_col:
                label_col = label_col[0]
                text_col = text_col[0]
                
                for _, row in df.iterrows():
                    combined_records.append({
                        'text': str(row.get(text_col, '')),
                        'label': int(row.get(label_col, 0)),
                        'source': 'huggingface',
                        'category': 'misogyny' if row.get(label_col, 0) == 1 else 'non_misogyny'
                    })
        
        # Process Gab Hate dataset
        if hasattr(self, 'gab_hate_df'):
            df = self.gab_hate_df
            # Gab dataset has multiple annotators, we'll use the main Hate column
            if 'Hate' in df.columns and 'Text' in df.columns:
                # Take unique texts to avoid duplicates
                unique_texts = df.drop_duplicates(subset=['Text'])
                for _, row in unique_texts.iterrows():
                    combined_records.append({
                        'text': str(row.get('Text', '')),
                        'label': int(row.get('Hate', 0)),
                        'source': 'gab_hate',
                        'category': 'hate_speech' if row.get('Hate', 0) == 1 else 'non_hate'
                    })
        
        # Process Labeled Data dataset
        if hasattr(self, 'labeled_data_df'):
            df = self.labeled_data_df
            if 'tweet' in df.columns and 'class' in df.columns:
                for _, row in df.iterrows():
                    # Map class 0=hate_speech, 1=offensive, 2=neither
                    label = 1 if row.get('class', 2) in [0, 1] else 0  # Consider hate and offensive as misogyny
                    combined_records.append({
                        'text': str(row.get('tweet', '')),
                        'label': label,
                        'source': 'labeled_data',
                        'category': 'hate_speech' if row.get('class', 2) == 0 else 'offensive' if row.get('class', 2) == 1 else 'neither'
                    })
        
        # Process Final Labels dataset
        if hasattr(self, 'final_labels_df'):
            df = self.final_labels_df
            if 'body' in df.columns and 'level_1' in df.columns:
                for _, row in df.iterrows():
                    # Map level_1 to misogyny label
                    is_misogyny = 1 if row.get('level_1', '') == 'Misogynistic' else 0
                    combined_records.append({
                        'text': str(row.get('body', '')),
                        'label': is_misogyny,
                        'source': 'final_labels',
                        'category': 'misogyny' if is_misogyny == 1 else 'non_misogyny',
                        'subcategory': row.get('level_2', 'none')
                    })
        
        # Create combined dataframe
        self.combined_df = pd.DataFrame(combined_records)
        
        logger.info(f"✅ Combined {len(combined_records)} total samples")
        return self.combined_df
    
    def generate_summary_report(self):
        """Generate a comprehensive summary report"""
        logger.info("Generating summary report...")
        
        # Analyze combined data
        total_samples = len(self.combined_df)
        misogyny_samples = len(self.combined_df[self.combined_df['label'] == 1])
        non_misogyny_samples = len(self.combined_df[self.combined_df['label'] == 0])
        
        # Text length analysis
        text_lengths = self.combined_df['text'].str.len()
        
        summary = {
            'total_samples': total_samples,
            'misogyny_samples': misogyny_samples,
            'non_misogyny_samples': non_misogyny_samples,
            'misogyny_ratio': misogyny_samples / total_samples if total_samples > 0 else 0,
            'avg_text_length': text_lengths.mean(),
            'min_text_length': text_lengths.min(),
            'max_text_length': text_lengths.max(),
            'sources': self.combined_df['source'].value_counts().to_dict(),
            'categories': self.combined_df['category'].value_counts().to_dict() if 'category' in self.combined_df.columns else {},
            'dataset_stats': self.dataset_stats
        }
        
        # Save summary
        with open('dataset_summary.json', 'w') as f:
            # Convert numpy types to native Python types for JSON serialization
            def convert_numpy(obj):
                if isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                return obj
            
            # Convert the summary dict
            summary_serializable = {}
            for key, value in summary.items():
                if isinstance(value, dict):
                    summary_serializable[key] = {k: convert_numpy(v) for k, v in value.items()}
                else:
                    summary_serializable[key] = convert_numpy(value)
            
            json.dump(summary_serializable, f, indent=2)
        
        logger.info("📊 Summary Report:")
        logger.info(f"   Total samples: {total_samples}")
        logger.info(f"   Misogyny samples: {misogyny_samples}")
        logger.info(f"   Non-misogyny samples: {non_misogyny_samples}")
        logger.info(f"   Misogyny ratio: {summary['misogyny_ratio']:.2%}")
        logger.info(f"   Average text length: {summary['avg_text_length']:.1f} characters")
        logger.info(f"   Sources: {summary['sources']}")
        
        return summary
    
    def save_combined_data(self, filename='combined_misogyny_data.csv'):
        """Save the combined dataset"""
        if hasattr(self, 'combined_df'):
            self.combined_df.to_csv(filename, index=False)
            logger.info(f"✅ Combined data saved to {filename}")
            return filename
        else:
            logger.error("❌ No combined data to save")
            return None

def main():
    """Main function to combine all datasets"""
    logger.info("🚀 Starting dataset combination process...")
    
    combiner = DatasetCombiner()
    
    # Step 1: Load all datasets
    combiner.load_local_datasets()
    combiner.load_huggingface_dataset()
    
    # Step 2: Analyze data quality
    quality_report = combiner.analyze_data_quality()
    
    # Step 3: Combine datasets
    combined_df = combiner.combine_datasets()
    
    # Step 4: Generate summary
    summary = combiner.generate_summary_report()
    
    # Step 5: Save combined data
    filename = combiner.save_combined_data()
    
    # Assess if data is enough for RAG
    total_samples = summary['total_samples']
    misogyny_ratio = summary['misogyny_ratio']
    
    logger.info("\n🎯 RAG Suitability Assessment:")
    if total_samples >= 1000:
        logger.info("✅ Sufficient data volume for RAG (>1000 samples)")
    else:
        logger.warning("⚠️ Limited data volume for RAG (<1000 samples)")
    
    if 0.1 <= misogyny_ratio <= 0.9:
        logger.info("✅ Good class balance for training")
    else:
        logger.warning("⚠️ Imbalanced classes - may need data augmentation")
    
    if summary['avg_text_length'] >= 20:
        logger.info("✅ Adequate text length for meaningful embeddings")
    else:
        logger.warning("⚠️ Short texts may limit embedding quality")
    
    logger.info(f"\n📈 Final Assessment: {'READY FOR RAG' if total_samples >= 1000 else 'NEEDS MORE DATA'}")
    
    return summary, combined_df

if __name__ == "__main__":
    main() 