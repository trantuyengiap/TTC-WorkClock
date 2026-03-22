import React from 'react';
import { Navigate, createBrowserRouter } from 'react-router-dom';
import AppLayout from '../layouts/AppLayout';
import AttendancePage from '../pages/AttendancePage';
import DashboardPage from '../pages/DashboardPage';
import GuidePage from '../pages/GuidePage';
import LoginPage from '../pages/LoginPage';
import NotificationsPage from '../pages/NotificationsPage';
import RulesPage from '../pages/RulesPage';
import SettingsPage from '../pages/SettingsPage';
import ShiftsPage from '../pages/ShiftsPage';
import UsersPage from '../pages/UsersPage';

function Protected({ children }: { children: React.ReactElement }) {
  const token = localStorage.getItem('access_token');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

export const appRouter = createBrowserRouter([
  { path: '/login', element: <LoginPage /> },
  {
    path: '/',
    element: (
      <Protected>
        <AppLayout />
      </Protected>
    ),
    children: [
      { index: true, element: <DashboardPage /> },
      { path: '/users', element: <UsersPage /> },
      { path: '/shifts', element: <ShiftsPage /> },
      { path: '/rules', element: <RulesPage /> },
      { path: '/attendance', element: <AttendancePage /> },
      { path: '/notifications', element: <NotificationsPage /> },
      { path: '/settings', element: <SettingsPage /> },
      { path: '/guide', element: <GuidePage /> },
    ],
  },
]);
