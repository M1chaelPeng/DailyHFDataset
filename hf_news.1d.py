#!/usr/bin/env python3
# <xbar.title>Hugging Face Datasets</xbar.title>
# <xbar.version>v2.1</xbar.version>
# <xbar.author>MichaelPeng</xbar.author>
# <xbar.desc>Track new datasets on Hugging Face Hub with stats</xbar.desc>
# <xbar.dependencies>python3,requests</xbar.dependencies>

import requests
import sys
import json
from datetime import datetime, timedelta, timezone

# Configuration
BASE_URL = "https://huggingface.co/api/datasets"
DAYS_TO_FETCH = 7  # 显示最近7天的数据集
LIMIT = 1000
MAX_DISPLAY = 20  # 菜单中最多显示的数据集数量

# 图标和颜色配置
ICONS = {
    'new': '🆕',
    'hot': '🔥',
    'trending': '📈',
    'dataset': '📊',
    'downloads': '⬇️',
    'likes': '❤️',
    'author': '👤',
    'time': '🕐',
    'size': '💾',
    'tag': '🏷️',
    'info': 'ℹ️',
    'link': '🔗',
    'refresh': '🔄',
    'browse': '🌐',
    'private': '🔒',
    'public': '🔓',
    'star': '⭐',
    'fork': '🔱'
}

COLORS = {
    'title': '#000000',
    'subtitle': '#666666',
    'accent': '#FF9800',
    'success': '#4CAF50',
    'error': '#F44336',
    'link': '#2196F3',
    'muted': '#9E9E9E',
    'likes': '#E91E63',
    'downloads': '#00BCD4'
}


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
            
            # 翻页处理
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
            return f"{minutes} minutes ago"
        elif hours < 24:
            return f"{int(hours)} hours ago"
        elif delta.days == 1:
            return "1 day ago"
        elif delta.days < 7:
            return f"{delta.days} days ago"
        elif delta.days < 30:
            weeks = delta.days // 7
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
        else:
            return created.strftime("%Y-%m-%d")
    except:
        return "Unknown"


def format_time_short(created_str):
    """格式化时间显示（简短版）"""
    try:
        created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        delta = now - created
        
        hours = delta.total_seconds() / 3600
        if hours < 1:
            minutes = int(delta.total_seconds() / 60)
            return f"{minutes}m"
        elif hours < 24:
            return f"{int(hours)}h"
        else:
            return f"{delta.days}d"
    except:
        return ""


def sanitize_text(text, max_length=50):
    """清理文本用于 xbar 显示"""
    if not text:
        return ""
    text = str(text).replace("|", "–").replace("\n", " ")
    if len(text) > max_length:
        text = text[:max_length-3] + "..."
    return text


def format_number(num):
    """格式化数字"""
    if num is None:
        return "0"
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    else:
        return str(num)


def get_dataset_emoji(dataset):
    """根据数据集特征返回合适的 emoji"""
    likes = dataset.get("likes", 0)
    downloads = dataset.get("downloads", 0)
    created_str = dataset.get("createdAt", "")
    
    # 检查是否是新数据集（24小时内）
    try:
        created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        hours_old = (now - created).total_seconds() / 3600
        
        if hours_old < 24:
            return ICONS['new']
        elif likes > 10 or downloads > 100:
            return ICONS['hot']
        elif likes > 5 or downloads > 50:
            return ICONS['trending']
    except:
        pass
    
    return ICONS['dataset']


def pad_string(text, length):
    """填充字符串到指定长度（支持中文）"""
    text_len = len(text.encode('gbk', errors='ignore'))
    if text_len < length:
        return text + ' ' * (length - text_len)
    return text


def format_stats_compact(likes, downloads):
    """紧凑格式化统计数据"""
    parts = []
    if likes > 0:
        parts.append(f"❤️{format_number(likes)}")
    if downloads > 0:
        parts.append(f"⬇️{format_number(downloads)}")
    
    if not parts:
        return "—"
    
    return " ".join(parts)


def print_dataset_details(dataset):
    """打印数据集详细信息的子菜单"""
    dataset_id = dataset.get("id", "Unknown")
    dataset_url = f"https://huggingface.co/datasets/{dataset_id}"
    
    # 基本信息
    print(f"--{ICONS['info']} Dataset Details | color={COLORS['muted']}")
    print(f"----Repository: {dataset_id} | font=Monaco size=11")
    print(f"----Created: {format_time_ago(dataset.get('createdAt', ''))} | font=Monaco size=11")
    
    # 是否私有
    is_private = dataset.get("private", False)
    print(f"----Status: {ICONS['private' if is_private else 'public']} {'Private' if is_private else 'Public'} | font=Monaco size=11")
    
    # 标签
    tags = dataset.get("tags", [])
    if tags:
        print(f"--{ICONS['tag']} Tags ({len(tags)}) | color={COLORS['muted']}")
        for tag in tags[:10]:  # 显示最多10个标签
            print(f"----{sanitize_text(tag, 30)} | font=Monaco size=11")
    
    # 描述
    description = dataset.get("description", "")
    if description:
        print(f"--{ICONS['info']} Description | color={COLORS['muted']}")
        # 将描述分成多行显示
        desc_lines = sanitize_text(description, 300).split(". ")
        for line in desc_lines[:5]:  # 显示最多5行
            if line.strip():
                print(f"----{line.strip()}. | font=Monaco size=11")
    
    # 快捷操作
    print(f"--{ICONS['link']} Actions | color={COLORS['muted']}")
    print(f"----Open in Browser | href={dataset_url} color={COLORS['link']}")
    print(f"----View Dataset Viewer | href={dataset_url}/viewer color={COLORS['link']}")
    print(f"----View Files | href={dataset_url}/tree/main color={COLORS['link']}")
    print(f"----Copy URL | bash='echo \"{dataset_url}\" | pbcopy' terminal=false")
    print(f"----Copy ID | bash='echo \"{dataset_id}\" | pbcopy' terminal=false")


def categorize_datasets(datasets):
    """将数据集按时间分类"""
    categories = {
        'today': [],
        'yesterday': [],
        'this_week': [],
        'older': []
    }
    
    now = datetime.now(timezone.utc)
    today = now.date()
    yesterday = today - timedelta(days=1)
    week_ago = today - timedelta(days=7)
    
    for ds in datasets:
        created_str = ds.get("createdAt", "")
        try:
            created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
            created_date = created.date()
            
            if created_date == today:
                categories['today'].append(ds)
            elif created_date == yesterday:
                categories['yesterday'].append(ds)
            elif created_date > week_ago:
                categories['this_week'].append(ds)
            else:
                categories['older'].append(ds)
        except:
            categories['older'].append(ds)
    
    return categories


def main():
    datasets, error = get_recent_datasets(DAYS_TO_FETCH)
    
    if error:
        print(f"{ICONS['dataset']} Error")
        print("---")
        print(f"Failed to fetch datasets | color={COLORS['error']}")
        print(f"Error: {error} | color={COLORS['error']} font=Monaco size=11")
        print("---")
        print(f"{ICONS['refresh']} Retry | refresh=true")
        sys.exit(1)
    
    if not datasets:
        print(f"{ICONS['dataset']} No new datasets")
        print("---")
        print(f"No datasets in last {DAYS_TO_FETCH} days | color={COLORS['muted']}")
        print(f"{ICONS['refresh']} Refresh | refresh=true")
        return
    
    # 按时间分类数据集
    categorized = categorize_datasets(datasets)
    
    # 显示菜单栏标题
    total_count = len(datasets)
    today_count = len(categorized['today'])
    
    if today_count > 0:
        print(f"{ICONS['new']} {today_count} today • {total_count} total")
    else:
        print(f"{ICONS['dataset']} {total_count} datasets")
    
    print("---")
    
    # 添加统计标题栏
    print(f"DATASETS {'·'*20} STATS {'·'*8} TIME | font=Monaco size=10 color={COLORS['muted']}")
    print("---")
    
    # 显示不同时间段的数据集
    display_count = 0
    
    # 今天的数据集
    if categorized['today']:
        print(f"{ICONS['new']} Today — {len(categorized['today'])} datasets | color={COLORS['accent']}")
        for ds in sorted(categorized['today'], key=lambda x: x.get('likes', 0), reverse=True)[:7]:
            display_count += 1
            print_dataset_item(ds, display_count)
        if categorized['today']:
            print("---")
    
    # 昨天的数据集
    if categorized['yesterday'] and display_count < MAX_DISPLAY:
        print(f"{ICONS['time']} Yesterday — {len(categorized['yesterday'])} datasets | color={COLORS['subtitle']}")
        for ds in sorted(categorized['yesterday'], key=lambda x: x.get('likes', 0), reverse=True)[:6]:
            display_count += 1
            if display_count > MAX_DISPLAY:
                break
            print_dataset_item(ds, display_count)
        if categorized['yesterday']:
            print("---")
    
    # 本周的数据集
    if categorized['this_week'] and display_count < MAX_DISPLAY:
        print(f"{ICONS['trending']} This Week — {len(categorized['this_week'])} datasets | color={COLORS['subtitle']}")
        for ds in sorted(categorized['this_week'], key=lambda x: x.get('likes', 0), reverse=True)[:10]:
            display_count += 1
            if display_count > MAX_DISPLAY:
                break
            print_dataset_item(ds, display_count)
    
    # 底部菜单
    print("---")
    print(f"{ICONS['refresh']} Refresh | refresh=true")
    print(f"{ICONS['browse']} Browse All Datasets | href=https://huggingface.co/datasets color={COLORS['link']}")
    print(f"{ICONS['trending']} Trending Datasets | href=https://huggingface.co/datasets?sort=trending color={COLORS['link']}")
    print("---")
    
    # 总结统计
    total_likes = sum(ds.get('likes', 0) for ds in datasets)
    total_downloads = sum(ds.get('downloads', 0) for ds in datasets)
    print(f"Summary: {total_count} datasets • {format_number(total_likes)} likes • {format_number(total_downloads)} downloads | color={COLORS['muted']} size=10")
    print(f"Last update: {datetime.now().strftime('%Y-%m-%d %H:%M')} | color={COLORS['muted']} size=10")


def print_dataset_item(ds, number):
    """打印单个数据集项目，在主菜单显示统计数据"""
    dataset_id = ds.get("id", "Unknown")
    dataset_name = dataset_id.split("/")[-1] if "/" in dataset_id else dataset_id
    author = dataset_id.split("/")[0] if "/" in dataset_id else ""
    
    # 获取统计数据
    downloads = ds.get("downloads", 0)
    likes = ds.get("likes", 0)
    time_str = format_time_short(ds.get("createdAt", ""))
    
    # 获取合适的emoji
    emoji = get_dataset_emoji(ds)
    
    # 格式化名称（固定长度）
    name_display = sanitize_text(dataset_name, 25)
    author_display = sanitize_text(author, 15) if author else "anonymous"
    
    # 构建显示文本，使用固定宽度布局
    # 使用 | 分隔不同部分，让显示更整齐
    dataset_url = f"https://huggingface.co/datasets/{dataset_id}"
    
    # 主显示行 - 包含所有信息
    # 格式: [emoji] 名称 | 作者 | 统计 | 时间
    name_part = f"{emoji} {name_display:<25}"
    author_part = f"@{author_display:<15}"
    
    # 统计信息部分
    stats_parts = []
    if likes > 0:
        stats_parts.append(f"❤️ {format_number(likes):>5}")
    else:
        stats_parts.append(f"{'':>7}")  # 占位
        
    if downloads > 0:
        stats_parts.append(f"⬇️ {format_number(downloads):>5}")
    else:
        stats_parts.append(f"{'':>7}")  # 占位
    
    stats_display = " ".join(stats_parts)
    
    # 时间部分
    time_display = f"[{time_str:>3}]" if time_str else "[   ]"
    
    # 组合所有部分
    full_display = f"{name_part} • {author_part} • {stats_display} • {time_display}"
    
    # 主菜单项 - 使用等宽字体
    print(f"{full_display} | href={dataset_url} font=Monaco size=12")
    
    # 添加交替显示的详细信息（按住Option键查看）
    if author:
        detail_text = f"  📝 {dataset_id} - Created {format_time_ago(ds.get('createdAt', ''))}"
        print(f"{detail_text} | alternate=true font=Monaco size=11 color={COLORS['subtitle']}")
    
    # 添加子菜单详细信息
    print_dataset_details(ds)


def print_compact_header():
    """打印紧凑的表头"""
    header = "Dataset Name" + " " * 15 + "Author" + " " * 10 + "Stats" + " " * 10 + "Time"
    print(f"{header} | font=Monaco size=10 color={COLORS['muted']}")
    print(f"{'─' * 70} | font=Monaco size=10 color={COLORS['muted']}")


if __name__ == "__main__":
    main()
