
import { Switch } from "@mui/material";
import { useTheme } from "@/components/ThemeProvider";
import { DarkMode, LightMode } from "@mui/icons-material";

const ThemeToggle = () => {
  const { theme, setTheme } = useTheme();
  const isDark = theme === "dark";

  return (
    <div className="flex items-center gap-2">
      <LightMode 
        sx={{ 
          fontSize: 18, 
          color: isDark ? 'rgba(255, 255, 255, 0.7)' : 'inherit',
          transition: 'all 0.3s ease'
        }} 
      />
      <Switch
        checked={isDark}
        onChange={() => setTheme(isDark ? "light" : "dark")}
        color="default"
        size="small"
        sx={{
          '& .MuiSwitch-switchBase': {
            color: isDark ? '#2196f3' : undefined,
          },
          '& .MuiSwitch-switchBase.Mui-checked': {
            color: '#2196f3',
          },
          '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
            backgroundColor: isDark ? 'rgba(33, 150, 243, 0.5)' : undefined,
          },
          '& .MuiSwitch-track': {
            backgroundColor: isDark ? 'rgba(33, 150, 243, 0.3)' : undefined,
          }
        }}
        className="mui-icon-glow"
      />
      <DarkMode 
        sx={{ 
          fontSize: 18, 
          color: isDark ? '#2196f3' : 'inherit',
          transition: 'all 0.3s ease',
          ...(isDark && {
            filter: 'drop-shadow(0 0 3px #2196f3)'
          })
        }} 
      />
    </div>
  );
};

export default ThemeToggle;
