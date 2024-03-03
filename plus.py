import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# 设置matplotlib支持中文和负号显示
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

st.title('客户GMV与增长率关系分析')

# 使用列来组织输入框
col1, col2 = st.columns(2)

with col1:
    st.header('新客')
    new_customer_count = st.number_input('人数', value=100, key='new_customer_count')
    new_customer_gmv = st.number_input('人均GMV', value=100.0, key='new_customer_gmv')

with col2:
    st.header('老客')
    existing_customer_count = st.number_input('人数', value=100, key='existing_customer_count')
    existing_customer_gmv = st.number_input('人均GMV', value=100.0, key='existing_customer_gmv')

# 用户选择增长率指标
growth_rate_option = st.radio(
    '选择增长率指标',
    ('新客增长率', '老客增长率'),
    horizontal=True
)

# 生成增长率范围 (-100% to 100%)
growth_rates = np.linspace(-1, 1, 200)

# 计算每个增长率下的总GMV
gmv_totals = []
for growth_rate in growth_rates:
    if growth_rate_option == '新客增长率':
        new_gmv_total = new_customer_count * new_customer_gmv * (1 + growth_rate)
        existing_gmv_total = existing_customer_count * existing_customer_gmv
    else:  # 老客增长率
        new_gmv_total = new_customer_count * new_customer_gmv
        existing_gmv_total = existing_customer_count * existing_customer_gmv * (1 + growth_rate)
    total_gmv = new_gmv_total + existing_gmv_total
    gmv_totals.append(total_gmv)

# 绘制图形
fig, ax = plt.subplots()
ax.plot(growth_rates * 100, gmv_totals)  # 将增长率转换为百分比形式
ax.set_xlabel('growth (%)')
ax.set_ylabel('GMV SUM')
ax.set_title('GMV change')
ax.grid(True)

st.pyplot(fig)
