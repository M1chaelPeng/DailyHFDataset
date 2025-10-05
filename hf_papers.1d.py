#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# <xbar.title>HuggingFace Daily Papers</xbar.title>
# <xbar.version>v1.0</xbar.version>
# <xbar.author>MichaelPeng</xbar.author>
# <xbar.desc>Display HuggingFace daily papers in menu bar</xbar.desc>
# <xbar.dependencies>python3,requests</xbar.dependencies>
# <xbar.abouturl>https://huggingface.co/papers</xbar.abouturl>

import json
import requests
from datetime import datetime, timezone
import sys

def get_daily_papers(date=None):
    """获取HuggingFace每日论文"""
    base_url = "https://huggingface.co/api/daily_papers"
    params = {}
    if date:
        params['date'] = date
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error | color=red")
        print("---")
        print(f"Failed to fetch papers: {str(e)}")
        sys.exit(1)

def truncate_text(text, max_length=50):
    """截断文本并添加省略号"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def format_paper_title(title, max_length=40):
    """格式化论文标题以适应菜单栏显示"""
    # 移除换行符和多余空格
    title = ' '.join(title.split())
    return truncate_text(title, max_length)

def main():
    # 获取今天的日期
    date = datetime.now().astimezone(timezone.utc)
    yesterday = datetime(date.year, date.month, date.day - 1).strftime("%Y-%m-%d")
    
    # 获取论文数据
    papers_data = get_daily_papers(yesterday)
    
    # 解析论文列表
    if isinstance(papers_data, list):
        papers = papers_data
    elif isinstance(papers_data, dict) and 'papers' in papers_data:
        papers = papers_data['papers']
    else:
        papers = []
    
    # 菜单栏显示
    paper_count = len(papers)
    if paper_count > 0:
        print(f"📄 HF Papers ({paper_count}) | color=#4CAF50")
    else:
        print("📄 No papers today | color=#999999")
    
    print("---")
    
    # 显示日期
    print(f"📅 Daily Paper for {yesterday} | color=#666666")
    print("---")
    
    if paper_count == 0:
        print("No papers available yesterday")
        print("---")
        print("Refresh | refresh=true")
        print("Open HF Papers | href=https://huggingface.co/papers")
        return
    
    # 显示论文列表
    for i, paper in enumerate(papers[:10], 1):  # 限制最多显示10篇
        # 获取论文信息
        paper_obj = paper.get('paper', {}) if isinstance(paper, dict) else paper
        
        # 提取论文详情
        title = paper_obj.get('title', 'Untitled')
        arxiv_id = paper_obj.get('id', '')
        summary = paper_obj.get('summary', '')
        authors = paper_obj.get('authors', [])
        upvotes = paper_obj.get('upvotes', 0)
        
        # 构建链接
        if arxiv_id:
            paper_url = f"https://huggingface.co/papers/{arxiv_id}"
            arxiv_url = f"https://arxiv.org/abs/{arxiv_id}"
        else:
            paper_url = "https://huggingface.co/papers"
            arxiv_url = ""
        
        # 主标题（可点击）
        formatted_title = format_paper_title(title)
        print(f"{i}. {formatted_title} | href={paper_url}")
        
        # 子菜单项
        # 显示完整标题
        if len(title) > 40:
            if len(title) > 60:
                print(f"-- {title[:59]}... | color=#333333")
            else:    
                print(f"-- {title[:60]} | color=#333333")
            print("-- ---")
        
        # 作者信息
        if authors:
            author_names = [author.get('name', '') for author in authors[:3]]
            author_str = ', '.join(author_names)
            if len(authors) > 3:
                author_str += f" et al. ({len(authors)} authors)"
            print(f"-- 👥 {author_str} | color=#666666")
        
        # 投票数
        if upvotes > 0:
            print(f"-- 👍 {upvotes} upvotes | color=#FF6B6B")
        
        # 摘要（截断显示）
        if summary:
            summary_lines = summary.split('\n')
            first_line = truncate_text(summary_lines[0], 60)
            print(f"-- 📝 {first_line} | color=#666666")
        
        # 链接
        print("-- ---")
        print(f"-- Open on HuggingFace | href={paper_url}")
        if arxiv_url:
            print(f"-- Open on arXiv | href={arxiv_url}")
            print(f"-- Copy arXiv ID | bash='echo {arxiv_id} | pbcopy' terminal=false")
        
        #print("---")
    
    # 如果论文数量超过20篇，显示提示
    if paper_count > 10:
        print(f"... and {paper_count - 10} more papers")
        print("---")
    
    # 底部菜单项
    print("Refresh | refresh=true")
    print("Open All Papers | href=https://huggingface.co/papers")
    
    # 历史日期快速访问
    print("---")
    print("Recent Days")
    for days_ago in range(1, 4):
        date = datetime.now().astimezone(timezone.utc)
        date = datetime(date.year, date.month, date.day - days_ago)
        date_str = date.strftime("%Y-%m-%d")
        weekday = date.strftime("%A")
        print(f"-- {weekday} ({date_str}) | href=https://huggingface.co/papers?date={date_str}")

if __name__ == "__main__":
    main()
