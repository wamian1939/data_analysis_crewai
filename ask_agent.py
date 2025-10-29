#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
向 CrewAI 智能体提问
"""
import requests
import json
import sys
import io

# UTF-8 编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_URL = "http://localhost:8000/api/v1/analyze"


def ask_question(question_text: str):
    """向智能体提问"""
    print("=" * 60)
    print("CrewAI Data Analysis")
    print("=" * 60)
    
    print(f"\n[Question] {question_text}")
    print("[Status] Analyzing...\n")
    
    try:
        # 发送请求
        response = requests.post(
            API_URL,
            json={
                "question": question_text,
                "user_id": "cli_user",
                "save_result": True
            },
            timeout=180  # 3分钟超时
        )
        
        # 获取结果
        result = response.json()
        
        # 显示结果
        print("=" * 60)
        print("[SUCCESS] Analysis Complete!")
        print("=" * 60)
        
        print(f"\n[Query ID] {result.get('query_id', 'N/A')}")
        print(f"[Time] {result.get('execution_time', 0):.2f} seconds")
        
        if result.get('data'):
            print(f"\n[Data] {len(result['data'])} rows:")
            print("-" * 60)
            for i, row in enumerate(result['data'][:10], 1):  # 显示前10条
                print(f"{i}. {row}")
            if len(result['data']) > 10:
                print(f"... and {len(result['data']) - 10} more rows")
        
        if result.get('insights'):
            print(f"\n[Insights]")
            print("-" * 60)
            for i, insight in enumerate(result['insights'], 1):
                print(f"{i}. {insight}")
        
        if result.get('executed_sql'):
            print("\n[SQL Query]")
            print("-" * 60)
            print(result['executed_sql'])
        
        print("\n" + "=" * 60)
        print("[Report] Full report generated!")
        print("=" * 60)
        
    except requests.exceptions.Timeout:
        print("[ERROR] Request timeout, please try again")
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to API service")
        print("        Please start API first: python api/main.py")
    except json.JSONDecodeError:
        print("[ERROR] Invalid API response")
        print(f"        Raw response: {response.text}")
    except Exception as e:
        print(f"[ERROR] {str(e)}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 从命令行参数获取问题
        question_from_cli = " ".join(sys.argv[1:])
        ask_question(question_from_cli)
    else:
        # 使用默认问题
        default_question = "哪个国家的客户消费最多？"
        ask_question(default_question)

