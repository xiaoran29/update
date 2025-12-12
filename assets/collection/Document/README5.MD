📺 直播源聚合处理工具 v2.00

🎯 项目概述

LiveSource-Collector 是一个功能强大的直播源处理系统，专门用于从多个网络源收集、整理、分类和去重电视直播频道数据。通过智能算法和多重质量控制机制，系统能自动生成多种格式的输出文件，适用于各种播放器环境。

🌟 核心亮点

🚀 高性能处理

· ⚡ 实时处理：支持大规模直播源数据的快速处理
· 🔄 智能去重：四级去重机制确保数据纯净度
· 📊 自动分类：50+个精准分类，覆盖全场景需求

🛡️ 质量保障

· ✅ 多重过滤：黑名单、协议过滤、响应时间筛选
· 🔍 智能纠错：自动修正频道名称错误
· ⭐ 手工优化：高质量源手工维护，确保核心频道稳定

🔄 灵活输出

· 📱 多版本适配：完整版、精简版、定制版满足不同需求
· 🎵 格式兼容：TXT和M3U双格式，兼容主流播放器
· 🌐 网页集成：体育赛事独立网页，一键复制便捷使用

📋 功能特性

特性 描述 优势
智能分类 基于词典的50+分类系统 精准分类，易于管理
自动去重 全局URL去重+分类内去重 减少重复，提升质量
质量筛选 响应时间+白名单优化 确保源稳定可用
格式转换 M3U/TXT自动互转 兼容各种播放器
实时更新 动态日期变量处理 自动获取最新源
错误恢复 重试机制+错误处理 提高处理成功率

🏗️ 系统架构

数据处理流程

```
输入源 → 数据获取 → 格式转换 → 名称标准化 → 
智能分类 → 质量过滤 → 去重处理 → 多格式输出
```

核心技术栈

· Python 3.6+：核心处理引擎
· 正则表达式：频道名称提取和标准化
· HTTP请求：网络数据采集
· 集合运算：高效去重算法
· 文件操作：多格式输出管理

📁 详细目录结构

输入目录 (assets/livesource/)

```
assets/livesource/
├── blacklist/                    # 质量控制系统
│   ├── blacklist_auto.txt       # 自动收集的无效源
│   ├── blacklist_manual.txt     # 手动维护的黑名单
│   └── whitelist_auto.txt       # 高速响应白名单
├── 主频道/                      # 主要频道分类词典
│   ├── 央视.txt                # 央视频道标准名称
│   ├── 卫视.txt                # 卫视频道标准名称
│   ├── 体育.txt                # 体育类频道
│   ├── 电影.txt                # 电影类频道
│   ├── 新闻.txt                # 新闻类频道
│   └── ... (共23个分类)
├── 地方台/                      # 地方频道词典
│   ├── 北京.txt
│   ├── 上海.txt
│   ├── 广东.txt
│   ├── 江苏.txt
│   ├── 浙江.txt
│   └── ... (共27个省份)
├── 手工区/                      # 手工维护高质量源
│   ├── 优质央视.txt
│   ├── 优质卫视.txt
│   ├── 港澳台.txt
│   ├── AKTV.txt
│   ├── 今日推荐.txt
│   └── about.txt
├── logo.txt                     # 频道Logo映射
├── urls-daily.txt               # 每日更新源列表
└── corrections_name.txt         # 频道名称修正词典
```

输出目录 (output/)

```
output/
├── full.txt                     # 完整版：所有分类
├── full.m3u                     # 完整版M3U格式
├── lite.txt                     # 精简版：主要频道
├── lite.m3u                     # 精简版M3U格式
├── custom.txt                   # 定制版：精选分类
├── custom.m3u                   # 定制版M3U格式
├── others.txt                   # 未分类频道
├── tiyu.txt                     # 体育赛事列表
├── tiyu.html                    # 体育赛事网页版
```

🚀 快速开始指南

环境准备

```bash
# 1. 安装Python 3.6或更高版本
python --version

# 2. 安装依赖库
pip install opencc

# 3. 克隆或下载项目
git clone [项目地址]
cd LiveSource-Collector
```

基础配置

1. 配置数据源：编辑 assets/livesource/urls-daily.txt，添加直播源URL
2. 更新分类词典：根据需要修改分类词典文件
3. 设置黑名单：添加已知无效源到黑名单文件

运行脚本

```bash
# 直接运行主脚本
python livesource.py

# 或指定输出目录（可选）
python livesource.py --output /path/to/output
```

预期输出

```
🚀 开始处理直播源...
📋 加载频道字典...
✅ 字典加载完成:
   央视: 45 条
   卫视: 32 条
   地方台: 31个分类已加载
   港澳台: 3个分类已加载
   其他分类: 27个分类已加载
🔴 黑名单统计信息:
   自动维护: 120 条
   手动维护: 36 条
   合并去重: 156 条
📡 处理URL: http://example.com/live.m3u
✅ 处理完成: 1285 个有效频道
📊 去重统计信息:
   处理的唯一URL数: 1234
   黑名单URL数: 156
   总处理URL数: 1390
   🔄 去重率: 11.2%
⏱️ 执行时间: 2分15秒
```

🔧 核心功能详解

1. 智能分类系统

分类逻辑：

```python
if "CCTV" in channel_name:
    # 归入央视频道
    yangshi_lines.append(processed_line)
elif channel_name in weishi_dictionary:
    # 归入卫视频道
    weishi_lines.append(processed_line)
elif channel_name in beijing_dictionary:
    # 归入北京地方台
    beijing_lines.append(processed_line)
# ... 更多分类判断
```

支持的主要分类：

· 央视频道：CCTV系列（含4K/8K超高清）
· 卫视频道：各省卫视（湖南、浙江、江苏等）
· 地方频道：31个省/直辖市/自治区
· 港澳台频道：香港、澳门、台湾地区频道
· 内容分类：电影、电视剧、体育、新闻等23类
· 直播平台：虎牙、斗鱼等游戏直播平台

2. 去重与质量控制

四级去重机制：

```python
# 1. 全局URL去重
if channel_address in processed_urls:
    return  # 跳过已处理URL
processed_urls.add(channel_address)

# 2. 黑名单过滤
if channel_address in combined_blacklist:
    return  # 跳过黑名单URL

# 3. 分类内去重
if not check_url_existence_in_category(url, category_list):
    category_list.append(line)

# 4. 协议过滤
if any(protocol in url for protocol in ['tvbus://', '/udp/']):
    return  # 跳过不稳定协议
```

3. 频道名称标准化

清理规则示例：

```python
# 移除冗余标识
removal_list = ["_电信", "高清", "超清", "HD", "4K", "频道", "台"]
for item in removal_list:
    channel_name = channel_name.replace(item, "")

# 繁简转换
channel_name = traditional_to_simplified(channel_name)

# 特殊处理：CCTV频道
if "CCTV" in channel_name:
    channel_name = re.sub(r'CCTV(\d+).*', r'CCTV\1', channel_name)
```

4. 体育赛事特殊处理

日期标准化：

```python
def normalize_date_to_md(text):
    """
    统一日期格式为 MM-DD
    输入: "01/01 比赛", "2024-01-01 比赛", "1月1日 比赛"
    输出: "1-1 比赛"
    """
    # 正则匹配和处理逻辑
    pass
```

⚙️ 配置文件详解

1. 数据源配置 (urls-daily.txt)

```
# 格式：每行一个URL，支持日期变量
http://example.com/live-{MMdd}.m3u     # 当月当天
http://example.com/live-{MMdd-1}.txt   # 前一天
https://raw.githubusercontent.com/xxx/xxx/main/live.m3u
```

2. 黑名单配置

自动黑名单格式：

```
响应时间(ms),URL
1234,http://example.com/bad1.m3u
2345,http://example.com/bad2.txt
```

手动黑名单格式：

```
# 每行一个URL
http://example.com/永久无效源1.m3u
http://example.com/永久无效源2.txt
```

3. 频道Logo映射 (logo.txt)

```
频道名称,Logo URL
CCTV1,http://example.com/logos/cctv1.png
湖南卫视,http://example.com/logos/hunan.png
```

4. 频道名称修正 (corrections_name.txt)

```
# 格式：正确名称,错误名称1,错误名称2,...
CCTV1,CCTV-1,CCTV1高清,CCTV1HD
湖南卫视,湖南电视台,湖南卫视高清
```

📊 输出格式说明

1. TXT格式输出

```
# 分类标题
央视频道,#genre#
# 频道列表
CCTV1,http://example.com/cctv1.m3u8
CCTV2,http://example.com/cctv2.m3u8

卫视频道,#genre#
湖南卫视,http://example.com/hunan.m3u8
浙江卫视,http://example.com/zhejiang.m3u8
```

2. M3U格式输出

```
#EXTM3U x-tvg-url="https://live.fanmingming.cn/e.xml"
#EXTINF:-1 tvg-id="CCTV1" tvg-name="CCTV1" tvg-logo="http://example.com/logo/cctv1.png" group-title="央视频道",CCTV1
http://example.com/cctv1.m3u8
```

3. 体育赛事HTML输出

```html
<!DOCTYPE html>
<html>
<head>
    <title>最新体育赛事</title>
    <style>/* 样式代码 */</style>
</head>
<body>
    <div class="item">
        <div class="title">🕒 1-1 NBA常规赛</div>
        <div class="url-wrapper">
            <div class="url">http://example.com/sports1.m3u8</div>
            <button class="copy-btn">复制</button>
        </div>
    </div>
</body>
</html>
```

🔄 自动化部署

Linux/Mac定时任务

```bash
# 编辑crontab
crontab -e

# 每天凌晨3点执行
0 3 * * * cd /path/to/LiveSource-Collector && python livesource.py >> /var/log/livesource.log 2>&1

# 每小时执行（测试用）
0 * * * * cd /path/to/LiveSource-Collector && python livesource.py
```

Windows计划任务

1. 创建批处理文件 update_livesource.bat：

```batch
@echo off
cd /d "C:\path\to\LiveSource-Collector"
python livesource.py
pause
```

1. 使用任务计划程序：
   · 打开"任务计划程序"
   · 创建基本任务
   · 设置每日触发时间
   · 指向批处理文件

Docker部署（可选）

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install opencc
CMD ["python", "livesource.py"]
```

🧪 测试与验证

测试数据准备

```python
# 创建测试配置文件
test_urls = [
    "http://example.com/test1.m3u",
    "http://example.com/test2.txt"
]

# 运行测试
python livesource.py --test --input test_urls.txt
```

验证输出

```bash
# 检查文件完整性
ls -la output/

# 检查文件行数
wc -l output/*.txt

# 检查M3U格式
head -n 20 output/full.m3u
```

🚨 故障排除

常见问题及解决方案

问题 可能原因 解决方案
URL获取失败 网络连接问题 检查网络，增加重试次数
内存不足 处理数据量过大 分批处理，优化词典大小
输出文件为空 源URL无效 检查urls-daily.txt配置
分类错误 词典不完整 更新分类词典文件
执行时间过长 网络延迟高 调整超时时间，使用本地缓存

调试模式

```bash
# 启用详细日志
python livesource.py --verbose

# 仅处理特定URL
python livesource.py --url http://example.com/test.m3u

# 输出调试信息到文件
python livesource.py --debug 2> debug.log
```

📈 性能优化建议

1. 网络优化

· 设置合理的超时时间：避免长时间等待无效响应
· 使用并发请求：并行处理多个URL源（需要代码调整）
· 启用本地缓存：缓存已处理的URL，减少重复请求

2. 内存优化

· 分批处理：大文件分块读取和处理
· 及时释放内存：处理完成后清理临时数据
· 使用生成器：流式处理大文件

3. 存储优化

· 定期清理旧文件：自动删除过期的输出文件
· 压缩输出：可选生成压缩格式输出
· 增量更新：仅处理变更的源

🔍 高级功能

自定义分类规则

```python
# 在脚本中添加自定义分类规则
custom_rules = {
    "游戏直播": ["英雄联盟", "王者荣耀", "原神"],
    "教育频道": ["学而思", "新东方", "跟谁学"]
}
```

质量评分系统

```python
def calculate_quality_score(url, response_time, stability):
    """
    计算直播源质量评分
    参数：
        url: 直播源URL
        response_time: 响应时间(ms)
        stability: 稳定性评分(0-100)
    返回：综合质量评分(0-100)
    """
    score = (1000 - min(response_time, 1000)) / 10
    score += stability * 0.9
    return min(score, 100)
```

多语言支持

```python
# 支持多语言频道名称
language_support = {
    "zh-CN": "央视一套",
    "zh-TW": "央視一套",
    "en-US": "CCTV1",
    "ja-JP": "CCTV1"
}
```

🤝 贡献指南

代码贡献

1. Fork项目仓库
2. 创建功能分支 (git checkout -b feature/AmazingFeature)
3. 提交更改 (git commit -m 'Add some AmazingFeature')
4. 推送到分支 (git push origin feature/AmazingFeature)
5. 开启Pull Request

数据贡献

· 添加新源：更新 urls-daily.txt
· 完善分类：更新分类词典文件
· 修正名称：更新 corrections_name.txt
· 提供Logo：更新 logo.txt

问题反馈

· Bug报告：在Issues中描述问题，提供复现步骤
· 功能建议：描述需求场景和预期效果
· 文档改进：修正文档错误或补充说明

📚 相关资源

工具推荐

· 播放器：VLC、PotPlayer、Kodi
· 测试工具：ffmpeg、curl、wget
· 编辑工具：Notepad++、VS Code、Sublime Text

学习资源

· M3U格式规范
· IPTV技术文档
· Python网络编程

社区支持

· GitHub Issues：技术问题讨论
· 论坛社区：相关技术论坛
· QQ群/微信群：用户交流群

📄 许可证

本项目采用 MIT许可证 - 查看 LICENSE 文件了解详情。

📞 联系方式

· 项目维护者：潇然
· 问题反馈：GitHub Issues
· 邮箱：your-email@example.com
· 文档：项目Wiki

🎉 致谢

感谢所有为项目做出贡献的开发者、测试者和用户！

---

最后更新：2024年1月
版本：v2.00
状态：稳定维护中

提示：直播源具有时效性，建议定期更新获取最新可用源。使用过程中请遵守相关法律法规，尊重版权。