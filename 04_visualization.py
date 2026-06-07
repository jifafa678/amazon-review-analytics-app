import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# =========================
# 1. 路径设置
# =========================
INPUT_DIR = Path("analysis_outputs")
FIGURE_DIR = Path("figures")
FIGURE_DIR.mkdir(exist_ok=True)

# 图像基础设置
plt.rcParams["figure.dpi"] = 120
plt.rcParams["savefig.dpi"] = 300
plt.rcParams["axes.unicode_minus"] = False


# =========================
# 2. 工具函数
# =========================
def save_current_fig(file_name):
    """保存当前图像"""
    output_path = FIGURE_DIR / file_name
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    print(f"图表已保存：{output_path}")


def read_result(file_name):
    """读取 SQL 分析结果"""
    path = INPUT_DIR / file_name
    if not path.exists():
        raise FileNotFoundError(f"找不到文件：{path}")
    return pd.read_csv(path)


# =========================
# 3. 图1：评分分布
# =========================
rating_dist = read_result("02_rating_distribution.csv")

plt.figure(figsize=(7, 5))
plt.bar(rating_dist["rating"].astype(str), rating_dist["review_count"])
plt.title("Rating Distribution")
plt.xlabel("Rating")
plt.ylabel("Number of Reviews")

for x, y in zip(rating_dist["rating"].astype(str), rating_dist["review_count"]):
    plt.text(x, y, str(y), ha="center", va="bottom", fontsize=9)

save_current_fig("01_rating_distribution.png")


# =========================
# 4. 图2：评论量最高的品牌 Top 10
# =========================
top_brands = read_result("03_top_brands_by_review_count.csv")

# 去掉 Unknown，避免图表被缺失品牌占据
top_brands = top_brands[top_brands["brand"] != "Unknown"].head(10)

plt.figure(figsize=(9, 5))
plt.barh(top_brands["brand"][::-1], top_brands["review_count"][::-1])
plt.title("Top 10 Brands by Review Count")
plt.xlabel("Number of Reviews")
plt.ylabel("Brand")

save_current_fig("02_top_10_brands_by_review_count.png")


# =========================
# 5. 图3：差评率最高的品牌 Top 10
# =========================
negative_brands = read_result("04_high_negative_ratio_brands.csv")
negative_brands = negative_brands[negative_brands["brand"] != "Unknown"].head(10)

plt.figure(figsize=(9, 5))
plt.barh(
    negative_brands["brand"][::-1],
    negative_brands["negative_review_ratio"][::-1]
)
plt.title("Top 10 Brands by Negative Review Ratio")
plt.xlabel("Negative Review Ratio")
plt.ylabel("Brand")

save_current_fig("03_top_10_negative_brands.png")


# =========================
# 6. 图4：验证购买评论与非验证购买评论的平均评分
# =========================
verified = read_result("06_verified_purchase_comparison.csv")
verified["purchase_type"] = verified["verified_purchase"].map({
    1: "Verified Purchase",
    0: "Non-Verified Purchase"
})

plt.figure(figsize=(7, 5))
plt.bar(verified["purchase_type"], verified["avg_rating"])
plt.title("Average Rating by Purchase Type")
plt.xlabel("Purchase Type")
plt.ylabel("Average Rating")
plt.ylim(0, 5)

for x, y in zip(verified["purchase_type"], verified["avg_rating"]):
    plt.text(x, y, f"{y:.2f}", ha="center", va="bottom", fontsize=9)

save_current_fig("04_avg_rating_by_purchase_type.png")


# =========================
# 7. 图5：验证购买评论与非验证购买评论的差评率
# =========================
plt.figure(figsize=(7, 5))
plt.bar(verified["purchase_type"], verified["negative_review_ratio"])
plt.title("Negative Review Ratio by Purchase Type")
plt.xlabel("Purchase Type")
plt.ylabel("Negative Review Ratio")

for x, y in zip(verified["purchase_type"], verified["negative_review_ratio"]):
    plt.text(x, y, f"{y:.3f}", ha="center", va="bottom", fontsize=9)

save_current_fig("05_negative_ratio_by_purchase_type.png")


# =========================
# 8. 图6：评论长度与 helpful vote 的关系
# =========================
length_helpful = read_result("07_review_length_and_helpful_vote.csv")

plt.figure(figsize=(9, 5))
plt.plot(
    length_helpful["review_length_group"],
    length_helpful["avg_helpful_vote"],
    marker="o"
)
plt.title("Review Length and Average Helpful Votes")
plt.xlabel("Review Length Group")
plt.ylabel("Average Helpful Votes")
plt.xticks(rotation=30)

for x, y in zip(length_helpful["review_length_group"], length_helpful["avg_helpful_vote"]):
    plt.text(x, y, f"{y:.2f}", ha="center", va="bottom", fontsize=9)

save_current_fig("06_review_length_and_helpful_votes.png")


# =========================
# 9. 图7：价格区间与平均评分
# =========================
price_group = read_result("09_price_group_performance.csv")

plt.figure(figsize=(9, 5))
plt.bar(price_group["price_group"], price_group["avg_rating"])
plt.title("Average Rating by Price Group")
plt.xlabel("Price Group")
plt.ylabel("Average Rating")
plt.ylim(0, 5)
plt.xticks(rotation=30)

for x, y in zip(price_group["price_group"], price_group["avg_rating"]):
    plt.text(x, y, f"{y:.2f}", ha="center", va="bottom", fontsize=9)

save_current_fig("07_avg_rating_by_price_group.png")


# =========================
# 10. 图8：价格区间与差评率
# =========================
plt.figure(figsize=(9, 5))
plt.bar(price_group["price_group"], price_group["negative_review_ratio"])
plt.title("Negative Review Ratio by Price Group")
plt.xlabel("Price Group")
plt.ylabel("Negative Review Ratio")
plt.xticks(rotation=30)

for x, y in zip(price_group["price_group"], price_group["negative_review_ratio"]):
    plt.text(x, y, f"{y:.3f}", ha="center", va="bottom", fontsize=9)

save_current_fig("08_negative_ratio_by_price_group.png")


# =========================
# 11. 图9：高口碑商品 Top 10
# =========================
high_products = read_result("10_high_reputation_products.csv").head(10)

# 商品标题太长，截断显示
high_products["short_title"] = high_products["product_title"].astype(str).str.slice(0, 35) + "..."

plt.figure(figsize=(10, 6))
plt.barh(high_products["short_title"][::-1], high_products["review_count"][::-1])
plt.title("Top High-Reputation Products by Review Count")
plt.xlabel("Number of Reviews")
plt.ylabel("Product")

save_current_fig("09_high_reputation_products.png")


# =========================
# 12. 图10：月度评论趋势
# =========================
monthly = read_result("08_monthly_review_trend.csv")
monthly["review_month"] = pd.to_datetime(monthly["review_month"], errors="coerce")

# 为避免早期月份太稀疏，图里只展示评论数大于等于 5 的月份
monthly_plot = monthly[monthly["monthly_review_count"] >= 5].copy()

plt.figure(figsize=(10, 5))
plt.plot(
    monthly_plot["review_month"],
    monthly_plot["monthly_review_count"],
    marker="o"
)
plt.title("Monthly Review Count Trend")
plt.xlabel("Month")
plt.ylabel("Number of Reviews")
plt.xticks(rotation=45)

save_current_fig("10_monthly_review_count_trend.png")


print("\n全部图表生成完成！")
print(f"图表已保存到文件夹：{FIGURE_DIR}")