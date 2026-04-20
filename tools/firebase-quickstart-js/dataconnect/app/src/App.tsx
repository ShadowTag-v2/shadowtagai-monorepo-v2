import React from 'react';
import { Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import RootLayout from './layout/RootLayout';
import ActorPage from './pages/Actor';
import AdvancedSearchPage from './pages/AdvancedSearch';
import Home from './pages/Home';
import MoviePage from './pages/Movie';
import MyProfilePage from './pages/MyProfile';
import NotFound from './pages/NotFound';
import VectorSearchPage from './pages/VectorSearch';

export default function App() {
  return (
    <Router>
      <RootLayout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/actor/:id" element={<ActorPage />} />
          <Route path="/movie/:id" element={<MoviePage />} />
          <Route path="/myprofile" element={<MyProfilePage />} />
          <Route path="/vectorsearch" element={<VectorSearchPage />} />
          <Route path="/advancedsearch" element={<AdvancedSearchPage />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </RootLayout>
    </Router>
  );
}
