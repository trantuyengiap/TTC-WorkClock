import { Button, Card, Form, Input, Typography, message } from 'antd';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';

export default function LoginPage() {
  const navigate = useNavigate();

  const onFinish = async (values: { username: string; password: string }) => {
    try {
      const response = await api.post('/auth/login', values);
      localStorage.setItem('access_token', response.data.access_token);
      message.success('Đăng nhập thành công');
      navigate('/');
    } catch {
      message.error('Sai tài khoản hoặc mật khẩu');
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'grid', placeItems: 'center', background: '#f5f5f5' }}>
      <Card style={{ width: 380 }}>
        <Typography.Title level={3}>Đăng nhập TTC WorkClock</Typography.Title>
        <Typography.Paragraph type="secondary">
          Tài khoản mặc định sau khi seed: admin / Admin@123
        </Typography.Paragraph>
        <Form layout="vertical" onFinish={onFinish}>
          <Form.Item label="Tên đăng nhập" name="username" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="Mật khẩu" name="password" rules={[{ required: true }]}>
            <Input.Password />
          </Form.Item>
          <Button type="primary" htmlType="submit" block>Đăng nhập</Button>
        </Form>
      </Card>
    </div>
  );
}
