#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试连续对话功能
"""
import requests
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_URL = "http://localhost:8000/api/v1/analyze"

# 对话历史
conversation_history = []

def ask_question(question):
    """发送问题并获取回复"""
    print("\n" + "=" * 60)
    print(f"[User] {question}")
    print("=" * 60)
    
    try:
        response = requests.post(
            API_URL,
            json={
                "question": question,
                "user_id": "test_user",
                "save_result": False,
                "conversation_history": conversation_history
            },
            timeout=120
        )
        
        result = response.json()
        
        # 显示结果
        print(f"\n[Query ID] {result.get('query_id')}")
        print(f"[Time] {result.get('execution_time', 0):.2f}s")
        
        if result.get('insights'):
            print("\n[Insights]")
            for insight in result['insights']:
                print(f"  - {insight}")
        
        if result.get('executed_sql'):
            print(f"\n[SQL] {result['executed_sql']}")
        
        # 构建助手回复内容
        assistant_content = ''
        if result.get('insights'):
            assistant_content = '\n'.join(result['insights'])
        elif result.get('report'):
            assistant_content = result['report'][:500]
        else:
            assistant_content = '已完成数据分析'
        
        # 更新对话历史
        conversation_history.append({
            "role": "user",
            "content": question
        })
        conversation_history.append({
            "role": "assistant",
            "content": assistant_content
        })
        
        print(f"\n[Conversation] Total messages: {len(conversation_history)}")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("CrewAI Continuous Conversation Test")
    print("=" * 60)
    print("\nThis script demonstrates continuous conversation capability.")
    print("The AI will remember previous questions and answers.")
    print("\nStarting conversation...\n")
    
    # 第一轮：基础查询
    if ask_question("哪个国家的客户消费最多？"):
        
        # 第二轮：追问细节（使用代词"它"）
        input("\nPress Enter to continue...")
        if ask_question("那它的平均客单价是多少？"):
            
            # 第三轮：对比分析
            input("\nPress Enter to continue...")
            ask_question("和第二名相比呢？")
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)
    print(f"\nFinal conversation history: {len(conversation_history)} messages")
    print("\nConversation flow:")
    for i, msg in enumerate(conversation_history, 1):
        role = "[User]" if msg['role'] == 'user' else "[AI]"
        content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
        print(f"{i}. {role} {content}")

