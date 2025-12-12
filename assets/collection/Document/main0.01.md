根据您的最新修正代码，以下是完整的输入和输出文件列表：

输入文件列表：

1. 黑名单和名单文件

```
assets/livesource/blacklist/blacklist_auto.txt
assets/livesource/blacklist/blacklist_manual.txt
assets/livesource/blacklist/whitelist_auto.txt
```

2. 频道字典文件（主频道）

```
assets/livesource/主频道/CCTV.txt
assets/livesource/主频道/卫视.txt
assets/livesource/主频道/数字.txt
assets/livesource/主频道/电影.txt
assets/livesource/主频道/电视剧.txt
assets/livesource/主频道/纪录片.txt
assets/livesource/主频道/动画片.txt
assets/livesource/主频道/收音机.txt
assets/livesource/主频道/综艺.txt
assets/livesource/主频道/虎牙.txt
assets/livesource/主频道/斗鱼.txt
assets/livesource/主频道/解说.txt
assets/livesource/主频道/音乐.txt
assets/livesource/主频道/美食.txt
assets/livesource/主频道/旅游.txt
assets/livesource/主频道/健康.txt
assets/livesource/主频道/财经.txt
assets/livesource/主频道/购物.txt
assets/livesource/主频道/游戏.txt
assets/livesource/主频道/新闻.txt
assets/livesource/主频道/中国.txt
assets/livesource/主频道/国际.txt
assets/livesource/主频道/体育.txt
assets/livesource/主频道/体育赛事.txt
assets/livesource/主频道/咪咕赛事.txt
assets/livesource/主频道/戏曲.txt
assets/livesource/主频道/春晚.txt
assets/livesource/主频道/直播中国.txt
assets/livesource/主频道/收藏频道.txt
```

3. 省级地方台字典文件

```
assets/livesource/地方台/北京.txt
assets/livesource/地方台/上海.txt
assets/livesource/地方台/广东.txt
assets/livesource/地方台/江苏.txt
assets/livesource/地方台/浙江.txt
assets/livesource/地方台/山东.txt
assets/livesource/地方台/四川.txt
assets/livesource/地方台/河南.txt
assets/livesource/地方台/湖南.txt
assets/livesource/地方台/重庆.txt
assets/livesource/地方台/天津.txt
assets/livesource/地方台/湖北.txt
assets/livesource/地方台/安徽.txt
assets/livesource/地方台/福建.txt
assets/livesource/地方台/辽宁.txt
assets/livesource/地方台/陕西.txt
assets/livesource/地方台/河北.txt
assets/livesource/地方台/江西.txt
assets/livesource/地方台/广西.txt
assets/livesource/地方台/云南.txt
assets/livesource/地方台/山西.txt
assets/livesource/地方台/黑龙江.txt
assets/livesource/地方台/吉林.txt
assets/livesource/地方台/贵州.txt
assets/livesource/地方台/甘肃.txt
assets/livesource/地方台/内蒙.txt
assets/livesource/地方台/新疆.txt
assets/livesource/地方台/海南.txt
assets/livesource/地方台/宁夏.txt
assets/livesource/地方台/青海.txt
assets/livesource/地方台/西藏.txt
assets/livesource/地方台/香港.txt
assets/livesource/地方台/澳门.txt
assets/livesource/地方台/台湾.txt
```

4. 手工区文件

```
assets/livesource/手工区/今日推荐.txt
assets/livesource/手工区/今日推台.txt
assets/livesource/手工区/浙江频道.txt
assets/livesource/手工区/广东频道.txt
assets/livesource/手工区/湖北频道.txt
assets/livesource/手工区/上海频道.txt
assets/livesource/手工区/江苏频道.txt
assets/livesource/手工区/优质央视.txt
assets/livesource/手工区/优质卫视.txt
assets/livesource/手工区/sports.txt
assets/livesource/手工区/about.txt
assets/livesource/手工区/AKTV.txt
```

5. 配置和元数据文件

```
assets/livesource/corrections_name.txt
assets/livesource/logo.txt
assets/livesource/urls-daily.txt
```

6. 在线URL（外部资源）

```
https://raw.githubusercontent.com/xiaoran67/update/refs/heads/main/assets/livesource/blacklist/whitelist_manual.txt
https://gitee.com/xiaoran67/update/raw/master/assets/livesource/about1080p.mp4
https://gitlab.com/xiaoran67/update/-/raw/main/assets/livesource/about1080p.mp4
```

输出文件列表：

1. 播放列表文件（在output目录下）

```
output/full.txt           # 完整版播放列表（文本格式）
output/full.m3u           # 完整版播放列表（M3U格式）
output/lite.txt           # 精简版播放列表（文本格式）
output/lite.m3u           # 精简版播放列表（M3U格式）
output/custom.txt         # 定制版播放列表（文本格式）
output/custom.m3u         # 定制版播放列表（M3U格式）
output/others.txt         # 未分类频道列表
```

2. 网页输出文件

```
output/tiyu.html          # 体育赛事网页
```

重要修正：

1. 输出目录变更：

· 所有输出文件现在都保存在 output/ 目录下

2. 完整的输出文件：

```
output/
├── full.txt        # 完整版播放列表（文本）
├── full.m3u        # 完整版播放列表（M3U格式）
├── lite.txt        # 精简版播放列表（文本）
├── lite.m3u        # 精简版播放列表（M3U格式）
├── custom.txt      # 定制版播放列表（文本）
├── custom.m3u      # 定制版播放列表（M3U格式）
├── others.txt      # 未分类频道列表
└── tiyu.html       # 体育赛事网页
```

文件数量统计：

· 输入文件：总共 73个 本地文件 + 3个 在线URL
  · 黑名单/白名单：3个
  · 主频道字典：29个
  · 地方台字典：37个
  · 手工区文件：11个
  · 配置文件：3个
· 输出文件：总共 8个 文件（4个文本 + 4个M3U + 1个网页）
  · output/ 目录下：7个文件
  · 体育赛事网页：1个

完整目录结构：

```
项目根目录/
├── assets/
│   └── livesource/
│       ├── blacklist/              # 黑名单和白名单（3个文件）
│       │   ├── blacklist_auto.txt
│       │   ├── blacklist_manual.txt
│       │   └── whitelist_auto.txt
│       ├── 主频道/                # 主频道字典（29个文件）
│       ├── 地方台/                # 地方台字典（37个文件）
│       ├── 手工区/                # 手工整理的频道（11个文件）
│       ├── corrections_name.txt    # 频道名称修正
│       ├── logo.txt              # 频道logo
│       └── urls-daily.txt        # 每日更新的源URL
└── output/                        # 所有输出文件目录
    ├── full.txt, full.m3u        # 完整版播放列表
    ├── lite.txt, lite.m3u        # 精简版播放列表
    ├── custom.txt, custom.m3u    # 定制版播放列表
    ├── others.txt                # 未分类频道列表
    └── tiyu.html                 # 体育赛事网页
```

特别说明：

1. 脚本会创建 output/ 目录：如果不存在会自动创建
2. URL处理：会处理 urls-daily.txt 中的URL，并替换日期变量 {MMdd} 和 {MMdd-1}
3. AKTV处理：优先从在线URL获取，失败时使用本地备用文件
4. 三种播放列表：
   · full.txt：完整版，包含所有分类
   · lite.txt：精简版，包含精简分类
   · custom.txt：定制版，包含定制分类