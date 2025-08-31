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
} from '@mui/material';
import BentoOutlinedIcon from '@mui/icons-material/BentoOutlined';
import MicOutlinedIcon from '@mui/icons-material/MicOutlined';
import VideocamOutlinedIcon from '@mui/icons-material/VideocamOutlined';
import SettingsOutlinedIcon from '@mui/icons-material/SettingsOutlined';
import { SidebarProps } from '../../types/interfaces';

const DRAWER_WIDTH = 280;

const Sidebar: React.FC<SidebarProps> = ({ currentRoute, user, onNavigate }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: BentoOutlinedIcon },
    { id: 'new_session', label: 'Nova Sessão', icon: MicOutlinedIcon },
    { id: 'sessions', label: 'Sessões', icon: VideocamOutlinedIcon },
    { id: 'settings', label: 'Configurações', icon: SettingsOutlinedIcon },
  ];

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: DRAWER_WIDTH,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: DRAWER_WIDTH,
          boxSizing: 'border-box',
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          backdropFilter: 'blur(20px)',
          border: 'none',
          borderRight: '1px solid rgba(255, 255, 255, 0.2)',
        },
      }}
    >
      <Box sx={{ p: 3 }}>
        {/* User Profile Section */}
        <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 4 }}>
          <Avatar
            src={user.avatar}
            alt={user.name}
            sx={{ width: 48, height: 48 }}
          />
          <Box>
            <Typography
              variant="subtitle1"
              sx={{
                fontWeight: 600,
                color: 'text.primary',
                lineHeight: 1.2,
              }}
            >
              {user.name}
            </Typography>
            <Typography
              variant="caption"
              color="text.secondary"
            >
              Lavínia Mendonça
            </Typography>
          </Box>
        </Stack>

        <Divider sx={{ mb: 3 }} />

        {/* Navigation Menu */}
        <List sx={{ p: 0 }}>
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentRoute === item.id;

            return (
              <ListItem key={item.id} disablePadding sx={{ mb: 1 }}>
                <ListItemButton
                  onClick={() => onNavigate(item.id)}
                  sx={{
                    borderRadius: 2,
                    py: 1.5,
                    px: 2,
                    backgroundColor: isActive ? 'primary.main' : 'transparent',
                    color: isActive ? 'white' : 'text.primary',
                    '&:hover': {
                      backgroundColor: isActive ? 'primary.dark' : 'rgba(0, 0, 0, 0.04)',
                    },
                  }}
                >
                  <ListItemIcon
                    sx={{
                      color: isActive ? 'white' : 'text.secondary',
                      minWidth: 40,
                    }}
                  >
                    <Icon />
                  </ListItemIcon>
                  <ListItemText
                    primary={item.label}
                    primaryTypographyProps={{
                      fontWeight: isActive ? 600 : 500,
                      fontSize: '0.95rem',
                    }}
                  />
                </ListItemButton>
              </ListItem>
            );
          })}
        </List>
      </Box>
    </Drawer>
  );
};

export default Sidebar;