python -m PyInstaller --onefile --hidden-import="sklearn.feature_extraction.text" --hidden-import="sklearn.metrics.pairwise" --hidden-import="hebrew_tokenizer.tokenizer" compare.py
