#!/bin/bash

# 设置UTF-8编码
export LANG=en_US.UTF-8

clear
echo ======================================
echo Portal项目启动脚本
echo ======================================
echo

# 检查Node.js是否安装
if ! command -v node &> /dev/null; then
    echo "系统未安装Node.js"
    echo "请先安装Node.js 24或更高版本"
    read -p "按回车键退出..."
    exit 1
fi

echo "已安装Node.js版本："
node --version
echo

# 检查npm是否安装
if ! command -v npm &> /dev/null; then
    echo "系统未安装npm"
    echo "请先安装npm"
    read -p "按回车键退出..."
    exit 1
fi

echo "已安装npm版本："
npm --version
echo

# 检查node_modules是否存在
if [ ! -d "node_modules" ]; then
    echo "正在安装依赖..."
    npm install
    if [ $? -ne 0 ]; then
        echo "错误：安装依赖失败"
        read -p "按回车键退出..."
        exit 1
    fi
    echo "依赖安装成功"
    echo
fi

# 编译TypeScript代码
echo "正在编译TypeScript代码..."
npm run build
if [ $? -ne 0 ]; then
    echo "错误：编译失败"
    read -p "按回车键退出..."
    exit 1
fi
echo "编译成功"
echo

echo ======================================
echo "正在启动项目..."
echo "访问地址：http://localhost:3000/portal/"
echo ======================================
echo

# 启动项目
npm run serve

if [ $? -ne 0 ]; then
    echo
    echo "项目启动失败"
    read -p "按回车键退出..."
    exit 1
fi