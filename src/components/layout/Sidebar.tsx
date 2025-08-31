import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Avatar,
  Typography,
  Box,
  Stack,
  Divider,
  Chip,
} from '@mui/material';
import DashboardRoundedIcon from '@mui/icons-material/DashboardRounded';
import MicRoundedIcon from '@mui/icons-material/MicRounded';
import VideoLibraryRoundedIcon from '@mui/icons-material/VideoLibraryRounded';
import SettingsRoundedIcon from '@mui/icons-material/SettingsRounded';
import PersonRoundedIcon from '@mui/icons-material/PersonRounded';
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

const DRAWER_WIDTH = 280;

const Sidebar: React.FC<SidebarProps> = ({ 
  currentRoute, 
  user, 
  onNavigate, 
  isMobile = false, 
  mobileOpen = false, 
  onMobileToggle 
}) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: DashboardRoundedIcon, badge: null },
    { id: 'new_session', label: 'Nova Sessão', icon: MicRoundedIcon, badge: 'Novo' },
    { id: 'sessions', label: 'Sessões', icon: VideoLibraryRoundedIcon, badge: null },
    { id: 'settings', label: 'Configurações', icon: SettingsRoundedIcon, badge: null },
  ];

  const drawerContent = (
      <Box sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
        {/* User Profile Section */}
        <Box 
          sx={{ 
            background: 'rgba(255,255,255,0.15)',
            borderRadius: 3,
            p: 3,
            mb: 4,
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255,255,255,0.2)'
          }}
        >
          <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 2 }}>
            <Box sx={{ position: 'relative' }}>
              <Avatar
                src={user.avatar}
                alt={user.name}
                sx={{ 
                  width: 56, 
                  height: 56,
                  border: '3px solid rgba(255,255,255,0.3)',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.2)'
                }}
              >
                <PersonRoundedIcon sx={{ fontSize: 32 }} />
              </Avatar>
              <Box 
                sx={{
                  position: 'absolute',
                  bottom: -2,
                  right: -2,
                  width: 16,
                  height: 16,
                  borderRadius: '50%',
                  backgroundColor: '#4caf50',
                  border: '2px solid white'
                }}
              />
            </Box>
            <Box sx={{ flex: 1 }}>
              <Typography
                variant="subtitle1"
                sx={{
                  fontWeight: 700,
                  color: 'white',
                  lineHeight: 1.2,
                  textShadow: '0 1px 2px rgba(0,0,0,0.3)'
                }}
              >
                {user.name}
              </Typography>
              <Typography
                variant="caption"
                sx={{
                  color: 'rgba(255,255,255,0.8)',
                  fontWeight: 500
                }}
              >
                Lavínia Mendonça
              </Typography>
            </Box>
          </Stack>
          <Chip 
            label="Online" 
            size="small" 
            sx={{ 
              backgroundColor: 'rgba(76,175,80,0.2)',
              color: '#4caf50',
              fontWeight: 600,
              border: '1px solid rgba(76,175,80,0.3)'
            }} 
          />
        </Box>

        {/* Navigation Menu */}
        <Box sx={{ flex: 1 }}>
          <Typography 
            variant="overline" 
            sx={{ 
              color: 'rgba(255,255,255,0.7)',
              fontWeight: 700,
              letterSpacing: 1.2,
              mb: 2,
              display: 'block'
            }}
          >
            NAVEGAÇÃO
          </Typography>
          <List sx={{ p: 0 }}>
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentRoute === item.id;

              return (
                <ListItem key={item.id} disablePadding sx={{ mb: 1 }}>
                  <ListItemButton
                    onClick={() => onNavigate(item.id)}
                    sx={{
                      borderRadius: 3,
                      py: 2,
                      px: 2.5,
                      backgroundColor: isActive ? 'rgba(255,255,255,0.2)' : 'transparent',
                      color: 'white',
                      backdropFilter: isActive ? 'blur(10px)' : 'none',
                      border: isActive ? '1px solid rgba(255,255,255,0.3)' : '1px solid transparent',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        backgroundColor: isActive ? 'rgba(255,255,255,0.25)' : 'rgba(255,255,255,0.1)',
                        transform: 'translateX(4px)',
                        boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
                      },
                    }}
                  >
                    <ListItemIcon
                      sx={{
                        color: 'white',
                        minWidth: 44,
                      }}
                    >
                      <Icon sx={{ fontSize: 24 }} />
                    </ListItemIcon>
                    <ListItemText
                      primary={item.label}
                      primaryTypographyProps={{
                        fontWeight: isActive ? 700 : 600,
                        fontSize: '1rem',
                        textShadow: '0 1px 2px rgba(0,0,0,0.3)'
                      }}
                    />
                    {item.badge && (
                      <Chip 
                        label={item.badge} 
                        size="small" 
                        sx={{ 
                          backgroundColor: '#ff4081',
                          color: 'white',
                          fontWeight: 600,
                          fontSize: '0.7rem',
                          height: 20,
                          '& .MuiChip-label': {
                            px: 1
                          }
                        }} 
                      />
                    )}
                  </ListItemButton>
                </ListItem>
              );
            })}
          </List>
        </Box>
      </Box>
    );

    return (
      <>
        {/* Mobile Drawer */}
        {isMobile ? (
          <Drawer
            variant="temporary"
            open={mobileOpen}
            onClose={onMobileToggle}
            ModalProps={{
              keepMounted: true, // Better open performance on mobile.
            }}
            sx={{
              display: { xs: 'block', md: 'none' },
              '& .MuiDrawer-paper': {
                width: DRAWER_WIDTH,
                boxSizing: 'border-box',
                background: 'linear-gradient(180deg, #667eea 0%, #764ba2 100%)',
                border: 'none',
                boxShadow: '4px 0 20px rgba(0,0,0,0.1)',
              },
            }}
          >
            {drawerContent}
          </Drawer>
        ) : (
          /* Desktop Drawer */
          <Drawer
            variant="permanent"
            sx={{
              display: { xs: 'none', md: 'block' },
              width: DRAWER_WIDTH,
              flexShrink: 0,
              '& .MuiDrawer-paper': {
                width: DRAWER_WIDTH,
                boxSizing: 'border-box',
                background: 'linear-gradient(180deg, #667eea 0%, #764ba2 100%)',
                border: 'none',
                boxShadow: '4px 0 20px rgba(0,0,0,0.1)',
              },
            }}
          >
            {drawerContent}
          </Drawer>
        )}
      </>
     );
 };

export default Sidebar;