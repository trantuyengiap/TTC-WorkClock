import { Button, Card, Space, Table } from 'antd';
import { useEffect, useState } from 'react';
import api from '../api/client';
import { StatusTag } from '../components/StatusTag';
import type { ReminderRule } from '../types';

export default function RulesPage() {
  const [rules, setRules] = useState<ReminderRule[]>([]);

  useEffect(() => {
    api.get('/reminder-rules').then((response: { data: ReminderRule[] }) => setRules(response.data));
  }, []);

  return (
    <Card title="Rule nhắc chấm công" extra={<Space><Button type="primary">Tạo rule</Button></Space>}>
      <Table
        rowKey="id"
        dataSource={rules}
        columns={[
          { title: 'Tên rule', dataIndex: 'name' },
          { title: 'Loại', dataIndex: 'rule_type' },
          { title: 'Kênh', dataIndex: 'channels', render: (value?: string[]) => value?.join(', ') || '-' },
          { title: 'Kích hoạt', dataIndex: 'is_active', render: (value: boolean) => <StatusTag value={value ? 'active' : 'inactive'} /> },
        ]}
      />
    </Card>
  );
}
