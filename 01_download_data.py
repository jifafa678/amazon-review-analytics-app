from datasets import load_dataset
import pandas as pd
from itertools import islice
from pathlib import Path

# =========================
# 1. 基础设置
# =========================
CATEGORY = "All_Beauty"
N_REVIEWS = 100000  # 第一轮先用1万条，确认能跑通
OUTPUT_DIR = Path("data_raw")
OUTPUT_DIR.mkdir(exist_ok=True)

# =========================
# 2. 下载评论数据
# =========================
print("正在读取评论数据...")

review_dataset = load_dataset(
    "McAuley-Lab/Amazon-Reviews-2023",
    f"raw_review_{CATEGORY}",
    split="full",
    streaming=True,
    trust_remote_code=True
)

review_rows = list(islice(review_dataset, N_REVIEWS))
reviews_df = pd.DataFrame(review_rows)

print("评论数据读取完成：", reviews_df.shape)

reviews_path = OUTPUT_DIR / f"reviews_{CATEGORY}_{N_REVIEWS}.csv"
reviews_df.to_csv(reviews_path, index=False, encoding="utf-8-sig")

print(f"评论数据已保存到：{reviews_path}")

# =========================
# 3. 根据评论里的商品ID，筛选商品元数据
# =========================
product_ids = set(reviews_df["parent_asin"].dropna().unique())

print("样本中涉及商品数量：", len(product_ids))
print("正在读取商品元数据...")

meta_dataset = load_dataset(
    "McAuley-Lab/Amazon-Reviews-2023",
    f"raw_meta_{CATEGORY}",
    split="full",
    streaming=True,
    trust_remote_code=True
)

meta_rows = []

for row in meta_dataset:
    if row.get("parent_asin") in product_ids:
        meta_rows.append(row)

meta_df = pd.DataFrame(meta_rows)

print("商品元数据读取完成：", meta_df.shape)

meta_path = OUTPUT_DIR / f"meta_{CATEGORY}_{N_REVIEWS}.csv"
meta_df.to_csv(meta_path, index=False, encoding="utf-8-sig")

print(f"商品元数据已保存到：{meta_path}")

# =========================
# 4. 简单检查
# =========================
print("\n评论数据字段：")
print(reviews_df.columns.tolist())

print("\n商品元数据字段：")
print(meta_df.columns.tolist())

print("\n评论数据前5行：")
print(reviews_df.head())

print("\n商品数据前5行：")
print(meta_df.head())

print("\n第一步完成：原始评论数据和商品元数据已下载。")