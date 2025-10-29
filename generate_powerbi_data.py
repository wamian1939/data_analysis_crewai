#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
为 Power BI 生成示例数据
运行后会向 API 发送几个问题，生成数据供 Power BI 使用
"""
import requests
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_URL = "http://localhost:8000/api/v1/analyze"

print("=" * 60)
print("Generate Sample Data for Power BI")
print("=" * 60)

# 示例问题
questions = [
    "哪个国家的客户消费最多？",
    "收入最高的艺人TOP10？",
    "最受欢迎的音乐流派是什么？"
]

for i, question in enumerate(questions, 1):
    print(f"\n[{i}/{len(questions)}] 正在分析: {question}")
    
    try:
        response = requests.post(
            API_URL,
            json={
                "question": question,
                "user_id": "powerbi_demo",
                "save_result": True
            },
            timeout=120
        )
        
        result = response.json()
        print(f"    [OK] Query ID: {result['query_id']}")
        
    except Exception as e:
        print(f"    [ERROR] {str(e)}")

print("\n" + "=" * 60)
print("[SUCCESS] Data generation complete!")
print("=" * 60)
print("\n现在可以在 Power BI 中刷新数据了：")
print("1. 打开 Power BI Desktop")
print("2. 获取数据 → Web")
print("3. 输入: http://localhost:8000/api/v1/history")
print("4. 点击「刷新」即可看到新数据")

