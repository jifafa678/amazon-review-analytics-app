import sqlite3
import pandas as pd
from pathlib import Path
import os

# =========================
# 1. 基础设置
# =========================
FULL_DB = Path("data_processed") / "amazon_reviews_analysis.db"
DEMO_DIR = Path("data_demo")
DEMO_DIR.mkdir(exist_ok=True)

DEMO_DB = DEMO_DIR / "amazon_reviews_demo.db"

# 在线展示版评论数量
# 如果生成的 db 仍然太大，可以改成 20000
DEMO_REVIEW_N = 30000

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

print("正在创建在线展示版数据库...")
print("完整数据库：", FULL_DB)
print("展示版数据库：", DEMO_DB)
print("展示版评论数：", DEMO_REVIEW_N)

# =========================
# 2. 连接完整数据库
# =========================
full_conn = sqlite3.connect(FULL_DB)

# =========================
# 3. 抽取展示版 reviews 表
# =========================
print("\n正在抽取评论表...")

reviews_demo = pd.read_sql_query(
    f"""
    SELECT *
    FROM reviews
    ORDER BY RANDOM()
    LIMIT {DEMO_REVIEW_N};
    """,
    full_conn
)

print("展示版评论表：", reviews_demo.shape)

# 获取展示版涉及的 product_id
product_ids = reviews_demo["product_id"].dropna().unique().tolist()
user_ids = reviews_demo["user_id"].dropna().unique().tolist()

print("展示版涉及商品数：", len(product_ids))
print("展示版涉及用户数：", len(user_ids))

# =========================
# 4. 抽取 products 表
# =========================
print("\n正在抽取商品表...")

products_full = pd.read_sql_query(
    "SELECT * FROM products;",
    full_conn
)

products_demo = products_full[
    products_full["product_id"].isin(product_ids)
].copy()

products_demo["brand"] = products_demo["brand"].apply(clean_brand_name)

print("展示版商品表：", products_demo.shape)

# =========================
# 5. 重新构建 users 表
# =========================
print("\n正在构建用户表...")

users_demo = reviews_demo.groupby("user_id").agg(
    review_count=("review_id", "count"),
    avg_rating_given=("rating", "mean"),
    first_review_time=("review_time", "min"),
    last_review_time=("review_time", "max"),
    total_helpful_vote=("helpful_vote", "sum"),
    negative_review_count=("is_negative", "sum")
).reset_index()

users_demo["first_review_time"] = pd.to_datetime(users_demo["first_review_time"], errors="coerce")
users_demo["last_review_time"] = pd.to_datetime(users_demo["last_review_time"], errors="coerce")

users_demo["active_days"] = (
    users_demo["last_review_time"] - users_demo["first_review_time"]
).dt.days

print("展示版用户表：", users_demo.shape)

# =========================
# 6. 重新构建 brands 表
# =========================
print("\n正在构建品牌表...")

review_product = reviews_demo.merge(
    products_demo[["product_id", "brand", "price", "average_rating", "rating_number"]],
    on="product_id",
    how="left"
)

brand_from_products = products_demo.groupby("brand").agg(
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

brands_demo = brand_from_products.merge(
    brand_from_reviews,
    on="brand",
    how="left"
)

print("展示版品牌表：", brands_demo.shape)

# =========================
# 7. 重新构建 monthly_metrics 表
# =========================
print("\n正在构建月度指标表...")

monthly_metrics_demo = reviews_demo.groupby(["product_id", "review_month"]).agg(
    monthly_review_count=("review_id", "count"),
    monthly_avg_rating=("rating", "mean"),
    monthly_negative_count=("is_negative", "sum"),
    monthly_negative_ratio=("is_negative", "mean"),
    monthly_helpful_vote=("helpful_vote", "sum"),
    monthly_verified_purchase_ratio=("verified_purchase", "mean")
).reset_index()

print("展示版月度指标表：", monthly_metrics_demo.shape)

# =========================
# 8. 写入展示版 SQLite 数据库
# =========================
print("\n正在写入展示版数据库...")

if DEMO_DB.exists():
    DEMO_DB.unlink()

demo_conn = sqlite3.connect(DEMO_DB)

reviews_demo.to_sql("reviews", demo_conn, if_exists="replace", index=False)
products_demo.to_sql("products", demo_conn, if_exists="replace", index=False)
users_demo.to_sql("users", demo_conn, if_exists="replace", index=False)
brands_demo.to_sql("brands", demo_conn, if_exists="replace", index=False)
monthly_metrics_demo.to_sql("monthly_metrics", demo_conn, if_exists="replace", index=False)

# =========================
# 9. 创建索引，提高网页搜索速度
# =========================
print("\n正在创建数据库索引...")

cursor = demo_conn.cursor()

cursor.execute("CREATE INDEX IF NOT EXISTS idx_reviews_product_id ON reviews(product_id);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_reviews_user_id ON reviews(user_id);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_reviews_rating ON reviews(rating);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_product_id ON products(product_id);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_title ON products(product_title);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_brands_brand ON brands(brand);")

demo_conn.commit()

# 压缩数据库文件
cursor.execute("VACUUM;")
demo_conn.close()
full_conn.close()

# =========================
# 10. 输出结果
# =========================
db_size_mb = os.path.getsize(DEMO_DB) / 1024 / 1024

print("\n在线展示版数据库创建完成！")
print("展示版数据库位置：", DEMO_DB)
print(f"展示版数据库大小：{db_size_mb:.2f} MB")

print("\n展示版数据库包含 5 张表：")
print("1. reviews 评论表：", reviews_demo.shape[0], "条")
print("2. products 商品表：", products_demo.shape[0], "条")
print("3. users 用户表：", users_demo.shape[0], "条")
print("4. brands 品牌表：", brands_demo.shape[0], "条")
print("5. monthly_metrics 月度指标表：", monthly_metrics_demo.shape[0], "条")

if db_size_mb <= 25:
    print("\n数据库大小适合通过 GitHub 网页上传。")
else:
    print("\n数据库仍然偏大。建议把 DEMO_REVIEW_N 改成 20000 后重新运行。")
