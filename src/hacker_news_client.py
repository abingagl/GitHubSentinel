import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from logger import LOG  # 假设你有一个自定义的日志模块

class HackerNewsClient:
    def __init__(self, config):
        self.base_url = config.get('base_url', 'https://news.ycombinator.com/')
        self.output_dir = config.get('output_dir', 'hacker_news')
    
    def fetch_top_stories(self):
        LOG.debug(f"[Fetching top stories from {self.base_url}]")
        response = requests.get(self.base_url)
        response.raise_for_status()  # 如果请求失败，抛出异常

        soup = BeautifulSoup(response.text, 'html.parser')
        stories = soup.find_all('tr', class_='athing')

        top_stories = []
        for story in stories:
            title_tag = story.find('span', class_='titleline').find('a')
            if title_tag:
                title = title_tag.text
                link = title_tag['href']
                top_stories.append({'title': title, 'link': link})

        LOG.debug(f"[Fetched {len(top_stories)} stories]")
        return top_stories

    def export_daily_stories(self):
        LOG.debug("[Preparing to export daily Hacker News stories]")
        today = datetime.now().date().isoformat()
        stories = self.fetch_top_stories()

        os.makedirs(self.output_dir, exist_ok=True)
        file_path = os.path.join(self.output_dir, f'hacker_news_{today}.md')

        with open(file_path, 'w') as file:
            file.write(f"# Hacker News for ({today})\n\n")
            for idx, story in enumerate(stories, start=1):
                file.write(f"{idx}. {story['title']}\n")
                file.write(f"   Link: {story['link']}\n")

        LOG.info(f"[Hacker News daily stories file generated: {file_path}]")
        return file_path

if __name__ == "__main__":
    client = HackerNewsClient()
    client.export_daily_stories()