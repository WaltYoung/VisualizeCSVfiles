import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from services.data_loader import scan_csv_files, load_csv_from_path, load_example_data
from services.data_manager import CSVDataManager
from view.ui_components import (
    render_query_section, render_editable_table,
    render_add_row_section, render_visualization, render_save_section
)

load_dotenv()

st.set_page_config(page_title="CSV 文件管理", layout="wide")
st.title("📁 CSV 文件增删改查与可视化")


def session_state_init():
    # ---------- 会话状态初始化 ----------
    if "manager" not in st.session_state:
        st.session_state.manager = CSVDataManager()
    if "filename" not in st.session_state:
        st.session_state.filename = ""
    if "directory_list" not in st.session_state:
        st.session_state.directory_list = [os.getenv("DEFAULT_LOAD_DIR_LIST")]  # 添加默认目录
    if "csv_files" not in st.session_state:
        st.session_state.csv_files = []


def sidebar_init():
    # ---------- 侧边栏：多目录配置及数据加载 ----------
    with st.sidebar:
        st.header("📂 从多个目录加载 CSV")

        # 显示已添加的目录
        if st.session_state.directory_list:
            st.write("当前目录列表：")
            for i, d in enumerate(st.session_state.directory_list):
                col1, col2 = st.columns([4, 1])
                col1.write(f"📁 {d}")
                if col2.button("❌", key=f"del_dir_{i}"):
                    st.session_state.directory_list.pop(i)
                    st.rerun()
        else:
            st.info("尚未添加任何目录，请下方添加")

        new_dir = st.text_input("添加目录路径（绝对路径或相对路径）")
        if st.button("➕ 添加目录"):
            from pathlib import Path

            if new_dir and new_dir.strip():
                path_obj = Path(new_dir.strip())
                if path_obj.exists() and path_obj.is_dir():
                    if str(path_obj) not in st.session_state.directory_list:
                        st.session_state.directory_list.append(str(path_obj))
                        st.success(f"已添加：{path_obj}")
                    else:
                        st.warning("目录已在列表中")
                else:
                    st.error("目录不存在，请检查路径")
                st.rerun()

        st.markdown("---")
        if st.session_state.directory_list:
            if st.button("🔍 扫描 CSV 文件"):
                st.session_state.csv_files = scan_csv_files(st.session_state.directory_list)
                if not st.session_state.csv_files:
                    st.warning("未找到任何 CSV 文件")
                else:
                    st.success(f"找到 {len(st.session_state.csv_files)} 个 CSV 文件")

            if st.session_state.csv_files:
                selected_display = st.selectbox(
                    "请选择一个 CSV 文件",
                    options=[display for _, display in st.session_state.csv_files],
                    key="csv_selector"
                )
                selected_path = None
                for path, display in st.session_state.csv_files:
                    if display == selected_display:
                        selected_path = path
                        break
                if st.button("📄 加载此文件"):
                    df, fname, error = load_csv_from_path(selected_path)
                    if error is None:
                        st.session_state.manager = CSVDataManager(df)
                        st.session_state.filename = fname
                        st.success(f"已加载 {fname}")
                        st.rerun()
                    else:
                        st.error(f"读取失败: {error}")

        st.markdown("---")
        st.header("其他数据源")
        uploaded_file = st.file_uploader("上传 CSV 文件", type=["csv"])
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.session_state.manager = CSVDataManager(df)
            st.session_state.filename = uploaded_file.name
            st.success(f"已加载 {uploaded_file.name}")

        if st.button("使用示例数据 (iris)"):
            df, fname = load_example_data()
            st.session_state.manager = CSVDataManager(df)
            st.session_state.filename = fname
            st.success("已加载示例数据集 iris")

        st.markdown("---")
        if st.session_state.manager.is_loaded():
            st.write(f"当前文件：**{st.session_state.filename}**")
            st.write(f"数据形状：{st.session_state.manager.df.shape[0]} 行 × {st.session_state.manager.df.shape[1]} 列")


def main_page_init():
    # ---------- 主区域 ----------
    if st.session_state.manager.is_loaded():
        df = st.session_state.manager.get_dataframe()

        # 查询过滤
        filtered_df = render_query_section(df)

        # 可编辑表格
        st.subheader("✏️ 数据表格（双击单元格编辑）")
        updated_df, selected_rows = render_editable_table(filtered_df, key_prefix="main")

        # 处理编辑后的数据同步到 manager
        if not updated_df.equals(filtered_df):
            # 将编辑结果合并回原 DataFrame
            for idx in updated_df.index:
                if idx in st.session_state.manager.df.index:
                    st.session_state.manager.df.loc[updated_df.index[idx]] = updated_df.loc[idx]
            st.success("表格数据已更新，请记得保存")

        # 增加行
        def add_row_callback(new_row):
            st.session_state.manager.add_row(new_row)
            st.success("新行已添加")
            st.rerun()

        render_add_row_section(df, add_row_callback)

        # 删除选中行
        if st.button("🗑️ 删除勾选的行"):
            if selected_rows is not None and len(selected_rows) > 0:
                # 获取选中行在 filtered_df 中的位置索引，然后映射到原 df 的索引
                selected_indices = [row['_selectedRowNodeInfo']['nodeRowIndex'] for row in selected_rows if
                                    '_selectedRowNodeInfo' in row]
                if selected_indices:
                    # 找到这些行在原 df 中的实际索引（因为 filtered_df 可能是 df 的子集）
                    indices_to_del = filtered_df.iloc[selected_indices].index.tolist()
                    st.session_state.manager.delete_rows(indices_to_del)
                    st.success("已删除选中行")
                    st.rerun()
            else:
                st.warning("请先在表格中勾选要删除的行")

        # 可视化
        render_visualization(st.session_state.manager.df)

        # 保存
        render_save_section(st.session_state.manager.df, st.session_state.filename)

    else:
        st.info("请从左侧添加目录并加载 CSV 文件，或使用上传/示例数据开始")


def main():
    session_state_init()
    sidebar_init()
    main_page_init()


if __name__ == "__main__":
    main()
