import { DashboardOutlined, NotificationOutlined, ScheduleOutlined, SettingOutlined, TeamOutlined, UserOutlined } from '@ant-design/icons';
import { Layout, Menu, Typography } from 'antd';
import { Link, Outlet, useLocation } from 'react-router-dom';

const { Header, Content, Sider } = Layout;

const items = [
  { key: '/', icon: <DashboardOutlined />, label: <Link to="/">Dashboard</Link> },
  { key: '/users', icon: <UserOutlined />, label: <Link to="/users">Nhân sự</Link> },
  { key: '/shifts', icon: <ScheduleOutlined />, label: <Link to="/shifts">Ca làm việc</Link> },
  { key: '/rules', icon: <TeamOutlined />, label: <Link to="/rules">Rule nhắc</Link> },
  { key: '/attendance', icon: <TeamOutlined />, label: <Link to="/attendance">Realtime events</Link> },
  { key: '/notifications', icon: <NotificationOutlined />, label: <Link to="/notifications">Notification logs</Link> },
  { key: '/settings', icon: <SettingOutlined />, label: <Link to="/settings">Cấu hình</Link> },
  { key: '/guide', icon: <SettingOutlined />, label: <Link to="/guide">Hướng dẫn</Link> },
];

export default function AppLayout() {
  const location = useLocation();

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider breakpoint="lg" collapsedWidth="0">
        <div style={{ color: '#fff', padding: 16, fontWeight: 700 }}>TTC WorkClock</div>
        <Menu theme="dark" mode="inline" selectedKeys={[location.pathname]} items={items} />
      </Sider>
      <Layout>
        <Header style={{ background: '#fff', padding: '0 24px' }}>
          <Typography.Title level={4} style={{ margin: '16px 0' }}>
            Quản trị chấm công tập trung
          </Typography.Title>
        </Header>
        <Content style={{ margin: 24 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}
