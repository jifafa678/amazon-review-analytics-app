import sqlite3
import pandas as pd
from pathlib import Path

# =========================
# 1. 路径设置
# =========================
DB_FILE = Path("data_processed") / "amazon_reviews_analysis.db"
OUTPUT_DIR = Path("analysis_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

conn = sqlite3.connect(DB_FILE)

print("已连接数据库：", DB_FILE)


# =========================
# 2. 定义一个运行 SQL 的函数
# =========================
def run_query(query_name, sql):
    print("\n" + "=" * 80)
    print(f"正在运行分析：{query_name}")
    print("=" * 80)

    df = pd.read_sql_query(sql, conn)

    print(df.head(10))

    output_path = OUTPUT_DIR / f"{query_name}.csv"
    df.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"结果已保存到：{output_path}")

    return df


# =========================
# 3. SQL 分析 1：整体数据概况
# =========================
sql_01 = """
SELECT
    (SELECT COUNT(*) FROM reviews) AS review_count,
    (SELECT COUNT(*) FROM products) AS product_count,
    (SELECT COUNT(*) FROM users) AS user_count,
    (SELECT COUNT(*) FROM brands) AS brand_count,
    ROUND((SELECT AVG(rating) FROM reviews), 3) AS avg_review_rating,
    ROUND((SELECT AVG(is_negative) FROM reviews), 3) AS negative_review_ratio,
    ROUND((SELECT AVG(verified_purchase) FROM reviews), 3) AS verified_purchase_ratio;
"""

run_query("01_overall_summary", sql_01)


# =========================
# 4. SQL 分析 2：评分分布
# =========================
sql_02 = """
SELECT
    rating,
    COUNT(*) AS review_count,
    ROUND(COUNT(*) * 1.0 / (SELECT COUNT(*) FROM reviews), 4) AS review_ratio
FROM reviews
GROUP BY rating
ORDER BY rating;
"""

run_query("02_rating_distribution", sql_02)


# =========================
# 5. SQL 分析 3：评论量最高的品牌
# =========================
sql_03 = """
SELECT
    p.brand,
    COUNT(r.review_id) AS review_count,
    COUNT(DISTINCT p.product_id) AS product_count,
    ROUND(AVG(r.rating), 3) AS avg_rating,
    ROUND(AVG(r.is_negative), 3) AS negative_review_ratio,
    ROUND(AVG(r.verified_purchase), 3) AS verified_purchase_ratio
FROM reviews r
LEFT JOIN products p
    ON r.product_id = p.product_id
GROUP BY p.brand
HAVING review_count >= 10
ORDER BY review_count DESC
LIMIT 20;
"""

run_query("03_top_brands_by_review_count", sql_03)


# =========================
# 6. SQL 分析 4：差评率最高的品牌
# =========================
sql_04 = """
SELECT
    p.brand,
    COUNT(r.review_id) AS review_count,
    COUNT(DISTINCT p.product_id) AS product_count,
    ROUND(AVG(r.rating), 3) AS avg_rating,
    ROUND(AVG(r.is_negative), 3) AS negative_review_ratio
FROM reviews r
LEFT JOIN products p
    ON r.product_id = p.product_id
GROUP BY p.brand
HAVING review_count >= 10
ORDER BY negative_review_ratio DESC, review_count DESC
LIMIT 20;
"""

run_query("04_high_negative_ratio_brands", sql_04)


# =========================
# 7. SQL 分析 5：评论量高但评分低的商品
# =========================
sql_05 = """
SELECT
    p.product_id,
    p.product_title,
    p.brand,
    COUNT(r.review_id) AS review_count,
    ROUND(AVG(r.rating), 3) AS avg_rating,
    ROUND(AVG(r.is_negative), 3) AS negative_review_ratio,
    ROUND(AVG(r.verified_purchase), 3) AS verified_purchase_ratio
FROM reviews r
LEFT JOIN products p
    ON r.product_id = p.product_id
GROUP BY p.product_id, p.product_title, p.brand
HAVING review_count >= 5
ORDER BY negative_review_ratio DESC, review_count DESC
LIMIT 20;
"""

run_query("05_risky_products_high_negative_ratio", sql_05)


# =========================
# 8. SQL 分析 6：验证购买评论 vs 非验证购买评论
# =========================
sql_06 = """
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

run_query("06_verified_purchase_comparison", sql_06)


# =========================
# 9. SQL 分析 7：评论长度与 helpful vote 的关系
# =========================
sql_07 = """
SELECT
    CASE
        WHEN review_length < 20 THEN '01_under_20'
        WHEN review_length < 50 THEN '02_20_49'
        WHEN review_length < 100 THEN '03_50_99'
        WHEN review_length < 200 THEN '04_100_199'
        ELSE '05_200_plus'
    END AS review_length_group,
    COUNT(*) AS review_count,
    ROUND(AVG(rating), 3) AS avg_rating,
    ROUND(AVG(helpful_vote), 3) AS avg_helpful_vote,
    ROUND(AVG(is_negative), 3) AS negative_review_ratio
FROM reviews
GROUP BY review_length_group
ORDER BY review_length_group;
"""

run_query("07_review_length_and_helpful_vote", sql_07)


# =========================
# 10. SQL 分析 8：月度评论趋势
# =========================
sql_08 = """
SELECT
    review_month,
    COUNT(*) AS monthly_review_count,
    ROUND(AVG(rating), 3) AS monthly_avg_rating,
    ROUND(AVG(is_negative), 3) AS monthly_negative_ratio,
    SUM(helpful_vote) AS monthly_helpful_vote
FROM reviews
GROUP BY review_month
ORDER BY review_month;
"""

run_query("08_monthly_review_trend", sql_08)


# =========================
# 11. SQL 分析 9：价格区间与评分表现
# =========================
sql_09 = """
SELECT
    CASE
        WHEN p.price IS NULL THEN 'unknown'
        WHEN p.price < 10 THEN '01_under_10'
        WHEN p.price < 20 THEN '02_10_19'
        WHEN p.price < 50 THEN '03_20_49'
        WHEN p.price < 100 THEN '04_50_99'
        ELSE '05_100_plus'
    END AS price_group,
    COUNT(r.review_id) AS review_count,
    COUNT(DISTINCT p.product_id) AS product_count,
    ROUND(AVG(r.rating), 3) AS avg_rating,
    ROUND(AVG(r.is_negative), 3) AS negative_review_ratio,
    ROUND(AVG(r.helpful_vote), 3) AS avg_helpful_vote
FROM reviews r
LEFT JOIN products p
    ON r.product_id = p.product_id
GROUP BY price_group
ORDER BY price_group;
"""

run_query("09_price_group_performance", sql_09)


# =========================
# 12. SQL 分析 10：高口碑商品
# =========================
sql_10 = """
SELECT
    p.product_id,
    p.product_title,
    p.brand,
    COUNT(r.review_id) AS review_count,
    ROUND(AVG(r.rating), 3) AS avg_rating,
    ROUND(AVG(r.is_negative), 3) AS negative_review_ratio,
    ROUND(AVG(r.verified_purchase), 3) AS verified_purchase_ratio,
    ROUND(AVG(r.review_length), 3) AS avg_review_length
FROM reviews r
LEFT JOIN products p
    ON r.product_id = p.product_id
GROUP BY p.product_id, p.product_title, p.brand
HAVING review_count >= 5 AND avg_rating >= 4.5
ORDER BY review_count DESC, avg_rating DESC
LIMIT 20;
"""

run_query("10_high_reputation_products", sql_10)


conn.close()

print("\n全部 SQL 分析完成！")
print("分析结果已保存到 analysis_outputs 文件夹。")