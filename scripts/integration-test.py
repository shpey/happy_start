#!/usr/bin/env python3
"""
智能思维项目 - 综合集成测试
验证所有系统组件的集成状态和功能
"""

import requests
import json
import time
import subprocess
import sys
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
import websockets

class IntegrationTester:
    """集成测试器"""
    
    def __init__(self):
        self.test_results = []
        self.services = {
            "backend": "http://localhost:8000",
            "frontend": "http://localhost:3000",
            "websocket": "ws://localhost:8000/ws"
        }
        self.test_user = {
            "username": "integration_test_user",
            "email": "test@example.com", 
            "password": "TestPassword123!",
            "full_name": "Integration Test User"
        }
        self.access_token = None
    
    def log_test(self, test_name: str, status: str, details: str = "", duration: float = 0):
        """记录测试结果"""
        result = {
            "test_name": test_name,
            "status": status,  # PASS, FAIL, SKIP
            "details": details,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⏭️"
        print(f"{status_icon} {test_name}: {details} ({duration:.2f}s)")
    
    def test_service_health(self):
        """测试服务健康状态"""
        print("\n🔍 1. 服务健康检查")
        print("-" * 50)
        
        for service_name, url in self.services.items():
            start_time = time.time()
            try:
                if service_name == "websocket":
                    # WebSocket测试将在后面单独进行
                    self.log_test(f"{service_name}_health", "SKIP", "WebSocket测试延后进行")
                    continue
                
                response = requests.get(f"{url}/health" if service_name == "backend" else url, timeout=5)
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    self.log_test(f"{service_name}_health", "PASS", f"服务正常运行", duration)
                else:
                    self.log_test(f"{service_name}_health", "FAIL", f"HTTP {response.status_code}", duration)
            except requests.exceptions.ConnectionError:
                duration = time.time() - start_time
                self.log_test(f"{service_name}_health", "FAIL", "连接失败", duration)
            except Exception as e:
                duration = time.time() - start_time
                self.log_test(f"{service_name}_health", "FAIL", str(e), duration)
    
    def test_api_endpoints(self):
        """测试API端点"""
        print("\n🔌 2. API端点测试")
        print("-" * 50)
        
        # 测试系统状态API
        self.test_system_status()
        
        # 测试用户管理API
        self.test_user_management()
        
        # 测试思维分析API
        self.test_thinking_analysis()
        
        # 测试文件上传API
        self.test_file_upload()
    
    def test_system_status(self):
        """测试系统状态API"""
        start_time = time.time()
        try:
            response = requests.get(f"{self.services['backend']}/api/v1/system/status")
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("system_status_api", "PASS", f"服务数: {len(data.get('services', []))}", duration)
            else:
                self.log_test("system_status_api", "FAIL", f"HTTP {response.status_code}", duration)
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("system_status_api", "FAIL", str(e), duration)
    
    def test_user_management(self):
        """测试用户管理功能"""
        # 测试用户注册
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.services['backend']}/api/v1/users/register",
                json=self.test_user
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.log_test("user_register", "PASS", f"用户ID: {data.get('user', {}).get('id')}", duration)
            elif response.status_code == 400 and "已存在" in response.text:
                self.log_test("user_register", "PASS", "用户已存在，跳过注册", duration)
                # 尝试登录获取token
                self.test_user_login()
            else:
                self.log_test("user_register", "FAIL", f"HTTP {response.status_code}", duration)
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("user_register", "FAIL", str(e), duration)
    
    def test_user_login(self):
        """测试用户登录"""
        start_time = time.time()
        try:
            login_data = {
                "username": self.test_user["username"],
                "password": self.test_user["password"]
            }
            response = requests.post(
                f"{self.services['backend']}/api/v1/users/login",
                json=login_data
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.log_test("user_login", "PASS", "登录成功", duration)
            else:
                self.log_test("user_login", "FAIL", f"HTTP {response.status_code}", duration)
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("user_login", "FAIL", str(e), duration)
    
    def test_thinking_analysis(self):
        """测试思维分析功能"""
        start_time = time.time()
        try:
            headers = {}
            if self.access_token:
                headers["Authorization"] = f"Bearer {self.access_token}"
            
            analysis_data = {
                "content": "这是一个测试思维分析的内容",
                "analysis_type": "comprehensive"
            }
            
            response = requests.post(
                f"{self.services['backend']}/api/v1/thinking/analyze",
                json=analysis_data,
                headers=headers
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("thinking_analysis", "PASS", f"分析ID: {data.get('analysis_id', 'N/A')}", duration)
            else:
                self.log_test("thinking_analysis", "FAIL", f"HTTP {response.status_code}", duration)
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("thinking_analysis", "FAIL", str(e), duration)
    
    def test_file_upload(self):
        """测试文件上传功能"""
        start_time = time.time()
        try:
            headers = {}
            if self.access_token:
                headers["Authorization"] = f"Bearer {self.access_token}"
            
            # 创建一个测试文件
            test_content = "这是一个测试文件内容"
            files = {"file": ("test.txt", test_content, "text/plain")}
            
            response = requests.post(
                f"{self.services['backend']}/api/v1/files/upload",
                files=files,
                headers=headers
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("file_upload", "PASS", f"文件ID: {data.get('file_id', 'N/A')}", duration)
            else:
                self.log_test("file_upload", "FAIL", f"HTTP {response.status_code}", duration)
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("file_upload", "FAIL", str(e), duration)
    
    def test_frontend_components(self):
        """测试前端组件"""
        print("\n🎨 3. 前端组件测试")
        print("-" * 50)
        
        # 测试主页访问
        start_time = time.time()
        try:
            response = requests.get(self.services["frontend"], timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                # 检查是否包含React应用的关键元素
                content = response.text
                if "root" in content and ("React" in content or "react" in content):
                    self.log_test("frontend_app", "PASS", "React应用加载正常", duration)
                else:
                    self.log_test("frontend_app", "PASS", "前端页面可访问", duration)
            else:
                self.log_test("frontend_app", "FAIL", f"HTTP {response.status_code}", duration)
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("frontend_app", "FAIL", str(e), duration)
    
    def test_security_features(self):
        """测试安全功能"""
        print("\n🔐 4. 安全功能测试")
        print("-" * 50)
        
        # 测试未授权访问
        self.test_unauthorized_access()
        
        # 测试JWT token验证
        self.test_token_validation()
        
        # 测试输入验证
        self.test_input_validation()
    
    def test_unauthorized_access(self):
        """测试未授权访问"""
        start_time = time.time()
        try:
            # 尝试不带token访问需要认证的API
            response = requests.get(f"{self.services['backend']}/api/v1/users/me")
            duration = time.time() - start_time
            
            if response.status_code == 401:
                self.log_test("unauthorized_access", "PASS", "正确拒绝未授权访问", duration)
            else:
                self.log_test("unauthorized_access", "FAIL", f"未预期的响应: {response.status_code}", duration)
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("unauthorized_access", "FAIL", str(e), duration)
    
    def test_token_validation(self):
        """测试token验证"""
        start_time = time.time()
        try:
            if not self.access_token:
                self.log_test("token_validation", "SKIP", "没有可用的access token")
                return
            
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(f"{self.services['backend']}/api/v1/users/me", headers=headers)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("token_validation", "PASS", f"用户: {data.get('username', 'N/A')}", duration)
            else:
                self.log_test("token_validation", "FAIL", f"HTTP {response.status_code}", duration)
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("token_validation", "FAIL", str(e), duration)
    
    def test_input_validation(self):
        """测试输入验证"""
        start_time = time.time()
        try:
            # 测试SQL注入防护
            malicious_data = {
                "username": "'; DROP TABLE users; --",
                "password": "password"
            }
            response = requests.post(
                f"{self.services['backend']}/api/v1/users/login",
                json=malicious_data
            )
            duration = time.time() - start_time
            
            if response.status_code in [400, 401, 422]:  # 应该被拒绝
                self.log_test("input_validation", "PASS", "SQL注入攻击被阻止", duration)
            else:
                self.log_test("input_validation", "FAIL", f"可能存在SQL注入漏洞: {response.status_code}", duration)
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("input_validation", "FAIL", str(e), duration)
    
    async def test_websocket_connection(self):
        """测试WebSocket连接"""
        print("\n🔄 5. WebSocket连接测试")
        print("-" * 50)
        
        start_time = time.time()
        try:
            # 尝试连接WebSocket
            uri = "ws://localhost:8000/ws/test"
            async with websockets.connect(uri, timeout=5) as websocket:
                # 发送测试消息
                test_message = {"type": "ping", "data": "integration_test"}
                await websocket.send(json.dumps(test_message))
                
                # 等待响应
                response = await websocket.recv()
                data = json.loads(response)
                
                duration = time.time() - start_time
                self.log_test("websocket_connection", "PASS", f"消息类型: {data.get('type', 'unknown')}", duration)
                
        except websockets.exceptions.ConnectionClosed:
            duration = time.time() - start_time
            self.log_test("websocket_connection", "FAIL", "连接被关闭", duration)
        except asyncio.TimeoutError:
            duration = time.time() - start_time
            self.log_test("websocket_connection", "FAIL", "连接超时", duration)
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("websocket_connection", "FAIL", str(e), duration)
    
    def test_database_connectivity(self):
        """测试数据库连接"""
        print("\n🗄️ 6. 数据库连接测试")
        print("-" * 50)
        
        # 通过API测试数据库连接
        start_time = time.time()
        try:
            response = requests.get(f"{self.services['backend']}/api/v1/system/health")
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                db_status = data.get("database", {})
                if db_status.get("status") == "healthy":
                    self.log_test("database_connectivity", "PASS", "数据库连接正常", duration)
                else:
                    self.log_test("database_connectivity", "FAIL", "数据库状态异常", duration)
            else:
                self.log_test("database_connectivity", "FAIL", f"HTTP {response.status_code}", duration)
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("database_connectivity", "FAIL", str(e), duration)
    
    def test_performance_metrics(self):
        """测试性能指标"""
        print("\n📊 7. 性能指标测试")
        print("-" * 50)
        
        # 测试API响应时间
        self.test_api_response_time()
        
        # 测试并发请求处理
        self.test_concurrent_requests()
    
    def test_api_response_time(self):
        """测试API响应时间"""
        endpoints = [
            "/health",
            "/api/v1/system/status"
        ]
        
        for endpoint in endpoints:
            times = []
            for i in range(5):  # 测试5次取平均值
                start_time = time.time()
                try:
                    response = requests.get(f"{self.services['backend']}{endpoint}")
                    if response.status_code == 200:
                        times.append(time.time() - start_time)
                except:
                    pass
            
            if times:
                avg_time = sum(times) / len(times)
                if avg_time < 0.5:  # 500ms以内认为正常
                    self.log_test(f"response_time_{endpoint.split('/')[-1]}", "PASS", f"平均响应时间: {avg_time:.3f}s", avg_time)
                else:
                    self.log_test(f"response_time_{endpoint.split('/')[-1]}", "FAIL", f"响应时间过长: {avg_time:.3f}s", avg_time)
            else:
                self.log_test(f"response_time_{endpoint.split('/')[-1]}", "FAIL", "无法获取响应时间", 0)
    
    def test_concurrent_requests(self):
        """测试并发请求处理"""
        start_time = time.time()
        try:
            import threading
            import queue
            
            results = queue.Queue()
            threads = []
            
            def make_request():
                try:
                    response = requests.get(f"{self.services['backend']}/health", timeout=10)
                    results.put(response.status_code == 200)
                except:
                    results.put(False)
            
            # 创建10个并发请求
            for i in range(10):
                thread = threading.Thread(target=make_request)
                threads.append(thread)
                thread.start()
            
            # 等待所有线程完成
            for thread in threads:
                thread.join()
            
            # 统计成功率
            success_count = 0
            while not results.empty():
                if results.get():
                    success_count += 1
            
            duration = time.time() - start_time
            success_rate = success_count / 10
            
            if success_rate >= 0.8:  # 80%以上成功率
                self.log_test("concurrent_requests", "PASS", f"成功率: {success_rate:.0%}", duration)
            else:
                self.log_test("concurrent_requests", "FAIL", f"成功率过低: {success_rate:.0%}", duration)
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("concurrent_requests", "FAIL", str(e), duration)
    
    def generate_test_report(self):
        """生成测试报告"""
        print("\n📋 测试报告")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        skipped_tests = len([r for r in self.test_results if r["status"] == "SKIP"])
        
        print(f"📊 总测试数: {total_tests}")
        print(f"✅ 通过: {passed_tests}")
        print(f"❌ 失败: {failed_tests}")
        print(f"⏭️ 跳过: {skipped_tests}")
        print(f"📈 成功率: {passed_tests/total_tests*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ 失败的测试:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"   • {result['test_name']}: {result['details']}")
        
        # 保存详细报告到文件
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "skipped": skipped_tests,
                "success_rate": passed_tests/total_tests*100
            },
            "details": self.test_results
        }
        
        with open("integration_test_report.json", "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 详细报告已保存到: integration_test_report.json")
        
        return passed_tests/total_tests >= 0.7  # 70%以上通过率认为系统基本健康
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🧪 智能思维项目 - 综合集成测试")
        print("=" * 60)
        print(f"⏰ 测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 按顺序执行测试
        self.test_service_health()
        self.test_api_endpoints()
        self.test_frontend_components()
        self.test_security_features()
        await self.test_websocket_connection()
        self.test_database_connectivity()
        self.test_performance_metrics()
        
        # 生成测试报告
        success = self.generate_test_report()
        
        print(f"\n⏰ 测试结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if success:
            print("🎉 集成测试总体通过！系统运行正常。")
        else:
            print("⚠️ 集成测试发现问题，需要修复后重新测试。")
        
        return success

async def main():
    """主函数"""
    tester = IntegrationTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 