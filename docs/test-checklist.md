# Checklist test

## Functional
- [ ] Đăng nhập bằng tài khoản admin seed.
- [ ] CRUD phòng ban.
- [ ] CRUD ca làm việc.
- [ ] CRUD nhân sự.
- [ ] CRUD rule nhắc.
- [ ] Trang dashboard hiển thị thống kê.
- [ ] Trang realtime attendance đọc được dữ liệu từ Elasticsearch.
- [ ] Test gửi Email thành công.
- [ ] Test gửi Viber thành công qua API cũ.
- [ ] Notification logs ghi đúng trạng thái.

## Compatibility
- [ ] Query `hikvision-*` không cần sửa Logstash.
- [ ] Field `employeeNoString` map đúng sang `attendance_code`.
- [ ] Fallback query hoạt động nếu aggregation Elasticsearch lỗi.

## Security
- [ ] JWT auth hoạt động.
- [ ] RBAC chặn user không đủ quyền.
- [ ] Secret không commit trong repo.
