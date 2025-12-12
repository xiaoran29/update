"""
LiveSource-Collector
IPTV直播源聚合处理工具 v1.01
功能：从多个来源获取直播源，进行分类、过滤、格式转换，生成播放列表
特点：基于0.00原版 优化名称、路径、注释
作者：潇然
版本：2025-9-1
"""
# ========= 模块导入区 =========
import urllib.request          # HTTP请求库，用于从网络获取直播源数据
from urllib.parse import urlparse  # URL解析工具，用于分析URL结构
import re                     # 正则表达式库，用于文本匹配和清洗
import os                     # 操作系统接口，用于文件和目录操作
from datetime import datetime, timedelta, timezone  # 日期时间处理模块
import random                 # 随机数生成，用于User-Agent轮换
import opencc                 # 简繁体转换库

import socket                 # 网络套接字库，用于网络请求
import time                   # 时间模块，用于延时和计时

# ========= 初始化输出目录 =========
os.makedirs('output', exist_ok=True)  # 创建输出目录，如果已存在则不会报错
print("创建输出目录: output")

# ========= 功能函数定义区 =========

# 简繁转换函数
def traditional_to_simplified(text: str) -> str:
    """将繁体中文转换为简体中文"""
    # 初始化转换器，"t2s"表示从繁体转为简体
    converter = opencc.OpenCC('t2s')
    simplified_text = converter.convert(text)
    return simplified_text

# 读取文本文件函数
def read_txt_to_array(file_name):
    """读取文本文件，返回非空行的数组"""
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            # 去除每行首尾空白字符，并过滤空行
            lines = [line.strip() for line in lines if line.strip()]
            return lines
    except FileNotFoundError:
        print(f"File '{file_name}' not found.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

# ========= URL处理工具函数 =========

def clean_url(url):
    """清理URL，移除$符号及其后面的内容"""
    last_dollar_index = url.rfind('$')  # 查找最后一个$符号的位置
    if last_dollar_index != -1:
        return url[:last_dollar_index]  # 截取$之前的部分
    return url

# 读取黑名单函数
def read_blacklist_from_txt(file_path):
    """读取黑名单文件，格式为'频道名称,URL'，返回URL列表（清理后）"""
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 提取逗号后面的URL部分，并去除空白字符，并清理URL（移除$及之后的部分)
    BlackList = []
    for line in lines:
        if ',' in line:
            url = line.split(',')[1].strip()
            cleaned_url = clean_url(url)  # 关键：黑名单URL也需要清理
            BlackList.append(cleaned_url)
    return BlackList

# ========= 黑名单初始化 =========
blacklist_auto = read_blacklist_from_txt('assets/livesource/blacklist/blacklist_auto.txt') 
blacklist_manual = read_blacklist_from_txt('assets/livesource/blacklist/blacklist_manual.txt') 
# 合并自动和手动黑名单，使用集合提高检索速度
combined_blacklist = set(blacklist_auto + blacklist_manual)

# ========= 频道分类存储变量定义 =========
# 说明：以下是用于存储不同分类频道的列表变量

# 核心频道（优先级最高）
yangshi_lines = []      # 存储央视频道数据
weishi_lines = []       # 存储卫视频道数据

# 省级地方台频道
beijing_lines = []      # 北京
shanghai_lines = []     # 上海
guangdong_lines = []    # 广东
jiangsu_lines = []      # 江苏
zhejiang_lines = []     # 浙江
shandong_lines = []     # 山东
sichuan_lines = []      # 四川
henan_lines = []        # 河南
hunan_lines = []        # 湖南
chongqing_lines = []    # 重庆
tianjin_lines = []      # 天津
hubei_lines = []        # 湖北
anhui_lines = []        # 安徽
fujian_lines = []       # 福建
liaoning_lines = []     # 辽宁
shaanxi_lines = []      # 陕西
hebei_lines = []        # 河北
jiangxi_lines = []      # 江西
guangxi_lines = []      # 广西
yunnan_lines = []       # 云南
shanxi_lines = []      # 山西
heilongjiang_lines = [] # 黑龙江
jilin_lines = []        # 吉林
guizhou_lines = []      # 贵州
gansu_lines = []        # 甘肃
neimenggu_lines = []    # 内蒙古
xinjiang_lines = []     # 新疆
hainan_lines = []       # 海南
ningxia_lines = []      # 宁夏
qinghai_lines = []      # 青海
xizang_lines = []       # 西藏

# 港澳台频道
hongkong_lines = []    # 香港
macau_lines = []       # 澳门
minnan_lines = []      # 闽南

# 其他分类频道
digital_lines = []     # 数字
movie_lines = []       # 电影
tv_drama_lines = []    # 电视剧
documentary_lines = [] # 纪录片
cartoon_lines = []     # 动画片
radio_lines = []       # 收音机
variety_lines = []     # 综艺
huya_lines = []        # 虎牙
douyu_lines = []       # 斗鱼
commentary_lines = []  # 解说
music_lines = []       # 音乐
food_lines = []        # 美食
travel_lines = []      # 旅游
health_lines = []      # 健康
finance_lines = []     # 财经
shopping_lines = []    # 购物
game_lines = []        # 游戏
news_lines = []        # 新闻
china_lines = []       # 中国
international_lines = [] # 国际
sports_lines = []      # 体育
tyss_lines = []        # 体育赛事（2025新增）
mgss_lines = []        # 咪咕赛事（2025新增）
traditional_opera_lines = [] # 戏曲频道
spring_festival_gala_lines = [] # 历届春晚
camera_lines = []      # 景区直播（直播中国）
favorite_lines = []    # 收藏频道

# 未分类频道（兜底处理）
other_lines = []
# ========= 新增：全局URL去重集合 =========
processed_urls = set()  # 用于记录已处理的URL，全局去重

# ========= 频道名称处理函数 =========

def process_name_string(input_str):
    """处理频道名称字符串，统一命名格式"""
    parts = input_str.split(',')
    processed_parts = []
    for part in parts:
        processed_part = process_part(part)
        processed_parts.append(processed_part)
    result_str = ','.join(processed_parts)
    return result_str

def process_part(part_str):
    """处理单个频道名称部分，统一CCTV和卫视格式"""
    # 处理CCTV频道名称
    if "CCTV" in part_str and "://" not in part_str:
        # 先剔除特定关键字
        part_str = part_str.replace("IPV6", "")
        part_str = part_str.replace("PLUS", "+")
        part_str = part_str.replace("1080", "")
        # 只保留数字、K和+号
        filtered_str = ''.join(char for char in part_str if char.isdigit() or char == 'K' or char == '+')
        # 处理特殊情况：如果没有找到频道数字，返回原名称（去掉CCTV）
        if not filtered_str.strip():
            filtered_str = part_str.replace("CCTV", "")

        # 特殊处理CCTV中的4K和8K名称
        if len(filtered_str) > 2 and re.search(r'4K|8K', filtered_str):
            # 删除4K或8K后面的字符，保留4K或8K
            filtered_str = re.sub(r'(4K|8K).*', r'\1', filtered_str)
            if len(filtered_str) > 2: 
                # 给4K或8K添加括号
                filtered_str = re.sub(r'(4K|8K)', r'(\1)', filtered_str)

        return "CCTV" + filtered_str 
        
    # 处理卫视频道名称
    elif "卫视" in part_str:
        # 匹配"卫视「.*」"模式，替换为"卫视"
        pattern = r'卫视「.*」'
        result_str = re.sub(pattern, '卫视', part_str)
        return result_str

    return part_str

# ========= 文件格式处理函数 =========

def get_url_file_extension(url):
    """获取URL的文件扩展名"""
    # 解析URL获取路径部分
    parsed_url = urlparse(url)
    path = parsed_url.path
    # 提取文件扩展名
    extension = os.path.splitext(path)[1]
    return extension

def convert_m3u_to_txt(m3u_content):
    """将M3U格式转换为TXT格式（频道名称,URL）"""
    # 按行分割M3U内容
    lines = m3u_content.split('\n')
    
    # 存储转换结果的列表
    txt_lines = []
    # 临时变量存储频道名称
    channel_name = ""

    for line in lines:
        # 跳过M3U头信息
        if line.startswith("#EXTM3U"):
            continue
        # 处理频道信息行
        if line.startswith("#EXTINF"):
            # 提取频道名称（通常在最后一个逗号后面）
            channel_name = line.split(',')[-1].strip()
        # 处理URL行
        elif line.startswith("http") or line.startswith("rtmp") or line.startswith("p3p"):
            txt_lines.append(f"{channel_name},{line.strip()}")

        # 处理格式为TXT但后缀为M3U的文件
        if "#genre#" not in line and "," in line and "://" in line:
            # 匹配格式：频道名称,http://xxx.xxx.xxx
            pattern = r'^[^,]+,[^\s]+://[^\s]+$'
            if bool(re.match(pattern, line)):
                txt_lines.append(line)

    # 返回转换后的TXT格式字符串
    return '\n'.join(txt_lines)

# 频道名称清理关键字列表
removal_list = ["_电信","电信","「LiTV」","频道","频陆","备陆","壹陆","贰陆","叁陆","肆陆","伍陆","陆陆","柒陆",
                "频晴","频粤","高清","超清","标清","斯特","粤陆","国陆","肆柒","频英","频特","频国","频壹",
                "频贰","肆贰","频测","咪咕","闽特","高特","频高","频标","汝阳","频效","国标","粤标","频推",
                "频流","粤高","频限","实时","美推","频美","（HD）","-HD","英陆","_ITV","(北美)","(HK)",
                "AKtv","「IPV4」","「IPV6」","[HD]","[BD]","[SD]","[VGA]","[超清]","4Gtv","1080","720",
                "480","HD","SD","4K","VGA","(HD)","(SD)","(4K)","(VGA)","{HD}","{SD}","{4K}","{VGA}",
                "「4gTV」","「回看」","<HD>","<SD>","<4K>","<VGA>"]

def clean_channel_name(channel_name, removal_list):
    """清理频道名称中的特定字符"""
    for item in removal_list:
        channel_name = channel_name.replace(item, "")

    # 移除末尾的'HD'
    if channel_name.endswith("HD"):
        channel_name = channel_name[:-2]  # 去掉最后两个字符"HD"

    # 移除末尾的'台'（如果频道名称长度大于3）
    if channel_name.endswith("台") and len(channel_name) > 3:
        channel_name = channel_name[:-1]  # 去掉最后一个字符"台"

    return channel_name

# ========= 频道分发核心函数（优化版） =========

def process_channel_line(line):
    """处理单行频道数据，进行分类分发"""
    # 检查是否为有效的频道行（包含频道名称和URL，且不是分组标题）
    if "#genre#" not in line and "#EXTINF:" not in line and "," in line and "://" in line:
        # 分割频道名称和URL
        parts = line.split(',', 1)
        if len(parts) < 2:
            return
        
        channel_name = parts[0].strip()
        channel_address = parts[1].strip()
        
        # ========== 优化1：提前清理URL ==========
        channel_address = clean_url(channel_address)
        
        # ========== 优化2：提前黑名单检查 ==========
        if channel_address in combined_blacklist:
            return
        
        # ========== 优化3：全局URL去重 ==========
        if channel_address in processed_urls:
            return
        processed_urls.add(channel_address)
        
        # 清理频道名称中的特定字符
        channel_name = clean_channel_name(channel_name, removal_list)
        # 繁体转简体
        channel_name = traditional_to_simplified(channel_name)

        # ========== 新增：频道名称纠错 ==========
        if channel_name in corrections_name:
            channel_name = corrections_name[channel_name]
        # ======================================

        # 重新组合行
        line = channel_name + "," + channel_address
        
        # 根据频道名称判断分类并分发（保持原有逻辑，但移除黑名单检查）
        # 1. 央视
        if "CCTV" in channel_name:
            yangshi_lines.append(process_name_string(line.strip()))
        # 2. 卫视
        elif channel_name in weishi_dictionary:
            weishi_lines.append(process_name_string(line.strip()))
        # 3. 北京
        elif channel_name in beijing_dictionary:
            beijing_lines.append(process_name_string(line.strip()))
        # 4. 上海
        elif channel_name in shanghai_dictionary:
            shanghai_lines.append(process_name_string(line.strip()))
        # 5. 广东
        elif channel_name in guangdong_dictionary:
            guangdong_lines.append(process_name_string(line.strip()))
        # 6. 江苏
        elif channel_name in jiangsu_dictionary:
            jiangsu_lines.append(process_name_string(line.strip()))
        # 7. 浙江
        elif channel_name in zhejiang_dictionary:
            zhejiang_lines.append(process_name_string(line.strip()))
        # 8. 山东
        elif channel_name in shandong_dictionary:
            shandong_lines.append(process_name_string(line.strip()))
        # 9. 四川
        elif channel_name in sichuan_dictionary:
            sichuan_lines.append(process_name_string(line.strip()))
        # 10. 河南
        elif channel_name in henan_dictionary:
            henan_lines.append(process_name_string(line.strip()))
        # 11. 湖南
        elif channel_name in hunan_dictionary:
            hunan_lines.append(process_name_string(line.strip()))
        # 12. 重庆
        elif channel_name in chongqing_dictionary:
            chongqing_lines.append(process_name_string(line.strip()))
        # 13. 天津
        elif channel_name in tianjin_dictionary:
            tianjin_lines.append(process_name_string(line.strip()))
        # 14. 湖北
        elif channel_name in hubei_dictionary:
            hubei_lines.append(process_name_string(line.strip()))
        # 15. 安徽
        elif channel_name in anhui_dictionary:
            anhui_lines.append(process_name_string(line.strip()))
        # 16. 福建
        elif channel_name in fujian_dictionary:
            fujian_lines.append(process_name_string(line.strip()))
        # 17. 辽宁
        elif channel_name in liaoning_dictionary:
            liaoning_lines.append(process_name_string(line.strip()))
        # 18. 陕西
        elif channel_name in shaanxi_dictionary:
            shaanxi_lines.append(process_name_string(line.strip()))
        # 19. 河北
        elif channel_name in hebei_dictionary:
            hebei_lines.append(process_name_string(line.strip()))
        # 20. 江西
        elif channel_name in jiangxi_dictionary:
            jiangxi_lines.append(process_name_string(line.strip()))
        # 21. 广西
        elif channel_name in guangxi_dictionary:
            guangxi_lines.append(process_name_string(line.strip()))
        # 22. 云南
        elif channel_name in yunnan_dictionary:
            yunnan_lines.append(process_name_string(line.strip()))
        # 23. 山西
        elif channel_name in shanxi_dictionary:
            shanxi_lines.append(process_name_string(line.strip()))
        # 24. 黑龙江
        elif channel_name in heilongjiang_dictionary:
            heilongjiang_lines.append(process_name_string(line.strip()))
        # 25. 吉林
        elif channel_name in jilin_dictionary:
            jilin_lines.append(process_name_string(line.strip()))
        # 26. 贵州
        elif channel_name in guizhou_dictionary:
            guizhou_lines.append(process_name_string(line.strip()))
        # 27. 甘肃
        elif channel_name in gansu_dictionary:
            gansu_lines.append(process_name_string(line.strip()))
        # 28. 内蒙古
        elif channel_name in neimenggu_dictionary:
            neimenggu_lines.append(process_name_string(line.strip()))
        # 29. 新疆
        elif channel_name in xinjiang_dictionary:
            xinjiang_lines.append(process_name_string(line.strip()))
        # 30. 海南
        elif channel_name in hainan_dictionary:
            hainan_lines.append(process_name_string(line.strip()))
        # 31. 宁夏
        elif channel_name in ningxia_dictionary:
            ningxia_lines.append(process_name_string(line.strip()))
        # 32. 青海
        elif channel_name in qinghai_dictionary:
            qinghai_lines.append(process_name_string(line.strip()))
        # 33. 西藏
        elif channel_name in xizang_dictionary:
            xizang_lines.append(process_name_string(line.strip()))
        # 34. 香港
        elif channel_name in hongkong_dictionary:
            hongkong_lines.append(process_name_string(line.strip()))
        # 35. 澳门
        elif channel_name in macau_dictionary:
            macau_lines.append(process_name_string(line.strip()))
        # 36. 闽南
        elif channel_name in minnan_dictionary:
            minnan_lines.append(process_name_string(line.strip()))
        # 37. 数字
        elif channel_name in digital_dictionary:
            digital_lines.append(process_name_string(line.strip()))
        # 38. 电影
        elif channel_name in movie_dictionary:
            movie_lines.append(process_name_string(line.strip()))
        # 39. 电视剧
        elif channel_name in tv_drama_dictionary:
            tv_drama_lines.append(process_name_string(line.strip()))
        # 40. 纪录片
        elif channel_name in documentary_dictionary:
            documentary_lines.append(process_name_string(line.strip()))
        # 41. 动画片
        elif channel_name in cartoon_dictionary:
            cartoon_lines.append(process_name_string(line.strip()))
        # 42. 收音机
        elif channel_name in radio_dictionary:
            radio_lines.append(process_name_string(line.strip()))
        # 43. 综艺
        elif channel_name in variety_dictionary:
            variety_lines.append(process_name_string(line.strip()))
        # 44. 虎牙
        elif channel_name in huya_dictionary:
            huya_lines.append(process_name_string(line.strip()))
        # 45. 斗鱼
        elif channel_name in douyu_dictionary:
            douyu_lines.append(process_name_string(line.strip()))
        # 46. 解说
        elif channel_name in commentary_dictionary:
            commentary_lines.append(process_name_string(line.strip()))
        # 47. 音乐
        elif channel_name in music_dictionary:
            music_lines.append(process_name_string(line.strip()))
        # 48. 美食
        elif channel_name in food_dictionary:
            food_lines.append(process_name_string(line.strip()))
        # 49. 旅游
        elif channel_name in travel_dictionary:
            travel_lines.append(process_name_string(line.strip()))
        # 50. 健康
        elif channel_name in health_dictionary:
            health_lines.append(process_name_string(line.strip()))
        # 51. 财经
        elif channel_name in finance_dictionary:
            finance_lines.append(process_name_string(line.strip()))
        # 52. 购物
        elif channel_name in shopping_dictionary:
            shopping_lines.append(process_name_string(line.strip()))
        # 53. 游戏
        elif channel_name in game_dictionary:
            game_lines.append(process_name_string(line.strip()))
        # 54. 新闻频道
        elif channel_name in news_dictionary:
            news_lines.append(process_name_string(line.strip()))
        # 55. 中国频道
        elif channel_name in china_dictionary:
            china_lines.append(process_name_string(line.strip()))
        # 56. 国际频道
        elif channel_name in international_dictionary:
            international_lines.append(process_name_string(line.strip()))
        # 57. 体育频道
        elif channel_name in sports_dictionary:
            sports_lines.append(process_name_string(line.strip()))
        # 58. 体育赛事（2025新增）
        elif any(keyword in channel_name for keyword in tyss_dictionary):
            tyss_lines.append(process_name_string(line.strip()))
        # 59. 咪咕赛事（2025新增）
        elif any(keyword in channel_name for keyword in mgss_dictionary):
            mgss_lines.append(process_name_string(line.strip()))
        # 60. 戏曲频道
        elif channel_name in traditional_opera_dictionary:
            traditional_opera_lines.append(process_name_string(line.strip()))
        # 61. 历届春晚
        elif channel_name in spring_festival_gala_dictionary:
            spring_festival_gala_lines.append(process_name_string(line.strip()))
        # 62. 景区直播
        elif channel_name in camera_dictionary:
            camera_lines.append(process_name_string(line.strip()))
        # 63. 收藏频道
        elif channel_name in favorite_dictionary:
            favorite_lines.append(process_name_string(line.strip()))
        else:
            other_lines.append(line.strip())

# ========= HTTP请求处理函数 =========

def get_random_user_agent():
    """随机获取User-Agent，用于HTTP请求头"""
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    ]
    return random.choice(USER_AGENTS)

def process_url(url):
    """处理单个URL，获取并解析直播源数据"""
    try:
        # 记录处理的URL，便于调试
        other_lines.append("◆◆◆　" + url)
        # 创建HTTP请求对象并添加自定义header
        req = urllib.request.Request(url)
        req.add_header('User-Agent', get_random_user_agent())

        # 发送HTTP请求并获取响应
        with urllib.request.urlopen(req) as response:
            # 以二进制方式读取数据
            data = response.read()
            # 将二进制数据解码为UTF-8字符串
            text = data.decode('utf-8')
            text = text.strip()

            # 检查是否为M3U格式文件
            is_m3u = text.startswith("#EXTM3U") or text.startswith("#EXTINF")
            if get_url_file_extension(url) == ".m3u" or get_url_file_extension(url) == ".m3u8" or is_m3u:
                # 将M3U格式转换为TXT格式
                text = convert_m3u_to_txt(text)

            # 逐行处理内容
            lines = text.split('\n')
            print(f"行数: {len(lines)}")
            
            for line in lines:
                # 过滤无效行：不是分组标题，包含逗号和URL，且不是tvbus或组播地址
                if "#genre#" not in line and "," in line and "://" in line and "tvbus://" not in line and "/udp/" not in line:
                    # 分割频道名称和URL
                    parts = line.split(',', 1)
                    if len(parts) < 2:
                        continue
                    
                    channel_name, channel_address = parts[0], parts[1]
                    
                    # 处理加速源（包含#号分隔的多个URL）
                    if "#" not in channel_address:
                        # 普通源，直接处理
                        process_channel_line(line)
                    else: 
                        # 加速源，按#号分割为多个URL分别处理
                        url_list = channel_address.split('#')
                        for channel_url in url_list:
                            if channel_url.strip():  # 跳过空URL
                                newline = f'{channel_name},{channel_url}'
                                process_channel_line(newline)

            # 每个URL处理完成后添加空行分隔
            other_lines.append('\n')

    except Exception as e:
        print(f"处理URL时发生错误：{e}")

# ========= 频道字典文件读取 =========

current_directory = os.getcwd()  # 获取当前工作目录

# 读取核心频道字典
yangshi_dictionary = read_txt_to_array('assets/livesource/主频道/CCTV.txt')  # 仅排序用
weishi_dictionary = read_txt_to_array('assets/livesource/主频道/卫视.txt')   # 过滤+排序

# 读取省级地方台字典
beijing_dictionary = read_txt_to_array('assets/livesource/地方台/北京.txt')
shanghai_dictionary = read_txt_to_array('assets/livesource/地方台/上海.txt')
guangdong_dictionary = read_txt_to_array('assets/livesource/地方台/广东.txt')
jiangsu_dictionary = read_txt_to_array('assets/livesource/地方台/江苏.txt')
zhejiang_dictionary = read_txt_to_array('assets/livesource/地方台/浙江.txt')
shandong_dictionary = read_txt_to_array('assets/livesource/地方台/山东.txt')
sichuan_dictionary = read_txt_to_array('assets/livesource/地方台/四川.txt')
henan_dictionary = read_txt_to_array('assets/livesource/地方台/河南.txt')
hunan_dictionary = read_txt_to_array('assets/livesource/地方台/湖南.txt')
chongqing_dictionary = read_txt_to_array('assets/livesource/地方台/重庆.txt')
tianjin_dictionary = read_txt_to_array('assets/livesource/地方台/天津.txt')
hubei_dictionary = read_txt_to_array('assets/livesource/地方台/湖北.txt')
anhui_dictionary = read_txt_to_array('assets/livesource/地方台/安徽.txt')
fujian_dictionary = read_txt_to_array('assets/livesource/地方台/福建.txt')
liaoning_dictionary = read_txt_to_array('assets/livesource/地方台/辽宁.txt')
shaanxi_dictionary = read_txt_to_array('assets/livesource/地方台/陕西.txt')
hebei_dictionary = read_txt_to_array('assets/livesource/地方台/河北.txt')
jiangxi_dictionary = read_txt_to_array('assets/livesource/地方台/江西.txt')
guangxi_dictionary = read_txt_to_array('assets/livesource/地方台/广西.txt')
yunnan_dictionary = read_txt_to_array('assets/livesource/地方台/云南.txt')
shanxi_dictionary = read_txt_to_array('assets/livesource/地方台/山西.txt')
heilongjiang_dictionary = read_txt_to_array('assets/livesource/地方台/黑龙江.txt')
jilin_dictionary = read_txt_to_array('assets/livesource/地方台/吉林.txt')
guizhou_dictionary = read_txt_to_array('assets/livesource/地方台/贵州.txt')
gansu_dictionary = read_txt_to_array('assets/livesource/地方台/甘肃.txt')
neimenggu_dictionary = read_txt_to_array('assets/livesource/地方台/内蒙.txt')
xinjiang_dictionary = read_txt_to_array('assets/livesource/地方台/新疆.txt')
hainan_dictionary = read_txt_to_array('assets/livesource/地方台/海南.txt')
ningxia_dictionary = read_txt_to_array('assets/livesource/地方台/宁夏.txt')
qinghai_dictionary = read_txt_to_array('assets/livesource/地方台/青海.txt')
xizang_dictionary = read_txt_to_array('assets/livesource/地方台/西藏.txt')

# 读取港澳台地区字典
hongkong_dictionary = read_txt_to_array('assets/livesource/地方台/香港.txt')
macau_dictionary = read_txt_to_array('assets/livesource/地方台/澳门.txt')
minnan_dictionary = read_txt_to_array('assets/livesource/地方台/闽南.txt')

# 读取其他分类字典
digital_dictionary = read_txt_to_array('assets/livesource/主频道/数字.txt')
movie_dictionary = read_txt_to_array('assets/livesource/主频道/电影.txt')
tv_drama_dictionary = read_txt_to_array('assets/livesource/主频道/电视剧.txt')
documentary_dictionary = read_txt_to_array('assets/livesource/主频道/纪录片.txt')
cartoon_dictionary = read_txt_to_array('assets/livesource/主频道/动画片.txt')
radio_dictionary = read_txt_to_array('assets/livesource/主频道/收音机.txt')
variety_dictionary = read_txt_to_array('assets/livesource/主频道/综艺.txt')
huya_dictionary = read_txt_to_array('assets/livesource/主频道/虎牙.txt')
douyu_dictionary = read_txt_to_array('assets/livesource/主频道/斗鱼.txt')
commentary_dictionary = read_txt_to_array('assets/livesource/主频道/解说.txt')
music_dictionary = read_txt_to_array('assets/livesource/主频道/音乐.txt')
food_dictionary = read_txt_to_array('assets/livesource/主频道/美食.txt')
travel_dictionary = read_txt_to_array('assets/livesource/主频道/旅游.txt')
health_dictionary = read_txt_to_array('assets/livesource/主频道/健康.txt')
finance_dictionary = read_txt_to_array('assets/livesource/主频道/财经.txt')
shopping_dictionary = read_txt_to_array('assets/livesource/主频道/购物.txt')
game_dictionary = read_txt_to_array('assets/livesource/主频道/游戏.txt')
news_dictionary = read_txt_to_array('assets/livesource/主频道/新闻.txt')
china_dictionary = read_txt_to_array('assets/livesource/主频道/中国.txt')
international_dictionary = read_txt_to_array('assets/livesource/主频道/国际.txt')
sports_dictionary = read_txt_to_array('assets/livesource/主频道/体育.txt')
tyss_dictionary = read_txt_to_array('assets/livesource/主频道/体育赛事.txt')
mgss_dictionary = read_txt_to_array('assets/livesource/主频道/咪咕赛事.txt')
traditional_opera_dictionary = read_txt_to_array('assets/livesource/主频道/戏曲.txt')
spring_festival_gala_dictionary = read_txt_to_array('assets/livesource/主频道/春晚.txt')
camera_dictionary = read_txt_to_array('assets/livesource/主频道/直播中国.txt')
favorite_dictionary = read_txt_to_array('assets/livesource/主频道/收藏频道.txt')

# ========= 频道名称纠错处理 =========

def load_corrections_name(filename):
    """加载频道名称纠错字典"""
    corrections = {}
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():  # 跳过空行
                continue
            parts = line.strip().split(',')
            correct_name = parts[0]
            for name in parts[1:]:
                corrections[name] = correct_name
    return corrections

# 读取纠错文件
corrections_name = load_corrections_name('assets/livesource/corrections_name.txt')

def correct_name_data(corrections, data):
    """使用纠错字典修正频道名称"""
    corrected_data = []
    for line in data:
        line = line.strip()
        if ',' not in line:
            # 行格式错误：跳过
            continue

        name, url = line.split(',', 1)

        # 应用纠错：如果名称在纠错字典中，且与正确名称不同，则替换
        if name in corrections and name != corrections[name]:
            name = corrections[name]

        corrected_data.append(f"{name},{url}")
    return corrected_data

def sort_data(order, data):
    """按指定顺序对数据进行排序"""
    # 创建名称到索引的映射字典
    order_dict = {name: i for i, name in enumerate(order)}

    # 定义排序键函数
    def sort_key(line):
        name = line.split(',')[0]
        return order_dict.get(name, len(order))  # 不在字典中的名称排在最后

    # 按照order中的顺序对数据进行排序
    sorted_data = sorted(data, key=sort_key)
    return sorted_data

# ========= 主处理流程 =========

# 记录执行开始时间
timestart = datetime.now()
print(f"开始时间: {datetime.now().strftime('%Y%m%d_%H_%M_%S')}")

# 读取URL列表
urls = read_txt_to_array('assets/livesource/urls-daily.txt')

# 处理每个URL
for url in urls:
    if url.startswith("http"):
        # 处理日期变量（特别处理113格式的URL）
        if "{MMdd}" in url:
            current_date_str = datetime.now().strftime("%m%d")
            url = url.replace("{MMdd}", current_date_str)

        if "{MMdd-1}" in url:
            yesterday_date_str = (datetime.now() - timedelta(days=1)).strftime("%m%d")
            url = url.replace("{MMdd-1}", yesterday_date_str)
            
        print(f"处理URL: {url}")
        process_url(url)

# ========= 白名单处理（优化：移除重复的check_url_existence） =========

print(f"添加白名单...")
whitelist_auto_lines = read_txt_to_array('assets/livesource/blacklist/whitelist_auto.txt')
for whitelist_line in whitelist_auto_lines:
    if "#genre#" not in whitelist_line and "," in whitelist_line and "://" in whitelist_line:
        whitelist_parts = whitelist_line.split(",")
        try:
            # 提取响应时间（毫秒）
            response_time = float(whitelist_parts[0].replace("ms", ""))
        except ValueError:
            print(f"response_time转换失败: {whitelist_line}")
            response_time = 60000  # 转换失败时设为60秒
        
        # 只添加响应时间小于2秒的高质量源
        if response_time < 2000:
            process_channel_line(",".join(whitelist_parts[1:]))

# ========= HTTP响应测试函数 =========

def get_http_response(url, timeout=8, retries=2, backoff_factor=1.0):
    """获取HTTP响应，支持重试机制"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                data = response.read()
                return data.decode('utf-8')
        except urllib.error.HTTPError as e:
            print(f"[HTTPError] Code: {e.code}, URL: {url}")
            break  # HTTP错误通常不会在重试中恢复
        except urllib.error.URLError as e:
            print(f"[URLError] Reason: {e.reason}, Attempt: {attempt + 1}")
        except socket.timeout:
            print(f"[Timeout] URL: {url}, Attempt: {attempt + 1}")
        except Exception as e:
            print(f"[Exception] {type(e).__name__}: {e}, Attempt: {attempt + 1}")
        
        # 指数退避重试：等待时间逐渐增加
        if attempt < retries - 1:
            time.sleep(backoff_factor * (2 ** attempt))

    return None  # 所有尝试失败后返回None

# ========= 体育赛事日期格式化 =========

def normalize_date_to_md(text):
    """将各种日期格式统一为MM-DD格式"""
    text = text.strip()

    # 定义替换函数
    def format_md(m):
        month = int(m.group(1))
        day = int(m.group(2))
        after = m.group(3) or ''
        # 如果后面不是空格开头，就添加空格
        if not after.startswith(' '):
            after = ' ' + after
        return f"{month:02d}-{day:02d}{after}"

    # MM/DD或M/D格式
    text = re.sub(r'^0?(\d{1,2})/0?(\d{1,2})(.*)', format_md, text)

    # YYYY-MM-DD或类似格式
    text = re.sub(r'^\d{4}-0?(\d{1,2})-0?(\d{1,2})(.*)', format_md, text)

    # 中文M月D日格式
    text = re.sub(r'^0?(\d{1,2})月0?(\d{1,2})日(.*)', format_md, text)

    return text

# 对体育赛事日期进行统一格式化
normalized_tyss_lines = [normalize_date_to_md(s) for s in tyss_lines]

# ========= AKTV特殊处理 =========

aktv_lines = []  # 存储AKTV频道数据
aktv_url = "https://aktv.space/live.m3u"  # AKTV源地址

# 尝试从网络获取AKTV源
aktv_text = get_http_response(aktv_url)
if aktv_text:
    print("AKTV成功获取内容")
    aktv_text = convert_m3u_to_txt(aktv_text)
    aktv_lines = aktv_text.strip().split('\n')
else:
    print("AKTV请求失败，从本地获取！")
    aktv_lines = read_txt_to_array('assets/livesource/手工区/AKTV.txt')

# 处理AKTV数据
for line in aktv_lines:
    process_channel_line(line)

# ========= 数据过滤函数 =========

def filter_lines(lines, exclude_keywords):
    """过滤包含特定关键词的行"""
    return [line for line in lines if not any(keyword in line for keyword in exclude_keywords)]

# ========= 生成HTML播放列表 =========

def generate_playlist_html(data_list, output_file='playlist.html'):
    """生成HTML格式的播放列表"""
    html_head = '''
    <!DOCTYPE html>
    <html lang="zh">
    <head>
        <meta charset="UTF-8">        
        <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6061710286208572"
     crossorigin="anonymous"></script>
        <!-- Setup Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-BS1Z4F5BDN"></script>
        <script> 
        window.dataLayer = window.dataLayer || []; 
        function gtag(){dataLayer.push(arguments);} 
        gtag('js', new Date()); 
        gtag('config', 'G-BS1Z4F5BDN'); 
        </script>
        <title>最新体育赛事</title>
        <style>
            body { font-family: sans-serif; padding: 20px; background: #f9f9f9; }
            .item { margin-bottom: 20px; padding: 12px; background: #fff; border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.06); }
            .title { font-weight: bold; font-size: 1.1em; color: #333; margin-bottom: 5px; }
            .url-wrapper { display: flex; align-items: center; gap: 10px; }
            .url {
                max-width: 80%;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                font-size: 0.9em;
                color: #555;
                background: #f0f0f0;
                padding: 6px;
                border-radius: 4px;
                flex-grow: 1;
            }
            .copy-btn {
                background-color: #007BFF;
                border: none;
                color: white;
                padding: 6px 10px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 0.8em;
            }
            .copy-btn:hover {
                background-color: #0056b3;
            }
        </style>
    </head>
    <body>
    <h2>📋 最新体育赛事列表</h2>
    '''

    html_body = ''
    for idx, entry in enumerate(data_list):
        if ',' not in entry:
            continue
        info, url = entry.split(',', 1)
        url_id = f"url_{idx}"
        html_body += f'''
        <div class="item">
            <div class="title">🕒 {info}</div>
            <div class="url-wrapper">
                <div class="url" id="{url_id}">{url}</div>
                <button class="copy-btn" onclick="copyToClipboard('{url_id}')">复制</button>
            </div>
        </div>
        '''

    html_tail = '''
    <script>
        function copyToClipboard(id) {
            const el = document.getElementById(id);
            const text = el.textContent;
            navigator.clipboard.writeText(text).then(() => {
                alert("已复制链接！");
            }).catch(err => {
                alert("复制失败: " + err);
            });
        }
    </script>
    </body>
    </html>
    '''

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_head + html_body + html_tail)
    print(f"✅ 网页已生成：{output_file}")

# ========= 体育赛事专用排序 =========

def custom_tyss_sort(lines):
    """体育赛事专用排序：数字开头倒序排在上面，其他升序排在下面"""
    digit_prefix = []
    others = []

    for line in lines:
        # 拆分出名称部分（逗号前部分）
        name_part = line.split(',')[0].strip()
        if name_part and name_part[0].isdigit():
            digit_prefix.append(line)
        else:
            others.append(line)

    # 分别排序：数字开头倒序，其他升序
    digit_prefix_sorted = sorted(digit_prefix, reverse=True)
    others_sorted = sorted(others)

    return digit_prefix_sorted + others_sorted

# ========= 体育赛事数据过滤和生成 =========

# 过滤关键词定义
keywords_to_exclude_tiyu_txt = ["玉玉软件", "榴芒电视", "公众号", "麻豆", "「回看」"]
keywords_to_exclude_tiyu = ["玉玉软件", "榴芒电视", "公众号", "咪视通", "麻豆", "「回看」"]

# 应用过滤和排序
normalized_tyss_lines = filter_lines(normalized_tyss_lines, keywords_to_exclude_tiyu_txt)
normalized_tyss_lines = custom_tyss_sort(set(normalized_tyss_lines))
filtered_tyss_lines = filter_lines(normalized_tyss_lines, keywords_to_exclude_tiyu)

# 生成HTML页面
generate_playlist_html(filtered_tyss_lines, 'output/tiyu.html')

# 生成TXT文件
with open('output/tiyu.txt', 'w', encoding='utf-8') as f:
    for line in filtered_tyss_lines:
        f.write(line + '\n')
print(f"体育赛事文本已保存到文件: tiyu.txt")

# ========= 随机URL获取函数 =========

def get_random_url(file_path):
    """从文件中随机获取一个URL"""
    urls = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # 查找逗号后面的部分，即URL
            url = line.strip().split(',')[-1]
            urls.append(url)    
    # 随机返回一个URL
    return random.choice(urls) if urls else None

# ========= 今日推荐和版本信息 =========

# 获取北京时间
utc_time = datetime.now(timezone.utc)
beijing_time = utc_time + timedelta(hours=8)
formatted_time = beijing_time.strftime("%Y%m%d %H:%M:%S")

# 生成今日推荐信息
MTV1 = "💯推荐," + get_random_url('assets/livesource/手工区/今日推荐.txt')
MTV2 = "🤫低调," + get_random_url('assets/livesource/手工区/今日推荐.txt')
MTV3 = "🟢使用," + get_random_url('assets/livesource/手工区/今日推荐.txt')
MTV4 = "⚠️禁止," + get_random_url('assets/livesource/手工区/今日推荐.txt')
MTV5 = "🚫贩卖," + get_random_url('assets/livesource/手工区/今日推荐.txt')

about_video1 = "https://gitee.com/xiaoran67/update/raw/master/assets/livesource/about1080p.mp4"
about_video2 = "https://gitlab.com/xiaoran67/update/-/raw/main/assets/livesource/about1080p.mp4"

# 生成版本信息
version = formatted_time + "," + get_random_url('assets/livesource/手工区/今日推台.txt')
about = "👨潇然," + get_random_url('assets/livesource/手工区/今日推台.txt')

# ========= 手工区数据补充 =========

print(f"处理手工区...")
# 补充手工维护的频道数据
zhejiang_lines = zhejiang_lines + read_txt_to_array('assets/livesource/手工区/浙江频道.txt')
guangdong_lines = guangdong_lines + read_txt_to_array('assets/livesource/手工区/广东频道.txt')
hubei_lines = hubei_lines + read_txt_to_array('assets/livesource/手工区/湖北频道.txt')
shanghai_lines = shanghai_lines + read_txt_to_array('assets/livesource/手工区/上海频道.txt')
jiangsu_lines = jiangsu_lines + read_txt_to_array('assets/livesource/手工区/江苏频道.txt')

# ========= 生成最终播放列表文件 =========

# 完整版播放列表（包含所有分类）
all_lines_full = ["🌐央视频道,#genre#"] + sort_data(yangshi_dictionary,correct_name_data(corrections_name,yangshi_lines)) + ['\n'] + \
        ["📡卫视频道,#genre#"] + sort_data(weishi_dictionary,correct_name_data(corrections_name,weishi_lines)) + ['\n'] + \
        ["🏛️北京频道,#genre#"] + sort_data(beijing_dictionary,correct_name_data(corrections_name,beijing_lines)) + ['\n'] + \
        ["🏙️上海频道,#genre#"] + sort_data(shanghai_dictionary,correct_name_data(corrections_name,shanghai_lines)) + ['\n'] + \
        ["🐯广东频道,#genre#"] + sort_data(guangdong_dictionary,correct_name_data(corrections_name,guangdong_lines)) + ['\n'] + \
        ["🎐江苏频道,#genre#"] + sort_data(jiangsu_dictionary,correct_name_data(corrections_name,jiangsu_lines)) + ['\n'] + \
        ["🧵浙江频道,#genre#"] + sort_data(zhejiang_dictionary,correct_name_data(corrections_name,zhejiang_lines)) + ['\n'] + \
        ["⛰️山东频道,#genre#"] + sort_data(shandong_dictionary,correct_name_data(corrections_name,shandong_lines)) + ['\n'] + \
        ["🐼四川频道,#genre#"] + sort_data(sichuan_dictionary,correct_name_data(corrections_name,sichuan_lines)) + ['\n'] + \
        ["🐘河南频道,#genre#"] + sort_data(henan_dictionary,correct_name_data(corrections_name,henan_lines)) + ['\n'] + \
        ["🌶️湖南频道,#genre#"] + sort_data(hunan_dictionary,correct_name_data(corrections_name,hunan_lines)) + ['\n'] + \
        ["🏞️重庆频道,#genre#"] + sort_data(chongqing_dictionary,correct_name_data(corrections_name,chongqing_lines)) + ['\n'] + \
        ["🚢天津频道,#genre#"] + sort_data(tianjin_dictionary,correct_name_data(corrections_name,tianjin_lines)) + ['\n'] + \
        ["🏯湖北频道,#genre#"] + sort_data(hubei_dictionary,correct_name_data(corrections_name,hubei_lines)) + ['\n'] + \
        ["🌾安徽频道,#genre#"] + sort_data(anhui_dictionary,correct_name_data(corrections_name,anhui_lines)) + ['\n'] + \
        ["🌊福建频道,#genre#"] + sort_data(fujian_dictionary,correct_name_data(corrections_name,fujian_lines)) + ['\n'] + \
        ["⛰️辽宁频道,#genre#"] + sort_data(liaoning_dictionary,correct_name_data(corrections_name,liaoning_lines)) + ['\n'] + \
        ["🔥陕西频道,#genre#"] + sort_data(shaanxi_dictionary,correct_name_data(corrections_name,shaanxi_lines)) + ['\n'] + \
        ["⛩️河北频道,#genre#"] + sort_data(hebei_dictionary,correct_name_data(corrections_name,hebei_lines)) + ['\n'] + \
        ["🔥江西频道,#genre#"] + sort_data(jiangxi_dictionary,correct_name_data(corrections_name,jiangxi_lines)) + ['\n'] + \
        ["💃广西频道,#genre#"] + sort_data(guangxi_dictionary,correct_name_data(corrections_name,guangxi_lines)) + ['\n'] + \
        ["☁️云南频道,#genre#"] + sort_data(yunnan_dictionary,correct_name_data(corrections_name,yunnan_lines)) + ['\n'] + \
        ["🏮山西频道,#genre#"] + sort_data(shanxi_dictionary,correct_name_data(corrections_name,shanxi_lines)) + ['\n'] + \
        ["🐻黑·龙·江,#genre#"] + sort_data(heilongjiang_dictionary,correct_name_data(corrections_name,heilongjiang_lines)) + ['\n'] + \
        ["🎎吉林频道,#genre#"] + sort_data(jilin_dictionary,correct_name_data(corrections_name,jilin_lines)) + ['\n'] + \
        ["⛰️贵州频道,#genre#"] + sort_data(guizhou_dictionary,correct_name_data(corrections_name,guizhou_lines)) + ['\n'] + \
        ["🐫甘肃频道,#genre#"] + sort_data(gansu_dictionary,correct_name_data(corrections_name,gansu_lines)) + ['\n'] + \
        ["🐮内·蒙·古,#genre#"] + sort_data(neimenggu_dictionary,correct_name_data(corrections_name,neimenggu_lines)) + ['\n'] + \
        ["🍇新疆频道,#genre#"] + sort_data(xinjiang_dictionary,correct_name_data(corrections_name,xinjiang_lines)) + ['\n'] + \
        ["🏝️海南频道,#genre#"] + sort_data(hainan_dictionary,correct_name_data(corrections_name,hainan_lines)) + ['\n'] + \
        ["🕌宁夏频道,#genre#"] + sort_data(ningxia_dictionary,correct_name_data(corrections_name,ningxia_lines)) + ['\n'] + \
        ["🐑青海频道,#genre#"] + sort_data(qinghai_dictionary,correct_name_data(corrections_name,qinghai_lines)) + ['\n'] + \
        ["🐐西藏频道,#genre#"] + sort_data(xizang_dictionary,correct_name_data(corrections_name,xizang_lines)) + ['\n'] + \
        ["🇭🇰香港频道,#genre#"] + sort_data(hongkong_dictionary,correct_name_data(corrections_name,hongkong_lines)) + ['\n'] + \
        ["🇲🇴澳门频道,#genre#"] + sort_data(macau_dictionary,correct_name_data(corrections_name,macau_lines)) + ['\n'] + \
        ["🇨🇳闽南频道,#genre#"] + sort_data(minnan_dictionary,correct_name_data(corrections_name,minnan_lines)) + ['\n'] + \
        ["🔢数字频道,#genre#"] + sort_data(digital_dictionary,correct_name_data(corrections_name,digital_lines)) + ['\n'] + \
        ["🎬电影频道,#genre#"] + sort_data(movie_dictionary,correct_name_data(corrections_name,movie_lines)) + ['\n'] + \
        ["📺电·视·剧,#genre#"] + sort_data(tv_drama_dictionary,correct_name_data(corrections_name,tv_drama_lines)) + ['\n'] + \
        ["🎥纪·录·片,#genre#"] + sort_data(documentary_dictionary,correct_name_data(corrections_name,documentary_lines)) + ['\n'] + \
        ["🐱动·画·片,#genre#"] + sort_data(cartoon_dictionary,correct_name_data(corrections_name,cartoon_lines)) + ['\n'] + \
        ["📻收·音·机,#genre#"] + sort_data(radio_dictionary,correct_name_data(corrections_name,radio_lines)) + ['\n'] + \
        ["🎭综艺频道,#genre#"] + sort_data(variety_dictionary,correct_name_data(corrections_name,variety_lines)) + ['\n'] + \
        ["🐯虎牙直播,#genre#"] + sort_data(huya_dictionary,correct_name_data(corrections_name,huya_lines)) + ['\n'] + \
        ["🐠斗鱼直播,#genre#"] + sort_data(douyu_dictionary,correct_name_data(corrections_name,douyu_lines)) + ['\n'] + \
        ["🎤解说频道,#genre#"] + sort_data(commentary_dictionary,correct_name_data(corrections_name,commentary_lines)) + ['\n'] + \
        ["🎵音乐频道,#genre#"] + sort_data(music_dictionary,correct_name_data(corrections_name,music_lines)) + ['\n'] + \
        ["🍜美食频道,#genre#"] + sort_data(food_dictionary,correct_name_data(corrections_name,food_lines)) + ['\n'] + \
        ["✈️旅游频道,#genre#"] + sort_data(travel_dictionary,correct_name_data(corrections_name,travel_lines)) + ['\n'] + \
        ["🏥健康频道,#genre#"] + sort_data(health_dictionary,correct_name_data(corrections_name,health_lines)) + ['\n'] + \
        ["💰财经频道,#genre#"] + sort_data(finance_dictionary,correct_name_data(corrections_name,finance_lines)) + ['\n'] + \
        ["🛍️购物频道,#genre#"] + sort_data(shopping_dictionary,correct_name_data(corrections_name,shopping_lines)) + ['\n'] + \
        ["🎮游戏频道,#genre#"] + sort_data(game_dictionary,correct_name_data(corrections_name,game_lines)) + ['\n'] + \
        ["📰新闻频道,#genre#"] + sort_data(news_dictionary,correct_name_data(corrections_name,news_lines)) + ['\n'] + \
        ["🇨🇳中国综合,#genre#"] + sort_data(china_dictionary,correct_name_data(corrections_name,china_lines)) + ['\n'] + \
        ["🌐国际频道,#genre#"] + sort_data(international_dictionary,correct_name_data(corrections_name,international_lines)) + ['\n'] + \
        ["⚽体育频道,#genre#"] + sort_data(sports_dictionary,correct_name_data(corrections_name,sports_lines)) + ['\n'] + \
        ["🏆体育赛事,#genre#"] + normalized_tyss_lines + ['\n'] + \
        ["🏈咪咕赛事,#genre#"] + sorted(set(mgss_lines)) + ['\n'] + \
        ["🎭戏曲频道,#genre#"] + sort_data(traditional_opera_dictionary,correct_name_data(corrections_name,traditional_opera_lines)) + ['\n'] + \
        ["🧨春晚频道,#genre#"] + sort_data(spring_festival_gala_dictionary,correct_name_data(corrections_name,spring_festival_gala_lines)) + ['\n'] + \
        ["🏞️景区直播,#genre#"] + sort_data(camera_dictionary,correct_name_data(corrections_name,camera_lines)) + ['\n'] + \
        ["⭐收藏频道,#genre#"] + sort_data(favorite_dictionary,correct_name_data(corrections_name,favorite_lines)) + ['\n'] + \
        ["📦其他频道,#genre#"] + sorted(set(other_lines)) + ['\n'] + \
        ["🕒更新时间,#genre#"] + [version] + [about] + [MTV1] + [MTV2] + [MTV3] + [MTV4] + [MTV5] + ['\n']

# 精简版播放列表（只包含核心频道）
all_lines_lite = ["🌐央视频道,#genre#"] + sort_data(yangshi_dictionary,correct_name_data(corrections_name,yangshi_lines)) + ['\n'] + \
        ["📡卫视频道,#genre#"] + sort_data(weishi_dictionary,correct_name_data(corrections_name,weishi_lines)) + ['\n'] + \
        ["🏠地·方·台,#genre#"] + \
        sort_data(beijing_dictionary, correct_name_data(corrections_name, beijing_lines)) + \
        sort_data(shanghai_dictionary, correct_name_data(corrections_name, shanghai_lines)) + \
        sort_data(tianjin_dictionary, correct_name_data(corrections_name, tianjin_lines)) + \
        sort_data(chongqing_dictionary, correct_name_data(corrections_name, chongqing_lines)) + \
        sort_data(guangdong_dictionary, correct_name_data(corrections_name, guangdong_lines)) + \
        sort_data(jiangsu_dictionary, correct_name_data(corrections_name, jiangsu_lines)) + \
        sort_data(zhejiang_dictionary, correct_name_data(corrections_name, zhejiang_lines)) + \
        sort_data(shandong_dictionary, correct_name_data(corrections_name, shandong_lines)) + \
        sort_data(henan_dictionary, correct_name_data(corrections_name, henan_lines)) + \
        sort_data(sichuan_dictionary, correct_name_data(corrections_name, sichuan_lines)) + \
        sort_data(hebei_dictionary, correct_name_data(corrections_name, hebei_lines)) + \
        sort_data(hunan_dictionary, correct_name_data(corrections_name, hunan_lines)) + \
        sort_data(hubei_dictionary, correct_name_data(corrections_name, hubei_lines)) + \
        sort_data(anhui_dictionary, correct_name_data(corrections_name, anhui_lines)) + \
        sort_data(fujian_dictionary, correct_name_data(corrections_name, fujian_lines)) + \
        sort_data(shaanxi_dictionary, correct_name_data(corrections_name, shaanxi_lines)) + \
        sort_data(liaoning_dictionary, correct_name_data(corrections_name, liaoning_lines)) + \
        sort_data(jiangxi_dictionary, correct_name_data(corrections_name, jiangxi_lines)) + \
        sort_data(heilongjiang_dictionary, correct_name_data(corrections_name, heilongjiang_lines)) + \
        sort_data(jilin_dictionary, correct_name_data(corrections_name, jilin_lines)) + \
        sort_data(shanxi_dictionary, correct_name_data(corrections_name, shanxi_lines)) + \
        sort_data(guangxi_dictionary, correct_name_data(corrections_name, guangxi_lines)) + \
        sort_data(yunnan_dictionary, correct_name_data(corrections_name, yunnan_lines)) + \
        sort_data(guizhou_dictionary, correct_name_data(corrections_name, guizhou_lines)) + \
        sort_data(gansu_dictionary, correct_name_data(corrections_name, gansu_lines)) + \
        sort_data(neimenggu_dictionary, correct_name_data(corrections_name, neimenggu_lines)) + \
        sort_data(xinjiang_dictionary, correct_name_data(corrections_name, xinjiang_lines)) + \
        sort_data(hainan_dictionary, correct_name_data(corrections_name, hainan_lines)) + \
        sort_data(ningxia_dictionary, correct_name_data(corrections_name, ningxia_lines)) + \
        sort_data(qinghai_dictionary, correct_name_data(corrections_name, qinghai_lines)) + \
        sort_data(xizang_dictionary, correct_name_data(corrections_name, xizang_lines)) + ['\n'] + \
        ["🕒更新时间,#genre#"] + [version] + [about] + [MTV1] + [MTV2] + [MTV3] + [MTV4] + [MTV5] + ['\n']

# 定制版播放列表
all_lines_custom = [
        "🌐央视频道,#genre#"] + sort_data(yangshi_dictionary, correct_name_data(corrections_name, yangshi_lines)) + ['\n'] + \
        ["📡卫视频道,#genre#"] + sort_data(weishi_dictionary, correct_name_data(corrections_name, weishi_lines)) + ['\n'] + \
        ["🕒更新时间,#genre#"] + [version] + [about] + [MTV1] + [MTV2] + [MTV3] + [MTV4] + [MTV5] + ['\n']

# 文件路径定义
output_full = "output/full.txt"
output_lite = "output/lite.txt"
output_custom = "output/custom.txt"
output_others = "output/others.txt"

try:
    # 写入完整版
    with open(output_full, 'w', encoding='utf-8') as f:
        for line in all_lines_full:
            f.write(line + '\n')
    print(f"合并后的文本已保存到文件: {output_full}")

    # 写入精简版
    with open(output_lite, 'w', encoding='utf-8') as f:
        for line in all_lines_lite:
            f.write(line + '\n')
    print(f"合并后的文本已保存到文件: {output_lite}")

    # 写入定制版
    with open(output_custom, 'w', encoding='utf-8') as f:
        for line in all_lines_custom:
            f.write(line + '\n')
    print(f"合并后的文本已保存到文件: {output_custom}")

    # 写入未分类源
    with open(output_others, 'w', encoding='utf-8') as f:
        for line in other_lines:
            f.write(line + '\n')
    print(f"Others已保存到文件: {output_others}")

except Exception as e:
    print(f"保存文件时发生错误：{e}")

# ========= 生成M3U格式文件 =========

print(f"time: {datetime.now().strftime('%Y%m%d_%H_%M_%S')}")

# 读取频道Logo库
channels_logos = read_txt_to_array('assets/livesource/logo.txt')

def get_logo_by_channel_name(channel_name):
    """根据频道名称获取Logo URL"""
    # 遍历Logo库查找频道名称
    for line in channels_logos:
        # 跳过空行
        if not line.strip():
            continue
        name, url = line.split(',')
        if name == channel_name:
            return url
    return None  # 未找到时返回None

def make_m3u(txt_file, m3u_file):
    """将TXT格式转换为M3U格式"""
    try:
        # M3U文件头
        output_text = '#EXTM3U x-tvg-url="https://live.fanmingming.cn/e.xml"\n'

        with open(txt_file, "r", encoding='utf-8') as file:
            input_text = file.read()

        lines = input_text.strip().split("\n")
        group_name = ""
        
        for line in lines:
            parts = line.split(",")
            # 处理分组标题行
            if len(parts) == 2 and "#genre#" in line:
                group_name = parts[0]
            # 处理频道行
            elif len(parts) == 2:
                channel_name = parts[0]
                channel_url = parts[1]
                logo_url = get_logo_by_channel_name(channel_name)
                
                if logo_url is None:  # 未找到Logo
                    output_text += f"#EXTINF:-1 group-title=\"{group_name}\",{channel_name}\n"
                    output_text += f"{channel_url}\n"
                else:  # 找到Logo
                    output_text += f"#EXTINF:-1 tvg-name=\"{channel_name}\" tvg-logo=\"{logo_url}\" group-title=\"{group_name}\",{channel_name}\n"
                    output_text += f"{channel_url}\n"

        # 写入M3U文件
        with open(f"{m3u_file}", "w", encoding='utf-8') as file:
            file.write(output_text)

        print(f"M3U文件 '{m3u_file}' 生成成功。")
        
    except Exception as e:
        print(f"发生错误: {e}")

# 为各个版本生成对应的M3U文件
make_m3u(output_full, output_full.replace(".txt", ".m3u"))
make_m3u(output_lite, output_lite.replace(".txt", ".m3u"))
make_m3u(output_custom, output_custom.replace(".txt", ".m3u"))

# ========= 统计信息和性能监控 =========

# 计算执行时间
timeend = datetime.now()
elapsed_time = timeend - timestart
total_seconds = elapsed_time.total_seconds()

# 转换为分钟和秒
minutes = int(total_seconds // 60)
seconds = int(total_seconds % 60)

# 格式化开始和结束时间
timestart_str = timestart.strftime("%Y%m%d_%H_%M_%S")
timeend_str = timeend.strftime("%Y%m%d_%H_%M_%S")

print(f"开始时间: {timestart_str}")
print(f"结束时间: {timeend_str}")
print(f"执行时间: {minutes} 分 {seconds} 秒")

# 统计各类数据行数
all_lines_full_count = len(all_lines_full)
combined_blacklist_count = len(combined_blacklist)
other_lines_count = len(other_lines)

print(f"黑名单行数: {combined_blacklist_count}")
print(f"完整版行数: {all_lines_full_count}")
print(f"其他源行数: {other_lines_count}")
print(f"处理的唯一URL数: {len(processed_urls)}")

# ========= 脚本结束 =========