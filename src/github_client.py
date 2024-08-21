# src/github_client.py

import requests  # 导入requests库用于HTTP请求
from datetime import datetime, date, timedelta, timezone  # 导入日期处理模块
import os  # 导入os模块用于文件和目录操作
from logger import LOG  # 导入日志模块

class GitHubClient:
    def __init__(self, token):
        self.token = token  # GitHub API令牌
        self.headers = {'Authorization': f'token {self.token}'}  # 设置HTTP头部认证信息

    def fetch_updates(self, repo, since=None, until=None):
        # 获取指定仓库的更新，可以指定开始和结束日期
        updates = {
            'commits': self.fetch_commits_wrapper(repo, since, until),  # 获取提交记录
            'issues': self.fetch_issues_wrapper(repo, since, until),  # 获取问题
            'pull_requests': self.fetch_pull_requests_wrapper(repo, since, until)  # 获取拉取请求
        }
        return updates

    def fetch_commits(self, repo, since=None, until=None):
        url = f'https://api.github.com/repos/{repo}/commits'  # 构建获取提交的API URL
        params = {}
        if since:
            params['since'] = since  # 如果指定了开始日期，添加到参数中
        if until:
            params['until'] = until  # 如果指定了结束日期，添加到参数中

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()  # 检查请求是否成功
        return response.json()  # 返回JSON格式的数据

    def fetch_issues(self, repo, since=None, until=None):
        url = f'https://api.github.com/repos/{repo}/issues'  # 构建获取问题的API URL
        params = {
            'state': 'closed',  # 仅获取已关闭的问题
            'since': since,
            'until': until
        }
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def fetch_pull_requests(self, repo, since=None, until=None):
        url = f'https://api.github.com/repos/{repo}/pulls'  # 构建获取拉取请求的API URL
        params = {
            'state': 'closed',  # 仅获取已合并的拉取请求
            'since': since,
            'until': until
        }
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def fetch_commits_wrapper(self, repo, since=None, until=None):
        commits = self.fetch_commits(repo, since, until)
        if since:
            since_date = datetime.fromisoformat(since.replace('Z', '+00:00')).astimezone(timezone.utc)
            commits = [cmt for cmt in commits if datetime.fromisoformat(cmt['commit']['committer']['date'].replace('Z', '+00:00')).astimezone(timezone.utc) >= since_date]
        if until:
            until_date = datetime.fromisoformat(until.replace('Z', '+00:00')).astimezone(timezone.utc)
            commits = [cmt for cmt in commits if datetime.fromisoformat(cmt['commit']['committer']['date'].replace('Z', '+00:00')).astimezone(timezone.utc) <= until_date]
        return commits
    
    def fetch_issues_wrapper(self, repo, since=None, until=None):
        issues = self.fetch_issues(repo, since, until)
        if until:
            until_date = datetime.fromisoformat(until.replace('Z', '+00:00')).astimezone(timezone.utc)
            issues = [issue for issue in issues if datetime.fromisoformat(issue['closed_at'].replace('Z', '+00:00')).astimezone(timezone.utc) <= until_date]
        return issues 

    def fetch_pull_requests_wrapper(self, repo, since=None, until=None):
        requests = self.fetch_pull_requests(repo, since, until)
        if since:
            since_date = datetime.fromisoformat(since.replace('Z', '+00:00')).astimezone(timezone.utc)
            requests = [pr for pr in requests if datetime.fromisoformat(pr['closed_at'].replace('Z', '+00:00')).astimezone(timezone.utc) >= since_date]
        if until:
            until_date = datetime.fromisoformat(until.replace('Z', '+00:00')).astimezone(timezone.utc)
            requests = [pr for pr in requests if datetime.fromisoformat(pr['closed_at'].replace('Z', '+00:00')).astimezone(timezone.utc) <= until_date]
        return requests 

    def export_daily_progress(self, repo):
        today = datetime.now().date().isoformat()  # 获取今天的日期
        updates = self.fetch_updates(repo, since=today)  # 获取今天的更新数据
        
        repo_dir = os.path.join('daily_progress', repo.replace("/", "_"))  # 构建存储路径
        os.makedirs(repo_dir, exist_ok=True)  # 确保目录存在
        
        file_path = os.path.join(repo_dir, f'{today}.md')  # 构建文件路径
        with open(file_path, 'w') as file:
            file.write(f"# Daily Progress for {repo} ({today})\n\n")
            file.write("\n## Issues Closed Today\n")
            for issue in updates['issues']:  # 写入今天关闭的问题
                file.write(f"- {issue['title']} #{issue['number']}\n")
        
        LOG.info(f"Exported daily progress to {file_path}")  # 记录日志
        return file_path

    def export_progress_by_date_range(self, repo, days):
        today = date.today()  # 获取当前日期
        since = today - timedelta(days=days)  # 计算开始日期
        
        updates = self.fetch_updates(repo, since=since.isoformat(), until=today.isoformat())  # 获取指定日期范围内的更新
        
        repo_dir = os.path.join('daily_progress', repo.replace("/", "_"))  # 构建目录路径
        os.makedirs(repo_dir, exist_ok=True)  # 确保目录存在
        
        # 更新文件名以包含日期范围
        date_str = f"{since}_to_{today}"
        file_path = os.path.join(repo_dir, f'{date_str}.md')  # 构建文件路径
        
        with open(file_path, 'w') as file:
            file.write(f"# Progress for {repo} ({since} to {today})\n\n")
            file.write(f"\n## Issues Closed in the Last {days} Days\n")
            for issue in updates['issues']:  # 写入在指定日期内关闭的问题
                file.write(f"- {issue['title']} #{issue['number']}\n")
        
        LOG.info(f"Exported time-range progress to {file_path}")  # 记录日志
        return file_path