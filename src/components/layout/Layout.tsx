import React from 'react';
import { Box } from '@mui/material';
import Sidebar from './Sidebar';
import { SidebarProps } from '../../types/interfaces';

interface LayoutProps extends SidebarProps {
  children: React.ReactNode;
}

const DRAWER_WIDTH = 280;

const Layout: React.FC<LayoutProps> = ({ children, currentRoute, user, onNavigate }) => {
  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar
        currentRoute={currentRoute}
        user={user}
        onNavigate={onNavigate}
      />
      
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          ml: `${DRAWER_WIDTH}px`,
          backgroundColor: 'background.default',
          minHeight: '100vh',
        }}
      >
        {children}
      </Box>
    </Box>
  );
};

export default Layout;