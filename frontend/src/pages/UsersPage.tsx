import { Button, Card, Space, Table, Typography } from 'antd';
import { useEffect, useState } from 'react';
import api from '../api/client';
import { StatusTag } from '../components/StatusTag';
import type { User } from '../types';

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);

  useEffect(() => {
    api.get('/users').then((response: { data: User[] }) => setUsers(response.data));
  }, []);

  return (
    <Card title="Quản lý nhân sự" extra={<Space><Button type="primary">Thêm nhân sự</Button><Button>Import CSV/Excel</Button></Space>}>
      <Typography.Paragraph>
        Phase 1 cung cấp nền CRUD backend và màn hình danh sách. Có thể mở rộng form chi tiết, import/export và phân trang server-side.
      </Typography.Paragraph>
      <Table
        rowKey="id"
        dataSource={users}
        columns={[
          { title: 'Username', dataIndex: 'username' },
          { title: 'Họ tên', dataIndex: 'full_name' },
          { title: 'Mã NV', dataIndex: 'employee_code' },
          { title: 'Mã chấm công', dataIndex: 'attendance_code' },
          { title: 'Email', dataIndex: 'email' },
          { title: 'Vai trò', dataIndex: 'role' },
          { title: 'Trạng thái', dataIndex: 'status', render: (value: string) => <StatusTag value={value} /> },
        ]}
      />
    </Card>
  );
}
