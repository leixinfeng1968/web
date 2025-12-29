#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件上传处理服务器
用于真正保存上传的课件文件到本地目录
"""

import os
import json
import time
import shutil
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import webbrowser

class UploadHandler(BaseHTTPRequestHandler):
    """处理文件上传的HTTP请求处理器"""
    
    def do_GET(self):
        """处理GET请求"""
        if self.path == '/':
            # 返回主页
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>文件上传服务</title>
                <meta charset="UTF-8">
                <style>
                    body { font-family: Arial, sans-serif; margin: 50px; }
                    .upload-area { border: 2px dashed #ccc; padding: 50px; text-align: center; margin: 20px 0; }
                    .upload-btn { background: #4CAF50; color: white; padding: 10px 20px; border: none; cursor: pointer; margin: 10px; }
                    .upload-btn:hover { background: #45a049; }
                    .file-list { margin-top: 20px; }
                    .file-item { padding: 5px; border-bottom: 1px solid #eee; }
                    .status { margin: 10px 0; padding: 10px; border-radius: 5px; }
                    .success { background: #d4edda; color: #155724; }
                    .error { background: #f8d7da; color: #721c24; }
                </style>
            </head>
            <body>
                <h1>📤 课件文件上传服务</h1>
                <p>请在此页面上传HTML课件文件，文件将被保存到本地uploads目录。</p>
                
                <div class="upload-area">
                    <h3>选择要上传的文件</h3>
                    <input type="file" id="fileInput" multiple accept=".html,.htm" />
                    <br><br>
                    <button class="upload-btn" onclick="uploadFiles()">🚀 上传文件</button>
                </div>
                
                <div id="status"></div>
                <div id="fileList" class="file-list"></div>
                
                <script>
                    let uploadedFiles = [];
                    
                    async function uploadFiles() {
                        const fileInput = document.getElementById('fileInput');
                        const files = fileInput.files;
                        
                        if (files.length === 0) {
                            showStatus('请选择要上传的文件', 'error');
                            return;
                        }
                        
                        showStatus('正在上传文件...', 'info');
                        
                        for (let file of files) {
                            try {
                                const content = await readFileContent(file);
                                const result = await saveFile(file.name, content);
                                
                                if (result.success) {
                                    uploadedFiles.push({
                                        name: file.name,
                                        path: result.path,
                                        size: file.size,
                                        timestamp: new Date().toLocaleString()
                                    });
                                    showStatus(`✅ ${file.name} 上传成功！保存位置: ${result.path}`, 'success');
                                } else {
                                    showStatus(`❌ ${file.name} 上传失败: ${result.error}`, 'error');
                                }
                            } catch (error) {
                                showStatus(`❌ ${file.name} 处理失败: ${error.message}`, 'error');
                            }
                        }
                        
                        updateFileList();
                    }
                    
                    function readFileContent(file) {
                        return new Promise((resolve, reject) => {
                            const reader = new FileReader();
                            reader.onload = e => resolve(e.target.result);
                            reader.onerror = e => reject(e);
                            reader.readAsText(file, 'UTF-8');
                        });
                    }
                    
                    async function saveFile(filename, content) {
                        try {
                            const response = await fetch('/upload', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify({ filename, content })
                            });
                            
                            const result = await response.json();
                            return result;
                        } catch (error) {
                            return { success: false, error: error.message };
                        }
                    }
                    
                    function showStatus(message, type) {
                        const statusDiv = document.getElementById('status');
                        statusDiv.innerHTML = `<div class="status ${type}">${message}</div>`;
                        
                        // 3秒后清除状态消息
                        setTimeout(() => {
                            statusDiv.innerHTML = '';
                        }, 3000);
                    }
                    
                    function updateFileList() {
                        const fileListDiv = document.getElementById('fileList');
                        if (uploadedFiles.length === 0) {
                            fileListDiv.innerHTML = '';
                            return;
                        }
                        
                        let html = '<h3>已上传的文件:</h3>';
                        uploadedFiles.forEach(file => {
                            html += `
                                <div class="file-item">
                                    📄 ${file.name}<br>
                                    📍 ${file.path}<br>
                                    📊 ${(file.size / 1024).toFixed(2)} KB | 🕒 ${file.timestamp}
                                </div>
                            `;
                        });
                        
                        fileListDiv.innerHTML = html;
                    }
                </script>
            </body>
            </html>
            """
            
            self.wfile.write(html_content.encode('utf-8'))
            
        elif self.path == '/files':
            # 返回已上传文件列表
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            files_info = self.get_uploaded_files()
            self.wfile.write(json.dumps(files_info).encode('utf-8'))
            
        else:
            self.send_error(404)
    
    def do_POST(self):
        """处理POST请求"""
        if self.path == '/upload':
            try:
                # 读取请求体
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                
                # 解析JSON数据
                data = json.loads(post_data.decode('utf-8'))
                filename = data.get('filename', '')
                content = data.get('content', '')
                
                # 保存文件
                saved_filename, saved_path = save_uploaded_file(filename, content)
                
                if saved_filename:
                    # 返回成功响应
                    response = {
                        'success': True,
                        'filename': saved_filename,
                        'path': saved_path,
                        'message': '文件上传成功'
                    }
                else:
                    response = {
                        'success': False,
                        'error': '文件保存失败'
                    }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
            except Exception as e:
                # 返回错误响应
                error_response = {
                    'success': False,
                    'error': str(e)
                }
                
                self.send_response(500)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
        else:
            self.send_error(404)
    
    def get_uploaded_files(self):
        """获取已上传的文件列表"""
        try:
            uploads_dir = os.path.join(os.getcwd(), "uploads")
            files = []
            
            if os.path.exists(uploads_dir):
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
            return []

def save_uploaded_file(filename, content):
    """保存上传的文件到uploads目录"""
    try:
        # 创建uploads目录
        uploads_dir = os.path.join(os.getcwd(), "uploads")
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)
            print(f"创建上传目录: {uploads_dir}")
        
        # 生成唯一文件名避免冲突
        timestamp = str(int(time.time()))
        random_suffix = str(hash(filename))[-6:]
        file_ext = Path(filename).suffix
        unique_filename = f"{timestamp}_{random_suffix}_{filename}"
        
        # 完整的文件路径
        file_path = os.path.join(uploads_dir, unique_filename)
        
        # 保存文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"文件已保存到: {file_path}")
        return unique_filename, file_path
        
    except Exception as e:
        print(f"保存文件时出错: {e}")
        return None, None

def parse_html_content(content, original_filename):
    """解析HTML内容提取信息"""
    try:
        # 提取标题
        title = original_filename.replace('.html', '').replace('.HTML', '')
        
        # 简单的正则表达式提取信息
        import re
        
        # 查找h1标签
        h1_match = re.search(r'<h1[^>]*>([^<]+)</h1>', content, re.IGNORECASE)
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
            match = re.search(pattern, content, re.IGNORECASE)
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

def main():
    """启动文件上传服务器"""
    server_port = 8080
    server_host = '0.0.0.0'  # 监听所有网络接口，允许其他设备访问
    
    # 创建HTTP服务器
    server = HTTPServer((server_host, server_port), UploadHandler)
    
    print("=" * 50)
    print("📤 文件上传处理服务器已启动")
    print("=" * 50)
    print(f"🌐 本地访问: http://localhost:{server_port}")
    print(f"🌐 网络访问: http://[您的IP地址]:{server_port}")
    print(f"📁 上传目录: {os.path.join(os.getcwd(), 'uploads')}")
    print("=" * 50)
    print("💡 使用说明:")
    print("1. 在本机上访问: http://localhost:8080")
    print("2. 在其他设备上访问: http://[本机IP]:8080")
    print("3. 选择要上传的HTML课件文件")
    print("4. 点击'上传文件'按钮")
    print("5. 文件将自动保存到uploads目录")
    print("=" * 50)
    print("⚠️  注意：其他设备需要与本机在同一网络下")
    print("⏹️  按 Ctrl+C 停止服务器")
    print("=" * 50)
    
    try:
        # 自动打开浏览器
        webbrowser.open(f'http://localhost:{server_port}')
        print("🚀 浏览器已自动打开...")
        
        # 启动服务器
        server.serve_forever()
        
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
        server.server_close()

if __name__ == '__main__':
    main()