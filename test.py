import plotly.graph_objects as go

x = [1, 2, 3, 4, 5]
y = [1, 2, 3, 4, 5]
size = [20, 40, 60, 80, 100]  # 点的大小
hover_text = ['A', 'B', 'C', 'D', 'E']  # 悬停文本

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=x,
    y=y,
    mode='markers',
    marker=dict(
        size=size,
        sizemode='diameter',  # 或者'size'
    ),
    hovertext=hover_text,  # 将悬停文本添加到数据中
    hoverinfo='text',  # 设置hoverinfo为'text'以显示hovertext
))

fig.show()
