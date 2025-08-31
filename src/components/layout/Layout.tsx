import React, { useState } from 'react';
import { Box, useMediaQuery, useTheme } from '@mui/material';
import Sidebar from './Sidebar';
interface UserProfile {
  name: string;
  avatar: string;
  isAuthenticated: boolean;
}

interface SidebarProps {
  currentRoute: string;
  user: UserProfile;
  onNavigate: (route: string) => void;
  isMobile?: boolean;
  mobileOpen?: boolean;
  onMobileToggle?: () => void;
}

interface LayoutProps extends SidebarProps {
  children: React.ReactNode;
}

const DRAWER_WIDTH = 280;

const Layout: React.FC<LayoutProps> = ({ children, currentRoute, user, onNavigate }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar
        currentRoute={currentRoute}
        user={user}
        onNavigate={onNavigate}
        isMobile={isMobile}
        mobileOpen={mobileOpen}
        onMobileToggle={handleDrawerToggle}
      />
      
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          ml: isMobile ? 0 : `${DRAWER_WIDTH}px`,
          backgroundColor: 'background.default',
          minHeight: '100vh',
          transition: theme.transitions.create(['margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
        }}
      >
        {children}
      </Box>
    </Box>
  );
};

export default Layout;