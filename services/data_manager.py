import pandas as pd

class CSVDataManager:
    """管理 CSV 数据的增删改查"""
    def __init__(self, df: pd.DataFrame = None):
        self.df = df.copy() if df is not None else None

    def is_loaded(self):
        return self.df is not None

    def get_dataframe(self):
        return self.df

    def update_row(self, row_index, column, value):
        """修改指定单元格"""
        if self.df is not None and row_index in self.df.index:
            self.df.at[row_index, column] = value
            return True
        return False

    def update_dataframe(self, new_df: pd.DataFrame):
        """整体替换 DataFrame（用于批量编辑后同步）"""
        if self.df is not None:
            # 保持索引一致（假设 new_df 包含原 df 的索引）
            self.df.update(new_df)
        else:
            self.df = new_df

    def add_row(self, row_dict):
        """添加新行"""
        if self.df is not None:
            new_row = pd.DataFrame([row_dict])
            self.df = pd.concat([self.df, new_row], ignore_index=True)
        else:
            self.df = pd.DataFrame([row_dict])

    def delete_rows(self, indices_to_delete):
        """根据索引列表删除行（基于 filtered_df 的全局索引映射）"""
        if self.df is not None and indices_to_delete:
            self.df = self.df.drop(indices_to_delete).reset_index(drop=True)

    def query_data(self, column, query_type, keyword=None, low=None, high=None):
        """查询过滤，返回新的 DataFrame"""
        if self.df is None:
            return None
        if query_type == "text":
            if keyword:
                if self.df[column].dtype == "object":
                    mask = self.df[column].astype(str).str.contains(keyword, case=False, na=False)
                else:
                    mask = self.df[column].astype(str).str.contains(keyword, case=False, na=False)
                return self.df[mask]
            else:
                return self.df
        elif query_type == "numeric":
            if low is not None and high is not None:
                return self.df[(self.df[column] >= low) & (self.df[column] <= high)]
            else:
                return self.df
        return self.df