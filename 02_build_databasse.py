import pandas as pd
import sqlite3
import ast
import re
from pathlib import Path

# =========================
# 1. 路径设置
# =========================
RAW_DIR = Path("data_raw")
OUTPUT_DIR = Path("data_processed")
OUTPUT_DIR.mkdir(exist_ok=True)

REVIEWS_FILE = RAW_DIR / "reviews_All_Beauty_100000.csv"
META_FILE = RAW_DIR / "meta_All_Beauty_100000.csv"

DB_FILE = OUTPUT_DIR / "amazon_reviews_analysis.db"

print("正在读取原始 CSV 文件...")

reviews = pd.read_csv(REVIEWS_FILE)
meta = pd.read_csv(META_FILE)

print("评论数据：", reviews.shape)
print("商品数据：", meta.shape)


# =========================
# 2. 工具函数
# =========================
def clean_price(x):
    """清洗价格字段，把 $12.99 这类内容转成数字"""
    if pd.isna(x):
        return None

    x = str(x)

    if x.lower() in ["none", "nan", ""]:
        return None

    match = re.search(r"[\d.]+", x)
    if match:
        try:
            return float(match.group())
        except ValueError:
            return None

    return None


def count_list_field(x):
    """统计 features、images、description 这类列表字段的长度"""
    if pd.isna(x):
        return 0

    try:
        value = ast.literal_eval(str(x))
        if isinstance(value, list):
            return len(value)
        if isinstance(value, dict):
            return len(value)
    except Exception:
        pass

    text = str(x)
    if text.lower() in ["none", "nan", ""]:
        return 0

    return 1


def text_length(x):
    """计算文本长度"""
    if pd.isna(x):
        return 0
    return len(str(x))


INVALID_BRAND_VALUES = {
    "",
    "-",
    "--",
    "N/A",
    "NA",
    "NONE",
    "NULL",
    "UNKNOWN",
    "NO BRAND",
    "NOT APPLICABLE",
}


def clean_brand_name(brand):
    """只清洗明显脏值和首尾装饰符，保留真实小众品牌。"""
    if pd.isna(brand):
        return "Unknown"

    text = str(brand).strip()
    if not text:
        return "Unknown"

    text = text.strip("\"'“”‘’")
    text = text.strip()
    text = text.strip("#+＋*•·|/\\:;，,。[](){}<>《》-–—")
    text = text.strip()
    text = text.strip("\"'“”‘’")
    text = text.strip()

    if not text:
        return "Unknown"

    if text.upper() in INVALID_BRAND_VALUES:
        return "Unknown"

    return text


def extract_brand_from_details(details):
    """优先从 details 字段中提取 Brand。"""
    if pd.isna(details):
        return None

    raw = str(details).strip()
    if not raw or raw.lower() in {"none", "nan", "null"}:
        return None

    try:
        parsed = ast.literal_eval(raw)
        if isinstance(parsed, dict):
            for key, value in parsed.items():
                if str(key).strip().lower() == "brand":
                    return value
    except Exception:
        pass

    match = re.search(r"""['"]Brand['"]\s*:\s*['"]([^'"]+)['"]""", raw)
    if match:
        return match.group(1)

    return None


def choose_final_brand(row):
    """优先 details.Brand，其次 store/brand，最后 Unknown。"""
    details_brand = clean_brand_name(extract_brand_from_details(row.get("details")))
    if details_brand != "Unknown":
        return details_brand

    store_brand = clean_brand_name(row.get("brand", row.get("store")))
    if store_brand != "Unknown":
        return store_brand

    return "Unknown"


# =========================
# 3. 清洗评论表 reviews
# =========================
print("正在清洗评论数据...")

reviews_clean = reviews.copy()

# 统一字段名
reviews_clean = reviews_clean.rename(columns={
    "parent_asin": "product_id",
    "title": "review_title",
    "text": "review_text"
})

# 生成 review_id
reviews_clean = reviews_clean.reset_index(drop=True)
reviews_clean["review_id"] = reviews_clean.index + 1

# 时间戳转换
reviews_clean["review_time"] = pd.to_datetime(
    reviews_clean["timestamp"],
    unit="ms",
    errors="coerce"
)

reviews_clean["review_date"] = reviews_clean["review_time"].dt.date.astype(str)
reviews_clean["review_month"] = reviews_clean["review_time"].dt.to_period("M").astype(str)

# 文本特征
reviews_clean["review_length"] = reviews_clean["review_text"].apply(text_length)
reviews_clean["review_title_length"] = reviews_clean["review_title"].apply(text_length)

# 评价标签
reviews_clean["is_negative"] = (reviews_clean["rating"] <= 2).astype(int)
reviews_clean["is_positive"] = (reviews_clean["rating"] >= 4).astype(int)

# 布尔值转成 0/1
reviews_clean["verified_purchase"] = reviews_clean["verified_purchase"].astype(int)

# 保留需要的字段
reviews_table = reviews_clean[[
    "review_id",
    "product_id",
    "user_id",
    "rating",
    "review_title",
    "review_text",
    "helpful_vote",
    "verified_purchase",
    "review_time",
    "review_date",
    "review_month",
    "review_length",
    "review_title_length",
    "is_negative",
    "is_positive"
]]

print("评论表完成：", reviews_table.shape)


# =========================
# 4. 清洗商品表 products
# =========================
print("正在清洗商品数据...")

products_clean = meta.copy()

products_clean = products_clean.rename(columns={
    "parent_asin": "product_id",
    "title": "product_title",
    "store": "brand"
})

# 去重，一个 product_id 保留一条
products_clean = products_clean.drop_duplicates(subset=["product_id"])

# 清洗价格
products_clean["price_clean"] = products_clean["price"].apply(clean_price)

# 商品内容特征
products_clean["feature_count"] = products_clean["features"].apply(count_list_field)
products_clean["description_length"] = products_clean["description"].apply(text_length)
products_clean["image_count"] = products_clean["images"].apply(count_list_field)

# 品牌清洗：优先 details.Brand，其次 store，保留数字开头等可能真实的小众品牌
products_clean["brand"] = products_clean.apply(choose_final_brand, axis=1)

products_table = products_clean[[
    "product_id",
    "product_title",
    "brand",
    "main_category",
    "price_clean",
    "average_rating",
    "rating_number",
    "feature_count",
    "description_length",
    "image_count"
]].rename(columns={
    "price_clean": "price"
})

print("商品表完成：", products_table.shape)


# =========================
# 5. 构建用户表 users
# =========================
print("正在构建用户表...")

users_table = reviews_table.groupby("user_id").agg(
    review_count=("review_id", "count"),
    avg_rating_given=("rating", "mean"),
    first_review_time=("review_time", "min"),
    last_review_time=("review_time", "max"),
    total_helpful_vote=("helpful_vote", "sum"),
    negative_review_count=("is_negative", "sum")
).reset_index()

users_table["active_days"] = (
    pd.to_datetime(users_table["last_review_time"]) -
    pd.to_datetime(users_table["first_review_time"])
).dt.days

print("用户表完成：", users_table.shape)


# =========================
# 6. 构建品牌表 brands
# =========================
print("正在构建品牌表...")

review_product = reviews_table.merge(
    products_table[["product_id", "brand", "price"]],
    on="product_id",
    how="left"
)

brand_from_products = products_table.groupby("brand").agg(
    product_count=("product_id", "nunique"),
    avg_product_rating=("average_rating", "mean"),
    total_rating_number=("rating_number", "sum"),
    avg_price=("price", "mean")
).reset_index()

brand_from_reviews = review_product.groupby("brand").agg(
    review_count=("review_id", "count"),
    avg_review_rating=("rating", "mean"),
    negative_review_ratio=("is_negative", "mean"),
    verified_purchase_ratio=("verified_purchase", "mean"),
    avg_helpful_vote=("helpful_vote", "mean")
).reset_index()

brands_table = brand_from_products.merge(
    brand_from_reviews,
    on="brand",
    how="left"
)

print("品牌表完成：", brands_table.shape)


# =========================
# 7. 构建商品月度指标表 monthly_metrics
# =========================
print("正在构建月度指标表...")

monthly_metrics_table = reviews_table.groupby(["product_id", "review_month"]).agg(
    monthly_review_count=("review_id", "count"),
    monthly_avg_rating=("rating", "mean"),
    monthly_negative_count=("is_negative", "sum"),
    monthly_negative_ratio=("is_negative", "mean"),
    monthly_helpful_vote=("helpful_vote", "sum"),
    monthly_verified_purchase_ratio=("verified_purchase", "mean")
).reset_index()

print("月度指标表完成：", monthly_metrics_table.shape)


# =========================
# 8. 写入 SQLite 数据库
# =========================
print("正在写入 SQLite 数据库...")

conn = sqlite3.connect(DB_FILE)

reviews_table.to_sql("reviews", conn, if_exists="replace", index=False)
products_table.to_sql("products", conn, if_exists="replace", index=False)
users_table.to_sql("users", conn, if_exists="replace", index=False)
brands_table.to_sql("brands", conn, if_exists="replace", index=False)
monthly_metrics_table.to_sql("monthly_metrics", conn, if_exists="replace", index=False)

conn.close()

print("\n数据库创建完成！")
print("数据库文件位置：", DB_FILE)

print("\n已创建 5 张表：")
print("1. reviews 评论表")
print("2. products 商品表")
print("3. users 用户表")
print("4. brands 品牌表")
print("5. monthly_metrics 商品月度指标表")

print("\n第二步完成：原始数据已清洗并写入 SQLite 数据库。")
