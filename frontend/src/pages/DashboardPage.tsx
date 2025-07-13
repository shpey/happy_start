import React from 'react';
import {
  Box,
  Typography,
  Breadcrumbs,
  Link
} from '@mui/material';
import { NavigateNext, Dashboard } from '@mui/icons-material';
import AnalyticsDashboard from '../components/Analytics/AnalyticsDashboard';
import { useAuth } from '../contexts/AuthContext';

const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  
  return (
    <Box>
      <Breadcrumbs separator={<NavigateNext fontSize="small" />} sx={{ mb: 1 }}>
        <Link underline="hover" color="inherit" href="/">
          首页
        </Link>
        <Typography color="text.primary">数据仪表板</Typography>
      </Breadcrumbs>

      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Dashboard /> 数据仪表板
      </Typography>

      <AnalyticsDashboard 
        userId={user?.id}
        isAdmin={user?.is_admin || false}
      />
    </Box>
  );
};

export default DashboardPage; 