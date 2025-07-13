import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ThinkingAnalysisPage from './pages/ThinkingAnalysisPage';
import KnowledgeGraphPage from './pages/KnowledgeGraphPage';
import CollaborationPage from './pages/CollaborationPage';
import ThreeDSpacePage from './pages/ThreeDSpacePage';
import DashboardPage from './pages/DashboardPage';
import AdvancedVisualizationPage from './pages/AdvancedVisualizationPage';
import QuickAccessPanel from './components/common/QuickAccessPanel';
import UserGuide from './components/common/UserGuide';
import NotificationDisplay from './components/common/NotificationDisplay';

function App() {
  return (
    <Routes>
      {/* 不需要Layout的页面 */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      
      {/* 需要Layout的页面 */}
      <Route path="/*" element={
        <Layout>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/thinking" element={<ThinkingAnalysisPage />} />
            <Route path="/knowledge" element={<KnowledgeGraphPage />} />
            <Route path="/collaboration" element={<CollaborationPage />} />
            <Route path="/3d-space" element={<ThreeDSpacePage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/visualization" element={<AdvancedVisualizationPage />} />
            <Route path="/models" element={<DashboardPage />} />
            <Route path="/sync" element={<DashboardPage />} />
            <Route path="/settings" element={<DashboardPage />} />
          </Routes>
          
          {/* 快速访问面板 */}
          <QuickAccessPanel />
          
          {/* 通知显示系统 */}
          <NotificationDisplay />
          
          {/* 用户引导 */}
          <UserGuide />
        </Layout>
      } />
    </Routes>
  );
}

export default App; 