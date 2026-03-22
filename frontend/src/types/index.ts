export interface DashboardStats {
  total_employees: number;
  checked_in_today: number;
  not_checked_in_today: number;
  notifications_sent_today: number;
  elasticsearch_status: string;
  worker_status: string;
  channels_status: Record<string, string>;
}

export interface User {
  id: number;
  username: string;
  full_name: string;
  employee_code?: string;
  attendance_code?: string;
  email?: string;
  title?: string;
  status: string;
  role: string;
  department_id?: number;
  shift_id?: number;
  is_active: boolean;
}

export interface Shift {
  id: number;
  name: string;
  code?: string;
  start_time: string;
  end_time: string;
  grace_minutes: number;
  is_night_shift: boolean;
  is_special: boolean;
  notes?: string;
}

export interface ReminderRule {
  id: number;
  name: string;
  rule_type: string;
  description?: string;
  is_active: boolean;
  schedule_config: Record<string, unknown>;
  conditions?: Record<string, unknown>;
  channels?: string[];
}

export interface AttendanceEvent {
  timestamp?: string;
  event_time?: string;
  user_id?: string;
  user_name?: string;
  device_name?: string;
  device_id?: string;
  outcome?: string;
  raw: Record<string, unknown>;
}

export interface NotificationLog {
  id: number;
  channel: string;
  recipient: string;
  template_name?: string;
  message: string;
  status: string;
  error_message?: string;
  retry_count: number;
  created_at: string;
}
