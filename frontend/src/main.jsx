import React from 'react';
import ReactDOM from 'react-dom/client';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import App from './App.jsx';
import DeepSearch from './pages/DeepSearch.jsx';
import TranslationPractice from './pages/TranslationPractice.jsx';
import './index.css';
// ... other imports
import './App.css'; 

// ... rest of the file

// Define the application's routes
const router = createBrowserRouter([
  {
    path: '/',
    element: <App />, // The main layout shell
    children: [
      {
        index: true, // Makes DeepSearch the default homepage for "/"
        element: <DeepSearch />,
      },
      {
        path: 'practice', // The path for the translation feature
        element: <TranslationPractice />,
      },
    ],
  },
]);

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);