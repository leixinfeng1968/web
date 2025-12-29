#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的文件上传服务器
用于处理课件文件的上传和保存
"""

import os
import json
import uuid
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs
import cgi
import shutil
from pathlib import Path

class UploadHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.upload_dir = os.path.join(os.getcwd(), "uploads")
        super().__init__(*args, **kwargs)
    
    def do_POST(self):
        """处理文件上传请求"""
        if self.path == '/upload':
            try:
                # 解析multipart form data
                content_type = self.headers['content-type']
                if not content_type.startswith('multipart/form-data'):
                    self.send_error(400, "Invalid content type")
                    return
                
                # 解析表单数据
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={
                        'REQUEST_METHOD': 'POST',
                        'CONTENT_TYPE': self.headers['Content-Type'],
                    }
                )
                
                uploaded_files = []
                
                # 处理文件字段
                if 'files' in form:
                    files = form['files']
                    if not isinstance(files, list):
                        files = [files]
                    
                    for file_item in files:
                        if file_item.filename:
                            # 获取文件内容
                            file_content = file_item.file.read()
                            filename = file_item.filename
                            
                            # 生成唯一文件名避免冲突
                            file_ext = Path(filename).suffix
                            unique_filename = f"{uuid.uuid4().hex}{file_ext}"
                            
                            # 保存文件
                            file_path = os.path.join(self.upload_dir, unique_filename)
                            os.makedirs(self.upload_dir, exist_ok=True)
                            
                            with open(file_path, 'wb') as f:
                                f.write(file_content)
                            
                            # 解析文件内容获取信息
                            file_info = self.parse_html_file(file_content, filename)
                            file_info['saved_filename'] = unique_filename
                            file_info['original_filename'] = filename
                            
                            uploaded_files.append(file_info)
                
                # 返回成功响应
                response = {
                    'success': True,
                    'files': uploaded_files,
                    'message': f'成功上传 {len(uploaded_files)} 个文件'
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                
            except Exception as e:
                error_response = {
                    'success': False,
                    'message': f'上传失败: {str(e)}'
                }
                self.send_response(500)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
        else:
            self.send_error(404)
    
    def parse_html_file(self, content, original_filename):
        """解析HTML文件提取信息"""
        try:
            # 将字节内容转换为字符串
            html_content = content.decode('utf-8', errors='ignore')
            
            # 提取标题
            title = original_filename.replace('.html', '').replace('.HTML', '')
            import re
            
            # 查找h1标签
            h1_match = re.search(r'<h1[^>]*>([^<]+)</h1>', html_content, re.IGNORECASE)
            if h1_match:
                title = h1_match.group(1).strip()
            
            # 提取作者信息
            author = "未知作者"
            author_patterns = [
                r'作者[：:]\s*([^\n\r<]+)',
                r'制作者[：:]\s*([^\n\r<]+)',
                r'制作者[：:]\s*([^\n\r<]+)'
            ]
            
            for pattern in author_patterns:
                match = re.search(pattern, html_content, re.IGNORECASE)
                if match:
                    author = match.group(1).strip()
                    break
            
            # 自动判断分类
            category = "九年级下册"  # 默认分类
            if '七年级上册' in title:
                category = "七年级上册"
            elif '七年级下册' in title:
                category = "七年级下册"
            elif '八年级上册' in title:
                category = "八年级上册"
            elif '八年级下册' in title:
                category = "八年级下册"
            elif '九年级上册' in title:
                category = "九年级上册"
            elif '九年级下册' in title:
                category = "九年级下册"
            elif '中考复习' in title:
                category = "中考复习"
            
            return {
                'title': title,
                'author': author,
                'category': category,
                'description': category
            }
            
        except Exception as e:
            print(f"解析HTML文件时出错: {e}")
            return {
                'title': original_filename.replace('.html', '').replace('.HTML', ''),
                'author': "未知作者",
                'category': "九年级下册",
                'description': "九年级下册"
            }
    
    def do_OPTIONS(self):
        """处理预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """处理GET请求 - 提供课件文件下载"""
        # 如果请求的是uploads目录下的文件，提供下载
        if self.path.startswith('/download/'):
            filename = self.path[10:]  # 移除 '/download/'
            file_path = os.path.join(self.upload_dir, filename)
            
            if os.path.exists(file_path):
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
                self.end_headers()
                
                with open(file_path, 'rb') as f:
                    shutil.copyfileobj(f, self.wfile)
            else:
                self.send_error(404, "File not found")
        else:
            # 其他GET请求使用默认处理
            super().do_GET()

def main():
    port = 8001
    server_address = ('', port)
    httpd = HTTPServer(server_address, UploadHandler)
    
    print(f"文件上传服务器启动在端口 {port}")
    print(f"上传目录: {os.path.join(os.getcwd(), 'uploads')}")
    print(f"上传端点: http://localhost:{port}/upload")
    print("按 Ctrl+C 停止服务器")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
        httpd.server_close()

if __name__ == '__main__':
    main()