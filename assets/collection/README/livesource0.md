IPTV直播源聚合处理工具 v0.01 详细技术说明

项目概述

这是一个过程式编程的IPTV直播源聚合处理工具基础版本，采用线性流程设计，实现了完整的直播源采集、分类、过滤和格式化功能。虽然架构相对简单，但功能完整，是后续版本的基础。

架构特点

1. 线性流程架构

```
初始化 → 加载配置 → 处理URL → 分类分发 → 生成输出
```

2. 全局变量驱动

· 使用大量全局列表变量存储各分类频道数据
· 通过函数直接操作全局状态
· 简单直观但耦合度较高

核心功能模块

1. 数据源处理模块

1.1 URL获取与处理

```python
def process_url(url):
    """
    核心URL处理流程：
    1. 发送HTTP请求获取内容
    2. 自动识别M3U格式并转换
    3. 逐行处理频道数据
    4. 支持多源加速（#分隔）
    """
```

1.2 多源支持机制

```python
# 支持"#"分隔的多重加速源
# 格式：频道名,源1#源2#源3
# 处理时会拆分成多个单独的行
```

1.3 日期变量替换

```python
# 支持动态日期占位符
{MMdd} → 当前日期（月日）
{MMdd-1} → 前一天日期
# 便于处理每日更新的直播源
```

2. 频道分类系统

2.1 分类存储结构

```python
# 共63个分类变量，全面覆盖各类频道
# 核心频道
yangshi_lines = []      # 央视频道
weishi_lines = []       # 卫视频道

# 省级地方台（33个省市自治区）
beijing_lines = []      # 北京
shanghai_lines = []     # 上海
# ... 其他31个省份

# 港澳台频道
hongkong_lines = []     # 香港
macau_lines = []        # 澳门
taiwan_lines = []       # 台湾

# 内容分类频道（22类）
digital_lines = []      # 数字频道
movie_lines = []        # 电影频道
# ... 其他20个内容分类

# 体育赛事专用
tyss_lines = []         # 体育赛事
mgss_lines = []         # 咪咕赛事

# 特殊频道
traditional_opera_lines = []    # 戏曲频道
spring_festival_gala_lines = [] # 春晚频道
camera_lines = []               # 直播中国
favorite_lines = []             # 收藏频道
```

2.2 分类字典机制

```python
# 使用字典文件定义分类规则
# assets/livesource/主频道/CCTV.txt
CCTV1
CCTV2
CCTV3
# ...

# 加载字典到内存
yangshi_dictionary = read_txt_to_array('assets/livesource/主频道/CCTV.txt')
```

2.3 分类分发逻辑

```python
def process_channel_line(line):
    """
    逐行分发频道到对应分类：
    1. 检查是否为有效频道行
    2. 清理频道名称
    3. 简繁转换
    4. URL清理（移除$参数）
    5. 63级if-elif链匹配分类
    6. 去重检查后添加到对应分类
    """
```

3. 频道名称处理系统

3.1 清理关键词列表

```python
# 42个需要移除的冗余关键词
removal_list = [
    "_电信", "电信", "「LiTV」", "频道", "频陆", "备陆", "壹陆", 
    "高清", "超清", "标清", "斯特", "1080", "720", "480", 
    "HD", "SD", "4K", "VGA", "(HD)", "(SD)", "(4K)", "(VGA)",
    # ... 更多关键词
]

def clean_channel_name(channel_name, removal_list):
    # 移除所有关键词
    # 移除末尾HD
    # 移除末尾"台"（仅限长度>3）
```

3.2 CCTV特殊处理

```python
def process_name_string(input_str):
    """
    CCTV名称规范化：
    1. 移除IPV6、PLUS、1080等字样
    2. 提取数字和K+符号
    3. 特殊处理4K/8K格式
    4. 统一格式：CCTV+数字+(4K/8K)
    """
```

3.3 卫视名称清理

```python
# 使用正则表达式移除"卫视「.*」"中的内容
# 湖南卫视「IPV6」 → 湖南卫视
```

3.4 简繁转换

```python
def traditional_to_simplified(text):
    # 使用opencc库进行繁转简
    # 确保所有频道名称为简体中文
```

4. 黑白名单系统

4.1 黑名单合并

```python
# 合并自动和手动黑名单
blacklist_auto = read_blacklist_from_txt('blacklist_auto.txt')
blacklist_manual = read_blacklist_from_txt('blacklist_manual.txt')
combined_blacklist = set(blacklist_auto + blacklist_manual)
# 使用集合提升查找效率（O(1)复杂度）
```

4.2 白名单筛选

```python
# 只添加响应时间<2000ms的高质量源
# 格式：ms,频道名,URL
response_time = float(whitelist_parts[0].replace("ms", ""))
if response_time < 2000:
    process_channel_line(",".join(whitelist_parts[1:]))
```

5. 数据去重机制

5.1 URL级别去重

```python
def check_url_existence(data_list, url):
    """
    检查URL是否已存在于分类列表中
    性能：O(n)复杂度，逐个对比
    问题：随着数据量增加，性能下降严重
    """
    urls = [item.split(',')[1] for item in data_list]
    return url not in urls
```

5.2 其他源去重

```python
# 使用other_lines_url列表记录已添加URL
if channel_address not in other_lines_url:
    other_lines_url.append(channel_address)
    other_lines.append(line.strip())
```

6. 格式转换模块

6.1 M3U转TXT

```python
def convert_m3u_to_txt(m3u_content):
    """
    转换M3U格式为TXT格式：
    1. 跳过#EXTM3U行
    2. 解析#EXTINF获取频道名
    3. 提取URL行
    4. 组合为 频道名,URL 格式
    """
```

6.2 TXT转M3U

```python
def make_m3u(txt_file, m3u_file):
    """
    生成M3U格式文件：
    1. 添加#EXTM3U头部和EPG链接
    2. 解析分组信息（#genre#）
    3. 添加频道Logo（从logo.txt读取）
    4. 输出#EXTINF格式行
    """
```

7. 体育赛事处理模块

7.1 日期格式化

```python
def normalize_date_to_md(text):
    """
    统一多种日期格式为MM-DD：
    1. MM/DD 或 M/D
    2. YYYY-MM-DD
    3. M月D日（中文）
    示例：03-07 NBA常规赛
    """
```

7.2 关键词过滤

```python
# 过滤违规内容
keywords_to_exclude_tiyu = [
    "玉玉软件", "榴芒电视", "公众号", 
    "咪视通", "麻豆", "「回看」"
]
```

7.3 专用排序算法

```python
def custom_tyss_sort(lines):
    """
    体育赛事特殊排序：
    1. 数字开头行倒序排列（最新日期在前）
    2. 其他行升序排列
    """
```

7.4 HTML页面生成

```python
def generate_playlist_html(data_list, output_file):
    """
    生成交互式HTML页面：
    1. 现代CSS样式设计
    2. 响应式布局
    3. 一键复制功能
    4. Google Analytics集成
    5. AdSense广告支持
    """
```

8. 特殊源处理

8.1 AKTV源获取

```python
# 优先从GitHub获取最新源
# 失败时使用本地备份
aktv_text = get_http_response(aktv_url)
if aktv_text:
    aktv_lines = convert_m3u_to_txt(aktv_text).split('\n')
else:
    aktv_lines = read_txt_to_array('assets/livesource/手工区/AKTV.txt')
```

8.2 手工区数据补充

```python
# 补充高质量手工源
zhejiang_lines += read_txt_to_array('assets/livesource/手工区/浙江频道.txt')
guangdong_lines += read_txt_to_array('assets/livesource/手工区/广东频道.txt')
# ... 其他省份
```

9. 名称纠错系统

9.1 纠错字典加载

```python
def load_corrections_name(filename):
    """
    加载频道名称纠错字典：
    格式：正确名称,错误名称1,错误名称2,...
    示例：CCTV1,CCTV-1,CCTV1高清
    """
```

9.2 应用纠错

```python
def correct_name_data(corrections, data):
    """
    遍历数据应用纠错：
    1. 分割每行为名称和URL
    2. 检查名称是否在纠错字典中
    3. 如果存在且不同，则替换为正确名称
    """
```

10. 排序系统

10.1 按字典顺序排序

```python
def sort_data(order, data):
    """
    按指定顺序对数据进行排序：
    1. 创建名称到索引的映射字典
    2. 使用排序键函数处理不在字典中的名称
    3. 返回按order顺序排列的数据
    """
```

10.2 CCTV特殊排序

```python
def custom_sort(s):
    """
    CCTV特殊排序规则：
    1. 普通CCTV排在最前
    2. CCTV-4K其次
    3. CCTV-8K最后
    """
```

11. 输出生成系统

11.1 多版本输出

```python
# 完整版（all_lines）：包含所有63个分类
# 精简版（all_lines_simple）：仅央视+卫视
# 定制版（all_lines_custom）：不含地方台，含其他所有分类
# 未分类源（output_others）：兜底存储
```

11.2 分组结构

```python
# 每个分类包含：
# 1. 分组标题：🌐央视频道,#genre#
# 2. 排序后的频道数据
# 3. 空行分隔符
```

11.3 今日推荐

```python
# 动态生成推荐信息
MTV1 = "💯推荐," + get_random_url('assets/livesource/手工区/今日推荐.txt')
MTV2 = "🤫低调," + get_random_url('assets/livesource/手工区/今日推荐.txt')
# ... 共5个推荐模板
```

12. HTTP请求处理

12.1 重试机制

```python
def get_http_response(url, timeout=8, retries=2, backoff_factor=1.0):
    """
    带重试的HTTP请求：
    1. 设置User-Agent
    2. 指数退避重试（1s, 2s, 4s...）
    3. 处理各种异常
    4. 返回解码后的内容或None
    """
```

12.2 随机User-Agent

```python
def get_random_user_agent():
    # 从4个User-Agent中随机选择
    # 避免被目标服务器封锁
```

13. 时间处理系统

13.1 北京时间获取

```python
# 本地时间处理（未统一时区）
timestart = datetime.now()  # 本地时间
```

13.2 执行时间统计

```python
elapsed_time = timeend - timestart
total_seconds = elapsed_time.total_seconds()
minutes = int(total_seconds // 60)
seconds = int(total_seconds % 60)
```

14. 文件系统结构

14.1 输入目录结构

```
assets/livesource/
├── 主频道/          # 63个分类字典文件
│   ├── CCTV.txt
│   ├── 卫视.txt
│   ├── 体育赛事.txt
│   └── ...
├── 地方台/          # 33个省份字典
├── 手工区/          # 手工整理的高质量源
│   ├── 浙江频道.txt
│   ├── 广东频道.txt
│   ├── AKTV.txt
│   └── ...
├── blacklist/       # 黑白名单
│   ├── blacklist_auto.txt
│   ├── blacklist_manual.txt
│   └── whitelist_auto.txt
├── urls-daily.txt   # 每日更新的数据源URL
├── logo.txt         # 频道Logo映射
└── corrections_name.txt  # 名称纠错字典
```

14.2 输出目录结构

```
output/
├── full.txt          # 完整版播放列表
├── full.m3u         # M3U格式完整版
├── lite.txt          # 精简版（央视+卫视）
├── lite.m3u         # M3U格式精简版
├── custom.txt        # 定制版（不含地方台）
├── custom.m3u       # M3U格式定制版
├── others.txt        # 未分类频道
├── tiyu.html        # 体育赛事网页
└── tiyu.txt         # 体育赛事文本
```

15. 性能特点分析

15.1 时间复杂度

```python
# 主要性能瓶颈：
1. check_url_existence(): O(n) 每次都要遍历整个列表
2. 63级if-elif链: O(63) 常数级但代码冗长
3. 多次重复的URL去重检查
```

15.2 空间复杂度

```python
# 内存使用：
1. 63个分类列表：每个存储频道数据
2. 多个字典：存储分类规则
3. 临时变量：处理过程中的中间数据
```

15.3 网络性能

```python
# 特点：
1. 串行处理URL：逐个请求，无并发
2. 支持重试机制：指数退避
3. 超时控制：默认8秒
```

16. 代码风格特点

16.1 过程式编程

```python
# 特点：
1. 大量全局变量
2. 函数直接操作全局状态
3. 线性执行流程
4. 代码耦合度高
```

16.2 注释风格

```python
# 详细的注释说明
# 包括功能、参数、返回值、示例
# 便于理解和维护
```

16.3 错误处理

```python
# try-except结构
# 打印错误信息但继续执行
# 优雅降级处理
```

17. 扩展性分析

17.1 添加新分类

```python
# 需要修改的步骤：
1. 添加新的全局列表变量
2. 加载对应的字典文件
3. 在process_channel_line()中添加新的if-elif分支
4. 在输出生成部分添加新的分类段落
```

17.2 修改处理逻辑

```python
# 影响范围：
1. 全局状态可能被多个函数修改
2. 需要仔细检查相关函数
3. 容易产生副作用
```

18. 优缺点分析

18.1 优点

1. 功能完整：实现了所有核心功能
2. 直观易懂：线性流程，便于理解
3. 快速上手：不需要复杂的面向对象知识
4. 兼容性好：简单的数据格式，易于集成

18.2 缺点

1. 性能问题：去重效率低（O(n)复杂度）
2. 代码冗长：63级if-elif链，重复代码多
3. 耦合度高：全局变量多，函数间依赖强
4. 维护困难：添加新功能需要修改多处
5. 扩展性差：分类数量硬编码

19. 与其他版本对比

特性 v0.01 v1.00 v2.00 v3.00
编程范式 过程式 过程式 过程式改进 面向对象
去重效率 O(n) O(1) O(1) O(1)
代码结构 线性 线性优化 模块化 模块化
分类数量 63 63 63 可配置
扩展性 差 中 中 好
维护性 差 中 中 好
性能 低 高 高 高

20. 典型使用场景

20.1 小规模数据处理

```python
# 适合场景：
- 数据源较少（<100个URL）
- 频道数量有限（<1000个）
- 分类数量固定（63个）
- 不需要频繁扩展
```

20.2 学习和教学

```python
# 教学价值：
- 展示完整的直播源处理流程
- 演示过程式编程特点
- 理解频道分类逻辑
- 学习数据清洗和格式化
```

20.3 快速原型开发

```python
# 原型开发：
- 快速验证功能需求
- 测试数据源质量
- 验证分类逻辑
- 生成基础播放列表
```

21. 改进建议

21.1 性能优化

```python
# 建议改进：
1. 使用集合进行URL去重（全局去重）
2. 缓存字典匹配结果
3. 批量处理数据，减少循环次数
```

21.2 代码重构

```python
# 重构方向：
1. 提取重复逻辑为函数
2. 使用字典映射替代if-elif链
3. 封装全局状态为类
4. 分离配置和业务逻辑
```

21.3 功能增强

```python
# 功能增强：
1. 添加源有效性检测
2. 支持更多输出格式（JSON、XML）
3. 添加Web管理界面
4. 支持定时任务
```

22. 总结

v0.01版本是一个功能完整但架构简单的基础版本，具有以下特点：

22.1 核心价值

1. 完整性：实现了从数据采集到输出的完整流程
2. 实用性：可以直接用于生产环境
3. 教育性：展示了直播源处理的完整思路

22.2 技术贡献

1. 基础架构：定义了频道分类的基本框架
2. 处理流程：确立了数据清洗和格式化的标准流程
3. 文件格式：规范了输入输出文件的结构

22.3 历史地位

作为项目的起点版本，v0.01奠定了后续版本的基础：

· 后续版本在其基础上进行优化和重构
· 保持了完全的文件格式兼容性
· 证明了核心功能的可行性

22.4 适用建议

· 新项目：不建议直接使用，推荐使用v3.00
· 学习研究：适合学习直播源处理的基本原理
· 历史维护：如果需要维护旧系统，了解此版本有助于理解兼容性需求

v0.01版本虽然存在性能和维护性问题，但作为历史起点，它为整个项目的演进提供了坚实的基础，展示了直播源聚合处理的核心思想和实现方法。