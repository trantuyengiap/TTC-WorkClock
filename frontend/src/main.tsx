import React from 'react';
import ReactDOM from 'react-dom/client';
import 'antd/dist/reset.css';
import { ConfigProvider } from 'antd';
import viVN from 'antd/locale/vi_VN';
import { RouterProvider } from 'react-router-dom';
import { appRouter } from './router';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ConfigProvider locale={viVN}>
      <RouterProvider router={appRouter} />
    </ConfigProvider>
  </React.StrictMode>,
);
