import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import plotly.express as px
import io
from utils.convert_util import convert_value_by_dtype

def render_query_section(df: pd.DataFrame):
    """渲染查询过滤区域，返回过滤后的 DataFrame"""
    st.subheader("🔍 数据查询")
    col1 = st.columns(1)[0]
    with col1:
        search_col = st.selectbox("选择列", df.columns)
        search_type = st.radio("查询方式", ["文本包含", "数值区间"], horizontal=True)

        if search_type == "文本包含":
            keyword = st.text_input("搜索关键词", "")
            if keyword:
                if df[search_col].dtype == "object":
                    mask = df[search_col].astype(str).str.contains(keyword, case=False, na=False)
                else:
                    mask = df[search_col].astype(str).str.contains(keyword, case=False, na=False)
                filtered_df = df[mask]
                st.info(f"找到 {len(filtered_df)} 条包含 '{keyword}' 的记录")
                st.dataframe(filtered_df)
            else:
                filtered_df = df
        else:
            try:
                min_val = float(df[search_col].min())
                max_val = float(df[search_col].max())
                low, high = st.slider(
                    f"数值范围 ({search_col})",
                    min_val, max_val, (min_val, max_val)
                )
                filtered_df = df[(df[search_col] >= low) & (df[search_col] <= high)]
                st.info(f"数值在 [{low:.2f}, {high:.2f}] 的记录数：{len(filtered_df)}")
            except:
                st.error("所选列不是数值类型，无法使用数值区间查询")
                filtered_df = df
    return filtered_df

def render_editable_table(df: pd.DataFrame, key_prefix=""):
    """渲染可编辑的 AgGrid 表格，返回编辑后的 DataFrame 和选中的行信息"""
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(editable=True, resizable=True, filter=True)
    gb.configure_selection(selection_mode="multiple", use_checkbox=True, header_checkbox=False)
    gb.configure_grid_options()
    grid_options = gb.build()

    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.MANUAL,
        allow_unsafe_jscode=True,
        fit_columns_on_grid_load=False,
        key=f"aggrid_{key_prefix}"
    )
    updated_df = grid_response['data']
    selected_rows = grid_response['selected_rows']
    return updated_df, selected_rows

def render_add_row_section(df: pd.DataFrame, on_add_callback):
    """渲染增加新行的展开区域，回调函数接收新行字典"""
    with st.expander("➕ 增加新行"):
        new_row = {}
        cols = st.columns(len(df.columns))
        for i, col in enumerate(df.columns):
            with cols[i]:
                new_row[col] = st.text_input(f"{col}", key=f"new_{col}_{id(df)}")
        if st.button("添加此行", key=f"add_btn_{id(df)}"):
            # 根据原列类型转换值
            for col, val in new_row.items():
                if val == "":
                    val = None
                else:
                    orig_dtype = df[col].dtype
                    val = convert_value_by_dtype(val, orig_dtype)
                new_row[col] = val
            on_add_callback(new_row)

def render_visualization(df: pd.DataFrame):
    """渲染数据可视化部分（散点图和直方图）"""
    st.subheader("📊 数据可视化")
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    if numeric_cols:
        selected_x = st.selectbox("选择 X 轴（数值列）", numeric_cols, key="viz_x")
        selected_y = st.selectbox("选择 Y 轴（数值列）", numeric_cols, key="viz_y")
        fig = px.scatter(df, x=selected_x, y=selected_y, title="散点图")
        st.plotly_chart(fig, width='stretch')

        hist_col = st.selectbox("显示直方图", numeric_cols, key="hist")
        fig_hist = px.histogram(df, x=hist_col, title=f"{hist_col} 分布")
        st.plotly_chart(fig_hist, width='stretch')
    else:
        st.info("没有数值列，无法绘制图表")

def render_save_section(df: pd.DataFrame, default_filename: str):
    """渲染保存区域，返回是否需要保存（用于下载）"""
    st.subheader("💾 保存文件")
    if st.button("保存到 CSV"):
        csv_buffer = io.BytesIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        st.download_button(
            label="点击下载 CSV",
            data=csv_buffer,
            file_name=default_filename or "data.csv",
            mime="text/csv"
        )
        st.success("数据已准备就绪，可点击下载保存")
        return True
    return False