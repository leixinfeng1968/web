#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版文件上传服务器 - 支持Git自动推送
上传的课件文件不仅保存到本地uploads目录，还会自动推送到Git仓库
"""

import os
import json
import time
import shutil
import subprocess
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import webbrowser

class GitUploadHandler(BaseHTTPRequestHandler):
    """处理文件上传的HTTP请求处理器 - 支持Git推送"""
    
    def do_GET(self):
        """处理GET请求"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>智能课件上传服务</title>
                <meta charset="UTF-8">
                <style>
                    body { font-family: Arial, sans-serif; margin: 50px; background: #f5f5f5; }
                    .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
                    .upload-area { border: 2px dashed #4CAF50; padding: 40px; text-align: center; margin: 20px 0; border-radius: 10px; background: #f9f9f9; }
                    .upload-btn { background: #4CAF50; color: white; padding: 15px 30px; border: none; cursor: pointer; margin: 10px; border-radius: 5px; font-size: 16px; }
                    .upload-btn:hover { background: #45a049; }
                    .file-list { margin-top: 20px; }
                    .file-item { padding: 15px; border-bottom: 1px solid #eee; background: #fafafa; border-radius: 5px; margin: 5px 0; }
                    .status { margin: 10px 0; padding: 15px; border-radius: 5px; font-weight: bold; }
                    .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
                    .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
                    .info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
                    .git-status { background: #fff3cd; color: #856404; padding: 10px; border-radius: 5px; margin: 10px 0; }
                    h1 { color: #333; text-align: center; }
                    .feature { background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #007bff; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🚀 智能课件上传系统</h1>
                    
                    <div class="feature">
                        <h3>✨ 智能功能</h3>
                        <p>📁 <strong>本地存储</strong>：文件自动保存到uploads目录</p>
                        <p>🌐 <strong>Git推送</strong>：文件自动推送到Git仓库</p>
                        <p>📝 <strong>自动记录</strong>：每次上传都有详细记录</p>
                    </div>
                    
                    <div class="upload-area">
                        <h3>📤 选择要上传的HTML课件文件</h3>
                        <input type="file" id="fileInput" multiple accept=".html,.htm" />
                        <br><br>
                        <button class="upload-btn" onclick="uploadFiles()">🚀 开始上传并推送到Git</button>
                    </div>
                    
                    <div id="status"></div>
                    <div id="gitStatus" class="git-status"></div>
                    <div id="fileList" class="file-list"></div>
                </div>
                
                <script>
                    let uploadedFiles = [];
                    let gitPushInProgress = false;
                    
                    async function uploadFiles() {
                        const fileInput = document.getElementById('fileInput');
                        const files = fileInput.files;
                        
                        if (files.length === 0) {
                            showStatus('请选择要上传的文件', 'error');
                            return;
                        }
                        
                        if (gitPushInProgress) {
                            showStatus('Git推送正在进行中，请稍候...', 'info');
                            return;
                        }
                        
                        showStatus('🔄 正在上传文件并推送到Git...', 'info');
                        gitPushInProgress = true;
                        
                        for (let file of files) {
                            try {
                                const content = await readFileContent(file);
                                const result = await saveFile(file.name, content);
                                
                                if (result.success) {
                                    uploadedFiles.push({
                                        name: file.name,
                                        path: result.path,
                                        gitUrl: result.git_url,
                                        size: file.size,
                                        timestamp: new Date().toLocaleString()
                                    });
                                    showStatus(`✅ ${file.name} 上传成功！Git推送完成！`, 'success');
                                } else {
                                    showStatus(`❌ ${file.name} 上传失败: ${result.error}`, 'error');
                                }
                            } catch (error) {
                                showStatus(`❌ ${file.name} 处理失败: ${error.message}`, 'error');
                            }
                        }
                        
                        updateFileList();
                        gitPushInProgress = false;
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
                        
                        // 5秒后清除状态消息
                        setTimeout(() => {
                            statusDiv.innerHTML = '';
                        }, 5000);
                    }
                    
                    function updateFileList() {
                        const fileListDiv = document.getElementById('fileList');
                        if (uploadedFiles.length === 0) {
                            fileListDiv.innerHTML = '';
                            return;
                        }
                        
                        let html = '<h3>📋 已上传并推送到Git的文件:</h3>';
                        uploadedFiles.forEach(file => {
                            html += `
                                <div class="file-item">
                                    📄 <strong>${file.name}</strong><br>
                                    📍 本地路径: ${file.path}<br>
                                    🌐 Git仓库: ${file.gitUrl || '推送中...'}<br>
                                    📊 ${(file.size / 1024).toFixed(2)} KB | 🕒 ${file.timestamp}
                                </div>
                            `;
                        });
                        
                        fileListDiv.innerHTML = html;
                    }
                    
                    // 页面加载时检查Git状态
                    window.onload = function() {
                        checkGitStatus();
                    }
                    
                    async function checkGitStatus() {
                        try {
                            const response = await fetch('/git-status');
                            const status = await response.json();
                            
                            const gitStatusDiv = document.getElementById('gitStatus');
                            if (status.git_ready) {
                                gitStatusDiv.innerHTML = `✅ Git仓库状态正常 - ${status.repository}`;
                            } else {
                                gitStatusDiv.innerHTML = `⚠️ Git配置需要检查 - ${status.message}`;
                            }
                        } catch (error) {
                            console.log('Git状态检查失败:', error);
                        }
                    }
                </script>
            </body>
            </html>
            """
            
            self.wfile.write(html_content.encode('utf-8'))
            
        elif self.path == '/files':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            files_info = self.get_uploaded_files()
            self.wfile.write(json.dumps(files_info).encode('utf-8'))
            
        elif self.path == '/git-status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            git_status = self.get_git_status()
            self.wfile.write(json.dumps(git_status).encode('utf-8'))
            
        else:
            self.send_error(404)
    
    def do_POST(self):
        """处理POST请求"""
        if self.path == '/upload':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                
                data = json.loads(post_data.decode('utf-8'))
                filename = data.get('filename', '')
                content = data.get('content', '')
                
                # 保存文件并推送到Git
                saved_filename, saved_path, git_url = save_uploaded_file_and_push_to_git(filename, content)
                
                if saved_filename:
                    response = {
                        'success': True,
                        'filename': saved_filename,
                        'path': saved_path,
                        'git_url': git_url,
                        'message': '文件上传成功并已推送到Git仓库'
                    }
                else:
                    response = {
                        'success': False,
                        'error': '文件保存或Git推送失败'
                    }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
            except Exception as e:
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
    
    def get_git_status(self):
        """获取Git仓库状态"""
        try:
            # 检查是否是Git仓库
            result = subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'], 
                                  capture_output=True, text=True, cwd=os.getcwd())
            
            if result.returncode != 0:
                return {
                    'git_ready': False,
                    'message': '当前目录不是Git仓库',
                    'repository': '未配置'
                }
            
            # 获取远程仓库信息
            result = subprocess.run(['git', 'remote', '-v'], 
                                  capture_output=True, text=True, cwd=os.getcwd())
            
            if result.returncode == 0 and result.stdout.strip():
                repository = result.stdout.strip().split('\n')[0].split()[1]
                return {
                    'git_ready': True,
                    'repository': repository,
                    'message': 'Git仓库配置正常'
                }
            else:
                return {
                    'git_ready': False,
                    'message': '未配置远程Git仓库',
                    'repository': '未配置'
                }
                
        except Exception as e:
            return {
                'git_ready': False,
                'message': f'Git状态检查失败: {str(e)}',
                'repository': '未知'
            }

def save_uploaded_file_and_push_to_git(filename, content):
    """保存上传的文件到uploads目录并推送到Git仓库"""
    try:
        # 创建uploads目录
        uploads_dir = os.path.join(os.getcwd(), "uploads")
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)
            print(f"创建上传目录: {uploads_dir}")
        
        # 生成唯一文件名
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
        
        # 推送到Git仓库
        git_url = push_to_git_repository(unique_filename, file_path)
        
        return unique_filename, file_path, git_url
        
    except Exception as e:
        print(f"保存文件时出错: {e}")
        return None, None, None

def push_to_git_repository(filename, file_path):
    """推送到Git仓库"""
    try:
        print(f"开始推送 {filename} 到Git仓库...")
        
        # 添加文件到Git
        result = subprocess.run(['git', 'add', file_path], 
                              capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode != 0:
            print(f"Git add失败: {result.stderr}")
            return None
        
        # 提交更改
        commit_message = f"添加课件文件: {filename} ({time.strftime('%Y-%m-%d %H:%M:%S')})"
        result = subprocess.run(['git', 'commit', '-m', commit_message], 
                              capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode != 0:
            print(f"Git commit失败: {result.stderr}")
            # 如果是"nothing to commit"，说明文件没有变化，这是正常的
            if "nothing to commit" in result.stderr:
                print("文件没有变化，跳过提交")
                return get_github_url()
            return None
        
        # 推送到远程仓库
        result = subprocess.run(['git', 'push', 'origin', 'main'], 
                              capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode != 0:
            print(f"Git push失败: {result.stderr}")
            return None
        
        print(f"成功推送到Git仓库: {filename}")
        return get_github_url()
        
    except Exception as e:
        print(f"Git推送过程中出错: {e}")
        return None

def get_github_url():
    """获取GitHub URL"""
    try:
        result = subprocess.run(['git', 'remote', '-v'], 
                              capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0 and result.stdout.strip():
            remote_url = result.stdout.strip().split('\n')[0].split()[1]
            # 转换为GitHub URL格式
            if remote_url.startswith('git@github.com:'):
                github_url = remote_url.replace('git@github.com:', 'https://github.com/').replace('.git', '')
                return github_url
            elif remote_url.startswith('https://github.com/'):
                return remote_url.replace('.git', '')
        
        return "GitHub仓库"
    except:
        return "GitHub仓库"

def parse_html_content(content, original_filename):
    """解析HTML内容提取信息"""
    try:
        title = original_filename.replace('.html', '').replace('.HTML', '')
        
        import re
        
        # 查找h1标签
        h1_match = re.search(r'<h1[^>]*>([^<]+)</h1>', content, re.IGNORECASE)
        if h1_match:
            title = h1_match.group(1).strip()
        
        # 提取作者信息
        author = "未知作者"
        author_patterns = [
            r'作者[：:]\s*([^\n\r<]+)',
            r'制作者[：:]\s*([^\n\r<]+)'
        ]
        
        for pattern in author_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                author = match.group(1).strip()
                break
        
        return {
            'title': title,
            'author': author,
            'filename': original_filename
        }
    except Exception as e:
        print(f"解析HTML内容时出错: {e}")
        return {
            'title': original_filename,
            'author': '未知作者',
            'filename': original_filename
        }

def main():
    """启动服务器"""
    server_host = '0.0.0.0'
    server_port = 8080
    
    print("🧠 智能文件上传处理服务器已启动")
    print("=" * 50)
    print(f"🌐 本地访问: http://localhost:{server_port}")
    print(f"🌐 网络访问: http://[您的IP地址]:{server_port}")
    print(f"📁 上传目录: {os.path.join(os.getcwd(), 'uploads')}")
    print(f"🌐 Git推送: 自动推送到Git仓库")
    print("=" * 50)
    print("💡 使用说明:")
    print("1. 在本机上访问: http://localhost:8080")
    print("2. 在其他设备上访问: http://[本机IP]:8080")
    print("3. 选择要上传的HTML课件文件")
    print("4. 点击'上传文件'按钮")
    print("5. 文件将自动保存到uploads目录并推送到Git仓库")
    print("=" * 50)
    print("⚠️  注意：")
    print("• 其他设备需要与本机在同一网络下")
    print("• 需要配置Git仓库才能自动推送")
    print("⏹️  按 Ctrl+C 停止服务器")
    print("=" * 50)
    
    try:
        server = HTTPServer((server_host, server_port), GitUploadHandler)
        print("🚀 浏览器已自动打开...")
        webbrowser.open(f'http://localhost:{server_port}')
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
        server.shutdown()

if __name__ == '__main__':
    main()