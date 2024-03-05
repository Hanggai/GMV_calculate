import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

st.set_page_config(page_title="GMV Growth Analysis Tool", layout="wide")

# 定义常量
NEW_CUSTOMER_TYPES = ['1st Order', '2nd Order', '3-4 Orders', '4+ Orders']  
OLD_CUSTOMER_TYPES = ['Baijiu', 'Huangjiu', 'Foreign Liquor', 'Wine', 'Beer']
GROWTH_RATE_RANGE = np.linspace(-1, 1, 41)

# 初始化数据
@st.cache_data
def init_data():
    # 新客户默认数据: 每种订单类型的平均GMV和客户数
    new_customer_defaults = {
        order_type: {'avg_gmv': float(avg_gmv), 'customer_count': count}
        for order_type, avg_gmv, count in zip(NEW_CUSTOMER_TYPES, [100, 150, 200, 250], [1000, 800, 500, 300])
    }
    # 老客户默认数据: 每种酒类的GMV
    old_customer_defaults = {
        alcohol_type: {'gmv': float(gmv)} 
        for alcohol_type, gmv in zip(OLD_CUSTOMER_TYPES, [100000, 80000, 120000, 90000, 85000])
    }
    return new_customer_defaults, old_customer_defaults

new_customer_defaults, old_customer_defaults = init_data()
new_customer_data = new_customer_defaults.copy()
old_customer_data = old_customer_defaults.copy()

# 选择变量
variable_options = [f"{key}-Average GMV Growth Rate" for key in NEW_CUSTOMER_TYPES] + \
                   [f"{key}-Customer Count Growth Rate" for key in NEW_CUSTOMER_TYPES] + \
                   [f"{alcohol_type}-Price Growth Rate" for alcohol_type in OLD_CUSTOMER_TYPES] + \
                   [f"{alcohol_type}-Order Count Growth Rate" for alcohol_type in OLD_CUSTOMER_TYPES]

# 侧边栏输入界面  
with st.sidebar:
    selected_var = st.selectbox('Select Variable：', options=variable_options)
    
    st.markdown("### New Customer Data Input")
    for order_type in NEW_CUSTOMER_TYPES:
        defaults = new_customer_defaults[order_type]
        with st.expander(f"New Customer - {order_type}"):
            avg_gmv = st.number_input(f"{order_type} Average GMV", value=defaults['avg_gmv'], step=1.0)
            customer_count = st.number_input(f"{order_type} Customer Count", value=defaults['customer_count'], step=1)
            new_customer_data[order_type] = {'avg_gmv': avg_gmv, 'customer_count': customer_count}
    
    st.markdown("### Old Customer Data Input")        
    for alcohol_type in OLD_CUSTOMER_TYPES:
        defaults = old_customer_defaults[alcohol_type]
        with st.expander(f"Old Customer - {alcohol_type}"):
            gmv = st.number_input(f"{alcohol_type} GMV", value=defaults['gmv'], step=1000.0) 
            old_customer_data[alcohol_type] = {'gmv': gmv}

# 计算GMV函数
@st.cache_data
def calculate_gmv(new_customer_data, old_customer_data, selected_var=None, growth_rate=0.0):
    # 复制输入数据,以免修改原始数据
    new_data = {k: {'avg_gmv': v['avg_gmv'], 'customer_count': v['customer_count']} for k, v in new_customer_data.items()}
    old_data = {k: {'gmv': v['gmv']} for k, v in old_customer_data.items()}
    
    # 根据选择的变量和增长率修改数据
    if selected_var:
        if "-Average GMV Growth Rate" in selected_var:
            category = selected_var.split('-')[0]
            new_data[category]['avg_gmv'] *= (1 + growth_rate)
        elif "-Customer Count Growth Rate" in selected_var:      
            category = selected_var.split('-')[0]
            new_data[category]['customer_count'] = int(new_data[category]['customer_count'] * (1 + growth_rate))
        elif "-Price Growth Rate" in selected_var:
            category = selected_var.split('-')[0] 
            old_data[category]['gmv'] *= (1 + growth_rate)
        elif "-Order Count Growth Rate" in selected_var:
            category = selected_var.split('-')[0]
            old_data[category]['gmv'] *= (1 + growth_rate)
    
    # 计算新客户GMV: 每种订单类型的平均GMV乘以客户数,再求和
    new_gmv = sum(v['avg_gmv'] * v['customer_count'] for v in new_data.values()) 
    # 计算老客户GMV: 直接对每种酒类的GMV求和
    old_gmv = sum(v['gmv'] for v in old_data.values())
    # 计算总GMV
    total_gmv = new_gmv + old_gmv
    
    return total_gmv, new_gmv, old_gmv, new_data, old_data

# 计算原始GMV
orig_total_gmv, orig_new_gmv, orig_old_gmv, _, _ = calculate_gmv(new_customer_data, old_customer_data)

# 设置增长率      
growth_rate = st.slider('Set Growth Rate：', min_value=-1.0, max_value=1.0, value=0.0, step=0.01)

# 计算新的GMV和数据  
new_total_gmv, new_new_gmv, new_old_gmv, new_customer_data_updated, old_customer_data_updated = calculate_gmv(new_customer_data, old_customer_data, selected_var, growth_rate)

# 生成表格1数据: 变量增长率对GMV的影响
table1_data = []
for rate in [-1, -0.5, 0, 0.5, 1]:
    total_gmv, _, _, _, _ = calculate_gmv(new_customer_data, old_customer_data, selected_var, rate)
    growth_rate = (total_gmv - orig_total_gmv) / orig_total_gmv
    table1_data.append([f"{rate:.0%}", f"{total_gmv:,.2f}", f"{growth_rate:.2%}"])
    
table1_df = pd.DataFrame(table1_data, columns=[f"{selected_var.split('-')[1][:2]} Growth Rate", "GMV", "GMV Growth Rate"])

# 生成表格2数据: 原始和新的GMV值
table2_data = [    
    ['Total GMV', f"{orig_total_gmv:,.2f}", f"{new_total_gmv:,.2f}", f"{(new_total_gmv - orig_total_gmv) / orig_total_gmv:.2%}"],
    ['New Customer GMV', f"{orig_new_gmv:,.2f}", f"{new_new_gmv:,.2f}", f"{(new_new_gmv - orig_new_gmv) / orig_new_gmv:.2%}"],
    ['Old Customer GMV', f"{orig_old_gmv:,.2f}", f"{new_old_gmv:,.2f}", f"{(new_old_gmv - orig_old_gmv) / orig_old_gmv:.2%}"]
]

table2_df = pd.DataFrame(table2_data, columns=['GMV Type', 'Original', 'New', 'Growth Rate'])

# 绘制图表
@st.cache_resource
def plot_gmv_growth(selected_var, growth_rate):
    variable, metric = selected_var.split('-')  
    
    x = GROWTH_RATE_RANGE
    # 对每个增长率,计算对应的GMV
    y1 = [calculate_gmv(new_customer_data, old_customer_data, selected_var, rate)[0] for rate in x]
    # 计算GMV增长率
    y2 = [(gmv - orig_total_gmv) / orig_total_gmv for gmv in y1]
        
    fig, ax1 = plt.subplots(figsize=(6, 4))
    gmv_line = ax1.plot(x, y1, color='blue', linewidth=2, label='GMV')
    ax1.set_xlabel(f"{metric[:2]} Growth Rate")
    ax1.set_ylabel("GMV", color='blue')
    ax1.tick_params('y', colors='blue')
    ax1.set_title(f"Impact of {variable} {metric} Change on GMV")
    ax1.grid()
    
    ax2 = ax1.twinx()
    gmv_growth_line = ax2.plot(x, y2, color='red', linewidth=1, linestyle='--', alpha=0.7, label='GMV Growth Rate')  
    ax2.set_ylabel("GMV Growth Rate", color='red')
    ax2.tick_params('y', colors='red')
    ax2.format_ydata = lambda x: f"{x:.0%}"
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0%}"))
    
    lines = gmv_line + gmv_growth_line
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left')
    
    return fig


# 显示表格1
st.markdown("### Original and New GMV Values")
st.table(table2_df)

# 显示表格2
st.markdown("### Impact of Variable Growth Rate on GMV")
st.table(table1_df)

# 显示图表
st.pyplot(plot_gmv_growth(selected_var, growth_rate))

