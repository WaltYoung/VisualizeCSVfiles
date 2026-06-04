import pandas as pd

class CSVDataManager:
    """管理 CSV 数据的增删改查"""
    def __init__(self, df: pd.DataFrame = None, file_path: str = None):
        self.df = df.copy() if df is not None else None
        self.file_path = file_path          # 原始文件路径
        self._modified = False

    def is_loaded(self):
        return self.df is not None

    def get_dataframe(self):
        return self.df

    def update_row(self, row_index, column, value):
        """修改指定单元格"""
        if self.df is not None and row_index in self.df.index:
            self.df.at[row_index, column] = value
            self._modified = True
            self._auto_save()
            return True
        return False

    def update_dataframe(self, new_df: pd.DataFrame):
        """整体替换 DataFrame（用于批量编辑后同步）"""
        if self.df is not None:
            # 保持索引一致（假设 new_df 包含原 df 的索引）
            self.df.update(new_df)
            self._modified = True
            self._auto_save()
        else:
            self._modified = True
            self._auto_save()
            self.df = new_df

    def add_row(self, row_dict):
        """添加新行"""
        if self.df is not None:
            new_row = pd.DataFrame([row_dict])
            self.df = pd.concat([self.df, new_row], ignore_index=True)
            self._modified = True
            self._auto_save()
        else:
            self.df = pd.DataFrame([row_dict])
            self._modified = True
            self._auto_save()

    def delete_rows(self, indices_to_delete):
        """根据索引列表删除行（基于 filtered_df 的全局索引映射）"""
        if self.df is not None and indices_to_delete:
            self.df = self.df.drop(indices_to_delete).reset_index(drop=True)
            self._modified = True
            self._auto_save()


    def save(self, new_path: str = None):
        """保存到文件（如果提供 new_path 则另存为）"""
        if self.df is None:
            return False
        target = new_path if new_path else self.file_path
        if target is None:
            return False
        self.df.to_csv(target, index=False)
        self._modified = False
        if new_path:
            self.file_path = new_path
        return True

    def _auto_save(self):
        """自动保存到当前文件路径，如果没有路径则静默失败（但会打印警告）"""
        if self.file_path:
            self.save()
        else:
            print("警告：当前数据没有关联的文件路径，无法自动保存。")

    def has_file_path(self):
        return self.file_path is not None