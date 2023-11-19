import * as React from 'react';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';

import StatblockPage from './pages/StatblockPage.js';
import AboutPage from './pages/AboutPage.tsx'


function App({ baseUrl }) {

  const router = createBrowserRouter([
    { path: "/", element: <StatblockPage baseUrl={baseUrl} /> },
    { path: "/about", element: <AboutPage /> }
  ]);

  return (
    <RouterProvider router={router} />
  );
}



export default App;
