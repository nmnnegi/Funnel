import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

console.log('Main.tsx loaded');
console.log('Environment:', import.meta.env);

const rootElement = document.getElementById('root');
console.log('Root element:', rootElement);

if (rootElement) {
  try {
    console.log('Creating root and rendering...');
    createRoot(rootElement).render(
      <StrictMode>
        <App />
      </StrictMode>,
    );
    console.log('Render completed successfully');
  } catch (error) {
    console.error('Error during render:', error);
    rootElement.innerHTML = `
      <div style="padding: 20px; color: red;">
        <h1>Failed to render application</h1>
        <pre>${error}</pre>
      </div>
    `;
  }
} else {
  console.error('Root element not found!');
  document.body.innerHTML = '<div style="padding: 20px; color: red;"><h1>Root element #root not found!</h1></div>';
}
