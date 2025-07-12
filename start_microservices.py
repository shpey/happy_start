#!/usr/bin/env python3
"""
智能思维平台 - 微服务启动管理器
一键启动和管理所有微服务
"""

import os
import sys
import subprocess
import time
import requests
import json
import threading
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import webbrowser
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.live import Live
import click
import yaml
import psutil

# 初始化控制台
console = Console()

class MicroserviceManager:
    """微服务管理器"""
    
    def __init__(self):
        self.services = {
            "infrastructure": {
                "consul": {
                    "command": "consul agent -dev -client=0.0.0.0",
                    "port": 8500,
                    "health_url": "http://localhost:8500/v1/status/leader",
                    "description": "服务注册与发现"
                },
                "redis": {
                    "command": "redis-server --port 6379",
                    "port": 6379,
                    "health_url": "redis://localhost:6379",
                    "description": "缓存和会话存储"
                },
                "postgres": {
                    "command": "pg_ctl -D /usr/local/var/postgres -l /usr/local/var/postgres/server.log start",
                    "port": 5432,
                    "health_url": "postgresql://localhost:5432",
                    "description": "主数据库"
                }
            },
            "core_services": {
                "api-gateway": {
                    "command": "python backend/microservices/gateway/main.py",
                    "port": 8080,
                    "health_url": "http://localhost:8080/health",
                    "description": "API网关和路由"
                },
                "auth-service": {
                    "command": "python backend/microservices/auth/main.py",
                    "port": 8081,
                    "health_url": "http://localhost:8081/health",
                    "description": "用户认证服务"
                },
                "thinking-service": {
                    "command": "python backend/microservices/thinking/main.py",
                    "port": 8082,
                    "health_url": "http://localhost:8082/health",
                    "description": "思维分析服务"
                },
                "collaboration-service": {
                    "command": "python backend/microservices/collaboration/main.py",
                    "port": 8083,
                    "health_url": "http://localhost:8083/health",
                    "description": "协作服务"
                }
            },
            "advanced_services": {
                "blockchain-service": {
                    "command": "python backend/microservices/blockchain/main.py",
                    "port": 8084,
                    "health_url": "http://localhost:8084/health",
                    "description": "区块链服务"
                },
                "graphql-service": {
                    "command": "python backend/microservices/graphql/main.py",
                    "port": 8085,
                    "health_url": "http://localhost:8085/health",
                    "description": "GraphQL API"
                },
                "ai-service": {
                    "command": "python backend/microservices/ai_advanced/main.py",
                    "port": 8086,
                    "health_url": "http://localhost:8086/health",
                    "description": "高级AI模型服务"
                },
                "quantum-service": {
                    "command": "python backend/microservices/quantum/main.py",
                    "port": 8087,
                    "health_url": "http://localhost:8087/health",
                    "description": "量子计算服务"
                }
            },
            "edge_services": {
                "edge-service": {
                    "command": "python backend/microservices/edge/main.py",
                    "port": 8088,
                    "health_url": "http://localhost:8088/health",
                    "description": "边缘计算服务"
                },
                "streaming-service": {
                    "command": "python backend/microservices/streaming/main.py",
                    "port": 8089,
                    "health_url": "http://localhost:8089/health",
                    "description": "实时数据流服务"
                },
                "voice-service": {
                    "command": "python backend/microservices/voice/main.py",
                    "port": 8090,
                    "health_url": "http://localhost:8090/health",
                    "description": "语音AI服务"
                }
            }
        }
        
        self.processes = {}
        self.service_status = {}
        self.startup_order = ["infrastructure", "core_services", "advanced_services", "edge_services"]
        
    def display_banner(self):
        """显示启动横幅"""
        banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                  🧠 智能思维平台 - 微服务架构                  ║
    ║                                                              ║
    ║  🔥 下一代AI驱动的思维分析与协作平台                           ║
    ║                                                              ║
    ║  技术栈：                                                     ║
    ║  • 🌐 微服务架构     • 🪙 区块链技术                           ║
    ║  • 🤖 高级AI模型     • ⚛️ 量子计算                            ║
    ║  • 📊 GraphQL API   • 🔄 实时数据流                           ║
    ║  • 🎯 边缘计算      • 🗣️ 语音AI                              ║
    ║                                                              ║
    ║  服务总数：11个微服务 + 基础设施                                ║
    ╚══════════════════════════════════════════════════════════════╝
        """
        console.print(Panel(banner, style="bold blue"))
    
    def check_prerequisites(self) -> bool:
        """检查前置条件"""
        console.print("\n🔍 检查系统前置条件...")
        
        prerequisites = {
            "Python >= 3.9": sys.version_info >= (3, 9),
            "Docker": self.check_docker(),
            "Redis": self.check_redis(),
            "PostgreSQL": self.check_postgres(),
            "端口可用性": self.check_ports(),
            "依赖包": self.check_dependencies()
        }
        
        table = Table(title="前置条件检查")
        table.add_column("项目", style="cyan")
        table.add_column("状态", style="green")
        table.add_column("描述", style="white")
        
        all_ok = True
        for item, status in prerequisites.items():
            status_text = "✅ 通过" if status else "❌ 失败"
            table.add_row(item, status_text, "")
            if not status:
                all_ok = False
        
        console.print(table)
        return all_ok
    
    def check_docker(self) -> bool:
        """检查Docker是否可用"""
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def check_redis(self) -> bool:
        """检查Redis是否可用"""
        try:
            result = subprocess.run(["redis-cli", "ping"], capture_output=True, text=True)
            return "PONG" in result.stdout
        except FileNotFoundError:
            return False
    
    def check_postgres(self) -> bool:
        """检查PostgreSQL是否可用"""
        try:
            result = subprocess.run(["pg_isready"], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def check_ports(self) -> bool:
        """检查端口是否可用"""
        ports_to_check = []
        for category in self.services.values():
            for service_info in category.values():
                ports_to_check.append(service_info["port"])
        
        for port in ports_to_check:
            if self.is_port_in_use(port):
                console.print(f"❌ 端口 {port} 已被占用")
                return False
        
        return True
    
    def check_dependencies(self) -> bool:
        """检查Python依赖包"""
        try:
            import fastapi
            import uvicorn
            import redis
            import sqlalchemy
            import qiskit
            import transformers
            return True
        except ImportError:
            return False
    
    def is_port_in_use(self, port: int) -> bool:
        """检查端口是否被占用"""
        for conn in psutil.net_connections():
            if conn.laddr.port == port:
                return True
        return False
    
    def start_service_category(self, category_name: str, services: Dict[str, Dict]):
        """启动一个服务类别"""
        console.print(f"\n🚀 启动 {category_name} 服务...")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            for service_name, service_info in services.items():
                task = progress.add_task(
                    f"启动 {service_name}...", 
                    total=None
                )
                
                try:
                    # 启动服务
                    process = subprocess.Popen(
                        service_info["command"],
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    
                    self.processes[service_name] = process
                    time.sleep(2)  # 等待服务启动
                    
                    # 检查服务健康状态
                    if self.check_service_health(service_name, service_info):
                        self.service_status[service_name] = "healthy"
                        progress.update(task, description=f"✅ {service_name} 已启动")
                    else:
                        self.service_status[service_name] = "unhealthy"
                        progress.update(task, description=f"❌ {service_name} 启动失败")
                    
                except Exception as e:
                    self.service_status[service_name] = "error"
                    progress.update(task, description=f"❌ {service_name} 错误: {str(e)}")
                
                progress.remove_task(task)
    
    def check_service_health(self, service_name: str, service_info: Dict) -> bool:
        """检查服务健康状态"""
        try:
            if service_info["health_url"].startswith("http"):
                response = requests.get(service_info["health_url"], timeout=5)
                return response.status_code == 200
            else:
                # 对于非HTTP服务，检查端口
                return not self.is_port_in_use(service_info["port"])
        except Exception:
            return False
    
    def display_service_status(self):
        """显示服务状态"""
        table = Table(title="🔧 微服务状态总览")
        table.add_column("服务名称", style="cyan")
        table.add_column("端口", style="yellow")
        table.add_column("状态", style="green")
        table.add_column("描述", style="white")
        table.add_column("访问地址", style="blue")
        
        for category_name, services in self.services.items():
            # 添加分类标题
            table.add_row(f"[bold]{category_name.upper()}[/bold]", "", "", "", "")
            
            for service_name, service_info in services.items():
                status = self.service_status.get(service_name, "unknown")
                status_icon = {
                    "healthy": "🟢 运行中",
                    "unhealthy": "🔴 异常",
                    "error": "❌ 错误",
                    "unknown": "⚪ 未知"
                }.get(status, "⚪ 未知")
                
                access_url = f"http://localhost:{service_info['port']}"
                
                table.add_row(
                    f"  {service_name}",
                    str(service_info["port"]),
                    status_icon,
                    service_info["description"],
                    access_url
                )
        
        console.print(table)
    
    def generate_service_dashboard(self):
        """生成服务仪表板"""
        healthy_count = sum(1 for status in self.service_status.values() if status == "healthy")
        total_count = len(self.service_status)
        
        dashboard_info = f"""
        🌟 智能思维平台 - 微服务仪表板
        
        📊 系统状态：
        • 运行中服务：{healthy_count}/{total_count}
        • 系统负载：{psutil.cpu_percent()}%
        • 内存使用：{psutil.virtual_memory().percent}%
        
        🔗 核心服务访问地址：
        • API网关：    http://localhost:8080
        • GraphQL：    http://localhost:8085/graphql
        • 区块链服务：  http://localhost:8084
        • AI服务：      http://localhost:8086
        • 量子计算：    http://localhost:8087
        
        📈 监控服务：
        • Prometheus：  http://localhost:9090
        • Grafana：     http://localhost:3000
        • Consul：      http://localhost:8500
        """
        
        console.print(Panel(dashboard_info, title="服务仪表板", style="green"))
    
    def open_service_urls(self):
        """打开服务访问地址"""
        urls_to_open = [
            "http://localhost:8080",    # API网关
            "http://localhost:8085/graphql",  # GraphQL
            "http://localhost:8087",    # 量子计算
            "http://localhost:8086",    # AI服务
        ]
        
        for url in urls_to_open:
            try:
                webbrowser.open(url)
                console.print(f"🌐 已打开: {url}")
            except Exception as e:
                console.print(f"❌ 无法打开 {url}: {e}")
    
    def start_all_services(self):
        """启动所有服务"""
        self.display_banner()
        
        # 检查前置条件
        if not self.check_prerequisites():
            console.print("❌ 前置条件检查失败，请解决上述问题后重试")
            return False
        
        # 按顺序启动服务
        for category_name in self.startup_order:
            if category_name in self.services:
                self.start_service_category(category_name, self.services[category_name])
                time.sleep(3)  # 等待服务稳定
        
        # 显示服务状态
        self.display_service_status()
        
        # 生成仪表板
        self.generate_service_dashboard()
        
        # 打开服务地址
        console.print("\n🌐 正在打开服务地址...")
        self.open_service_urls()
        
        return True
    
    def stop_all_services(self):
        """停止所有服务"""
        console.print("\n🛑 正在停止所有服务...")
        
        for service_name, process in self.processes.items():
            try:
                process.terminate()
                process.wait(timeout=5)
                console.print(f"✅ 已停止 {service_name}")
            except subprocess.TimeoutExpired:
                process.kill()
                console.print(f"⚠️ 强制停止 {service_name}")
            except Exception as e:
                console.print(f"❌ 停止 {service_name} 时出错: {e}")
        
        console.print("🏁 所有服务已停止")
    
    def monitor_services(self):
        """监控服务状态"""
        console.print("\n📊 开始监控服务状态...")
        
        try:
            while True:
                # 更新服务状态
                for category_name, services in self.services.items():
                    for service_name, service_info in services.items():
                        if service_name in self.processes:
                            is_healthy = self.check_service_health(service_name, service_info)
                            self.service_status[service_name] = "healthy" if is_healthy else "unhealthy"
                
                # 显示状态
                os.system('clear' if os.name == 'posix' else 'cls')
                self.display_service_status()
                
                time.sleep(10)  # 每10秒检查一次
                
        except KeyboardInterrupt:
            console.print("\n⏹️ 停止监控")

# CLI命令接口
@click.group()
def cli():
    """智能思维平台 - 微服务管理器"""
    pass

@cli.command()
@click.option('--monitor', is_flag=True, help='启动后进入监控模式')
@click.option('--open-urls', is_flag=True, default=True, help='自动打开服务地址')
def start(monitor, open_urls):
    """启动所有微服务"""
    manager = MicroserviceManager()
    
    if manager.start_all_services():
        if monitor:
            manager.monitor_services()
        else:
            console.print("\n✨ 所有服务已启动！按 Ctrl+C 停止服务")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                manager.stop_all_services()

@cli.command()
def stop():
    """停止所有微服务"""
    manager = MicroserviceManager()
    manager.stop_all_services()

@cli.command()
def status():
    """查看服务状态"""
    manager = MicroserviceManager()
    manager.display_service_status()

@cli.command()
def monitor():
    """监控服务状态"""
    manager = MicroserviceManager()
    manager.monitor_services()

@cli.command()
def dashboard():
    """显示服务仪表板"""
    manager = MicroserviceManager()
    manager.generate_service_dashboard()

@cli.command()
def install():
    """安装依赖包"""
    console.print("📦 正在安装微服务依赖...")
    
    try:
        subprocess.run([
            "pip", "install", "-r", "backend/requirements.microservices.txt"
        ], check=True)
        console.print("✅ 依赖安装完成")
    except subprocess.CalledProcessError as e:
        console.print(f"❌ 依赖安装失败: {e}")

if __name__ == "__main__":
    cli() 