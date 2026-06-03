import sqlite3
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Amazon 商品口碑洞察与风险识别平台", page_icon="📊", layout="wide")
DB_PATH = Path("data_demo") / "amazon_reviews_demo.db"

FIELD_NAME_MAP = {
    "product_id": "商品ID", "product_title": "商品名称", "brand": "品牌", "main_category": "商品类目",
    "price": "价格", "product_avg_rating": "商品平均评分", "total_rating_number": "累计评分数",
    "sample_review_count": "样本评论数", "sample_avg_rating": "样本平均评分", "bad_review_rate": "差评率",
    "verified_purchase_rate": "验证购买占比", "review_id": "评论ID", "rating": "评分",
    "review_title": "评论标题", "review_text": "评论内容", "helpful_vote": "有用票数",
    "verified_purchase": "是否验证购买", "review_date": "评论日期", "risk_score": "口碑风险评分",
    "risk_level": "口碑风险等级", "product_count": "商品数", "review_count": "评论量",
    "avg_review_rating": "平均评分", "negative_review_ratio": "差评率", "verified_purchase_ratio": "验证购买占比",
    "avg_helpful_vote": "平均有用票数"
}

st.markdown("""
<style>
.stApp{background:radial-gradient(circle at 8% 8%,rgba(0,209,255,.16),transparent 28%),radial-gradient(circle at 88% 10%,rgba(58,123,255,.14),transparent 25%),linear-gradient(180deg,#06111F 0%,#071827 45%,#05101D 100%);color:#F2FBFF}
html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"]{background:#06111F!important}header[data-testid="stHeader"]{background:rgba(6,17,31,.96)!important;border-bottom:1px solid rgba(0,209,255,.18)!important}.block-container{max-width:1420px;padding-top:.8rem;padding-bottom:3rem}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#071A2B 0%,#06111F 100%)!important;border-right:1px solid rgba(0,209,255,.35)!important}section[data-testid="stSidebar"] *{color:#F2FBFF!important}section[data-testid="stSidebar"] label,section[data-testid="stSidebar"] p{color:#EAF8FF!important;font-size:15px!important;font-weight:700!important}
section[data-testid="stSidebar"] div[data-baseweb="input"],section[data-testid="stSidebar"] div[data-baseweb="select"]>div,div[data-testid="stSelectbox"] div[data-baseweb="select"]>div{background-color:rgba(10,32,54,.98)!important;border:1px solid rgba(0,209,255,.58)!important;border-radius:10px!important;min-height:46px!important;box-shadow:0 0 12px rgba(0,209,255,.12),inset 0 0 10px rgba(0,209,255,.06)!important}
section[data-testid="stSidebar"] input,div[data-testid="stSelectbox"] span,div[data-testid="stSelectbox"] div,div[data-testid="stSelectbox"] input{color:#fff!important;-webkit-text-fill-color:#fff!important;font-size:16px!important;font-weight:700!important}div[role="listbox"]{background-color:#0A2036!important;border:1px solid rgba(0,209,255,.45)!important}div[role="option"],div[role="option"] span,div[role="option"] div{color:#fff!important;background-color:#0A2036!important;font-size:15px!important;font-weight:650!important}div[role="option"]:hover{background-color:rgba(0,209,255,.22)!important}
button[data-testid="stSidebarCollapseButton"] svg,button[data-testid="stSidebarCollapsedControl"] svg,[data-testid="stSidebarCollapseButton"] svg,[data-testid="stSidebarCollapsedControl"] svg,button[aria-label="Open sidebar"] svg,button[aria-label="Close sidebar"] svg,button[title="Open sidebar"] svg,button[title="Close sidebar"] svg,div[data-testid="stExpander"] summary svg,details summary svg{color:#fff!important;fill:#fff!important;stroke:#fff!important;filter:drop-shadow(0 0 5px rgba(0,209,255,.9))!important;opacity:1!important}
button[data-testid="stSidebarCollapseButton"] svg path,button[data-testid="stSidebarCollapsedControl"] svg path,[data-testid="stSidebarCollapseButton"] svg path,[data-testid="stSidebarCollapsedControl"] svg path,button[aria-label="Open sidebar"] svg path,button[aria-label="Close sidebar"] svg path,button[title="Open sidebar"] svg path,button[title="Close sidebar"] svg path,div[data-testid="stExpander"] summary svg path,details summary svg path{fill:#fff!important;stroke:#fff!important}
button[data-testid="stSidebarCollapseButton"],button[data-testid="stSidebarCollapsedControl"],button[aria-label="Open sidebar"],button[aria-label="Close sidebar"],button[title="Open sidebar"],button[title="Close sidebar"]{background:rgba(0,209,255,.16)!important;border:1px solid rgba(0,209,255,.45)!important;border-radius:8px!important}
section[data-testid="stSidebar"] div[data-testid="stTextInput"],section[data-testid="stSidebar"] div[data-testid="stTextInput"]>div{background:transparent!important}
section[data-testid="stSidebar"] div[data-testid="stTextInput"] div[data-baseweb="input"],section[data-testid="stSidebar"] div[data-testid="stTextInput"] div[data-baseweb="base-input"]{background-color:rgba(10,32,54,.98)!important;border-radius:10px!important}
section[data-testid="stSidebar"] div[data-testid="stTextInput"] div[data-baseweb="input"]{border:1px solid rgba(0,209,255,.58)!important;min-height:46px!important;box-shadow:0 0 12px rgba(0,209,255,.12),inset 0 0 10px rgba(0,209,255,.06)!important}
section[data-testid="stSidebar"] div[data-testid="stTextInput"] input{background-color:rgba(10,32,54,.98)!important;color:#fff!important;-webkit-text-fill-color:#fff!important;caret-color:#00D1FF!important;border-radius:10px!important}
section[data-testid="stSidebar"] div[data-testid="stTextInput"] input:focus{background-color:rgba(10,32,54,.98)!important;color:#fff!important;-webkit-text-fill-color:#fff!important}
section[data-testid="stSidebar"] div[data-testid="stTextInput"] input::placeholder{color:rgba(220,245,255,.72)!important;-webkit-text-fill-color:rgba(220,245,255,.72)!important}
.hero-box{background:linear-gradient(135deg,rgba(8,32,56,.99),rgba(5,18,34,.99));border:1px solid rgba(0,209,255,.58);border-radius:18px;padding:34px 38px;margin:.5rem 0 24px;box-shadow:0 0 28px rgba(0,209,255,.18),inset 0 0 32px rgba(0,209,255,.08)}.hero-title{font-size:39px;font-weight:900;color:#fff;margin-bottom:12px;letter-spacing:0;text-shadow:0 0 14px rgba(0,209,255,.45)}.hero-subtitle{font-size:16px;line-height:1.9;color:#D7F4FF;max-width:1160px;font-weight:500}.tag-chip{display:inline-block;padding:7px 14px;margin:18px 9px 0 0;border-radius:999px;background:rgba(0,209,255,.14);border:1px solid rgba(0,209,255,.48);color:#fff;font-size:13px;font-weight:700}
.section-title{font-size:28px;font-weight:900;color:#fff;margin:14px 0 8px;text-shadow:0 0 12px rgba(0,209,255,.28)}.section-desc{color:#C7E9F7;font-size:16px;margin-bottom:18px;line-height:1.75;font-weight:500}.metric-panel,.insight-card,.table-card,.comment-card{background:linear-gradient(180deg,rgba(14,48,78,.94),rgba(8,30,52,.94));border:1px solid rgba(0,209,255,.36);border-radius:14px;box-shadow:0 0 18px rgba(0,209,255,.12),inset 0 0 18px rgba(0,209,255,.06)}.metric-panel{padding:22px 20px}.metric-label{color:#D2F5FF;font-size:15px;margin-bottom:12px;font-weight:800}.metric-value{color:#fff;font-size:34px;font-weight:950;letter-spacing:0;text-shadow:0 0 12px rgba(0,209,255,.38)}.insight-card{padding:15px 17px;min-height:106px;color:#E8FAFF;line-height:1.65}.insight-label{color:#93E9FF;font-size:13px;font-weight:800;margin-bottom:8px}.insight-value{color:#fff;font-size:18px;font-weight:850}.insight-note{color:#C6E8F5;font-size:13px;margin-top:6px}.table-card{padding:12px;margin:10px 0 20px}.comment-card{padding:14px 15px;margin-bottom:12px;color:#E8FAFF;line-height:1.65}.comment-meta{color:#AEEFFF;font-size:13px;font-weight:800;margin-bottom:6px}.comment-title{color:#fff;font-weight:850;margin-bottom:5px}.comment-text{color:#D7F4FF;font-size:14px}.small-muted{font-size:14px;color:#C4E7F6;line-height:1.8}
button[data-baseweb="tab"]{background-color:rgba(0,209,255,.08);border-radius:12px 12px 0 0;padding:10px 18px!important}button[data-baseweb="tab"] p{color:#fff!important;font-size:19px!important;font-weight:850!important}button[data-baseweb="tab"][aria-selected="true"]{background-color:rgba(0,209,255,.20)!important;border-bottom:2px solid #00D1FF!important}div[data-testid="stDataFrame"]{border-radius:12px;overflow:hidden;border:1px solid rgba(0,209,255,.25);box-shadow:0 0 14px rgba(0,209,255,.08)}div[data-testid="stDataFrame"] [role="columnheader"]{background:rgba(220,244,255,.96)!important;color:#06111F!important;font-weight:900!important}div[data-testid="stDataFrame"] [role="gridcell"]{min-height:42px!important;white-space:normal!important}div[data-testid="stExpander"]{background:rgba(8,30,52,.66);border-radius:12px;border:1px solid rgba(0,209,255,.18)}hr{border-color:rgba(0,209,255,.18)}
</style>
""", unsafe_allow_html=True)

if not DB_PATH.exists():
    st.error(f"未找到数据库文件：{DB_PATH}")
    st.stop()

@st.cache_data(show_spinner=False)
def query_data(sql: str, params: tuple = ()) -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(sql, conn, params=list(params))


def add_product_risk(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    x = df.copy()
    x["bad_review_rate"] = x["bad_review_rate"].fillna(0).clip(0, 1)
    x["verified_purchase_rate"] = x["verified_purchase_rate"].fillna(0).clip(0, 1)
    x["sample_review_count"] = x["sample_review_count"].fillna(0)
    x["product_avg_rating"] = x["product_avg_rating"].fillna(x.get("sample_avg_rating", 0)).fillna(0)
    max_reviews = max(float(x["sample_review_count"].max()), 1.0)
    rating_risk = ((5 - x["product_avg_rating"]) / 4 * 100).clip(0, 100)
    bad_rate_risk = x["bad_review_rate"] * 100
    volume_risk = (x["sample_review_count"] / max_reviews * 100).clip(0, 100)
    verified_risk = (1 - x["verified_purchase_rate"]) * 100
    x["risk_score"] = (bad_rate_risk * 0.45 + rating_risk * 0.30 + (bad_rate_risk * volume_risk / 100) * 0.15 + verified_risk * 0.10).round(1)

    def level(row):
        if row["risk_score"] >= 60 or (row["bad_review_rate"] >= 0.35 and row["sample_review_count"] >= 10) or (row["product_avg_rating"] <= 2.8 and row["sample_review_count"] >= 5):
            return "高风险"
        if row["risk_score"] >= 35 or row["bad_review_rate"] >= 0.18 or row["product_avg_rating"] < 3.6:
            return "中风险"
        return "低风险"

    x["risk_level"] = x.apply(level, axis=1)
    return x


def add_brand_risk(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    x = df.copy()
    x["negative_review_ratio"] = x["negative_review_ratio"].fillna(0).clip(0, 1)
    x["verified_purchase_ratio"] = x["verified_purchase_ratio"].fillna(0).clip(0, 1)
    x["avg_review_rating"] = x["avg_review_rating"].fillna(0)
    max_reviews = max(float(x["review_count"].max()), 1.0)
    x["risk_score"] = (x["negative_review_ratio"] * 100 * 0.48 + ((5 - x["avg_review_rating"]) / 4 * 100).clip(0, 100) * 0.30 + (x["review_count"] / max_reviews * 100).clip(0, 100) * x["negative_review_ratio"] * 0.12 + (1 - x["verified_purchase_ratio"]) * 100 * 0.10).round(1)
    x["risk_level"] = pd.cut(x["risk_score"], bins=[-1, 34.999, 59.999, 101], labels=["低风险", "中风险", "高风险"]).astype(str)
    return x


def cn_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns={c: FIELD_NAME_MAP.get(c, c) for c in df.columns})


def format_verified(value):
    return "是" if int(value or 0) == 1 else "否"


def truncate_text(value, length=150):
    text = "" if pd.isna(value) else str(value).strip()
    return text if len(text) <= length else text[:length].rstrip() + "..."


def product_column_config():
    return {
        "商品名称": st.column_config.TextColumn("商品名称", width="large"),
        "品牌": st.column_config.TextColumn("品牌", width="medium"),
        "商品类目": st.column_config.TextColumn("商品类目", width="medium"),
        "价格": st.column_config.NumberColumn("价格", format="$%.2f", width="small"),
        "商品平均评分": st.column_config.NumberColumn("商品平均评分", format="%.2f", width="small"),
        "累计评分数": st.column_config.NumberColumn("累计评分数", format="%d", width="small"),
        "样本评论数": st.column_config.NumberColumn("样本评论数", format="%d", width="small"),
        "差评率": st.column_config.NumberColumn("差评率", format="%.1f%%", width="small"),
        "验证购买占比": st.column_config.NumberColumn("验证购买占比", format="%.1f%%", width="small"),
        "口碑风险评分": st.column_config.NumberColumn("口碑风险评分", format="%.1f", width="small"),
        "口碑风险等级": st.column_config.TextColumn("口碑风险等级", width="small"),
    }


def review_column_config():
    return {
        "评分": st.column_config.NumberColumn("评分", format="%.1f", width="small"),
        "评论标题": st.column_config.TextColumn("评论标题", width="medium"),
        "评论内容": st.column_config.TextColumn("评论内容", width="large"),
        "有用票数": st.column_config.NumberColumn("有用票数", format="%d", width="small"),
        "是否验证购买": st.column_config.TextColumn("是否验证购买", width="small"),
        "评论日期": st.column_config.TextColumn("评论日期", width="small"),
    }


def display_dataframe(df: pd.DataFrame, height=360, column_config=None):
    st.markdown('<div class="table-card">', unsafe_allow_html=True)
    st.dataframe(df, width="stretch", height=height, hide_index=True, column_config=column_config)
    st.markdown("</div>", unsafe_allow_html=True)


def prepare_product_display(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["product_title", "brand", "main_category", "price", "product_avg_rating", "total_rating_number", "sample_review_count", "bad_review_rate", "verified_purchase_rate", "risk_score", "risk_level"]
    x = df[[c for c in cols if c in df.columns]].copy()
    if "bad_review_rate" in x:
        x["bad_review_rate"] = (x["bad_review_rate"] * 100).round(1)
    if "verified_purchase_rate" in x:
        x["verified_purchase_rate"] = (x["verified_purchase_rate"] * 100).round(1)
    return cn_columns(x)


def prepare_review_display(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["rating", "review_title", "review_text", "helpful_vote", "verified_purchase", "review_date"]
    x = df[[c for c in cols if c in df.columns]].copy()
    if "verified_purchase" in x:
        x["verified_purchase"] = x["verified_purchase"].fillna(0).astype(int).map({1: "是", 0: "否"})
    return cn_columns(x)


def show_field_expander(include_reviews=True):
    with st.expander("字段说明", expanded=False):
        st.markdown("""
        - **商品平均评分**：样本评论中的平均评分。
        - **样本评论数**：当前数据集中收录的评论数量。
        - **差评率**：低评分评论占比。
        - **验证购买占比**：带有 verified purchase 标记的评论占比。
        - **口碑风险等级**：根据差评率、平均评分、评论规模等指标综合判断的风险水平。
        """)
        if include_reviews:
            st.markdown("- **有用票数**：其他用户认为该评论有帮助的次数。")


def sci_bar_chart(df, x_col, y_col, title, orientation="v", height=380):
    fig = go.Figure()
    if orientation == "h":
        fig.add_trace(go.Bar(x=df[x_col], y=df[y_col], orientation="h", marker=dict(color="rgba(0,209,255,.75)", line=dict(color="rgba(160,240,255,.95)", width=1)), hovertemplate="%{y}<br>数值：%{x}<extra></extra>"))
    else:
        fig.add_trace(go.Bar(x=df[x_col], y=df[y_col], marker=dict(color="rgba(0,209,255,.75)", line=dict(color="rgba(160,240,255,.95)", width=1)), hovertemplate="%{x}<br>数值：%{y}<extra></extra>"))
    fig.update_layout(title=dict(text=title, font=dict(size=17, color="#EAF8FF")), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#DDF7FF", size=13), height=height, margin=dict(l=20, r=20, t=55, b=30), xaxis=dict(showgrid=True, gridcolor="rgba(0,209,255,.12)", zeroline=False), yaxis=dict(showgrid=False, zeroline=False))
    return fig


def sci_line_chart(df, x_col, y_col, title, height=380):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df[x_col], y=df[y_col], mode="lines+markers", line=dict(color="#00D1FF", width=3), marker=dict(size=7, color="#8AF3FF", line=dict(color="#00D1FF", width=1)), hovertemplate="%{x}<br>数值：%{y}<extra></extra>"))
    fig.update_layout(title=dict(text=title, font=dict(size=17, color="#EAF8FF")), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#DDF7FF", size=13), height=height, margin=dict(l=20, r=20, t=55, b=30), xaxis=dict(showgrid=True, gridcolor="rgba(0,209,255,.12)", zeroline=False), yaxis=dict(showgrid=True, gridcolor="rgba(0,209,255,.12)", zeroline=False))
    return fig


def show_comment_cards(df: pd.DataFrame, title: str):
    st.markdown(f"**{title}**")
    if df.empty:
        st.caption("当前商品暂无符合条件的评论。")
        return
    for _, row in df.head(5).iterrows():
        st.markdown(f"""
        <div class="comment-card">
            <div class="comment-meta">评分 {row.get('rating', 0):.1f} · 验证购买：{format_verified(row.get('verified_purchase', 0))} · 有用票数：{int(row.get('helpful_vote', 0) or 0)}</div>
            <div class="comment-title">{truncate_text(row.get('review_title', ''), 70) or '无标题'}</div>
            <div class="comment-text">{truncate_text(row.get('review_text', ''), 150)}</div>
        </div>
        """, unsafe_allow_html=True)


st.markdown("""
<div class="hero-box">
    <div class="hero-title">Amazon 商品口碑洞察与风险识别平台</div>
    <div class="hero-subtitle">面向电商运营、品控和风控场景，聚合商品评分、评论规模、差评率、验证购买占比与有用票数，帮助快速发现高风险商品、异常品牌和典型负面反馈。</div>
    <span class="tag-chip">商品口碑监测</span><span class="tag-chip">差评风险识别</span><span class="tag-chip">品牌表现对比</span><span class="tag-chip">典型评论洞察</span>
</div>
""", unsafe_allow_html=True)

summary = query_data("""
SELECT
    (SELECT COUNT(*) FROM reviews) AS review_count,
    (SELECT COUNT(*) FROM products) AS product_count,
    (SELECT COUNT(*) FROM users) AS user_count,
    (SELECT COUNT(*) FROM brands) AS brand_count,
    ROUND((SELECT AVG(rating) FROM reviews), 3) AS avg_rating,
    ROUND((SELECT AVG(is_negative) FROM reviews), 3) AS negative_review_ratio;
""")
review_count = int(summary.loc[0, "review_count"])
product_count = int(summary.loc[0, "product_count"])
user_count = int(summary.loc[0, "user_count"])
brand_count = int(summary.loc[0, "brand_count"])
avg_rating = float(summary.loc[0, "avg_rating"])
negative_ratio = float(summary.loc[0, "negative_review_ratio"])

st.markdown('<div class="section-title">一、数据概览</div>', unsafe_allow_html=True)
st.markdown('<div class="section-desc">从评论规模、商品覆盖、品牌覆盖和整体评分水平快速判断当前样本的数据质量与口碑基线。</div>', unsafe_allow_html=True)
for col, (label, value) in zip(st.columns(6), [("评论数", f"{review_count:,}"), ("商品数", f"{product_count:,}"), ("用户数", f"{user_count:,}"), ("品牌数", f"{brand_count:,}"), ("平均评分", f"{avg_rating:.3f}"), ("差评率", f"{negative_ratio:.1%}")]):
    with col:
        st.markdown(f'<div class="metric-panel"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)

product_risk_sql = """
SELECT p.product_id,p.product_title,p.brand,p.main_category,p.price,p.average_rating AS product_avg_rating,p.rating_number AS total_rating_number,
COUNT(r.review_id) AS sample_review_count,ROUND(AVG(r.is_negative),3) AS bad_review_rate,ROUND(AVG(r.verified_purchase),3) AS verified_purchase_rate,ROUND(AVG(r.rating),3) AS sample_avg_rating
FROM products p LEFT JOIN reviews r ON p.product_id=r.product_id
GROUP BY p.product_id,p.product_title,p.brand,p.main_category,p.price,p.average_rating,p.rating_number
HAVING sample_review_count>=1;
"""
all_product_risk = add_product_risk(query_data(product_risk_sql))
brand_all = add_brand_risk(query_data("""
SELECT brand,product_count,review_count,ROUND(avg_review_rating,3) AS avg_review_rating,ROUND(negative_review_ratio,3) AS negative_review_ratio,ROUND(verified_purchase_ratio,3) AS verified_purchase_ratio,ROUND(avg_helpful_vote,3) AS avg_helpful_vote
FROM brands WHERE brand IS NOT NULL AND brand!='' AND brand!='Unknown' AND review_count>=5;
"""))
verified_compare = query_data("SELECT verified_purchase, ROUND(AVG(rating),3) AS avg_rating FROM reviews GROUP BY verified_purchase;")
verified_rating = verified_compare.set_index("verified_purchase")["avg_rating"].to_dict() if not verified_compare.empty else {}
verified_gap = float(verified_rating.get(1, 0) - verified_rating.get(0, 0))

highest_bad_brand = brand_all.sort_values(["negative_review_ratio", "review_count"], ascending=[False, False]).head(1)
highest_volume_brand = brand_all.sort_values("review_count", ascending=False).head(1)
high_risk_count = int((all_product_risk["risk_level"] == "高风险").sum()) if not all_product_risk.empty else 0
insights = []
if not highest_bad_brand.empty:
    r = highest_bad_brand.iloc[0]; insights.append(("差评率最高品牌", str(r["brand"]), f"差评率 {r['negative_review_ratio']:.1%}，评论量 {int(r['review_count']):,}"))
if not highest_volume_brand.empty:
    r = highest_volume_brand.iloc[0]; insights.append(("评论量最高品牌", str(r["brand"]), f"评论量 {int(r['review_count']):,}，平均评分 {r['avg_review_rating']:.2f}"))
insights.append(("高风险商品数量", f"{high_risk_count:,} 个", "基于差评率、平均评分、评论规模和验证购买占比综合判断"))
insights.append(("验证购买评分差异", f"{verified_gap:+.2f} 分", "验证购买评论平均评分减去非验证购买评论平均评分"))

st.markdown('<div class="section-title">核心洞察区</div>', unsafe_allow_html=True)
st.markdown('<div class="section-desc">自动提炼当前数据中的风险信号和运营关注点，帮助先看结论再看明细。</div>', unsafe_allow_html=True)
for col, (label, value, note) in zip(st.columns(4), insights[:4]):
    with col:
        st.markdown(f'<div class="insight-card"><div class="insight-label">{label}</div><div class="insight-value">{value}</div><div class="insight-note">{note}</div></div>', unsafe_allow_html=True)

st.sidebar.title("筛选条件")
st.sidebar.caption("可通过商品关键词、品牌、评分和样本评论数定位商品口碑表现。")
keyword = st.sidebar.text_input("商品关键词", value="")
brand_df = query_data("SELECT DISTINCT brand FROM products WHERE brand IS NOT NULL AND brand!='' ORDER BY brand;")
brand_options = ["全部品牌"] + brand_df["brand"].dropna().astype(str).tolist()
selected_brand = st.sidebar.selectbox(
    "品牌关键词",
    brand_options,
    index=None,
    placeholder="输入品牌名称搜索匹配",
)
min_rating = st.sidebar.slider("最低商品平均评分", 0.0, 5.0, 0.0, 0.1)
min_sample_reviews = st.sidebar.selectbox("最低样本评论数", options=[0, 1, 2, 3, 5, 10, 20, 50, 100], index=1)
limit_n = st.sidebar.slider("最多显示商品数", 10, 200, 50, 10)
st.sidebar.markdown("---")
st.sidebar.markdown('<div class="small-muted">可尝试关键词：<b>shampoo</b>、<b>hair</b>、<b>brush</b>、<b>oil</b>、<b>cream</b>。</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["商品口碑概览", "品牌表现对比", "评论行为分析"])

with tab1:
    st.markdown('<div class="section-title">商品口碑概览</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">根据筛选条件查看商品核心口碑指标，并优先识别差评集中、评分偏低或评论规模较大的风险商品。</div>', unsafe_allow_html=True)
    show_field_expander(include_reviews=False)

    product_sql = """
    SELECT p.product_id,p.product_title,p.brand,p.main_category,p.price,p.average_rating AS product_avg_rating,p.rating_number AS total_rating_number,
    COUNT(r.review_id) AS sample_review_count,ROUND(AVG(r.rating),3) AS sample_avg_rating,ROUND(AVG(r.is_negative),3) AS bad_review_rate,ROUND(AVG(r.verified_purchase),3) AS verified_purchase_rate,ROUND(AVG(r.helpful_vote),3) AS avg_helpful_vote
    FROM products p LEFT JOIN reviews r ON p.product_id=r.product_id WHERE 1=1
    """
    params = []
    if keyword.strip():
        product_sql += " AND p.product_title LIKE ? "; params.append(f"%{keyword.strip()}%")
    if selected_brand and selected_brand != "全部品牌":
        product_sql += " AND p.brand = ? "; params.append(selected_brand)
    product_sql += """
    GROUP BY p.product_id,p.product_title,p.brand,p.main_category,p.price,p.average_rating,p.rating_number
    HAVING product_avg_rating>=? AND sample_review_count>=?
    ORDER BY sample_review_count DESC,bad_review_rate DESC LIMIT ?;
    """
    params.extend([min_rating, min_sample_reviews, limit_n])
    product_result = add_product_risk(query_data(product_sql, tuple(params)))
    high_count = int((product_result["risk_level"] == "高风险").sum()) if not product_result.empty else 0
    st.markdown(f'<div class="insight-card"><div class="insight-label">当前筛选结果</div><div class="insight-value">返回 {len(product_result)} 个商品，其中高风险商品 {high_count} 个</div><div class="insight-note">保留原筛选逻辑，并新增口碑风险评分与风险等级用于排序和预警。</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">高风险商品 Top 10</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">优先展示风险评分最高的商品，便于运营和品控团队快速进入问题商品排查。</div>', unsafe_allow_html=True)
    high_risk_top = product_result.sort_values(["risk_score", "bad_review_rate", "sample_review_count"], ascending=[False, False, False]).head(10)
    display_dataframe(prepare_product_display(high_risk_top), height=300, column_config=product_column_config())

    st.markdown('<div class="section-title">商品列表</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">展示商品名称、品牌、类目、评分、评论规模、差评率和风险等级等业务分析字段。</div>', unsafe_allow_html=True)
    display_dataframe(prepare_product_display(product_result), height=390, column_config=product_column_config())

    st.markdown('<div class="section-title">典型评论洞察</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">选择商品后查看评论明细，并自动抽取高赞评论、典型差评和验证购买差评。</div>', unsafe_allow_html=True)
    show_field_expander(include_reviews=True)
    if len(product_result) > 0:
        product_result = product_result.copy()
        product_result["display_name"] = product_result["product_id"] + " | " + product_result["product_title"].astype(str).str.slice(0, 90)
        selected_product_display = st.selectbox("选择一个商品查看评论", product_result["display_name"].tolist())
        selected_product_id = selected_product_display.split(" | ")[0]
        review_detail = query_data("""
        SELECT review_id,rating,review_title,review_text,helpful_vote,verified_purchase,review_date,review_length,is_negative
        FROM reviews WHERE product_id=? ORDER BY helpful_vote DESC,review_length DESC LIMIT 100;
        """, (selected_product_id,))
        st.caption(f"当前展示商品：{selected_product_id}；最多展示 100 条评论。")
        c1, c2, c3 = st.columns(3)
        with c1:
            show_comment_cards(review_detail.sort_values("helpful_vote", ascending=False), "高赞评论 Top 5")
        with c2:
            show_comment_cards(review_detail[review_detail["rating"] <= 2].sort_values(["rating", "helpful_vote"], ascending=[True, False]), "典型差评 Top 5")
        with c3:
            verified_bad = review_detail[(review_detail["verified_purchase"] == 1) & (review_detail["rating"] <= 2)]
            show_comment_cards(verified_bad.sort_values(["rating", "helpful_vote"], ascending=[True, False]), "验证购买差评 Top 5")
        st.markdown("**评论明细表**")
        display_dataframe(prepare_review_display(review_detail), height=360, column_config=review_column_config())
    else:
        st.info("当前筛选条件下没有商品。可以尝试更换关键词，或降低评分、评论数门槛。")

with tab2:
    st.markdown('<div class="section-title">品牌表现对比</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">从评论规模、差评率、平均评分和风险等级对比品牌表现，识别重点风险品牌与优势品牌。</div>', unsafe_allow_html=True)
    show_field_expander(include_reviews=False)
    brand_performance = add_brand_risk(query_data("""
    SELECT brand,product_count,review_count,ROUND(avg_review_rating,3) AS avg_review_rating,ROUND(negative_review_ratio,3) AS negative_review_ratio,ROUND(verified_purchase_ratio,3) AS verified_purchase_ratio,ROUND(avg_helpful_vote,3) AS avg_helpful_vote
    FROM brands WHERE brand IS NOT NULL AND brand!='Unknown' AND review_count>=10 ORDER BY review_count DESC LIMIT 30;
    """))
    left_col, right_col = st.columns([1.15, 1])
    with left_col:
        st.markdown("**评论量较高的品牌**")
        brand_display = brand_performance.copy()
        brand_display["negative_review_ratio"] = (brand_display["negative_review_ratio"] * 100).round(1)
        brand_display["verified_purchase_ratio"] = (brand_display["verified_purchase_ratio"] * 100).round(1)
        display_dataframe(cn_columns(brand_display), height=420)
    with right_col:
        chart_df = brand_performance.head(15).sort_values("review_count", ascending=True)
        st.plotly_chart(sci_bar_chart(chart_df, "review_count", "brand", "品牌评论量 Top 15", "h", 420), width="stretch", config={"displayModeBar": False})

    st.markdown('<div class="section-title">品牌四象限分析图</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">以品牌评论量和差评率定位品牌风险位置，点越大代表覆盖商品越多。</div>', unsafe_allow_html=True)
    if not brand_performance.empty:
        x_mid = float(brand_performance["review_count"].median())
        y_mid = float(brand_performance["negative_review_ratio"].median())
        color_map = {"低风险": "#5FF0A5", "中风险": "#FFD166", "高风险": "#FF5C7A"}
        fig = go.Figure()
        for level, df_level in brand_performance.groupby("risk_level"):
            fig.add_trace(go.Scatter(x=df_level["review_count"], y=df_level["negative_review_ratio"], mode="markers+text", text=df_level["brand"].where(df_level["review_count"].rank(ascending=False) <= 6, ""), textposition="top center", marker=dict(size=(df_level["product_count"].clip(lower=1) ** 0.5) * 9 + 8, color=color_map.get(level, "#00D1FF"), line=dict(color="rgba(255,255,255,.85)", width=1), opacity=.82), name=level, customdata=df_level[["brand", "product_count", "avg_review_rating", "verified_purchase_ratio", "risk_score"]], hovertemplate="品牌：%{customdata[0]}<br>评论量：%{x:,}<br>差评率：%{y:.1%}<br>商品数：%{customdata[1]}<br>平均评分：%{customdata[2]:.2f}<br>验证购买占比：%{customdata[3]:.1%}<br>风险评分：%{customdata[4]:.1f}<extra></extra>"))
        fig.add_vline(x=x_mid, line_dash="dash", line_color="rgba(255,255,255,.38)")
        fig.add_hline(y=y_mid, line_dash="dash", line_color="rgba(255,255,255,.38)")
        fig.update_layout(height=500, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#DDF7FF"), margin=dict(l=20, r=20, t=35, b=35), xaxis=dict(title="品牌评论量", showgrid=True, gridcolor="rgba(0,209,255,.12)", zeroline=False), yaxis=dict(title="差评率", tickformat=".0%", showgrid=True, gridcolor="rgba(0,209,255,.12)", zeroline=False), legend=dict(title="口碑风险等级"))
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        st.markdown('<div class="small-muted"><b>四象限解读：</b><br>高评论量 + 高差评率：重点风险品牌；高评论量 + 低差评率：优势品牌；低评论量 + 高差评率：潜在风险品牌；低评论量 + 低差评率：普通观察品牌。</div>', unsafe_allow_html=True)

    risk_brands = add_brand_risk(query_data("""
    SELECT brand,product_count,review_count,ROUND(avg_review_rating,3) AS avg_review_rating,ROUND(negative_review_ratio,3) AS negative_review_ratio,ROUND(verified_purchase_ratio,3) AS verified_purchase_ratio
    FROM brands WHERE brand IS NOT NULL AND brand!='Unknown' AND review_count>=10 ORDER BY negative_review_ratio DESC,review_count DESC LIMIT 30;
    """))
    st.markdown('<div class="section-title">差评风险品牌</div>', unsafe_allow_html=True)
    r1, r2 = st.columns([1.15, 1])
    with r1:
        st.markdown("**差评率较高的品牌**")
        risk_display = risk_brands.copy()
        risk_display["negative_review_ratio"] = (risk_display["negative_review_ratio"] * 100).round(1)
        risk_display["verified_purchase_ratio"] = (risk_display["verified_purchase_ratio"] * 100).round(1)
        display_dataframe(cn_columns(risk_display), height=420)
    with r2:
        risk_chart_df = risk_brands.head(15).sort_values("negative_review_ratio", ascending=True)
        fig = sci_bar_chart(risk_chart_df, "negative_review_ratio", "brand", "差评率 Top 15", "h", 420)
        fig.update_xaxes(tickformat=".0%")
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

with tab3:
    st.markdown('<div class="section-title">评论行为分析</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">从评分分布、验证购买、评论长度和月度趋势观察用户评论行为，为口碑判断提供背景解释。</div>', unsafe_allow_html=True)
    rating_dist = query_data("SELECT rating, COUNT(*) AS review_count FROM reviews GROUP BY rating ORDER BY rating;")
    verified_df = query_data("""
    SELECT verified_purchase,COUNT(*) AS review_count,ROUND(AVG(rating),3) AS avg_rating,ROUND(AVG(is_negative),3) AS bad_review_rate,ROUND(AVG(helpful_vote),3) AS avg_helpful_vote,ROUND(AVG(review_length),3) AS avg_review_length
    FROM reviews GROUP BY verified_purchase ORDER BY verified_purchase DESC;
    """)
    verified_df["purchase_type"] = verified_df["verified_purchase"].fillna(0).astype(int).map({1: "验证购买", 0: "非验证购买"})
    c1, c2 = st.columns([1, 1])
    with c1:
        st.plotly_chart(sci_bar_chart(rating_dist, "rating", "review_count", "评分分布", "v", 360), width="stretch", config={"displayModeBar": False})
    with c2:
        st.markdown("**验证购买评论对比**")
        verified_display = verified_df[["purchase_type", "review_count", "avg_rating", "bad_review_rate", "avg_helpful_vote", "avg_review_length"]].copy()
        verified_display["bad_review_rate"] = (verified_display["bad_review_rate"] * 100).round(1)
        verified_display = verified_display.rename(columns={"purchase_type": "购买类型", "review_count": "评论量", "avg_rating": "平均评分", "bad_review_rate": "差评率", "avg_helpful_vote": "平均有用票数", "avg_review_length": "平均评论长度"})
        display_dataframe(verified_display, height=360)

    length_helpful = query_data("""
    SELECT CASE WHEN review_length<20 THEN '01_20字以下' WHEN review_length<50 THEN '02_20-49字' WHEN review_length<100 THEN '03_50-99字' WHEN review_length<200 THEN '04_100-199字' ELSE '05_200字以上' END AS review_length_group,
    COUNT(*) AS review_count,ROUND(AVG(helpful_vote),3) AS avg_helpful_vote,ROUND(AVG(rating),3) AS avg_rating,ROUND(AVG(is_negative),3) AS bad_review_rate
    FROM reviews GROUP BY review_length_group ORDER BY review_length_group;
    """)
    st.markdown('<div class="section-title">评论长度与有用票数</div>', unsafe_allow_html=True)
    st.plotly_chart(sci_line_chart(length_helpful, "review_length_group", "avg_helpful_vote", "不同评论长度组的平均有用票数", 360), width="stretch", config={"displayModeBar": False})
    length_display = length_helpful.copy()
    length_display["bad_review_rate"] = (length_display["bad_review_rate"] * 100).round(1)
    length_display = length_display.rename(columns={"review_length_group": "评论长度分组", "review_count": "评论量", "avg_helpful_vote": "平均有用票数", "avg_rating": "平均评分", "bad_review_rate": "差评率"})
    display_dataframe(length_display, height=260)

    monthly_df = query_data("""
    SELECT review_month,COUNT(*) AS monthly_review_count,ROUND(AVG(rating),3) AS monthly_avg_rating,ROUND(AVG(is_negative),3) AS monthly_negative_ratio
    FROM reviews GROUP BY review_month HAVING monthly_review_count>=10 ORDER BY review_month;
    """)
    st.markdown('<div class="section-title">月度评论趋势</div>', unsafe_allow_html=True)
    if len(monthly_df) > 0:
        monthly_df["review_month"] = pd.to_datetime(monthly_df["review_month"], errors="coerce")
        monthly_df = monthly_df.dropna(subset=["review_month"])
        st.plotly_chart(sci_line_chart(monthly_df, "review_month", "monthly_review_count", "月度评论数量趋势", 380), width="stretch", config={"displayModeBar": False})
        monthly_display = monthly_df.copy()
        monthly_display["monthly_negative_ratio"] = (monthly_display["monthly_negative_ratio"] * 100).round(1)
        monthly_display = monthly_display.rename(columns={"review_month": "评论月份", "monthly_review_count": "月度评论量", "monthly_avg_rating": "月度平均评分", "monthly_negative_ratio": "月度差评率"})
        display_dataframe(monthly_display, height=300)
    else:
        st.info("当前数据中暂无足够的月度趋势数据。")
