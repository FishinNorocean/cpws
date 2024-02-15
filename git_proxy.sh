#!/bin/bash

if [ -z "$1" ]; then
    echo "请提供代理地址作为参数。"
    exit 1
fi

proxy_address="$1:10809"  # 添加端口号

git config --global http.proxy "$proxy_address"
git config --global https.proxy "$proxy_address"

# 读取代理设置，包含端口号
echo "HTTP 代理设置为: $(git config --global --get http.proxy)"
echo "HTTPS 代理设置为: $(git config --global --get https.proxy)"
