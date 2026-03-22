import { Card, Table, Typography } from 'antd';
import { useEffect, useState } from 'react';
import api from '../api/client';
import type { AttendanceEvent } from '../types';

export default function AttendancePage() {
  const [events, setEvents] = useState<AttendanceEvent[]>([]);

  useEffect(() => {
    api.get('/attendance/events?minutes=30&size=100').then((response: { data: AttendanceEvent[] }) => setEvents(response.data));
  }, []);

  return (
    <Card title="Realtime attendance events">
      <Typography.Paragraph>
        Dữ liệu lấy trực tiếp từ Elasticsearch `hikvision-*`, vẫn tương thích các field `@timestamp`, `hikvision.dateTime`, `hikvision.AccessControllerEvent.*`.
      </Typography.Paragraph>
      <Table
        rowKey={(record: AttendanceEvent) => `${record.timestamp}-${record.user_id}-${record.device_id}`}
        scroll={{ x: 1000 }}
        dataSource={events}
        columns={[
          { title: 'Thời gian', dataIndex: 'event_time' },
          { title: 'Mã NV', dataIndex: 'user_id' },
          { title: 'Họ tên', dataIndex: 'user_name' },
          { title: 'Thiết bị', dataIndex: 'device_name' },
          { title: 'Outcome', dataIndex: 'outcome' },
          { title: 'JSON thô', dataIndex: 'raw', render: (value: Record<string, unknown>) => <pre style={{ whiteSpace: 'pre-wrap', margin: 0 }}>{JSON.stringify(value, null, 2)}</pre> },
        ]}
      />
    </Card>
  );
}
