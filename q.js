#!name=番茄小说解析
#!desc=番茄小说书源解析
#!author=@Wuang备份
#!openUrl=https://raw.githubusercontent.com/zyzdai/api/refs/heads/main/fq.plugin
#!homepage=https://github.com/W126-L
#!icon=https://raw.githubusercontent.com/W126-L/Tool/main/IconSet/fanqie.png
#!tag=阿旺の库

[Script]
http-response ^https://reading.snssdk.com/reading/reader/full/v/\?item_id=* script-path=https://raw.githubusercontent.com/zyzdai/api/refs/heads/main/fanqie.js, requires-body=true, timeout=60