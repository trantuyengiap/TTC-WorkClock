import { Card, Col, Row, Statistic, Table, Typography } from 'antd';
import { useEffect, useState } from 'react';
import api from '../api/client';
import { StatusTag } from '../components/StatusTag';
import type { DashboardStats } from '../types';

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);

  useEffect(() => {
    api.get('/dashboard/stats').then((response: { data: DashboardStats }) => setStats(response.data));
  }, []);

  if (!stats) return <div>Đang tải...</div>;

  return (
    <Row gutter={[16, 16]}>
      <Col span={6}><Card><Statistic title="Tổng nhân viên" value={stats.total_employees} /></Card></Col>
      <Col span={6}><Card><Statistic title="Đã chấm hôm nay" value={stats.checked_in_today} /></Card></Col>
      <Col span={6}><Card><Statistic title="Chưa chấm hôm nay" value={stats.not_checked_in_today} /></Card></Col>
      <Col span={6}><Card><Statistic title="Cảnh báo đã gửi" value={stats.notifications_sent_today} /></Card></Col>
      <Col span={12}>
        <Card title="Tình trạng hệ thống">
          <Typography.Paragraph>Elasticsearch: <StatusTag value={stats.elasticsearch_status} /></Typography.Paragraph>
          <Typography.Paragraph>Worker: <StatusTag value={stats.worker_status} /></Typography.Paragraph>
        </Card>
      </Col>
      <Col span={12}>
        <Card title="Kênh thông báo">
          <Table
            rowKey="channel"
            pagination={false}
            dataSource={Object.entries(stats.channels_status).map(([channel, status]) => ({ channel, status }))}
            columns={[
              { title: 'Kênh', dataIndex: 'channel' },
              { title: 'Trạng thái', dataIndex: 'status', render: (value: string) => <StatusTag value={value} /> },
            ]}
          />
        </Card>
      </Col>
    </Row>
  );
}
