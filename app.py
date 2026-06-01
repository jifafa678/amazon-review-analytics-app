import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st


# =========================
# 1. 页面设置
# =========================
st.set_page_config(
    page_title="Amazon Review Analytics",
    page_icon="📊",
    layout="wide"
)

DB_PATH = Path("data_demo") / "amazon_reviews_demo.db"


# =========================
# 2. 数据库连接
# =========================
@st.cache_resource
def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


conn = get_connection()


def query_data(sql, params=None):
    if params is None:
        params = []
    return pd.read_sql_query(sql, conn, params=params)


# =========================
# 3. 页面标题
# =========================
st.title("Amazon 商品评论数据库检索与口碑分析平台")
st.caption(
    "基于 Amazon 商品评论数据构建的在线展示版数据库，支持商品搜索、品牌筛选、评论查看和口碑风险分析。"
)

st.markdown(
    """
    **项目说明：** 本地完整版处理 100,000 条评论；当前在线展示版抽样保留 30,000 条评论，
    用于网页部署和交互式展示。数据库包含评论、商品、用户、品牌和月度指标 5 张关系表。
    """
)


# =========================
# 4. 总览指标
# =========================
summary_sql = """
SELECT
    (SELECT COUNT(*) FROM reviews) AS review_count,
    (SELECT COUNT(*) FROM products) AS product_count,
    (SELECT COUNT(*) FROM users) AS user_count,
    (SELECT COUNT(*) FROM brands) AS brand_count,
    ROUND((SELECT AVG(rating) FROM reviews), 3) AS avg_rating,
    ROUND((SELECT AVG(is_negative) FROM reviews), 3) AS negative_review_ratio,
    ROUND((SELECT AVG(verified_purchase) FROM reviews), 3) AS verified_purchase_ratio;
"""

summary = query_data(summary_sql)

st.subheader("一、数据库概况")

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric("评论数", f"{int(summary.loc[0, 'review_count']):,}")
col2.metric("商品数", f"{int(summary.loc[0, 'product_count']):,}")
col3.metric("用户数", f"{int(summary.loc[0, 'user_count']):,}")
col4.metric("品牌数", f"{int(summary.loc[0, 'brand_count']):,}")
col5.metric("平均评分", f"{summary.loc[0, 'avg_rating']:.3f}")
col6.metric("差评率", f"{summary.loc[0, 'negative_review_ratio']:.1%}")

st.markdown("---")


# =========================
# 5. 侧边栏筛选
# =========================
st.sidebar.header("筛选条件")

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
min_sample_reviews = st.sidebar.number_input("最低样本评论数", min_value=0, value=1, step=1)
limit_n = st.sidebar.slider("最多显示商品数", 10, 200, 50, 10)


# =========================
# 6. 商品搜索
# =========================
st.subheader("二、商品搜索与口碑概览")

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

product_result = query_data(product_sql, params)

st.write(f"当前筛选条件下找到 **{len(product_result)}** 个商品。")
st.dataframe(product_result, use_container_width=True)


# =========================
# 7. 商品评论明细
# =========================
st.subheader("三、商品评论明细查看")

if len(product_result) > 0:
    product_result["display_name"] = (
        product_result["product_id"]
        + " | "
        + product_result["product_title"].astype(str).str.slice(0, 80)
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

    review_detail = query_data(review_sql, [selected_product_id])

    st.write(f"当前商品展示评论数：**{len(review_detail)}**")
    st.dataframe(review_detail, use_container_width=True)
else:
    st.info("当前筛选条件下没有商品，请调整关键词、品牌或评分条件。")


st.markdown("---")


# =========================
# 8. 品牌表现分析
# =========================
st.subheader("四、品牌表现分析")

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

left_col, right_col = st.columns(2)

with left_col:
    st.write("评论量 Top 品牌")
    st.dataframe(brand_performance, use_container_width=True)

with right_col:
    st.write("品牌评论量 Top 15")
    chart_data = brand_performance.head(15).set_index("brand")["review_count"]
    st.bar_chart(chart_data)


# =========================
# 9. 差评风险品牌
# =========================
st.subheader("五、差评风险品牌")

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

risk_left, risk_right = st.columns(2)

with risk_left:
    st.write("差评率较高的品牌")
    st.dataframe(risk_brands, use_container_width=True)

with risk_right:
    st.write("差评率 Top 15")
    risk_chart = risk_brands.head(15).set_index("brand")["negative_review_ratio"]
    st.bar_chart(risk_chart)


# =========================
# 10. 评分分布
# =========================
st.subheader("六、评分分布与评论行为")

rating_sql = """
SELECT
    rating,
    COUNT(*) AS review_count
FROM reviews
GROUP BY rating
ORDER BY rating;
"""

rating_dist = query_data(rating_sql)

rating_col, length_col = st.columns(2)

with rating_col:
    st.write("评分分布")
    st.bar_chart(rating_dist.set_index("rating")["review_count"])

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
    ROUND(AVG(helpful_vote), 3) AS avg_helpful_vote
FROM reviews
GROUP BY review_length_group
ORDER BY review_length_group;
"""

length_helpful = query_data(length_sql)

with length_col:
    st.write("评论长度与平均 helpful vote")
    st.line_chart(length_helpful.set_index("review_length_group")["avg_helpful_vote"])


# =========================
# 11. 月度趋势
# =========================
st.subheader("七、月度评论趋势")

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

if len(monthly_df) > 0:
    monthly_df["review_month"] = pd.to_datetime(monthly_df["review_month"], errors="coerce")
    monthly_df = monthly_df.dropna(subset=["review_month"])
    monthly_df = monthly_df.set_index("review_month")

    st.line_chart(monthly_df[["monthly_review_count"]])
    st.dataframe(monthly_df.reset_index(), use_container_width=True)
else:
    st.info("暂无足够的月度评论数据用于展示。")


# =========================
# 12. 页脚
# =========================
st.markdown("---")
st.markdown(
    """
    **技术栈：** Python / SQLite / SQL / Pandas / Streamlit  
    **数据库结构：** reviews、products、users、brands、monthly_metrics  
    **分析目标：** 商品搜索、品牌表现、差评风险识别、评论行为分析与口碑监测。
    """
)