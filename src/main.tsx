// Prevent theme flash
const initializeTheme = () => {
  const theme = localStorage.getItem('vite-ui-theme') || 'system';
  if (theme === 'system') {
    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    document.documentElement.classList.add(systemTheme);
    document.documentElement.setAttribute('data-theme', systemTheme);
  } else {
    document.documentElement.classList.add(theme);
    document.documentElement.setAttribute('data-theme', theme);
  }
};

initializeTheme();

import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.tsx'
import './index.css'

const root = document.getElementById('root')
if (!root) {
  throw new Error('Root element not found')
}

createRoot(root).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
