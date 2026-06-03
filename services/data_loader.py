from pathlib import Path
import pandas as pd

def scan_csv_files(directories):
    """扫描给定目录列表中的所有 CSV 文件（递归子目录）"""
    files = []
    for d in directories:
        path = Path(d)
        if path.exists() and path.is_dir():
            for f in path.rglob("*.csv"):
                files.append((str(f), f"{f.name} (位于 {path})"))
    return files

def load_csv_from_path(file_path):
    """根据路径加载 CSV 文件，返回 DataFrame 和文件名"""
    try:
        df = pd.read_csv(file_path)
        filename = Path(file_path).name
        return df, filename, None
    except Exception as e:
        return None, None, str(e)

def load_example_data():
    """加载示例数据集（iris）"""
    import plotly.express as px
    df = px.data.iris()
    return df, "iris.csv"