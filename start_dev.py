#!/usr/bin/env python3
"""
智能思维与灵境融合项目 - 开发环境一键启动脚本
"""

import subprocess
import sys
import os
import time
import threading
import signal
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import psutil

class Colors:
    """终端颜色常量"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class DevServer:
    """开发服务器管理器"""
    
    def __init__(self):
        self.processes = []
        self.running = True
        
    def print_banner(self):
        """打印启动横幅"""
        banner = f"""
{Colors.HEADER}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                智能思维与灵境融合项目                          ║
║              Intelligent Thinking & Metaverse                ║  
║                   开发环境启动工具                           ║
╚══════════════════════════════════════════════════════════════╝
{Colors.ENDC}

{Colors.OKCYAN}🚀 准备启动开发环境...{Colors.ENDC}
"""
        print(banner)
    
    def check_dependencies(self):
        """检查系统依赖"""
        print(f"{Colors.OKBLUE}📋 检查系统依赖...{Colors.ENDC}")
        
        dependencies = {
            'docker': 'Docker',
            'docker-compose': 'Docker Compose', 
            'node': 'Node.js',
            'npm': 'NPM',
            'python': 'Python'
        }
        
        missing = []
        for cmd, name in dependencies.items():
            try:
                result = subprocess.run([cmd, '--version'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    version = result.stdout.strip().split('\n')[0]
                    print(f"  ✅ {name}: {version}")
                else:
                    missing.append(name)
            except FileNotFoundError:
                missing.append(name)
        
        if missing:
            print(f"{Colors.FAIL}❌ 缺少依赖: {', '.join(missing)}{Colors.ENDC}")
            return False
        
        print(f"{Colors.OKGREEN}✅ 所有依赖检查通过{Colors.ENDC}")
        return True
    
    def check_ports(self):
        """检查端口占用"""
        print(f"{Colors.OKBLUE}🔍 检查端口占用...{Colors.ENDC}")
        
        ports = {
            3000: "React前端",
            8000: "FastAPI后端", 
            5432: "PostgreSQL",
            6379: "Redis",
            7474: "Neo4j浏览器",
            7687: "Neo4j Bolt"
        }
        
        occupied = []
        for port, service in ports.items():
            if self.is_port_occupied(port):
                occupied.append(f"{service} (端口 {port})")
                print(f"  ⚠️  端口 {port} 已被占用 ({service})")
            else:
                print(f"  ✅ 端口 {port} 可用 ({service})")
        
        if occupied:
            print(f"{Colors.WARNING}⚠️ 以下服务端口已被占用: {', '.join(occupied)}{Colors.ENDC}")
            print(f"{Colors.WARNING}这可能导致服务启动冲突{Colors.ENDC}")
            return False
        
        return True
    
    def is_port_occupied(self, port):
        """检查端口是否被占用"""
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port:
                    return True
            return False
        except:
            # 备用方法
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(('localhost', port)) == 0
    
    def setup_environment(self):
        """设置开发环境"""
        print(f"{Colors.OKBLUE}⚙️ 设置开发环境...{Colors.ENDC}")
        
        # 检查环境变量文件
        if not os.path.exists('.env'):
            if os.path.exists('env.example'):
                print("  📋 复制环境变量模板...")
                subprocess.run(['cp', 'env.example', '.env'])
                print(f"  ✅ 已创建 .env 文件，请根据需要修改配置")
            else:
                print(f"  {Colors.WARNING}⚠️ 未找到环境变量模板{Colors.ENDC}")
        
        # 创建必要的目录
        directories = [
            'logs',
            'uploads', 
            'models_cache',
            'backend/logs'
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            print(f"  📁 创建目录: {directory}")
    
    def start_infrastructure(self):
        """启动基础设施服务（数据库等）"""
        print(f"{Colors.OKBLUE}🗄️ 启动基础设施服务...{Colors.ENDC}")
        
        try:
            # 启动Docker Compose服务
            print("  🐳 启动 Docker 服务...")
            process = subprocess.Popen(
                ['docker-compose', 'up', '-d', 'postgres', 'redis', 'neo4j'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                print(f"  ✅ Docker 服务启动成功")
                
                # 等待服务就绪
                print("  ⏳ 等待服务就绪...")
                time.sleep(10)
                
                return True
            else:
                print(f"  {Colors.FAIL}❌ Docker 服务启动失败: {stderr}{Colors.ENDC}")
                return False
                
        except Exception as e:
            print(f"  {Colors.FAIL}❌ 启动基础设施失败: {e}{Colors.ENDC}")
            return False
    
    def initialize_database(self):
        """初始化数据库"""
        print(f"{Colors.OKBLUE}🗃️ 初始化数据库...{Colors.ENDC}")
        
        try:
            # 运行数据库初始化脚本
            result = subprocess.run(
                [sys.executable, 'backend/scripts/init_db.py'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"  ✅ 数据库初始化成功")
                return True
            else:
                print(f"  {Colors.WARNING}⚠️ 数据库初始化警告: {result.stderr}{Colors.ENDC}")
                # 即使有警告也继续执行
                return True
                
        except Exception as e:
            print(f"  {Colors.FAIL}❌ 数据库初始化失败: {e}{Colors.ENDC}")
            return False
    
    def install_dependencies(self):
        """安装项目依赖"""
        print(f"{Colors.OKBLUE}📦 安装项目依赖...{Colors.ENDC}")
        
        # 安装后端依赖
        print("  🐍 安装 Python 依赖...")
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', 'backend/requirements.txt'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("  ✅ Python 依赖安装成功")
        else:
            print(f"  {Colors.WARNING}⚠️ Python 依赖安装警告: {result.stderr}{Colors.ENDC}")
        
        # 安装前端依赖
        if os.path.exists('frontend/package.json'):
            print("  📦 安装 Node.js 依赖...")
            result = subprocess.run(
                ['npm', 'install'],
                cwd='frontend',
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("  ✅ Node.js 依赖安装成功")
            else:
                print(f"  {Colors.WARNING}⚠️ Node.js 依赖安装警告: {result.stderr}{Colors.ENDC}")
    
    def start_backend(self):
        """启动后端服务"""
        print(f"{Colors.OKGREEN}🚀 启动后端服务...{Colors.ENDC}")
        
        def run_backend():
            try:
                process = subprocess.Popen(
                    [sys.executable, 'main.py'],
                    cwd='backend',
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                self.processes.append(process)
                
                # 实时输出日志
                for line in process.stdout:
                    if self.running:
                        print(f"  🐍 [Backend] {line.strip()}")
                    else:
                        break
                        
            except Exception as e:
                print(f"  {Colors.FAIL}❌ 后端启动失败: {e}{Colors.ENDC}")
        
        backend_thread = threading.Thread(target=run_backend, daemon=True)
        backend_thread.start()
        
        # 等待后端启动
        time.sleep(5)
        return True
    
    def start_frontend(self):
        """启动前端服务"""
        print(f"{Colors.OKGREEN}🚀 启动前端服务...{Colors.ENDC}")
        
        def run_frontend():
            try:
                process = subprocess.Popen(
                    ['npm', 'start'],
                    cwd='frontend',
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                self.processes.append(process)
                
                # 实时输出日志
                for line in process.stdout:
                    if self.running:
                        print(f"  ⚛️  [Frontend] {line.strip()}")
                    else:
                        break
                        
            except Exception as e:
                print(f"  {Colors.FAIL}❌ 前端启动失败: {e}{Colors.ENDC}")
        
        frontend_thread = threading.Thread(target=run_frontend, daemon=True)
        frontend_thread.start()
        
        return True
    
    def print_success_info(self):
        """打印启动成功信息"""
        success_info = f"""
{Colors.OKGREEN}{Colors.BOLD}
🎉 开发环境启动成功！
{Colors.ENDC}

{Colors.OKCYAN}📊 服务状态:{Colors.ENDC}
  • 前端应用: {Colors.OKGREEN}http://localhost:3000{Colors.ENDC}
  • 后端API: {Colors.OKGREEN}http://localhost:8000{Colors.ENDC}
  • API文档: {Colors.OKGREEN}http://localhost:8000/docs{Colors.ENDC}
  • Neo4j浏览器: {Colors.OKGREEN}http://localhost:7474{Colors.ENDC}

{Colors.OKCYAN}🎮 快速开始:{Colors.ENDC}
  • 访问前端应用开始体验
  • 使用演示账号: demo_user / demo123
  • 管理员账号: admin / admin123

{Colors.OKCYAN}📝 开发工具:{Colors.ENDC}
  • 查看API文档: {Colors.OKBLUE}http://localhost:8000/docs{Colors.ENDC}
  • 数据库管理: {Colors.OKBLUE}http://localhost:7474{Colors.ENDC}
  • 日志文件: {Colors.OKBLUE}./logs/{Colors.ENDC}

{Colors.WARNING}按 Ctrl+C 停止服务{Colors.ENDC}
"""
        print(success_info)
    
    def cleanup(self):
        """清理进程"""
        print(f"\n{Colors.WARNING}🛑 正在关闭服务...{Colors.ENDC}")
        
        self.running = False
        
        # 终止启动的进程
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
        
        # 停止Docker服务
        try:
            subprocess.run(['docker-compose', 'down'], 
                         capture_output=True, timeout=30)
            print(f"  ✅ Docker 服务已停止")
        except:
            print(f"  {Colors.WARNING}⚠️ Docker 服务停止失败{Colors.ENDC}")
        
        print(f"{Colors.OKGREEN}✅ 清理完成{Colors.ENDC}")
    
    def run(self):
        """运行开发服务器"""
        try:
            self.print_banner()
            
            # 检查系统环境
            if not self.check_dependencies():
                sys.exit(1)
            
            # 检查端口
            self.check_ports()
            
            # 设置环境
            self.setup_environment()
            
            # 安装依赖
            self.install_dependencies()
            
            # 启动基础设施
            if not self.start_infrastructure():
                sys.exit(1)
            
            # 初始化数据库
            if not self.initialize_database():
                print(f"{Colors.WARNING}⚠️ 数据库初始化失败，但继续启动服务{Colors.ENDC}")
            
            # 启动应用服务
            self.start_backend()
            self.start_frontend()
            
            # 显示成功信息
            self.print_success_info()
            
            # 保持运行
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()

def main():
    """主函数"""
    server = DevServer()
    
    # 注册信号处理器
    def signal_handler(sig, frame):
        server.running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    server.run()

if __name__ == "__main__":
    main() 