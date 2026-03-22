import { Card, List, Typography } from 'antd';

export default function GuidePage() {
  return (
    <Card title="Hướng dẫn sử dụng nhanh">
      <Typography.Paragraph>
        Website quản trị cho phép cấu hình tập trung user, ca làm việc, rule nhắc, kênh gửi và xem realtime attendance từ Elasticsearch.
      </Typography.Paragraph>
      <List
        bordered
        dataSource={[
          '1. Đăng nhập bằng tài khoản admin seed mặc định và đổi mật khẩu.',
          '2. Tạo phòng ban, ca làm việc, sau đó import nhân sự từ file cũ hoặc CSV.',
          '3. Khai báo kênh nhận thông báo cho từng nhân sự.',
          '4. Tạo rule nhắc vào ca/ra ca và chọn template phù hợp.',
          '5. Kiểm tra trang Realtime events để xác nhận Elasticsearch đang trả dữ liệu đúng field mapping.',
          '6. Dùng popup Test gửi thông báo để xác nhận provider Viber/Email hoạt động.',
        ]}
        renderItem={(item: string) => <List.Item>{item}</List.Item>}
      />
    </Card>
  );
}
