import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import { NotificationProvider } from './components/common/NotificationProvider';
import { CustomThemeProvider } from './contexts/ThemeContext';
import ErrorBoundary from './components/common/ErrorBoundary';
import './index.css';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <ErrorBoundary>
      <BrowserRouter>
        <CustomThemeProvider>
          <NotificationProvider>
            <App />
          </NotificationProvider>
        </CustomThemeProvider>
      </BrowserRouter>
    </ErrorBoundary>
  </React.StrictMode>
); 