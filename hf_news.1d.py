#!/usr/bin/env python3
# <xbar.title>Hugging Face Datasets</xbar.title>
# <xbar.version>v1.1</xbar.version>
# <xbar.author>MichaelPeng (modified)</xbar.author>
# <xbar.desc>Track new datasets on Hugging Face Hub, showing top 5 by likes and downloads.</xbar.desc>
# <xbar.dependencies>python3,requests</xbar.dependencies>

import requests
import sys
from datetime import datetime, timedelta, timezone

# Configuration
BASE_URL = "https://huggingface.co/api/datasets"
DAYS_TO_FETCH = 7  # 获取最近7天的数据集
LIMIT = 1000
TOP_N = 5 # 在每个类别中显示前N个数据集


def get_recent_datasets(n_days):
    """获取最近 n 天的数据集"""
    params = {
        "limit": LIMIT,
        "sort": "createdAt",
        "direction": "-1",
        "full": "true",
    }
    
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=n_days)
    datasets = []
    url = BASE_URL
    
    try:
        while url:
            r = requests.get(url, params=params, timeout=10)
            r.raise_for_status()
            data = r.json()
            
            stop = False
            for ds in data:
                if "createdAt" in ds:
                    created = datetime.fromisoformat(ds["createdAt"].replace("Z", "+00:00"))
                    if created >= cutoff_date:
                        datasets.append(ds)
                    else:
                        stop = True
                        break
            
            if stop:
                break
            
            if "Link" in r.headers and 'rel="next"' in r.headers["Link"]:
                url = r.headers["Link"].split(";")[0].strip("<>")
                params = {}
            else:
                url = None
                
    except Exception as e:
        return None, str(e)
    
    return datasets, None


def format_time_ago(created_str):
    """格式化时间显示"""
    try:
        created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        delta = now - created
        
        hours = delta.total_seconds() / 3600
        if hours < 1:
            minutes = int(delta.total_seconds() / 60)
            return f"{minutes}m ago"
        elif hours < 24:
            return f"{int(hours)}h ago"
        else:
            days = delta.days
            return f"{days}d ago"
    except:
        return ""


def sanitize_text(text):
    """清理文本用于 xbar 显示"""
    if not text:
        return ""
    text = str(text).replace("|", "–")
    if len(text) > 50:
        text = text[:47] + "..."
    return text


def format_number(num):
    """格式化数字"""
    if num is None or num == 0:
        return ""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    else:
        return str(num)


def format_downloads(downloads):
    """格式化下载数"""
    formatted = format_number(downloads)
    return f"↓{formatted}" if formatted else ""


def format_likes(likes):
    """格式化点赞数"""
    formatted = format_number(likes)
    return f"❤️{formatted}" if formatted else ""


def print_dataset_section(title, dataset_list):
    """打印一个数据集部分（例如 Top 5 Likes）"""
    print(title)
    if not dataset_list:
        print(f"No datasets in this category | color=gray")
        return
        
    for ds in dataset_list:
        dataset_id = ds.get("id", "Unknown")
        dataset_name = sanitize_text(dataset_id.split("/")[-1] if "/" in dataset_id else dataset_id)
        author = sanitize_text(dataset_id.split("/")[0] if "/" in dataset_id else "")
        
        time_ago = format_time_ago(ds.get("createdAt", ""))
        downloads = format_downloads(ds.get("downloads", 0))
        likes = format_likes(ds.get("likes", 0))
        
        display_parts = [dataset_name]
        if author:
            display_parts.append(f"by {author}")
        if time_ago:
            display_parts.append(time_ago)
        
        stats = []
        if downloads:
            stats.append(downloads)
        if likes:
            stats.append(likes)
        if stats:
            display_parts.append(" ".join(stats))
        
        display_text = " • ".join(display_parts)
        dataset_url = f"https://huggingface.co/datasets/{dataset_id}"
        
        print(f"{display_text} | href={dataset_url}")


def main():
    datasets, error = get_recent_datasets(DAYS_TO_FETCH)
    
    if error:
        print("🤗 Error")
        print("---")
        print(f"Failed to fetch datasets | color=red")
        print(f"Error: {error} | color=red")
        print(f"Retry | refresh=true")
        sys.exit(1)
    
    if not datasets:
        print("🤗 0 new")
        print("---")
        print(f"No new datasets in the last {DAYS_TO_FETCH} days")
        print(f"Refresh | refresh=true")
        return
    
    # 分别获取点赞和下载的Top N
    top_likes = sorted(datasets, key=lambda x: x.get("likes", 0), reverse=True)[:TOP_N]
    top_downloads = sorted(datasets, key=lambda x: x.get("downloads", 0), reverse=True)[:TOP_N]
    
    count = len(datasets)
    print(f"🤗 {count} new")
    
    print("---")
    
    # 显示点赞Top 5
    print_dataset_section(f"Top {TOP_N} by Likes ❤️", top_likes)
    
    print("---")
    
    # 显示下载Top 5
    print_dataset_section(f"Top {TOP_N} by Downloads ↓", top_downloads)

    # 底部菜单
    print("---")
    print(f"Refresh | refresh=true")
    print(f"Browse All Datasets | href=https://huggingface.co/datasets")
    print(f"Found {count} new datasets in last {DAYS_TO_FETCH} days | color=gray")


if __name__ == "__main__":
    main()