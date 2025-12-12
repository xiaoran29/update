🐍 livesource.py v2.00 详细技术说明

📋 脚本概述

这是一个全功能直播源聚合处理工具，从多个网络源收集直播数据，进行智能分类、去重和格式转换，最终生成多种播放器兼容的格式。v2.00版本在v1.00基础上进行了架构重构，增强了代码健壮性和功能完整性。

🏗️ 整体架构

模块化设计

```python
# 模块组织原则：高内聚，低耦合
# 1. 配置初始化模块
# 2. 数据处理核心模块
# 3. 输入输出模块
# 4. 统计监控模块
# 5. 主流程协调模块
```

处理流程概览

```
📂 初始化配置 → 📥 数据收集 → 🧹 数据清洗 → 🏷️ 智能分类 → ✅ 质量控制 → 📤 多格式输出
    │               │              │              │               │              │
    ├─ 时区设置      ├─ URL源获取   ├─ 名称标准化    ├─ 55个分类匹配 ├─ 黑白名单过滤 ├─ TXT格式生成
    ├─ 目录创建      ├─ 日期变量替换 ├─ 繁简转换      ├─ 优先级排序  ├─ URL去重检查 ├─ M3U格式生成
    ├─ 字典加载      ├─ HTTP请求    ├─ 冗余清理      ├─ 纠错处理    ├─ 响应时间筛选 ├─ HTML页面生成
    └─ 黑名单加载     └─ 格式转换     └─ 特殊格式处理  └─ 未分类兜底   └─ 手工区去重   └─ JSON统计报告
```

🔧 核心功能模块

1. 时间处理系统

```python
def get_beijing_time():
    """获取北京时间（UTC+8），统一所有时间戳"""
    utc_now = datetime.now(timezone.utc)
    beijing_now = utc_now + timedelta(hours=8)
    return beijing_now
```

应用场景：

· 脚本执行时间记录
· URL日期变量替换：{MMdd}、{MMdd-1}
· 版本信息生成
· 统计报告时间戳

2. 简繁转换引擎

```python
def traditional_to_simplified(text: str) -> str:
    """使用OpenCC库进行繁体到简体转换"""
    converter = opencc.OpenCC('t2s')
    simplified_text = converter.convert(text)
    return simplified_text
```

处理范围：

· 港澳台频道名称标准化
· 繁体中文节目名称统一
· 提高分类匹配准确性

3. URL处理管道

3.1 URL清理机制

```python
def clean_url(url):
    """移除URL中的额外参数（$之后的内容）"""
    last_dollar_index = url.rfind('$')  # 处理URL中的扩展参数
    if last_dollar_index != -1:
        return url[:last_dollar_index]  # 保留主要部分
    return url
```

处理示例：

```
输入：http://example.com/live.m3u$1920x1080
输出：http://example.com/live.m3u

输入：rtmp://server/live$bitrate=2000
输出：rtmp://server/live
```

3.2 格式转换系统

```python
def convert_m3u_to_txt(m3u_content):
    """智能识别M3U格式并转换为标准TXT格式"""
    # 处理逻辑：
    # 1. 识别#EXTM3U标签
    # 2. 提取#EXTINF中的频道名称
    # 3. 匹配对应URL行
    # 4. 转换为"名称,URL"格式
```

格式转换示例：

```
#EXTM3U
#EXTINF:-1,中央电视台-1
http://example.com/cctv1
#EXTINF:-1,湖南卫视
http://example.com/hunan

转换为：
中央电视台-1,http://example.com/cctv1
湖南卫视,http://example.com/hunan
```

4. 频道名称智能处理系统

4.1 名称清理引擎

```python
def clean_channel_name(channel_name, removal_list):
    """清理频道名称中的冗余词汇（支持75个清理关键词）"""
    # 第一阶段：关键词替换
    for item in removal_list:  # 75个清理关键词
        channel_name = channel_name.replace(item, "")
    
    # 第二阶段：特殊处理
    if channel_name.endswith("HD"):
        channel_name = channel_name[:-2]  # 移除末尾HD
    
    if channel_name.endswith("台") and len(channel_name) > 3:
        channel_name = channel_name[:-1]  # 移除末尾"台"字
        
    return channel_name
```

清理关键词分类：

类别 示例关键词 作用
运营商标记 _电信, 电信 去除运营商信息
画质标记 高清, 超清, [HD], [4K] 标准化画质描述
平台标记 AKtv, 咪咕, 「IPV4」 去除平台标识
冗余词汇 频道, 斯特, 闽特 清理无意义词汇
特殊标记 (北美), (HK), 「回看」 统一地区标识

4.2 CCTV智能标准化

```python
def process_name_string(input_str):
    """CCTV频道名称智能标准化处理"""
    if "CCTV" in part_str and "://" not in part_str:
        # 处理步骤：
        # 1. 移除特殊标记：IPV6, PLUS, 1080
        # 2. 提取核心数字：CCTV后面的数字部分
        # 3. 特殊处理4K/8K频道
        # 4. 统一输出格式：CCTV数字 或 CCTV(4K)
```

标准化效果：

· CCTV-1 HD → CCTV1
· CCTV-5+ 体育 → CCTV5+
· CCTV-4K 超高清 → CCTV(4K)
· CCTV-8K 测试 → CCTV(8K)

4.3 卫视名称清理

```python
elif "卫视" in part_str:
    pattern = r'卫视「.*」'  # 匹配卫视后的描述信息
    result_str = re.sub(pattern, '卫视', part_str)  # 统一为"卫视"
    return result_str
```

处理效果：

· 湖南卫视「高清」 → 湖南卫视
· 浙江卫视「蓝光」 → 浙江卫视

5. 频道分发系统（核心模块）

5.1 分发逻辑架构

```python
def classify_channel(channel_name, processed_line, channel_address):
    """三级分类体系，优先级从高到低"""
    # 第一级：央视（最高优先级）
    if "CCTV" in channel_name:
        yangshi_lines.append(processed_line)
        return True
    
    # 第二级：卫视和省级地方台（27个省份）
    elif channel_name in weishi_dictionary:
        weishi_lines.append(processed_line)
        return True
    elif channel_name in beijing_dictionary:
        beijing_lines.append(processed_line)
        return True
    # ... 其他25个省份
    
    # 第三级：专业频道和港澳台（28个分类）
    elif channel_name in digital_dictionary:
        digital_lines.append(processed_line)
        return True
    elif channel_name in movie_dictionary:
        movie_lines.append(processed_line)
        return True
    # ... 其他26个分类
    
    # 未分类：兜底处理
    if channel_address not in other_lines_url:
        other_lines_url.append(channel_address)
        other_lines.append(processed_line)
        return True
    
    return False
```

5.2 处理流程顺序

```python
def process_channel_line(line):
    """单行频道数据处理流程"""
    # 步骤1：格式验证（过滤无效行）
    if "#genre#" not in line and "#EXTINF:" not in line and "," in line and "://" in line:
        # 步骤2：分割数据
        parts = line.split(',', 1)
        
        # 步骤3：URL预处理
        channel_address = clean_url(parts[1].strip())
        
        # 步骤4：黑名单过滤（提前过滤）
        if channel_address in combined_blacklist:
            print(f"🚫 黑名单过滤: {parts[0].strip()}")
            return
        
        # 步骤5：全局去重检查
        if channel_address in processed_urls:
            print(f"🔄 URL去重: {parts[0].strip()}")
            return
        processed_urls.add(channel_address)  # 记录已处理URL
        
        # 步骤6：名称处理管道
        channel_name = clean_channel_name(parts[0].strip(), removal_list)
        channel_name = traditional_to_simplified(channel_name)
        
        # 步骤7：名称纠错
        if channel_name in corrections_name:
            channel_name = corrections_name[channel_name]
        
        # 步骤8：分类分发
        classify_channel(channel_name, process_name_string(f"{channel_name},{channel_address}"), channel_address)
```

6. 质量控制系统

6.1 四级去重机制

```python
# 第一级：全局URL哈希去重（O(1)复杂度）
processed_urls = set()  # 全局集合，记录所有处理过的URL

# 第二级：黑名单过滤
combined_blacklist = set()  # 合并自动和手动黑名单

# 第三级：分类内去重
other_lines_url = []  # 专门用于未分类频道的URL去重

# 第四级：手工区内部去重（v2.00新增）
def read_and_deduplicate_manual(file_path):
    """手工区文件内部URL去重"""
    seen_urls = set()  # 每个文件独立去重
    unique_lines = []
    # ... 去重逻辑
```

6.2 白名单质量筛选

```python
# 白名单格式：响应时间,频道名称,URL
# 示例：200ms,中央电视台-1,http://example.com/cctv1

for whitelist_line in whitelist_auto_lines:
    whitelist_parts = whitelist_line.split(",")
    response_time = float(whitelist_parts[0].replace("ms", ""))
    
    # 基于响应时间的质量分级
    if response_time < 2000:  # 高速源：<2秒
        process_channel_line(",".join(whitelist_parts[1:]))
    else:  # 慢速源：≥2秒，被过滤
        print(f"  ⚠️  白名单跳过(响应慢)")
```

质量等级：

· 金牌源：< 1000ms (1秒以内)
· 银牌源：1000ms - 2000ms (1-2秒)
· 铜牌源：2000ms - 5000ms (2-5秒，被过滤)
· 淘汰源：> 5000ms (5秒以上，被过滤)

7. HTTP请求处理系统

7.1 智能重试机制

```python
def get_http_response(url, timeout=8, retries=2, backoff_factor=1.0):
    """带指数退避的重试机制"""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return data.decode('utf-8')
        except Exception as e:
            if attempt < retries - 1:
                # 指数退避：1秒 → 2秒 → 4秒
                time.sleep(backoff_factor * (2 ** attempt))
    return None  # 所有重试失败后返回None
```

7.2 随机User-Agent轮换

```python
def get_random_user_agent():
    """随机选择User-Agent，防止请求被拦截"""
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",  # Chrome 91
        "Mozilla/5.0 (Windows NT 10.0)...",              # Chrome 90
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",  # Chrome 89
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",  # Chrome 88
    ]
    return random.choice(USER_AGENTS)  # 随机选择，提高成功率
```

8. 体育赛事处理系统

8.1 日期格式标准化

```python
def normalize_date_to_md(text):
    """统一各种日期格式为MM-DD"""
    # 支持格式：
    # 01/01 比赛 → 01-01 比赛
    # 2024-01-01 比赛 → 01-01 比赛
    # 1月1日 比赛 → 01-01 比赛
    # 1-1 比赛 → 01-01 比赛
```

8.2 智能排序算法

```python
def custom_tyss_sort(lines):
    """体育赛事专用排序（数字开头倒序，其他升序）"""
    digit_prefix = []  # 数字开头的行（日期格式）
    others = []        # 其他行
    
    for line in lines:
        name_part = line.split(',')[0].strip()
        if name_part and name_part[0].isdigit():  # 判断是否以数字开头
            digit_prefix.append(line)  # 日期赛事
        else:
            others.append(line)  # 非日期赛事
    
    # 数字开头倒序（最新的在前），其他升序
    digit_prefix_sorted = sorted(digit_prefix, reverse=True)
    others_sorted = sorted(others)
    
    return digit_prefix_sorted + others_sorted  # 组合结果
```

8.3 HTML页面生成

```python
def generate_playlist_html(data_list, output_file='playlist.html'):
    """生成响应式体育赛事HTML页面"""
    # 特性：
    # 1. 响应式设计（移动端友好）
    # 2. 一键复制链接功能
    # 3. 简洁美观的UI
    # 4. 内置Google Analytics统计
    # 5. 广告支持（Google AdSense）
```

9. 多格式输出系统

9.1 TXT格式生成（3个版本）

```python
# 完整版 (full.txt) - 包含55个完整分类
# 精简版 (lite.txt) - 仅央视+卫视+更新信息
# 定制版 (custom.txt) - 不含地方台的专业频道集合

# 文件结构示例：
"""
🌐央视频道,#genre#
CCTV1,http://example.com/cctv1
CCTV2,http://example.com/cctv2

📡卫视频道,#genre#
湖南卫视,http://example.com/hunan
浙江卫视,http://example.com/zhejiang

🕒更新时间,#genre#
20240101 10:00:00,http://example.com/version
💯推荐,http://example.com/recommend
"""
```

9.2 M3U格式转换

```python
def make_m3u(txt_file, m3u_file):
    """TXT转M3U格式，集成Logo和EPG"""
    # 特性：
    # 1. 自动匹配台标（从logo.txt）
    # 2. 集成EPG电子节目指南
    # 3. 分组信息保留
    # 4. 兼容VLC/PotPlayer/Kodi等播放器
```

M3U格式示例：

```m3u
#EXTM3U x-tvg-url="https://live.fanmingming.cn/e.xml"
#EXTINF:-1 tvg-id="CCTV1" tvg-name="CCTV1" tvg-logo="http://example.com/logo/cctv1.png" group-title="央视频道",CCTV1
http://example.com/cctv1
```

9.3 JSON统计报告（v2.00新增）

```python
# 生成详细的JSON格式统计信息
{
    "metadata": {
        "version": "v2.00",
        "start_time": "20240101 10:00:00",
        "end_time": "20240101 10:02:05",
        "duration_seconds": 125,
        "duration_formatted": "2分5秒"
    },
    "statistics": {
        "processed_urls": 1245,
        "blacklist_urls": 156,
        "total_processed_urls": 1401,
        "duplicate_rate": 11.1,
        "total_lines": 15420,
        "other_lines": 2890
    },
    "category_counts": {
        "央视": 150,
        "卫视": 89,
        "体育赛事": 23,
        "其他": 267
    }
}
```

10. 主流程控制

10.1 模块化主函数

```python
def main():
    """主控制函数，协调所有处理模块"""
    print("🎬 IPTV直播源聚合处理工具 v2.00 开始运行")
    
    # 步骤1-9的模块化执行
    initialize_system()           # 初始化
    load_resources()              # 加载资源
    process_url_sources()         # 处理URL源
    process_whitelist()           # 处理白名单
    process_aktv()                # 处理AKTV
    process_manual_sources()      # 处理手工区
    process_sports()              # 处理体育赛事
    generate_outputs()            # 生成输出
    generate_statistics()         # 生成统计
    
    print("🎉 IPTV直播源处理完成！")
```

10.2 错误处理机制

```python
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断程序")
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
        # 可以添加日志记录、邮件通知等扩展功能
```

📊 数据处理统计

去重统计系统

```python
# 计算去重率
processed_urls_count = len(processed_urls)      # 唯一URL数
blacklist_urls_count = len(combined_blacklist)  # 黑名单URL数
total_processed_urls = processed_urls_count + blacklist_urls_count

if total_processed_urls > 0:
    duplication_rate = (1 - processed_urls_count / total_processed_urls) * 100
    print(f"🔄 去重率: {duplication_rate:.1f}%")
```

去重效果分析：

· 去重率高（>20%）：源质量较差，重复内容多
· 去重率中等（10%-20%）：源质量正常
· 去重率低（<10%）：源质量优秀，重复内容少

分类统计

```python
# 55个分类统计
category_stats = {
    "央视频道": len(yangshi_lines),
    "卫视频道": len(weishi_lines),
    "省级地方台": sum([len(beijing_lines), len(shanghai_lines), ...]),  # 27个省份
    "港澳台频道": sum([len(hongkong_lines), len(macau_lines), len(taiwan_lines)]),
    "专业频道": sum([len(movie_lines), len(sports_lines), ...]),  # 23个专业分类
    "体育赛事": len(filtered_tyss_lines),
    "未分类": len(other_lines)
}
```

⚙️ 配置系统

字典文件结构

```
assets/livesource/
├── 📂 主频道/           # 23个核心分类字典
│   ├── CCTV.txt        # 央视频道标准名称（排序用）
│   ├── 卫视.txt        # 卫视频道标准名称（过滤+排序）
│   ├── 电影.txt        # 电影频道字典
│   ├── 体育.txt        # 体育频道字典
│   └── ... (20个文件)
├── 📂 地方台/           # 27个省级地方台字典
│   ├── 北京.txt        # 北京频道字典
│   ├── 上海.txt        # 上海频道字典
│   ├── 广东.txt        # 广东频道字典
│   └── ... (24个文件)
├── 📂 手工区/           # 高质量手工维护源
│   ├── 浙江频道.txt    # 浙江手工源（内部去重）
│   ├── 广东频道.txt    # 广东手工源（内部去重）
│   ├── AKTV.txt        # AKTV特殊源
│   └── 今日推荐.txt    # 每日推荐源
├── 📂 blacklist/        # 黑白名单管理系统
│   ├── blacklist_auto.txt    # 自动收集黑名单
│   ├── blacklist_manual.txt  # 手工维护黑名单
│   └── whitelist_auto.txt    # 高速响应白名单
├── 📄 logo.txt         # 台标映射文件（频道名→URL）
├── 📄 urls-daily.txt   # 每日更新的源URL列表
└── 📄 corrections_name.txt  # 频道名称纠错字典
```

纠错文件格式

```txt
# corrections_name.txt
# 格式：正确名称,错误名称1,错误名称2,错误名称3
CCTV1,CCTV-1,中央1台,央视1套
湖南卫视,湖南电视台,湖南卫视频道
浙江卫视,浙江电视台,浙江卫视频道
```

🚀 执行时间线

阶段1：初始化（0-5秒）

```
1. 创建输出目录
2. 加载黑名单（自动+手动，合并去重）
3. 加载55个分类字典
4. 加载名称纠错字典
5. 初始化全局变量和集合
```

阶段2：数据获取（5-30秒）

```
1. 读取URL列表（urls-daily.txt）
2. 处理日期变量（{MMdd}、{MMdd-1}）
3. 发送HTTP请求（带重试机制）
4. 格式识别和转换（M3U→TXT）
5. 多URL源拆分处理（#分隔符）
```

阶段3：数据处理（30-60秒）

```
1. 逐行解析数据（过滤无效行）
2. URL清理（去除$参数）
3. 黑名单过滤（提前过滤）
4. 全局URL去重（O(1)复杂度）
5. 频道名称标准化（清理+繁简转换）
6. 名称纠错（基于纠错字典）
7. 智能分类分发（55个分类）
```

阶段4：特殊处理（60-90秒）

```
1. 白名单处理（高速源筛选，<2秒）
2. AKTV源处理（网络优先，本地备援）
3. 手工区处理（内部URL去重）
4. 体育赛事处理（日期标准化+过滤+排序）
```

阶段5：输出生成（90-120秒）

```
1. 生成完整版（full.txt，55个分类）
2. 生成精简版（lite.txt，央视+卫视）
3. 生成定制版（custom.txt，专业频道）
4. 生成M3U格式（*.m3u，带Logo+EPG）
5. 生成HTML页面（tiyu.html，体育赛事）
6. 生成JSON统计（statistics.json，详细数据）
```

阶段6：统计报告（120-125秒）

```
1. 计算执行时间
2. 统计去重效果
3. 输出分类数量
4. 生成性能报告
5. 保存JSON格式统计
```

🔧 v2.00新增特性

1. 架构优化

· 函数式编程架构：更清晰的模块划分
· 错误处理增强：完善的异常捕获机制
· 代码注释规范：详细的函数和模块说明

2. 手工区内部去重

```python
def read_and_deduplicate_manual(file_path):
    """手工区文件内部URL去重，避免同一文件内重复"""
    seen_urls = set()  # 每个文件独立的URL集合
    unique_lines = []
    
    for line in lines:
        if "#genre#" not in line and "," in line and "://" in line:
            parts = line.split(',', 1)
            if len(parts) >= 2:
                channel_url = clean_url(parts[1].strip())
                
                # 只检查当前文件内部的URL重复
                if channel_url not in seen_urls:
                    seen_urls.add(channel_url)
                    unique_lines.append(line)
    
    return unique_lines
```

3. JSON统计报告

```python
# 生成结构化的JSON格式统计
stats_output = {
    "metadata": {...},      # 元数据信息
    "statistics": {...},    # 统计数字
    "category_counts": {...} # 分类数量
}

# 保存为statistics.json，便于程序化分析
```

4. 台湾地区支持

```python
# v2.00新增台湾频道分类
taiwan_lines = []           # 存储台湾频道数据
taiwan_dictionary = []      # 台湾频道字典
```

📈 性能优化点

1. 算法优化

· 集合去重：O(1)复杂度，替代O(n)列表查找
· 提前过滤：在处理早期进行黑名单和去重检查
· 批量处理：多URL源拆分为单URL并行潜力

2. 内存优化

· 分批处理：避免一次性加载所有数据
· 及时释放：处理完成后释放临时数据
· 生成器使用：支持后续流式处理改造

3. 网络优化

· 指数退避重试：智能重试策略
· 随机User-Agent：防止请求被拦截
· 连接池优化：支持后续HTTP连接池改造

4. 文件IO优化

· 缓冲写入：批量写入减少IO次数
· 编码统一：所有文件UTF-8编码
· 路径优化：相对路径和缓存机制

🛡️ 容错与健壮性

1. 异常处理机制

```python
# 多层异常捕获
try:
    # 高风险操作
    process_url(url)
except HTTPError as e:
    print(f"[HTTPError] 代码: {e.code}")
except (URLError, socket.timeout) as e:
    print(f"[网络错误] {type(e).__name__}")
except Exception as e:
    print(f"[异常] {type(e).__name__}: {e}")
```

2. 数据验证

```python
# 输入数据验证
if "#genre#" not in line and "#EXTINF:" not in line and "," in line and "://" in line:
    # 有效数据格式才处理
    process_channel_line(line)

# URL有效性检查
if url.startswith("http"):
    # 只处理HTTP/HTTPS协议
    process_url(url)
```

3. 资源清理

```python
# 确保资源正确释放
with urllib.request.urlopen(req, timeout=timeout) as response:
    data = response.read()
    return data.decode('utf-8')  # 自动关闭连接

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(content)  # 自动关闭文件
```

🔮 扩展性设计

1. 插件化架构支持

```python
# 支持后续插件扩展
# plugins/
#   ├── source_plugin.py    # 数据源插件
#   ├── filter_plugin.py    # 过滤器插件
#   ├── output_plugin.py    # 输出格式插件
#   └── monitor_plugin.py   # 监控插件
```

2. 配置化支持

```python
# 支持配置文件扩展
# config.yaml
#   sources:
#     - type: http
#       url: http://example.com/live.m3u
#     - type: file
#       path: local_sources.txt
#   filters:
#     blacklist: blacklist.txt
#     whitelist: whitelist.txt
```

3. 并行处理支持

```python
# 支持多线程/多进程改造
import concurrent.futures

# 示例：多线程URL处理
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    futures = {executor.submit(process_url, url): url for url in urls}
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
```

📊 监控与调试

1. 详细日志系统

```python
# 分级日志输出
print(f"📡 开始处理URL: {url}")        # 信息级别
print(f"🚫 黑名单过滤: {channel_name}") # 警告级别
print(f"❌ 处理URL时发生错误: {e}")     # 错误级别
print(f"✅ 成功处理: {processed_count} 个频道") # 成功级别
```

2. 性能监控

```python
# 执行时间监控
timestart = get_beijing_time()
# ... 处理过程 ...
timeend = get_beijing_time()
elapsed_time = timeend - timestart

print(f"执行时间: {elapsed_time.total_seconds():.2f}秒")
```

3. 内存监控

```python
# 内存使用监控（示例）
import sys

def get_memory_usage():
    """获取当前内存使用情况"""
    # 可用于监控内存泄漏
    pass
```

🎯 设计原则总结

1. 单一职责原则

· 每个函数只做一件事
· 模块功能清晰分离
· 便于测试和维护

2. 开闭原则

· 对扩展开放，对修改关闭
· 支持插件化扩展
· 配置文件驱动

3. 接口隔离原则

· 清晰的输入输出接口
· 模块间低耦合
· 便于集成和替换

4. 依赖倒置原则

· 高层模块不依赖低层模块
· 抽象不依赖细节
· 支持多种数据源和输出格式

5. DRY原则

· 避免重复代码
· 提取公共函数
· 代码复用最大化

📁 输出文件说明

1. 完整版输出结构

```
output/
├── 📄 full.txt            # 完整版（55个分类）
├── 🎵 full.m3u            # M3U格式完整版
├── 📄 lite.txt            # 精简版（央视+卫视）
├── 🎵 lite.m3u            # M3U格式精简版
├── 📄 custom.txt          # 定制版（专业频道）
├── 🎵 custom.m3u          # M3U格式定制版
├── 📄 others.txt          # 未分类频道
├── 🌐 tiyu.html           # 体育赛事网页
├── 📄 tiyu.txt            # 体育赛事文本
├── 📊 statistics.json     # JSON格式统计（v2.00新增）
└── 📋 processing.log      # 处理日志（可选）
```

2. 文件大小预估

文件 大小范围 适用场景
full.txt 15-50KB 专业用户，全面覆盖
lite.txt 3-10KB 普通用户，快速加载
custom.txt 5-20KB 进阶用户，平衡选择
tiyu.html 10-30KB 体育爱好者，网页浏览
statistics.json 1-5KB 数据分析，程序处理

3. 文件格式说明

```txt
# TXT格式
🌐央视频道,#genre#        # 分组标题（频道分类）
CCTV1,http://example.com/cctv1  # 频道行（名称,URL）

# M3U格式
#EXTM3U x-tvg-url="EPG地址"      # M3U头部（EPG支持）
#EXTINF:-1 tvg-id="ID" tvg-logo="LOGO" group-title="分组",名称
http://example.com/url          # 频道URL

# JSON格式
{
  "metadata": {...},           # 元数据
  "statistics": {...},         # 统计信息
  "category_counts": {...}     # 分类统计
}
```

这个v2.00版本的脚本是一个功能完整、设计专业的直播源处理系统，具有良好的可维护性、扩展性和健壮性，适合各种规模的直播源处理需求。