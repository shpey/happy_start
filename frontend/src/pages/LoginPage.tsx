import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Container,
  InputAdornment,
  IconButton,
  Divider,
  Card,
  CardContent,
  Grid,
  Stack,
  Fade,
  Slide
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Email,
  Lock,
  Login as LoginIcon,
  Psychology,
  ArrowBack,
  Google as GoogleIcon,
  GitHub as GitHubIcon
} from '@mui/icons-material';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { post } from '../services/api';

interface LoginFormData {
  username: string;
  password: string;
}

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const validationSchema = Yup.object({
    username: Yup.string()
      .min(3, '用户名至少3个字符')
      .max(50, '用户名最多50个字符')
      .required('请输入用户名或邮箱'),
    password: Yup.string()
      .min(8, '密码至少8个字符')
      .required('请输入密码'),
  });

  const formik = useFormik<LoginFormData>({
    initialValues: {
      username: '',
      password: '',
    },
    validationSchema,
    onSubmit: async (values) => {
      setIsLoading(true);
      setError(null);
      setSuccess(null);

      try {
        const response = await post('/users/login', values);
        
        if (response.success !== false) {
          // 存储令牌和用户信息
          localStorage.setItem('access_token', response.access_token);
          localStorage.setItem('refresh_token', response.refresh_token);
          localStorage.setItem('user_info', JSON.stringify(response.user));

          setSuccess('登录成功！正在跳转...');
          
          // 延时跳转以显示成功消息
          setTimeout(() => {
            navigate('/dashboard');
          }, 1500);
        } else {
          setError(response.message || '登录失败');
        }
      } catch (err: any) {
        setError(err.response?.data?.detail || '登录失败，请检查用户名和密码');
      } finally {
        setIsLoading(false);
      }
    },
  });

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        py: 3
      }}
    >
      <Container maxWidth="sm">
        <Fade in timeout={800}>
          <Box>
            {/* 返回按钮 */}
            <Button
              startIcon={<ArrowBack />}
              onClick={() => navigate('/')}
              sx={{
                mb: 2,
                color: 'white',
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.1)'
                }
              }}
            >
              返回首页
            </Button>

            {/* 登录卡片 */}
            <Slide in timeout={1000} direction="up">
              <Paper
                elevation={8}
                sx={{
                  borderRadius: 4,
                  overflow: 'hidden',
                  bgcolor: 'background.paper'
                }}
              >
                {/* 头部 */}
                <Box
                  sx={{
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    color: 'white',
                    p: 4,
                    textAlign: 'center'
                  }}
                >
                  <Psychology sx={{ fontSize: 48, mb: 2 }} />
                  <Typography variant="h4" fontWeight="bold" gutterBottom>
                    欢迎回来
                  </Typography>
                  <Typography variant="body1" sx={{ opacity: 0.9 }}>
                    登录您的智能思维分析账户
                  </Typography>
                </Box>

                {/* 表单区域 */}
                <CardContent sx={{ p: 4 }}>
                  <form onSubmit={formik.handleSubmit}>
                    <Stack spacing={3}>
                      {/* 错误提示 */}
                      {error && (
                        <Alert severity="error" sx={{ borderRadius: 2 }}>
                          {error}
                        </Alert>
                      )}

                      {/* 成功提示 */}
                      {success && (
                        <Alert severity="success" sx={{ borderRadius: 2 }}>
                          {success}
                        </Alert>
                      )}

                      {/* 用户名输入 */}
                      <TextField
                        fullWidth
                        name="username"
                        label="用户名或邮箱"
                        value={formik.values.username}
                        onChange={formik.handleChange}
                        onBlur={formik.handleBlur}
                        error={formik.touched.username && Boolean(formik.errors.username)}
                        helperText={formik.touched.username && formik.errors.username}
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <Email color="action" />
                            </InputAdornment>
                          ),
                        }}
                        sx={{
                          '& .MuiOutlinedInput-root': {
                            borderRadius: 2,
                          },
                        }}
                      />

                      {/* 密码输入 */}
                      <TextField
                        fullWidth
                        name="password"
                        label="密码"
                        type={showPassword ? 'text' : 'password'}
                        value={formik.values.password}
                        onChange={formik.handleChange}
                        onBlur={formik.handleBlur}
                        error={formik.touched.password && Boolean(formik.errors.password)}
                        helperText={formik.touched.password && formik.errors.password}
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <Lock color="action" />
                            </InputAdornment>
                          ),
                          endAdornment: (
                            <InputAdornment position="end">
                              <IconButton
                                onClick={togglePasswordVisibility}
                                edge="end"
                              >
                                {showPassword ? <VisibilityOff /> : <Visibility />}
                              </IconButton>
                            </InputAdornment>
                          ),
                        }}
                        sx={{
                          '& .MuiOutlinedInput-root': {
                            borderRadius: 2,
                          },
                        }}
                      />

                      {/* 登录按钮 */}
                      <Button
                        fullWidth
                        type="submit"
                        variant="contained"
                        size="large"
                        disabled={isLoading}
                        startIcon={isLoading ? <CircularProgress size={20} /> : <LoginIcon />}
                        sx={{
                          py: 1.5,
                          borderRadius: 2,
                          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                          '&:hover': {
                            background: 'linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%)',
                          },
                        }}
                      >
                        {isLoading ? '登录中...' : '登录'}
                      </Button>

                      {/* 分隔线 */}
                      <Divider sx={{ my: 2 }}>
                        <Typography variant="body2" color="text.secondary">
                          或
                        </Typography>
                      </Divider>

                      {/* 社交登录 */}
                      <Grid container spacing={2}>
                        <Grid item xs={6}>
                          <Button
                            fullWidth
                            variant="outlined"
                            startIcon={<GoogleIcon />}
                            sx={{
                              py: 1.5,
                              borderRadius: 2,
                              textTransform: 'none',
                            }}
                          >
                            Google
                          </Button>
                        </Grid>
                        <Grid item xs={6}>
                          <Button
                            fullWidth
                            variant="outlined"
                            startIcon={<GitHubIcon />}
                            sx={{
                              py: 1.5,
                              borderRadius: 2,
                              textTransform: 'none',
                            }}
                          >
                            GitHub
                          </Button>
                        </Grid>
                      </Grid>

                      {/* 注册链接 */}
                      <Box textAlign="center">
                        <Typography variant="body2" color="text.secondary">
                          还没有账户？{' '}
                          <Link
                            to="/register"
                            style={{
                              color: '#667eea',
                              textDecoration: 'none',
                              fontWeight: 'bold'
                            }}
                          >
                            立即注册
                          </Link>
                        </Typography>
                      </Box>

                      {/* 忘记密码 */}
                      <Box textAlign="center">
                        <Link
                          to="/forgot-password"
                          style={{
                            color: '#667eea',
                            textDecoration: 'none',
                            fontSize: '0.875rem'
                          }}
                        >
                          忘记密码？
                        </Link>
                      </Box>
                    </Stack>
                  </form>
                </CardContent>

                {/* 底部信息 */}
                <Box
                  sx={{
                    bgcolor: 'grey.50',
                    p: 3,
                    textAlign: 'center',
                    borderTop: '1px solid',
                    borderColor: 'divider'
                  }}
                >
                  <Typography variant="body2" color="text.secondary">
                    登录即表示您同意我们的
                    <Link to="/terms" style={{ color: '#667eea', textDecoration: 'none' }}>
                      服务条款
                    </Link>
                    和
                    <Link to="/privacy" style={{ color: '#667eea', textDecoration: 'none' }}>
                      隐私政策
                    </Link>
                  </Typography>
                </Box>
              </Paper>
            </Slide>
          </Box>
        </Fade>
      </Container>
    </Box>
  );
};

export default LoginPage; 