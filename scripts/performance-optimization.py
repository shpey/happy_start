#!/usr/bin/env python3
"""
智能思维项目 - 性能优化脚本
自动优化系统配置和性能参数
"""

import os
import sys
import json
import subprocess
import platform
import psutil
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import requests

class PerformanceOptimizer:
    """性能优化器"""
    
    def __init__(self):
        self.system_info = self.get_system_info()
        self.optimization_results = []
        self.api_base_url = "http://localhost:8000"
    
    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        return {
            "platform": platform.platform(),
            "cpu_count": psutil.cpu_count(),
            "cpu_count_logical": psutil.cpu_count(logical=True),
            "memory_total_gb": psutil.virtual_memory().total / 1024 / 1024 / 1024,
            "disk_total_gb": psutil.disk_usage('/').total / 1024 / 1024 / 1024,
            "python_version": platform.python_version(),
            "is_windows": platform.system() == "Windows",
            "is_linux": platform.system() == "Linux",
            "is_macos": platform.system() == "Darwin"
        }
    
    def log_optimization(self, category: str, action: str, result: str, impact: str = "medium"):
        """记录优化操作"""
        optimization = {
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "action": action,
            "result": result,
            "impact": impact
        }
        self.optimization_results.append(optimization)
        
        impact_icon = "🔥" if impact == "high" else "⚡" if impact == "medium" else "💡"
        print(f"{impact_icon} [{category}] {action}: {result}")
    
    def optimize_python_environment(self):
        """优化Python环境"""
        print("\n🐍 Python环境优化")
        print("-" * 50)
        
        # 检查Python版本
        python_version = platform.python_version()
        if python_version < "3.9":
            self.log_optimization(
                "python", 
                "版本检查", 
                f"建议升级Python版本 (当前: {python_version}, 推荐: 3.11+)",
                "high"
            )
        else:
            self.log_optimization(
                "python", 
                "版本检查", 
                f"Python版本良好 ({python_version})",
                "low"
            )
        
        # 检查pip版本
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                                  capture_output=True, text=True)
            if "23." not in result.stdout:
                subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
                self.log_optimization(
                    "python", 
                    "pip升级", 
                    "pip已升级到最新版本",
                    "medium"
                )
        except Exception as e:
            self.log_optimization(
                "python", 
                "pip检查", 
                f"pip检查失败: {e}",
                "low"
            )
        
        # 安装性能优化包
        performance_packages = [
            "uvloop",  # 高性能事件循环
            "orjson",  # 快速JSON库
            "cython"   # Python编译器
        ]
        
        for package in performance_packages:
            try:
                __import__(package)
                self.log_optimization(
                    "python", 
                    f"{package}检查", 
                    f"{package}已安装",
                    "low"
                )
            except ImportError:
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", package], 
                                 check=True, capture_output=True)
                    self.log_optimization(
                        "python", 
                        f"{package}安装", 
                        f"{package}安装成功",
                        "medium"
                    )
                except subprocess.CalledProcessError:
                    self.log_optimization(
                        "python", 
                        f"{package}安装", 
                        f"{package}安装失败（可能不兼容当前平台）",
                        "low"
                    )
    
    def optimize_database_config(self):
        """优化数据库配置"""
        print("\n🗄️ 数据库配置优化")
        print("-" * 50)
        
        memory_gb = self.system_info["memory_total_gb"]
        
        # 根据系统内存优化数据库连接池
        if memory_gb >= 16:
            max_connections = 100
            pool_size = 20
        elif memory_gb >= 8:
            max_connections = 50
            pool_size = 10
        else:
            max_connections = 20
            pool_size = 5
        
        # 生成优化的数据库配置
        db_config = {
            "pool_size": pool_size,
            "max_overflow": max_connections - pool_size,
            "pool_timeout": 30,
            "pool_recycle": 3600,
            "echo": False,  # 生产环境关闭SQL日志
            "pool_pre_ping": True  # 连接预检查
        }
        
        config_path = os.path.join("backend", "database_config.json")
        with open(config_path, "w") as f:
            json.dump(db_config, f, indent=2)
        
        self.log_optimization(
            "database", 
            "连接池配置", 
            f"已优化数据库连接池配置 (pool_size: {pool_size}, max_connections: {max_connections})",
            "high"
        )
        
        # Redis配置优化
        redis_config = {
            "max_connections": min(50, max_connections),
            "retry_on_timeout": True,
            "socket_keepalive": True,
            "socket_keepalive_options": {},
            "connection_pool_kwargs": {
                "max_connections": min(50, max_connections)
            }
        }
        
        redis_config_path = os.path.join("backend", "redis_config.json")
        with open(redis_config_path, "w") as f:
            json.dump(redis_config, f, indent=2)
        
        self.log_optimization(
            "database", 
            "Redis配置", 
            f"已优化Redis连接配置 (max_connections: {redis_config['max_connections']})",
            "medium"
        )
    
    def optimize_web_server(self):
        """优化Web服务器配置"""
        print("\n🚀 Web服务器优化")
        print("-" * 50)
        
        cpu_count = self.system_info["cpu_count"]
        memory_gb = self.system_info["memory_total_gb"]
        
        # 计算最优worker数量
        workers = min(cpu_count * 2 + 1, 8)  # 不超过8个worker
        
        # 根据内存计算worker内存限制
        worker_memory_mb = int((memory_gb * 0.7 * 1024) / workers)  # 使用70%内存
        
        # 生成uvicorn配置
        uvicorn_config = {
            "host": "0.0.0.0",
            "port": 8000,
            "workers": workers,
            "worker_class": "uvicorn.workers.UvicornWorker",
            "worker_connections": 1000,
            "max_requests": 1000,
            "max_requests_jitter": 100,
            "timeout": 30,
            "keepalive": 2,
            "backlog": 2048
        }
        
        config_path = os.path.join("backend", "uvicorn_config.json")
        with open(config_path, "w") as f:
            json.dump(uvicorn_config, f, indent=2)
        
        self.log_optimization(
            "web_server", 
            "Uvicorn配置", 
            f"已优化Web服务器配置 (workers: {workers}, memory_per_worker: {worker_memory_mb}MB)",
            "high"
        )
        
        # 生成启动脚本
        start_script = f"""#!/bin/bash
# 优化的服务器启动脚本
export PYTHONPATH=$PWD
export PYTHONUNBUFFERED=1

# 内存限制
ulimit -v {worker_memory_mb * 1024}

# 启动服务器
uvicorn main:app \\
    --host 0.0.0.0 \\
    --port 8000 \\
    --workers {workers} \\
    --worker-class uvicorn.workers.UvicornWorker \\
    --access-log \\
    --log-level info
"""
        
        script_path = os.path.join("backend", "start_optimized.sh")
        with open(script_path, "w") as f:
            f.write(start_script)
        
        # 使脚本可执行
        if not self.system_info["is_windows"]:
            os.chmod(script_path, 0o755)
        
        self.log_optimization(
            "web_server", 
            "启动脚本", 
            f"已生成优化启动脚本: {script_path}",
            "medium"
        )
    
    def optimize_frontend_build(self):
        """优化前端构建配置"""
        print("\n🎨 前端构建优化")
        print("-" * 50)
        
        frontend_dir = "frontend"
        if not os.path.exists(frontend_dir):
            self.log_optimization(
                "frontend", 
                "目录检查", 
                "前端目录不存在，跳过优化",
                "low"
            )
            return
        
        # 检查package.json
        package_json_path = os.path.join(frontend_dir, "package.json")
        if os.path.exists(package_json_path):
            with open(package_json_path, "r", encoding="utf-8") as f:
                package_data = json.load(f)
            
            # 添加优化的构建脚本
            package_data["scripts"]["build:prod"] = "vite build --mode production"
            package_data["scripts"]["build:analyze"] = "vite build --mode production && npx vite-bundle-analyzer dist"
            package_data["scripts"]["preview:prod"] = "vite preview --port 3000"
            
            with open(package_json_path, "w", encoding="utf-8") as f:
                json.dump(package_data, f, indent=2, ensure_ascii=False)
            
            self.log_optimization(
                "frontend", 
                "构建脚本", 
                "已添加优化的构建脚本",
                "medium"
            )
        
        # 创建优化的Vite配置
        vite_config_path = os.path.join(frontend_dir, "vite.config.prod.ts")
        vite_config = """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

export default defineConfig({
  plugins: [react()],
  
  // 生产环境优化
  build: {
    outDir: 'dist',
    sourcemap: false,  // 生产环境关闭sourcemap
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,  // 移除console.log
        drop_debugger: true,
        pure_funcs: ['console.log', 'console.info', 'console.debug']
      }
    },
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          material: ['@mui/material', '@mui/icons-material'],
          three: ['three', '@react-three/fiber', '@react-three/drei'],
          router: ['react-router-dom'],
          redux: ['@reduxjs/toolkit', 'react-redux'],
          charts: ['recharts', 'chart.js'],
          utils: ['lodash', 'date-fns', 'axios']
        }
      }
    },
    chunkSizeWarningLimit: 1000
  },
  
  // 性能优化
  define: {
    __DEV__: false,
    'process.env.NODE_ENV': '"production"'
  },
  
  // 静态资源优化
  assetsInclude: ['**/*.woff', '**/*.woff2'],
  
  // 别名配置
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@components': resolve(__dirname, 'src/components'),
      '@pages': resolve(__dirname, 'src/pages'),
      '@services': resolve(__dirname, 'src/services'),
      '@utils': resolve(__dirname, 'src/utils'),
      '@types': resolve(__dirname, 'src/types'),
      '@assets': resolve(__dirname, 'src/assets'),
      '@styles': resolve(__dirname, 'src/styles')
    }
  },
  
  // 预览服务器配置
  preview: {
    port: 3000,
    host: true,
    strictPort: true
  },
  
  // 依赖优化
  optimizeDeps: {
    include: ['react', 'react-dom', '@mui/material', '@mui/icons-material'],
    exclude: ['@types/*']
  }
})
"""
        
        with open(vite_config_path, "w", encoding="utf-8") as f:
            f.write(vite_config)
        
        self.log_optimization(
            "frontend", 
            "Vite配置", 
            "已创建优化的生产环境Vite配置",
            "high"
        )
    
    def optimize_system_limits(self):
        """优化系统限制"""
        print("\n⚙️ 系统限制优化")
        print("-" * 50)
        
        if self.system_info["is_windows"]:
            self.log_optimization(
                "system", 
                "系统限制", 
                "Windows系统，跳过系统限制优化",
                "low"
            )
            return
        
        # 生成系统优化建议
        optimizations = []
        
        # 文件描述符限制
        try:
            import resource
            soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
            if soft < 65536:
                optimizations.append(f"建议增加文件描述符限制: 当前 {soft}, 建议 65536")
        except:
            pass
        
        # 进程限制
        try:
            soft, hard = resource.getrlimit(resource.RLIMIT_NPROC)
            if soft < 32768:
                optimizations.append(f"建议增加进程数限制: 当前 {soft}, 建议 32768")
        except:
            pass
        
        if optimizations:
            limits_conf = """# 智能思维项目系统限制优化
# 添加到 /etc/security/limits.conf

* soft nofile 65536
* hard nofile 65536
* soft nproc 32768
* hard nproc 32768
"""
            
            with open("system_limits.conf", "w") as f:
                f.write(limits_conf)
            
            for opt in optimizations:
                self.log_optimization("system", "限制检查", opt, "medium")
            
            self.log_optimization(
                "system", 
                "配置文件", 
                "已生成system_limits.conf，请管理员手动应用",
                "high"
            )
        else:
            self.log_optimization(
                "system", 
                "系统限制", 
                "系统限制配置良好",
                "low"
            )
    
    def optimize_memory_usage(self):
        """优化内存使用"""
        print("\n🧠 内存使用优化")
        print("-" * 50)
        
        memory_gb = self.system_info["memory_total_gb"]
        
        # 生成内存优化建议
        if memory_gb < 4:
            suggestions = [
                "系统内存较少，建议增加到8GB以上",
                "启用交换文件以防止内存不足",
                "减少并发worker数量",
                "使用轻量级数据库配置"
            ]
            impact = "high"
        elif memory_gb < 8:
            suggestions = [
                "内存适中，建议优化垃圾回收",
                "监控内存使用情况",
                "适当的缓存配置"
            ]
            impact = "medium"
        else:
            suggestions = [
                "内存充足，可以启用内存缓存",
                "增加数据库连接池大小",
                "启用预加载和预缓存"
            ]
            impact = "low"
        
        for suggestion in suggestions:
            self.log_optimization("memory", "优化建议", suggestion, impact)
        
        # 生成垃圾回收优化配置
        gc_config = {
            "gc_threshold": [700, 10, 10],  # 调整垃圾回收阈值
            "enable_gc_debugging": False,
            "memory_limit_mb": int(memory_gb * 1024 * 0.8)  # 使用80%内存作为软限制
        }
        
        with open("memory_config.json", "w") as f:
            json.dump(gc_config, f, indent=2)
        
        self.log_optimization(
            "memory", 
            "垃圾回收配置", 
            f"已生成内存优化配置 (limit: {gc_config['memory_limit_mb']}MB)",
            "medium"
        )
    
    def check_service_health(self):
        """检查服务健康状态"""
        print("\n🔍 服务健康检查")
        print("-" * 50)
        
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            if response.status_code == 200:
                self.log_optimization(
                    "service", 
                    "健康检查", 
                    "后端服务运行正常",
                    "low"
                )
                
                # 获取性能指标
                try:
                    metrics_response = requests.get(f"{self.api_base_url}/api/v1/monitoring/system/status", timeout=5)
                    if metrics_response.status_code == 200:
                        data = metrics_response.json()
                        self.log_optimization(
                            "service", 
                            "性能指标", 
                            f"服务状态: {data.get('status', 'unknown')}, 运行时间: {data.get('uptime_seconds', 0):.0f}秒",
                            "low"
                        )
                except:
                    pass
            else:
                self.log_optimization(
                    "service", 
                    "健康检查", 
                    f"后端服务响应异常: HTTP {response.status_code}",
                    "high"
                )
        except requests.exceptions.ConnectionError:
            self.log_optimization(
                "service", 
                "健康检查", 
                "后端服务未运行或无法连接",
                "high"
            )
        except Exception as e:
            self.log_optimization(
                "service", 
                "健康检查", 
                f"检查失败: {e}",
                "medium"
            )
    
    def generate_optimization_report(self):
        """生成优化报告"""
        print("\n📊 优化报告")
        print("=" * 60)
        
        total_optimizations = len(self.optimization_results)
        high_impact = len([o for o in self.optimization_results if o["impact"] == "high"])
        medium_impact = len([o for o in self.optimization_results if o["impact"] == "medium"])
        low_impact = len([o for o in self.optimization_results if o["impact"] == "low"])
        
        print(f"🎯 总优化项目: {total_optimizations}")
        print(f"🔥 高影响优化: {high_impact}")
        print(f"⚡ 中等影响优化: {medium_impact}")
        print(f"💡 低影响优化: {low_impact}")
        
        # 按类别分组
        categories = {}
        for opt in self.optimization_results:
            category = opt["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append(opt)
        
        print(f"\n📋 分类统计:")
        for category, opts in categories.items():
            print(f"   {category}: {len(opts)} 项")
        
        # 保存详细报告
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "system_info": self.system_info,
            "summary": {
                "total": total_optimizations,
                "high_impact": high_impact,
                "medium_impact": medium_impact,
                "low_impact": low_impact
            },
            "categories": categories,
            "optimizations": self.optimization_results
        }
        
        with open("performance_optimization_report.json", "w") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 详细报告已保存到: performance_optimization_report.json")
        
        # 生成建议
        print(f"\n🚀 下一步建议:")
        if high_impact > 0:
            print("   1. 优先处理高影响项目，这些可以显著提升性能")
        if medium_impact > 0:
            print("   2. 处理中等影响项目，进一步优化系统")
        print("   3. 定期运行此脚本检查新的优化机会")
        print("   4. 监控系统性能指标，验证优化效果")
    
    def run_all_optimizations(self):
        """运行所有优化"""
        print("🚀 智能思维项目 - 性能优化")
        print("=" * 60)
        print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"💻 系统信息: {self.system_info['platform']}")
        print(f"🧠 内存: {self.system_info['memory_total_gb']:.1f}GB")
        print(f"⚙️ CPU: {self.system_info['cpu_count']} 核心")
        
        # 执行各种优化
        self.optimize_python_environment()
        self.optimize_database_config()
        self.optimize_web_server()
        self.optimize_frontend_build()
        self.optimize_system_limits()
        self.optimize_memory_usage()
        self.check_service_health()
        
        # 生成报告
        self.generate_optimization_report()
        
        print(f"\n⏰ 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🎉 性能优化完成！")

def main():
    """主函数"""
    optimizer = PerformanceOptimizer()
    optimizer.run_all_optimizations()

if __name__ == "__main__":
    main() 