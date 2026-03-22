import { Card, Descriptions } from 'antd';
import { useEffect, useState } from 'react';
import api from '../api/client';

export default function SettingsPage() {
  const [data, setData] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    api.get('/settings/system').then((response: { data: Record<string, unknown> }) => setData(response.data));
  }, []);

  return (
    <Card title="Cấu hình hệ thống">
      <Descriptions bordered column={1} items={[
        { key: 'db', label: 'Database', children: String(data?.database ?? '-') },
        { key: 'es', label: 'Elasticsearch index', children: String(data?.elasticsearch_index_pattern ?? '-') },
        { key: 'tz', label: 'Timezone', children: String(data?.timezone ?? '-') },
        { key: 'map', label: 'Field mapping', children: <pre>{JSON.stringify(data?.field_mapping ?? {}, null, 2)}</pre> },
      ]} />
    </Card>
  );
}
