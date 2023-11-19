import * as React from 'react';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';

import StatblockPage from './pages/StatblockPage';


function App({ baseUrl }) {

  const router = createBrowserRouter([
    { path: "/", element: <StatblockPage baseUrl={baseUrl} /> }
  ]);

  return (
    <RouterProvider router={router} />
  );
}



export default App;
