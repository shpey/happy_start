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
  CardContent,
  Grid,
  Stack,
  Fade,
  Slide,
  LinearProgress,
  Chip
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Email,
  Lock,
  Person,
  AccountCircle,
  PersonAdd,
  Psychology,
  ArrowBack,
  Google as GoogleIcon,
  GitHub as GitHubIcon,
  Check,
  Close
} from '@mui/icons-material';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { post } from '../services/api';

interface RegisterFormData {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  full_name: string;
}

interface PasswordStrength {
  score: number;
  label: string;
  color: 'error' | 'warning' | 'info' | 'success';
  checks: {
    length: boolean;
    uppercase: boolean;
    lowercase: boolean;
    number: boolean;
    special: boolean;
  };
}

const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [passwordStrength, setPasswordStrength] = useState<PasswordStrength>({
    score: 0,
    label: '非常弱',
    color: 'error',
    checks: {
      length: false,
      uppercase: false,
      lowercase: false,
      number: false,
      special: false
    }
  });

  const validationSchema = Yup.object({
    username: Yup.string()
      .min(3, '用户名至少3个字符')
      .max(50, '用户名最多50个字符')
      .matches(/^[a-zA-Z0-9_]+$/, '用户名只能包含字母、数字和下划线')
      .matches(/^[a-zA-Z]/, '用户名必须以字母开头')
      .required('请输入用户名'),
    email: Yup.string()
      .email('请输入有效的邮箱地址')
      .required('请输入邮箱'),
    password: Yup.string()
      .min(8, '密码至少8个字符')
      .matches(/[A-Z]/, '密码必须包含至少一个大写字母')
      .matches(/[a-z]/, '密码必须包含至少一个小写字母')
      .matches(/[0-9]/, '密码必须包含至少一个数字')
      .matches(/[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/, '密码必须包含至少一个特殊字符')
      .required('请输入密码'),
    confirmPassword: Yup.string()
      .oneOf([Yup.ref('password')], '两次输入的密码不一致')
      .required('请确认密码'),
    full_name: Yup.string()
      .min(2, '姓名至少2个字符')
      .max(100, '姓名最多100个字符')
      .required('请输入姓名'),
  });

  const calculatePasswordStrength = (password: string): PasswordStrength => {
    const checks = {
      length: password.length >= 8,
      uppercase: /[A-Z]/.test(password),
      lowercase: /[a-z]/.test(password),
      number: /[0-9]/.test(password),
      special: /[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(password)
    };

    const score = Object.values(checks).filter(Boolean).length;
    
    let label = '非常弱';
    let color: 'error' | 'warning' | 'info' | 'success' = 'error';

    if (score >= 4) {
      label = '强';
      color = 'success';
    } else if (score >= 3) {
      label = '中等';
      color = 'info';
    } else if (score >= 2) {
      label = '弱';
      color = 'warning';
    }

    return { score, label, color, checks };
  };

  const formik = useFormik<RegisterFormData>({
    initialValues: {
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      full_name: '',
    },
    validationSchema,
    onSubmit: async (values) => {
      setIsLoading(true);
      setError(null);
      setSuccess(null);

      try {
        const { confirmPassword, ...registerData } = values;
        const response = await post('/users/register', registerData);
        
        if (response.success !== false) {
          // 存储令牌和用户信息
          localStorage.setItem('access_token', response.access_token);
          localStorage.setItem('refresh_token', response.refresh_token);
          localStorage.setItem('user_info', JSON.stringify(response.user));

          setSuccess('注册成功！欢迎加入智能思维分析平台！');
          
          // 延时跳转
          setTimeout(() => {
            navigate('/dashboard');
          }, 2000);
        } else {
          setError(response.message || '注册失败');
        }
      } catch (err: any) {
        setError(err.response?.data?.detail || '注册失败，请检查输入信息');
      } finally {
        setIsLoading(false);
      }
    },
  });

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const password = e.target.value;
    formik.handleChange(e);
    setPasswordStrength(calculatePasswordStrength(password));
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const toggleConfirmPasswordVisibility = () => {
    setShowConfirmPassword(!showConfirmPassword);
  };

  const renderPasswordCheck = (label: string, passed: boolean) => (
    <Box display="flex" alignItems="center" gap={1}>
      {passed ? (
        <Check sx={{ color: 'success.main', fontSize: 16 }} />
      ) : (
        <Close sx={{ color: 'error.main', fontSize: 16 }} />
      )}
      <Typography
        variant="body2"
        sx={{ color: passed ? 'success.main' : 'text.secondary' }}
      >
        {label}
      </Typography>
    </Box>
  );

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
      <Container maxWidth="md">
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

            {/* 注册卡片 */}
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
                    加入我们
                  </Typography>
                  <Typography variant="body1" sx={{ opacity: 0.9 }}>
                    创建您的智能思维分析账户，开启AI思维之旅
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

                      {/* 用户名和姓名 */}
                      <Grid container spacing={2}>
                        <Grid item xs={12} md={6}>
                          <TextField
                            fullWidth
                            name="username"
                            label="用户名"
                            value={formik.values.username}
                            onChange={formik.handleChange}
                            onBlur={formik.handleBlur}
                            error={formik.touched.username && Boolean(formik.errors.username)}
                            helperText={formik.touched.username && formik.errors.username}
                            InputProps={{
                              startAdornment: (
                                <InputAdornment position="start">
                                  <Person color="action" />
                                </InputAdornment>
                              ),
                            }}
                            sx={{
                              '& .MuiOutlinedInput-root': {
                                borderRadius: 2,
                              },
                            }}
                          />
                        </Grid>
                        <Grid item xs={12} md={6}>
                          <TextField
                            fullWidth
                            name="full_name"
                            label="姓名"
                            value={formik.values.full_name}
                            onChange={formik.handleChange}
                            onBlur={formik.handleBlur}
                            error={formik.touched.full_name && Boolean(formik.errors.full_name)}
                            helperText={formik.touched.full_name && formik.errors.full_name}
                            InputProps={{
                              startAdornment: (
                                <InputAdornment position="start">
                                  <AccountCircle color="action" />
                                </InputAdornment>
                              ),
                            }}
                            sx={{
                              '& .MuiOutlinedInput-root': {
                                borderRadius: 2,
                              },
                            }}
                          />
                        </Grid>
                      </Grid>

                      {/* 邮箱输入 */}
                      <TextField
                        fullWidth
                        name="email"
                        label="邮箱"
                        type="email"
                        value={formik.values.email}
                        onChange={formik.handleChange}
                        onBlur={formik.handleBlur}
                        error={formik.touched.email && Boolean(formik.errors.email)}
                        helperText={formik.touched.email && formik.errors.email}
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
                        onChange={handlePasswordChange}
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

                      {/* 密码强度指示器 */}
                      {formik.values.password && (
                        <Box>
                          <Box display="flex" alignItems="center" gap={2} mb={1}>
                            <Typography variant="body2" color="text.secondary">
                              密码强度:
                            </Typography>
                            <Chip
                              label={passwordStrength.label}
                              color={passwordStrength.color}
                              size="small"
                            />
                          </Box>
                          <LinearProgress
                            variant="determinate"
                            value={(passwordStrength.score / 5) * 100}
                            color={passwordStrength.color}
                            sx={{ height: 6, borderRadius: 3 }}
                          />
                          <Box mt={1}>
                            <Grid container spacing={1}>
                              <Grid item xs={12} sm={6}>
                                {renderPasswordCheck('至少8个字符', passwordStrength.checks.length)}
                                {renderPasswordCheck('包含大写字母', passwordStrength.checks.uppercase)}
                                {renderPasswordCheck('包含小写字母', passwordStrength.checks.lowercase)}
                              </Grid>
                              <Grid item xs={12} sm={6}>
                                {renderPasswordCheck('包含数字', passwordStrength.checks.number)}
                                {renderPasswordCheck('包含特殊字符', passwordStrength.checks.special)}
                              </Grid>
                            </Grid>
                          </Box>
                        </Box>
                      )}

                      {/* 确认密码输入 */}
                      <TextField
                        fullWidth
                        name="confirmPassword"
                        label="确认密码"
                        type={showConfirmPassword ? 'text' : 'password'}
                        value={formik.values.confirmPassword}
                        onChange={formik.handleChange}
                        onBlur={formik.handleBlur}
                        error={formik.touched.confirmPassword && Boolean(formik.errors.confirmPassword)}
                        helperText={formik.touched.confirmPassword && formik.errors.confirmPassword}
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <Lock color="action" />
                            </InputAdornment>
                          ),
                          endAdornment: (
                            <InputAdornment position="end">
                              <IconButton
                                onClick={toggleConfirmPasswordVisibility}
                                edge="end"
                              >
                                {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
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

                      {/* 注册按钮 */}
                      <Button
                        fullWidth
                        type="submit"
                        variant="contained"
                        size="large"
                        disabled={isLoading}
                        startIcon={isLoading ? <CircularProgress size={20} /> : <PersonAdd />}
                        sx={{
                          py: 1.5,
                          borderRadius: 2,
                          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                          '&:hover': {
                            background: 'linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%)',
                          },
                        }}
                      >
                        {isLoading ? '注册中...' : '创建账户'}
                      </Button>

                      {/* 分隔线 */}
                      <Divider sx={{ my: 2 }}>
                        <Typography variant="body2" color="text.secondary">
                          或使用以下方式注册
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

                      {/* 登录链接 */}
                      <Box textAlign="center">
                        <Typography variant="body2" color="text.secondary">
                          已有账户？{' '}
                          <Link
                            to="/login"
                            style={{
                              color: '#667eea',
                              textDecoration: 'none',
                              fontWeight: 'bold'
                            }}
                          >
                            立即登录
                          </Link>
                        </Typography>
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
                    注册即表示您同意我们的
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

export default RegisterPage; 