import { Tag } from 'antd';

export function StatusTag({ value }: { value: string }) {
  const colorMap: Record<string, string> = {
    success: 'green',
    configured: 'blue',
    active: 'green',
    failed: 'red',
    online: 'green',
    green: 'green',
    yellow: 'gold',
    red: 'red',
  };

  return <Tag color={colorMap[value] ?? 'default'}>{value}</Tag>;
}
