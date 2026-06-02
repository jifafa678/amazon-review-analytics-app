import sqlite3
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# =========================================================
# 1. 页面基础设置
# =========================================================
st.set_page_config(
    page_title="Amazon 评论数据分析平台",
    page_icon="📊",
    layout="wide"
)

DB_PATH = Path("data_demo") / "amazon_reviews_demo.db"


# =========================================================
# 2. 深蓝科技风样式
# =========================================================
st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at 8% 8%, rgba(0, 209, 255, 0.22), transparent 28%),
            radial-gradient(circle at 88% 10%, rgba(58, 123, 255, 0.18), transparent 25%),
            linear-gradient(180deg, #06111F 0%, #071827 45%, #05101D 100%);
        color: #F2FBFF;
    }

    /* 全页面背景兜底，避免顶部出现白条 */
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: #06111F !important;
}

/* Streamlit 默认顶部栏改成深色透明 */
header[data-testid="stHeader"] {
    background: rgba(6, 17, 31, 0.96) !important;
    border-bottom: 1px solid rgba(0, 209, 255, 0.18) !important;
}

/* 顶部右侧 Deploy / 菜单区域颜色统一 */
header[data-testid="stHeader"] * {
    color: #DFF7FF !important;
}

/* 减少页面顶部空白 */
.block-container {
    max-width: 1420px;
    padding-top: 0.8rem;
    padding-bottom: 3rem;
}

/* 防止标题卡片边框被挤压 */
.hero-box {
    margin-top: 0.5rem;
    overflow: visible;
}

    /* 左侧筛选栏 */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #071A2B 0%, #06111F 100%) !important;
        border-right: 1px solid rgba(0, 209, 255, 0.35) !important;
    }

    section[data-testid="stSidebar"] * {
        color: #F2FBFF !important;
        font-size: 15px;
    }

    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p {
        color: #EAF8FF !important;
        font-size: 15px !important;
        font-weight: 700 !important;
    }

    /* 侧边栏输入框、下拉框统一样式 */
    section[data-testid="stSidebar"] div[data-baseweb="input"],
    section[data-testid="stSidebar"] div[data-testid="stTextInput"] div[data-baseweb="input"],
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: rgba(10, 32, 54, 0.98) !important;
        border: 1px solid rgba(0, 209, 255, 0.58) !important;
        border-radius: 10px !important;
        min-height: 46px !important;
        box-shadow:
            0 0 12px rgba(0, 209, 255, 0.12),
            inset 0 0 10px rgba(0, 209, 255, 0.06) !important;
    }

    section[data-testid="stSidebar"] input {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        background-color: transparent !important;
        caret-color: #00D1FF !important;
    }

    section[data-testid="stSidebar"] input::placeholder {
        color: rgba(220, 245, 255, 0.72) !important;
        -webkit-text-fill-color: rgba(220, 245, 255, 0.72) !important;
    }

    section[data-testid="stSidebar"] div[data-baseweb="select"] span {
        color: #FFFFFF !important;
        font-size: 16px !important;
        font-weight: 700 !important;
    }

    section[data-testid="stSidebar"] svg {
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
    }

    div[role="listbox"] {
        background-color: #0A2036 !important;
        border: 1px solid rgba(0, 209, 255, 0.45) !important;
    }

    div[role="option"] {
        color: #FFFFFF !important;
        background-color: #0A2036 !important;
        font-size: 15px !important;
    }

    div[role="option"]:hover {
        background-color: rgba(0, 209, 255, 0.22) !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stSlider"] * {
        color: #EAF8FF !important;
        font-size: 14px !important;
        font-weight: 650 !important;
    }

    /* 主页面里的选择框、标签、说明文字 */
    div[data-testid="stSelectbox"] label,
    div[data-testid="stSelectbox"] label p,
    div[data-testid="stWidgetLabel"] label,
    div[data-testid="stWidgetLabel"] label p {
        color: #EAF8FF !important;
        font-size: 16px !important;
        font-weight: 800 !important;
    }

    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background-color: rgba(10, 32, 54, 0.98) !important;
        border: 1px solid rgba(0, 209, 255, 0.58) !important;
        border-radius: 10px !important;
        min-height: 46px !important;
        box-shadow:
            0 0 12px rgba(0, 209, 255, 0.12),
            inset 0 0 10px rgba(0, 209, 255, 0.06) !important;
    }

    div[data-testid="stSelectbox"] span {
        color: #FFFFFF !important;
        font-size: 16px !important;
        font-weight: 700 !important;
    }

    /* 顶部标题卡片 */
    .hero-box {
        background:
            linear-gradient(135deg, rgba(8, 32, 56, 0.99), rgba(5, 18, 34, 0.99));
        border: 1px solid rgba(0, 209, 255, 0.58);
        border-radius: 22px;
        padding: 34px 38px;
        margin-bottom: 24px;
        box-shadow:
            0 0 28px rgba(0, 209, 255, 0.22),
            inset 0 0 32px rgba(0, 209, 255, 0.08);
    }

    .hero-title {
        font-size: 39px;
        font-weight: 900;
        color: #FFFFFF;
        margin-bottom: 12px;
        letter-spacing: -0.5px;
        text-shadow: 0 0 14px rgba(0, 209, 255, 0.55);
    }

    .hero-subtitle {
        font-size: 16px;
        line-height: 1.9;
        color: #D7F4FF;
        max-width: 1120px;
        font-weight: 500;
    }

    .tag-chip {
        display: inline-block;
        padding: 7px 14px;
        margin-right: 9px;
        margin-top: 18px;
        border-radius: 999px;
        background: rgba(0, 209, 255, 0.18);
        border: 1px solid rgba(0, 209, 255, 0.52);
        color: #FFFFFF;
        font-size: 13px;
        font-weight: 700;
    }

    /* 模块标题 */
    .section-title {
        font-size: 28px;
        font-weight: 900;
        color: #FFFFFF;
        margin-top: 14px;
        margin-bottom: 10px;
        text-shadow: 0 0 12px rgba(0, 209, 255, 0.34);
    }

    .section-desc {
        color: #C7E9F7;
        font-size: 16px;
        margin-bottom: 18px;
        line-height: 1.75;
        font-weight: 500;
    }

    /* 顶部指标卡片 */
    .metric-panel {
        background:
            linear-gradient(180deg, rgba(14, 48, 78, 1), rgba(8, 30, 52, 1));
        border: 1px solid rgba(0, 209, 255, 0.62);
        border-radius: 18px;
        padding: 24px 22px;
        box-shadow:
            0 0 22px rgba(0, 209, 255, 0.22),
            inset 0 0 18px rgba(0, 209, 255, 0.08);
    }

    .metric-label {
        color: #D2F5FF;
        font-size: 15px;
        margin-bottom: 12px;
        font-weight: 800;
    }

    .metric-value {
        color: #FFFFFF;
        font-size: 36px;
        font-weight: 950;
        letter-spacing: -0.5px;
        text-shadow: 0 0 12px rgba(0, 209, 255, 0.45);
    }

    .insight-box {
        background: rgba(0, 209, 255, 0.12);
        border-left: 5px solid #00D1FF;
        border-radius: 12px;
        padding: 15px 18px;
        margin-bottom: 18px;
        color: #E8FAFF;
        font-size: 16px;
        line-height: 1.85;
        font-weight: 560;
    }

    /* Tab 字体变大 */
    button[data-baseweb="tab"] {
        background-color: rgba(0, 209, 255, 0.08);
        border-radius: 12px 12px 0 0;
        padding: 10px 18px !important;
    }

    button[data-baseweb="tab"] p {
        color: #FFFFFF !important;
        font-size: 19px !important;
        font-weight: 850 !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: rgba(0, 209, 255, 0.20) !important;
        border-bottom: 2px solid #00D1FF !important;
    }

    /* 表格区域 */
    div[data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid rgba(0, 209, 255, 0.28);
        box-shadow: 0 0 14px rgba(0, 209, 255, 0.08);
    }

    .small-muted {
        font-size: 14px;
        color: #C4E7F6;
        line-height: 1.8;
    }

    hr {
        border-color: rgba(0, 209, 255, 0.18);
    }
    /* 主页面：选择商品查看评论的下拉框，统一改成深蓝底白字 */
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background-color: rgba(10, 32, 54, 0.98) !important;
    border: 1px solid rgba(0, 209, 255, 0.58) !important;
    border-radius: 10px !important;
    min-height: 46px !important;
    box-shadow:
        0 0 12px rgba(0, 209, 255, 0.12),
        inset 0 0 10px rgba(0, 209, 255, 0.06) !important;
}

/* 下拉框里的选中商品文字 */
div[data-testid="stSelectbox"] div[data-baseweb="select"] span,
div[data-testid="stSelectbox"] div[data-baseweb="select"] div,
div[data-testid="stSelectbox"] div[data-baseweb="select"] input {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    font-size: 16px !important;
    font-weight: 700 !important;
}

/* 下拉箭头 */
div[data-testid="stSelectbox"] svg {
    color: #FFFFFF !important;
    fill: #FFFFFF !important;
}

/* 展开后的选项列表 */
div[role="listbox"] {
    background-color: #0A2036 !important;
    border: 1px solid rgba(0, 209, 255, 0.45) !important;
}

div[role="option"],
div[role="option"] span,
div[role="option"] div {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    background-color: #0A2036 !important;
    font-size: 15px !important;
    font-weight: 650 !important;
}

div[role="option"]:hover {
    background-color: rgba(0, 209, 255, 0.22) !important;
}
    /* 强制修复：商品关键词输入框与品牌下拉框保持一致 */
section[data-testid="stSidebar"] div[data-testid="stTextInput"] {
    background-color: transparent !important;
}

section[data-testid="stSidebar"] div[data-testid="stTextInput"] > div {
    background-color: transparent !important;
}

section[data-testid="stSidebar"] div[data-testid="stTextInput"] div[data-baseweb="input"] {
    background-color: #08213A !important;
    border: 1px solid rgba(0, 209, 255, 0.58) !important;
    border-radius: 10px !important;
    min-height: 46px !important;
    box-shadow:
        0 0 12px rgba(0, 209, 255, 0.12),
        inset 0 0 10px rgba(0, 209, 255, 0.06) !important;
}

section[data-testid="stSidebar"] div[data-testid="stTextInput"] div[data-baseweb="base-input"] {
    background-color: #08213A !important;
    border-radius: 10px !important;
}

section[data-testid="stSidebar"] div[data-testid="stTextInput"] input {
    background-color: #08213A !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    caret-color: #00D1FF !important;
    border-radius: 10px !important;
}

section[data-testid="stSidebar"] div[data-testid="stTextInput"] input:focus {
    background-color: #08213A !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}

section[data-testid="stSidebar"] div[data-testid="stTextInput"] input::placeholder {
    color: rgba(220, 245, 255, 0.65) !important;
    -webkit-text-fill-color: rgba(220, 245, 255, 0.65) !important;
}
    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# 3. 数据库查询函数
# =========================================================
if not DB_PATH.exists():
    st.error(f"未找到数据库文件：{DB_PATH}")
    st.stop()


@st.cache_data(show_spinner=False)
def query_data(sql: str, params: tuple = ()) -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(sql, conn, params=list(params))


def sci_bar_chart(df, x_col, y_col, title, orientation="v", height=380):
    fig = go.Figure()

    if orientation == "h":
        fig.add_trace(
            go.Bar(
                x=df[x_col],
                y=df[y_col],
                orientation="h",
                marker=dict(
                    color="rgba(0, 209, 255, 0.75)",
                    line=dict(color="rgba(160, 240, 255, 0.95)", width=1)
                ),
                hovertemplate="%{y}<br>数值：%{x}<extra></extra>"
            )
        )
    else:
        fig.add_trace(
            go.Bar(
                x=df[x_col],
                y=df[y_col],
                marker=dict(
                    color="rgba(0, 209, 255, 0.75)",
                    line=dict(color="rgba(160, 240, 255, 0.95)", width=1)
                ),
                hovertemplate="%{x}<br>数值：%{y}<extra></extra>"
            )
        )

    fig.update_layout(
        title=dict(text=title, font=dict(size=17, color="#EAF8FF")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#DDF7FF", size=13),
        height=height,
        margin=dict(l=20, r=20, t=55, b=30),
        xaxis=dict(showgrid=True, gridcolor="rgba(0, 209, 255, 0.12)", zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False)
    )
    return fig


def sci_line_chart(df, x_col, y_col, title, height=380):
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df[x_col],
            y=df[y_col],
            mode="lines+markers",
            line=dict(color="#00D1FF", width=3),
            marker=dict(size=7, color="#8AF3FF", line=dict(color="#00D1FF", width=1)),
            hovertemplate="%{x}<br>数值：%{y}<extra></extra>"
        )
    )

    fig.update_layout(
        title=dict(text=title, font=dict(size=17, color="#EAF8FF")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#DDF7FF", size=13),
        height=height,
        margin=dict(l=20, r=20, t=55, b=30),
        xaxis=dict(showgrid=True, gridcolor="rgba(0, 209, 255, 0.12)", zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(0, 209, 255, 0.12)", zeroline=False)
    )
    return fig


# =========================================================
# 4. 顶部标题区
# =========================================================
st.markdown(
    """
    <div class="hero-box">
        <div class="hero-title">Amazon 商品评论数据智能看板</div>
        <div class="hero-subtitle">
            本项目基于 Amazon 商品评论公开数据构建电商评论分析数据库。
            本地完整版处理 100,000 条评论；当前在线展示版抽样保留 30,000 条评论，
            用于商品检索、品牌对比、评论行为分析和口碑风险监测。
            页面支持关键词搜索、品牌筛选、评分筛选、评论明细查看与差评风险识别。
        </div>
        <span class="tag-chip">Python</span>
        <span class="tag-chip">SQL</span>
        <span class="tag-chip">SQLite</span>
        <span class="tag-chip">Streamlit</span>
        <span class="tag-chip">电商数据分析</span>
        <span class="tag-chip">口碑风险监测</span>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# 5. 总览指标
# =========================================================
summary_sql = """
SELECT
    (SELECT COUNT(*) FROM reviews) AS review_count,
    (SELECT COUNT(*) FROM products) AS product_count,
    (SELECT COUNT(*) FROM users) AS user_count,
    (SELECT COUNT(*) FROM brands) AS brand_count,
    ROUND((SELECT AVG(rating) FROM reviews), 3) AS avg_rating,
    ROUND((SELECT AVG(is_negative) FROM reviews), 3) AS negative_review_ratio;
"""

summary = query_data(summary_sql)

review_count = int(summary.loc[0, "review_count"])
product_count = int(summary.loc[0, "product_count"])
user_count = int(summary.loc[0, "user_count"])
brand_count = int(summary.loc[0, "brand_count"])
avg_rating = float(summary.loc[0, "avg_rating"])
negative_ratio = float(summary.loc[0, "negative_review_ratio"])

st.markdown('<div class="section-title">一、数据库总览</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-desc">在线展示版数据库包含 reviews、products、users、brands、monthly_metrics 五张关系表。</div>',
    unsafe_allow_html=True
)

metric_cols = st.columns(6)
metrics = [
    ("评论数", f"{review_count:,}"),
    ("商品数", f"{product_count:,}"),
    ("用户数", f"{user_count:,}"),
    ("品牌数", f"{brand_count:,}"),
    ("平均评分", f"{avg_rating:.3f}"),
    ("差评率", f"{negative_ratio:.1%}")
]

for col, (label, value) in zip(metric_cols, metrics):
    with col:
        st.markdown(
            f"""
            <div class="metric-panel">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("<br>", unsafe_allow_html=True)


# =========================================================
# 6. 侧边栏筛选器
# =========================================================
st.sidebar.title("筛选条件")
st.sidebar.caption("可通过商品关键词、品牌、评分和样本评论数进行检索。")

brand_sql = """
SELECT DISTINCT brand
FROM products
WHERE brand IS NOT NULL
  AND brand != ''
ORDER BY brand;
"""

brand_df = query_data(brand_sql)
brand_options = ["全部品牌"] + brand_df["brand"].dropna().tolist()

keyword = st.sidebar.text_input("商品关键词", value="")
selected_brand = st.sidebar.selectbox("品牌", brand_options)
min_rating = st.sidebar.slider("最低商品平均评分", 0.0, 5.0, 0.0, 0.1)

min_sample_reviews = st.sidebar.selectbox(
    "最低样本评论数",
    options=[0, 1, 2, 3, 5, 10, 20, 50, 100],
    index=1
)

limit_n = st.sidebar.slider("最多显示商品数", 10, 200, 50, 10)

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div class="small-muted">
    可尝试关键词：<b>shampoo</b>、<b>hair</b>、<b>brush</b>、<b>oil</b>、<b>cream</b>。
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# 7. 页面标签
# =========================================================
tab1, tab2, tab3 = st.tabs([
    "商品检索",
    "品牌看板",
    "评论行为"
])


# =========================================================
# Tab 1：商品检索
# =========================================================
with tab1:
    st.markdown('<div class="section-title">二、商品检索与口碑概览</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-desc">根据关键词和品牌筛选商品，并查看样本评论数、平均评分、差评率和验证购买占比。</div>',
        unsafe_allow_html=True
    )

    product_sql = """
    SELECT
        p.product_id,
        p.product_title,
        p.brand,
        p.main_category,
        p.price,
        p.average_rating AS product_avg_rating,
        p.rating_number AS total_rating_number,
        COUNT(r.review_id) AS sample_review_count,
        ROUND(AVG(r.rating), 3) AS sample_avg_rating,
        ROUND(AVG(r.is_negative), 3) AS negative_review_ratio,
        ROUND(AVG(r.verified_purchase), 3) AS verified_purchase_ratio,
        ROUND(AVG(r.helpful_vote), 3) AS avg_helpful_vote
    FROM products p
    LEFT JOIN reviews r
        ON p.product_id = r.product_id
    WHERE 1 = 1
    """

    params = []

    if keyword.strip():
        product_sql += " AND p.product_title LIKE ? "
        params.append(f"%{keyword.strip()}%")

    if selected_brand != "全部品牌":
        product_sql += " AND p.brand = ? "
        params.append(selected_brand)

    product_sql += """
    GROUP BY
        p.product_id,
        p.product_title,
        p.brand,
        p.main_category,
        p.price,
        p.average_rating,
        p.rating_number
    HAVING
        product_avg_rating >= ?
        AND sample_review_count >= ?
    ORDER BY
        sample_review_count DESC,
        negative_review_ratio DESC
    LIMIT ?;
    """

    params.extend([min_rating, min_sample_reviews, limit_n])

    product_result = query_data(product_sql, tuple(params))

    st.markdown(
        f"""
        <div class="insight-box">
        当前筛选条件下共返回 <b>{len(product_result)}</b> 个商品。
        结果默认按照样本评论数和差评率排序，方便优先识别高关注度商品和潜在口碑风险商品。
        </div>
        """,
        unsafe_allow_html=True
    )

    st.dataframe(product_result, width="stretch", height=390)

    st.markdown('<div class="section-title">评论明细查看</div>', unsafe_allow_html=True)

    if len(product_result) > 0:
        product_result = product_result.copy()
        product_result["display_name"] = (
            product_result["product_id"]
            + " | "
            + product_result["product_title"].astype(str).str.slice(0, 90)
        )

        selected_product_display = st.selectbox(
            "选择一个商品查看评论",
            product_result["display_name"].tolist()
        )

        selected_product_id = selected_product_display.split(" | ")[0]

        review_sql = """
        SELECT
            review_id,
            rating,
            review_title,
            review_text,
            helpful_vote,
            verified_purchase,
            review_date,
            review_length,
            is_negative
        FROM reviews
        WHERE product_id = ?
        ORDER BY helpful_vote DESC, review_length DESC
        LIMIT 100;
        """

        review_detail = query_data(review_sql, (selected_product_id,))

        st.caption(f"当前展示商品：{selected_product_id}；最多展示 100 条评论。")
        st.dataframe(review_detail, width="stretch", height=360)
    else:
        st.info("当前筛选条件下没有商品。可以尝试更换关键词，或降低评分、评论数门槛。")


# =========================================================
# Tab 2：品牌看板
# =========================================================
with tab2:
    st.markdown('<div class="section-title">三、品牌表现与口碑风险</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-desc">对比高评论量品牌，并识别差评率较高的品牌，用于辅助商品运营和口碑监测。</div>',
        unsafe_allow_html=True
    )

    brand_performance_sql = """
    SELECT
        brand,
        product_count,
        review_count,
        ROUND(avg_review_rating, 3) AS avg_review_rating,
        ROUND(negative_review_ratio, 3) AS negative_review_ratio,
        ROUND(verified_purchase_ratio, 3) AS verified_purchase_ratio,
        ROUND(avg_helpful_vote, 3) AS avg_helpful_vote
    FROM brands
    WHERE brand IS NOT NULL
      AND brand != 'Unknown'
      AND review_count >= 10
    ORDER BY review_count DESC
    LIMIT 30;
    """

    brand_performance = query_data(brand_performance_sql)

    left_col, right_col = st.columns([1.15, 1])

    with left_col:
        st.markdown("**评论量较高的品牌**")
        st.dataframe(brand_performance, width="stretch", height=420)

    with right_col:
        chart_df = brand_performance.head(15).copy()
        chart_df = chart_df.sort_values("review_count", ascending=True)
        fig = sci_bar_chart(
            chart_df,
            x_col="review_count",
            y_col="brand",
            title="品牌评论量 Top 15",
            orientation="h",
            height=420
        )
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    risk_brand_sql = """
    SELECT
        brand,
        product_count,
        review_count,
        ROUND(avg_review_rating, 3) AS avg_review_rating,
        ROUND(negative_review_ratio, 3) AS negative_review_ratio,
        ROUND(verified_purchase_ratio, 3) AS verified_purchase_ratio
    FROM brands
    WHERE brand IS NOT NULL
      AND brand != 'Unknown'
      AND review_count >= 10
    ORDER BY negative_review_ratio DESC, review_count DESC
    LIMIT 30;
    """

    risk_brands = query_data(risk_brand_sql)

    st.markdown('<div class="section-title">差评风险品牌</div>', unsafe_allow_html=True)

    risk_left, risk_right = st.columns([1.15, 1])

    with risk_left:
        st.markdown("**差评率较高的品牌**")
        st.dataframe(risk_brands, width="stretch", height=420)

    with risk_right:
        risk_chart_df = risk_brands.head(15).copy()
        risk_chart_df = risk_chart_df.sort_values("negative_review_ratio", ascending=True)
        fig = sci_bar_chart(
            risk_chart_df,
            x_col="negative_review_ratio",
            y_col="brand",
            title="差评率 Top 15",
            orientation="h",
            height=420
        )
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


# =========================================================
# Tab 3：评论行为
# =========================================================
with tab3:
    st.markdown('<div class="section-title">四、评论行为分析</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-desc">从评分分布、验证购买、评论长度和月度趋势等角度观察用户评论行为。</div>',
        unsafe_allow_html=True
    )

    rating_sql = """
    SELECT
        rating,
        COUNT(*) AS review_count
    FROM reviews
    GROUP BY rating
    ORDER BY rating;
    """

    rating_dist = query_data(rating_sql)

    verified_sql = """
    SELECT
        verified_purchase,
        COUNT(*) AS review_count,
        ROUND(AVG(rating), 3) AS avg_rating,
        ROUND(AVG(is_negative), 3) AS negative_review_ratio,
        ROUND(AVG(helpful_vote), 3) AS avg_helpful_vote,
        ROUND(AVG(review_length), 3) AS avg_review_length
    FROM reviews
    GROUP BY verified_purchase
    ORDER BY verified_purchase DESC;
    """

    verified_df = query_data(verified_sql)
    verified_df["purchase_type"] = verified_df["verified_purchase"].map({
        1: "验证购买",
        0: "非验证购买"
    })

    c1, c2 = st.columns([1, 1])

    with c1:
        fig = sci_bar_chart(
            rating_dist,
            x_col="rating",
            y_col="review_count",
            title="评分分布",
            orientation="v",
            height=360
        )
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    with c2:
        st.markdown("**验证购买评论对比**")
        st.dataframe(verified_df, width="stretch", height=360)

    length_sql = """
    SELECT
        CASE
            WHEN review_length < 20 THEN '01_under_20'
            WHEN review_length < 50 THEN '02_20_49'
            WHEN review_length < 100 THEN '03_50_99'
            WHEN review_length < 200 THEN '04_100_199'
            ELSE '05_200_plus'
        END AS review_length_group,
        COUNT(*) AS review_count,
        ROUND(AVG(helpful_vote), 3) AS avg_helpful_vote,
        ROUND(AVG(rating), 3) AS avg_rating,
        ROUND(AVG(is_negative), 3) AS negative_review_ratio
    FROM reviews
    GROUP BY review_length_group
    ORDER BY review_length_group;
    """

    length_helpful = query_data(length_sql)

    st.markdown('<div class="section-title">评论长度与 Helpful Vote</div>', unsafe_allow_html=True)

    fig = sci_line_chart(
        length_helpful,
        x_col="review_length_group",
        y_col="avg_helpful_vote",
        title="不同评论长度组的平均 helpful vote",
        height=360
    )
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    st.dataframe(length_helpful, width="stretch", height=260)

    monthly_sql = """
    SELECT
        review_month,
        COUNT(*) AS monthly_review_count,
        ROUND(AVG(rating), 3) AS monthly_avg_rating,
        ROUND(AVG(is_negative), 3) AS monthly_negative_ratio
    FROM reviews
    GROUP BY review_month
    HAVING monthly_review_count >= 10
    ORDER BY review_month;
    """

    monthly_df = query_data(monthly_sql)

    st.markdown('<div class="section-title">月度评论趋势</div>', unsafe_allow_html=True)

    if len(monthly_df) > 0:
        monthly_df["review_month"] = pd.to_datetime(monthly_df["review_month"], errors="coerce")
        monthly_df = monthly_df.dropna(subset=["review_month"])

        fig = sci_line_chart(
            monthly_df,
            x_col="review_month",
            y_col="monthly_review_count",
            title="月度评论数量趋势",
            height=380
        )
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

        st.dataframe(monthly_df, width="stretch", height=300)
    else:
        st.info("当前数据中暂无足够的月度趋势数据。")
