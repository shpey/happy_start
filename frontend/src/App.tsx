import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import ThinkingAnalysisPage from './pages/ThinkingAnalysisPage';
import KnowledgeGraphPage from './pages/KnowledgeGraphPage';
import CollaborationPage from './pages/CollaborationPage';
import ThreeDSpacePage from './pages/ThreeDSpacePage';
import DashboardPage from './pages/DashboardPage';
import QuickAccessPanel from './components/common/QuickAccessPanel';
import UserGuide from './components/common/UserGuide';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/thinking" element={<ThinkingAnalysisPage />} />
        <Route path="/knowledge" element={<KnowledgeGraphPage />} />
        <Route path="/collaboration" element={<CollaborationPage />} />
        <Route path="/3d-space" element={<ThreeDSpacePage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/models" element={<DashboardPage />} />
        <Route path="/sync" element={<DashboardPage />} />
        <Route path="/settings" element={<DashboardPage />} />
      </Routes>
      
      {/* 快速访问面板 */}
      <QuickAccessPanel />
      
      {/* 用户引导 */}
      <UserGuide />
    </Layout>
  );
}

export default App; 