import { Button, Card, Space, Table } from 'antd';
import { useEffect, useState } from 'react';
import api from '../api/client';
import type { Shift } from '../types';

export default function ShiftsPage() {
  const [shifts, setShifts] = useState<Shift[]>([]);

  useEffect(() => {
    api.get('/shifts').then((response: { data: Shift[] }) => setShifts(response.data));
  }, []);

  return (
    <Card title="Quản lý ca làm việc" extra={<Space><Button type="primary">Thêm ca</Button></Space>}>
      <Table
        rowKey="id"
        dataSource={shifts}
        columns={[
          { title: 'Tên ca', dataIndex: 'name' },
          { title: 'Mã', dataIndex: 'code' },
          { title: 'Giờ vào', dataIndex: 'start_time' },
          { title: 'Giờ ra', dataIndex: 'end_time' },
          { title: 'Grace', dataIndex: 'grace_minutes' },
          { title: 'Ca đêm', dataIndex: 'is_night_shift', render: (value: boolean) => (value ? 'Có' : 'Không') },
        ]}
      />
    </Card>
  );
}
