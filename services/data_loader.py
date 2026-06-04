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

def save_uploaded_file(uploaded_file, target_dir="uploaded"):
    """将上传的文件保存到本地，返回保存路径"""
    Path(target_dir).mkdir(exist_ok=True)
    file_path = Path(target_dir) / uploaded_file.name
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return str(file_path)

def save_example_data(df, filename, target_dir="examples"):
    """将示例数据保存到本地，返回保存路径"""
    Path(target_dir).mkdir(exist_ok=True)
    file_path = Path(target_dir) / filename
    df.to_csv(file_path, index=False)
    return str(file_path)