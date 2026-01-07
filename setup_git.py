#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git仓库快速配置脚本
帮助用户快速设置Git仓库并推送到GitHub
"""

import os
import subprocess
import sys

def run_command(command, cwd=None):
    """执行命令并返回结果"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=cwd)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_git_installed():
    """检查Git是否已安装"""
    success, stdout, stderr = run_command("git --version")
    if success:
        print("✅ Git已安装:", stdout.strip())
        return True
    else:
        print("❌ Git未安装，请先安装Git")
        return False

def configure_git():
    """配置Git用户信息"""
    print("\n🔧 配置Git用户信息")
    print("请输入您的Git信息（如果没有，可以先跳过）:")
    
    # 获取用户输入
    name = input("请输入您的姓名 (用于Git提交): ").strip()
    email = input("请输入您的邮箱: ").strip()
    
    if name:
        success, stdout, stderr = run_command(f'git config --global user.name "{name}"')
        if success:
            print(f"✅ 已设置用户名: {name}")
        else:
            print(f"❌ 设置用户名失败: {stderr}")
    
    if email:
        success, stdout, stderr = run_command(f'git config --global user.email "{email}"')
        if success:
            print(f"✅ 已设置邮箱: {email}")
        else:
            print(f"❌ 设置邮箱失败: {stderr}")

def init_git_repo():
    """初始化Git仓库"""
    print("\n🔄 初始化Git仓库")
    
    # 检查是否已经是Git仓库
    success, stdout, stderr = run_command("git rev-parse --is-inside-work-tree")
    if success:
        print("✅ 当前目录已经是Git仓库")
        return True
    
    # 初始化仓库
    success, stdout, stderr = run_command("git init")
    if success:
        print("✅ Git仓库初始化成功")
        
        # 设置默认分支为main
        run_command("git branch -M main")
        print("✅ 已设置默认分支为main")
        return True
    else:
        print(f"❌ Git仓库初始化失败: {stderr}")
        return False

def add_remote_repo():
    """添加远程仓库"""
    print("\n🌐 配置远程Git仓库")
    print("请选择以下选项之一:")
    print("1. 创建新的GitHub仓库")
    print("2. 使用现有的仓库地址")
    print("3. 跳过远程仓库配置")
    
    choice = input("请输入选择 (1-3): ").strip()
    
    if choice == "1":
        print("\n📝 创建GitHub仓库步骤:")
        print("1. 访问 https://github.com")
        print("2. 点击右上角的 '+' 按钮，选择 'New repository'")
        print("3. 填写仓库信息:")
        print("   - 仓库名称: 初中数学课件库")
        print("   - 描述: 初中数学动态交互课件集合")
        print("   - 可见性: 公开或私有")
        print("4. 创建仓库后，复制仓库地址")
        print("5. 回到这里输入仓库地址")
        
        repo_url = input("\n请输入GitHub仓库地址 (如: https://github.com/用户名/仓库名.git): ").strip()
        if repo_url:
            return add_remote_url(repo_url)
    
    elif choice == "2":
        repo_url = input("请输入现有仓库地址: ").strip()
        if repo_url:
            return add_remote_url(repo_url)
    
    elif choice == "3":
        print("⏭️ 跳过远程仓库配置")
        return True
    
    else:
        print("❌ 无效选择")
        return False

def add_remote_url(repo_url):
    """添加远程仓库URL"""
    # 检查是否已有远程仓库
    success, stdout, stderr = run_command("git remote -v")
    if success and stdout.strip():
        print("ℹ️  发现现有远程仓库配置:")
        print(stdout.strip())
        
        choice = input("是否要替换现有远程仓库? (y/N): ").strip().lower()
        if choice != 'y':
            return False
        
        # 移除现有远程仓库
        run_command("git remote remove origin")
    
    # 添加新的远程仓库
    success, stdout, stderr = run_command(f'git remote add origin "{repo_url}"')
    if success:
        print(f"✅ 已添加远程仓库: {repo_url}")
        return True
    else:
        print(f"❌ 添加远程仓库失败: {stderr}")
        return False

def first_commit_and_push():
    """首次提交并推送"""
    print("\n📤 首次提交并推送到远程仓库")
    
    # 检查是否有远程仓库
    success, stdout, stderr = run_command("git remote -v")
    if not success or not stdout.strip():
        print("⚠️  没有配置远程仓库，跳过推送")
        return False
    
    # 添加所有文件
    print("📁 添加文件到Git...")
    success, stdout, stderr = run_command("git add .")
    if not success:
        print(f"❌ 添加文件失败: {stderr}")
        return False
    print("✅ 文件添加成功")
    
    # 检查是否有变化
    success, stdout, stderr = run_command("git status --porcelain")
    if not stdout.strip():
        print("ℹ️  没有文件变化需要提交")
        return True
    
    # 提交
    print("📝 创建提交...")
    success, stdout, stderr = run_command('git commit -m "初始提交：创建课件上传系统"')
    if not success:
        print(f"❌ 提交失败: {stderr}")
        return False
    print("✅ 提交创建成功")
    
    # 推送
    print("🚀 推送到远程仓库...")
    success, stdout, stderr = run_command("git push -u origin main")
    if success:
        print("✅ 推送到远程仓库成功!")
        return True
    else:
        print(f"⚠️  推送失败 (可能需要Git认证): {stderr}")
        print("💡 您可能需要:")
        print("   1. 配置GitHub访问令牌")
        print("   2. 或使用SSH密钥")
        print("   3. 稍后手动推送")
        return False

def show_next_steps():
    """显示后续步骤"""
    print("\n" + "="*50)
    print("🎉 Git仓库配置完成!")
    print("="*50)
    print("📋 后续步骤:")
    print("1. 启动智能上传服务器:")
    print("   python git_push_server.py")
    print()
    print("2. 访问上传页面:")
    print("   本机: http://localhost:8080")
    print("   网络: http://192.168.2.9:8080")
    print()
    print("3. 上传课件文件:")
    print("   - 选择HTML课件文件")
    print("   - 点击上传按钮")
    print("   - 文件将自动保存并推送到Git")
    print()
    print("4. 在GitHub上查看:")
    print("   https://github.com/您的用户名/仓库名/tree/main/uploads")
    print("="*50)

def main():
    """主函数"""
    print("🚀 Git仓库快速配置向导")
    print("="*50)
    
    # 检查Git安装
    if not check_git_installed():
        print("\n💡 请先安装Git:")
        print("   下载地址: https://git-scm.com/downloads")
        sys.exit(1)
    
    # 配置Git用户信息
    configure_git()
    
    # 初始化仓库
    if not init_git_repo():
        print("❌ Git仓库初始化失败")
        sys.exit(1)
    
    # 添加远程仓库
    if not add_remote_repo():
        print("❌ 远程仓库配置失败")
        print("💡 您可以稍后手动配置远程仓库")
    
    # 首次提交
    first_commit_and_push()
    
    # 显示后续步骤
    show_next_steps()

if __name__ == '__main__':
    main()