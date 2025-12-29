#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的文件保存脚本
"""

import os
import json
import time
import hashlib
from pathlib import Path

def save_file(filename, content):
    """保存文件到uploads目录"""
    try:
        # 创建uploads目录
        uploads_dir = os.path.join(os.getcwd(), "uploads")
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)
            print(f"创建上传目录: {uploads_dir}")
        
        # 生成唯一文件名避免冲突
        timestamp = str(int(time.time()))
        random_suffix = hashlib.md5(filename.encode()).hexdigest()[:6]
        unique_filename = f"{timestamp}_{random_suffix}_{filename}"
        
        # 完整的文件路径
        file_path = os.path.join(uploads_dir, unique_filename)
        
        # 保存文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 文件已保存到: {file_path}")
        return unique_filename, file_path
        
    except Exception as e:
        print(f"❌ 保存文件时出错: {e}")
        return None, None

def list_uploaded_files():
    """列出已上传的文件"""
    try:
        uploads_dir = os.path.join(os.getcwd(), "uploads")
        if not os.path.exists(uploads_dir):
            print("uploads目录不存在")
            return []
        
        files = []
        for filename in os.listdir(uploads_dir):
            if filename.endswith(('.html', '.htm')):
                file_path = os.path.join(uploads_dir, filename)
                stat = os.stat(file_path)
                
                files.append({
                    'name': filename,
                    'path': file_path,
                    'size': stat.st_size,
                    'modified': time.ctime(stat.st_mtime)
                })
        
        return files
    except Exception as e:
        print(f"列出文件时出错: {e}")
        return []

if __name__ == '__main__':
    print("📁 文件保存工具")
    print("=" * 40)
    
    # 显示已上传的文件
    files = list_uploaded_files()
    print(f"\n📋 当前已上传的文件 ({len(files)} 个):")
    for file in files:
        print(f"  📄 {file['name']} ({file['size']} bytes)")
    
    print(f"\n📂 上传目录: {os.path.join(os.getcwd(), 'uploads')}")
    print("\n💡 使用说明:")
    print("1. 在网页端使用文件上传功能")
    print("2. 文件将被自动保存到uploads目录")
    print("3. 文件名会添加时间戳和哈希后缀避免冲突")