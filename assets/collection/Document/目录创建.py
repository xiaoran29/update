#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📁 直播源系统目录结构创建脚本
"""

import os
import shutil

def create_directory_structure():
    """📁 创建完整的目录结构"""
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 主目录
    directories = [
        "scripts/livesource",
        "scripts/livesource/blacklist",
        "scripts/livesource/主频道",
        "scripts/livesource/地方台",
        "scripts/livesource/手工区", 
        "scripts/livesource/定制频道",
        "output/livesource"
    ]
    
    # 创建目录
    for directory in directories:
        dir_path = os.path.join(base_dir, directory)
        os.makedirs(dir_path, exist_ok=True)
        print(f"📁 创建目录: {directory}")
    
    # 创建主频道分类文件
    main_categories = [
        "央视.txt", "卫视.txt", "新闻.txt", "电影.txt", "体育.txt",
        "音乐.txt", "戏曲.txt", "少儿.txt", "教育.txt", "财经.txt",
        "法治.txt", "生活.txt", "旅游.txt", "健康.txt", "农业.txt",
        "科技.txt", "军事.txt", "国际.txt", "卡通.txt", "4K8K.txt",
        "数字频道.txt", "购物.txt", "测试.txt"
    ]
    
    for category in main_categories:
        file_path = os.path.join(base_dir, "scripts/livesource/主频道", category)
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("# " + category.replace('.txt', '') + "频道关键词\n")
                f.write("# 每行一个关键词\n\n")
                if category == "央视.txt":
                    for i in range(1, 18):
                        f.write(f"CCTV{i}\n")
                    f.write("CCTV4K\nCCTV8K\nCCTV4K超高清\nCCTV8K超高清\n")
                elif category == "卫视.txt":
                    f.write("湖南卫视\n浙江卫视\n江苏卫视\n东方卫视\n北京卫视\n")
                    f.write("安徽卫视\n山东卫视\n天津卫视\n广东卫视\n深圳卫视\n")
            print(f"📄 创建文件: 主频道/{category}")
    
    # 创建地方台分类文件
    provinces = [
        "北京.txt", "上海.txt", "天津.txt", "重庆.txt",
        "广东.txt", "江苏.txt", "浙江.txt", "山东.txt", "河南.txt",
        "四川.txt", "湖北.txt", "湖南.txt", "福建.txt", "安徽.txt",
        "河北.txt", "山西.txt", "辽宁.txt", "吉林.txt", "黑龙江.txt",
        "陕西.txt", "甘肃.txt", "青海.txt", "云南.txt", "贵州.txt",
        "广西.txt", "内蒙古.txt", "宁夏.txt", "新疆.txt", "西藏.txt"
    ]
    
    for province in provinces:
        file_path = os.path.join(base_dir, "scripts/livesource/地方台", province)
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                province_name = province.replace('.txt', '')
                f.write(f"# {province_name}地方台关键词\n")
                f.write(f"{province_name}卫视\n")
                f.write(f"{province_name}电视台\n")
                if province_name in ["北京", "上海", "天津", "重庆"]:
                    f.write(f"{province_name}新闻\n{province_name}影视\n{province_name}体育\n")
            print(f"📄 创建文件: 地方台/{province}")
    
    # 创建手工区文件
    manual_files = [
        "港澳台.txt", "优质央视.txt", "AKTV.txt", "今日推荐.txt",
        "赛事直播.txt", "高清电影.txt", "音乐现场.txt"
    ]
    
    for manual_file in manual_files:
        file_path = os.path.join(base_dir, "scripts/livesource/手工区", manual_file)
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# {manual_file.replace('.txt', '')}\n")
                f.write("# 手工维护的高质量源\n\n")
            print(f"📄 创建文件: 手工区/{manual_file}")
    
    # 创建定制频道文件
    custom_categories = [
        "虎牙直播.txt", "斗鱼直播.txt", "B站直播.txt", "快手直播.txt",
        "抖音直播.txt", "游戏直播.txt", "电商直播.txt", "教育直播.txt",
        "企业直播.txt", "监控直播.txt", "风景直播.txt", "宠物直播.txt",
        "车载直播.txt", "航拍直播.txt", "水下直播.txt", "天文直播.txt",
        "极地直播.txt", "海岛直播.txt", "农场直播.txt", "工厂直播.txt",
        "工地直播.txt", "实验室.txt", "博物馆.txt"
    ]
    
    for custom_file in custom_categories:
        file_path = os.path.join(base_dir, "scripts/livesource/定制频道", custom_file)
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# {custom_file.replace('.txt', '')}\n")
                f.write("# 定制直播源关键词\n\n")
            print(f"📄 创建文件: 定制频道/{custom_file}")
    
    # 创建黑名单文件
    blacklist_files = {
        "blacklist_auto.txt": "# 🤖 自动收集的无效URL\n# 格式: 每行一个URL\n\n",
        "blacklist_manual.txt": "# 👨‍💻 手工维护的永久黑名单\n# 格式: 每行一个URL\n\n",
        "whitelist_auto.txt": "# ⚡ 高速响应源白名单\n# 格式: 每行一个URL\n\n"
    }
    
    for filename, content in blacklist_files.items():
        file_path = os.path.join(base_dir, "scripts/livesource/blacklist", filename)
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"📄 创建文件: blacklist/{filename}")
    
    # 创建其他关键文件
    other_files = {
        "logo.txt": "# 🖼️ 台标映射文件\n# 格式: 频道名称,Logo_URL\n\nCCTV1,http://example.com/logo/cctv1.png\n湖南卫视,http://example.com/logo/hunan.png\n",
        "urls-daily.txt": """# 📅 每日更新的源URL列表
# 支持日期变量: {MMdd}, {MMdd-1}, {yyyyMMdd}, {YYMMdd}
# 多个源用 # 分隔表示加速源

# 示例URL
http://example.com/live/{MMdd}.txt
http://backup.example.com/live/{MMdd}.txt#http://mirror.example.com/live/{MMdd}.txt

# M3U格式源
http://example.com/playlist.m3u
""",
        "corrections_name.txt": """# 🔧 频道别名修正
# 格式: 错误名称->正确名称

CCTV-1->CCTV1
央视1套->CCTV1
湖南电视台->湖南卫视
浙江电视台->浙江卫视
"""
    }
    
    for filename, content in other_files.items():
        file_path = os.path.join(base_dir, "scripts/livesource", filename)
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"📄 创建文件: {filename}")
    
    # 创建示例脚本
    script_path = os.path.join(base_dir, "livesource.py")
    if not os.path.exists(script_path):
        shutil.copy(__file__, script_path)
        print(f"🐍 创建主脚本: livesource.py")
    
    print("\n" + "="*60)
    print("🎉 目录结构创建完成！")
    print("="*60)
    print("\n📋 下一步操作:")
    print("1. 📝 编辑 urls-daily.txt 添加直播源URL")
    print("2. 🎯 编辑各分类文件添加频道关键词")
    print("3. 🖼️ 编辑 logo.txt 添加台标映射")
    print("4. 🐍 运行 python livesource.py 开始处理")
    print("="*60)

if __name__ == "__main__":
    create_directory_structure()