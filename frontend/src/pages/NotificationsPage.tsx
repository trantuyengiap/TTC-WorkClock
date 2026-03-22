import { Button, Card, Form, Input, Modal, Select, Table } from 'antd';
import { useEffect, useState } from 'react';
import api from '../api/client';
import { StatusTag } from '../components/StatusTag';
import type { NotificationLog } from '../types';

export default function NotificationsPage() {
  const [logs, setLogs] = useState<NotificationLog[]>([]);
  const [open, setOpen] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    api.get('/notifications/logs').then((response: { data: NotificationLog[] }) => setLogs(response.data));
  }, []);

  const submitTest = async () => {
    await api.post('/notifications/test', form.getFieldsValue());
    setOpen(false);
  };

  return (
    <Card title="Lịch sử gửi thông báo" extra={<Button type="primary" onClick={() => setOpen(true)}>Test gửi thử</Button>}>
      <Table
        rowKey="id"
        dataSource={logs}
        columns={[
          { title: 'Kênh', dataIndex: 'channel' },
          { title: 'Người nhận', dataIndex: 'recipient' },
          { title: 'Template', dataIndex: 'template_name' },
          { title: 'Nội dung', dataIndex: 'message' },
          { title: 'Trạng thái', dataIndex: 'status', render: (value: string) => <StatusTag value={value} /> },
          { title: 'Retry', dataIndex: 'retry_count' },
          { title: 'Thời gian', dataIndex: 'created_at' },
        ]}
      />
      <Modal title="Test gửi thông báo" open={open} onOk={submitTest} onCancel={() => setOpen(false)}>
        <Form layout="vertical" form={form} initialValues={{ channel: 'email' }}>
          <Form.Item label="Kênh" name="channel"><Select options={[{ value: 'email', label: 'Email' }, { value: 'viber', label: 'Viber' }]} /></Form.Item>
          <Form.Item label="Người nhận" name="recipient"><Input /></Form.Item>
          <Form.Item label="Nội dung" name="message"><Input.TextArea rows={4} /></Form.Item>
        </Form>
      </Modal>
    </Card>
  );
}
