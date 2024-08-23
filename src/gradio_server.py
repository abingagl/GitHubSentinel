import gradio as gr  # 导入Gradio库用于创建GUI

from config import Config  # 导入配置管理模块
from github_client import GitHubClient  # 导入用于GitHub API操作的客户端
from report_generator import ReportGenerator  # 导入报告生成器模块
from llm import LLM  # 导入处理语言模型的LLM类
from subscription_manager import SubscriptionManager  # 导入订阅管理器
from logger import LOG  # 导入日志记录器

# 初始化各个组件
config = Config()
github_client = GitHubClient(config.github_token)
llm = LLM()
report_generator = ReportGenerator(llm)
subscription_manager = SubscriptionManager(config.subscriptions_file)

def export_progress_by_date_range(repo: str, days: int) -> tuple[str, str]:
    """
    导出并生成指定时间范围内项目的进展报告。

    :param repo: GitHub项目的名称或ID
    :param days: 时间范围，以天为单位
    :return: 包含报告内容和文件路径的元组
    """
    # 导出原始数据文件
    raw_file_path = github_client.export_progress_by_date_range(repo, days)
    
    # 生成报告
    report, report_file_path = report_generator.generate_report_by_date_range(raw_file_path, days)
    
    return report, report_file_path

# 创建Gradio界面
with gr.Blocks() as demo:
    gr.Markdown("# GitHub Sentinel\n## 项目进展报告生成工具\n\n请根据以下选项生成GitHub项目的进展报告。")

    with gr.Row():
        with gr.Column(scale=1, min_width=300, elem_id="left_column"):
            repo = gr.Dropdown(
                choices=subscription_manager.list_subscriptions(),  # 填充下拉菜单选项
                label="选择项目", 
                info="选择一个已订阅的GitHub项目来生成进展报告"
            )
            days = gr.Slider(
                value=2, 
                minimum=1, 
                maximum=7, 
                step=1, 
                label="报告周期",
                info="选择生成项目过去一段时间的进展，单位：天"
            )
            generate_button = gr.Button("生成报告", elem_id="generate_button")

        with gr.Column(scale=2, min_width=600, elem_id="right_column"):
            report_output = gr.Markdown(label="进展报告")  # 输出Markdown文本
            file_output = gr.File(label="下载报告")  # 输出报告文件下载链接

    generate_button.click(
        fn=export_progress_by_date_range, 
        inputs=[repo, days], 
        outputs=[report_output, file_output]
    )

# 启动Gradio界面
if __name__ == "__main__":
    demo.launch(
        share=True,  # 允许公共访问
        server_name="0.0.0.0"  # 绑定所有IP地址
    )
