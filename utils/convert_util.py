def convert_value_by_dtype(value, target_dtype):
    """根据目标数据类型尝试转换输入值"""
    if value == "" or value is None:
        return None
    if target_dtype in ['int64', 'float64']:
        try:
            return float(value) if '.' in str(value) else int(value)
        except:
            return value
    return value