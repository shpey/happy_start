import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  Breadcrumbs,
  Link
} from '@mui/material';
import { NavigateNext, Dashboard, TrendingUp, People, Psychology } from '@mui/icons-material';

const DashboardPage: React.FC = () => {
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

      <Grid container spacing={3}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h4" color="primary">2,847</Typography>
              <Typography variant="body2">总用户数</Typography>
              <Chip label="+12%" size="small" color="success" sx={{ mt: 1 }} />
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h4" color="secondary">15,693</Typography>
              <Typography variant="body2">思维分析次数</Typography>
              <Chip label="+25%" size="small" color="success" sx={{ mt: 1 }} />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h4" color="success.main">8,742</Typography>
              <Typography variant="body2">知识节点</Typography>
              <Chip label="+18%" size="small" color="success" sx={{ mt: 1 }} />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h4" color="warning.main">1,234</Typography>
              <Typography variant="body2">协作会话</Typography>
              <Chip label="+31%" size="small" color="success" sx={{ mt: 1 }} />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>系统性能监控</Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <Typography variant="body2" gutterBottom>CPU 使用率</Typography>
                <LinearProgress variant="determinate" value={75} sx={{ height: 8, borderRadius: 1 }} />
                <Typography variant="caption">75%</Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="body2" gutterBottom>内存使用率</Typography>
                <LinearProgress variant="determinate" value={62} color="success" sx={{ height: 8, borderRadius: 1 }} />
                <Typography variant="caption">62%</Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="body2" gutterBottom>网络延迟</Typography>
                <LinearProgress variant="determinate" value={95} color="info" sx={{ height: 8, borderRadius: 1 }} />
                <Typography variant="caption">18ms</Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardPage; 