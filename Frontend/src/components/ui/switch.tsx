"use client";

import React from "react";
import Switch from "react-switch";

interface ThemeSwitchProps {
  theme: "light" | "dark";
  toggleTheme: () => void;
}

export const ThemeSwitch: React.FC<ThemeSwitchProps> = ({
  theme,
  toggleTheme,
}) => {
  return (
    <div className="flex items-center space-x-2">
      <span className={`text-sm font-medium ${theme === "light" ? "text-orange-600" : "text-cyan-400"
        }`}>
        {theme === "light" ? "Chế độ sáng" : "Chế độ tối"}
      </span>

      <Switch
        onChange={toggleTheme}
        checked={theme === "dark"}
        /** MÀU NỀN THANH SWITCH */
        offColor="#f97316"  // Light mode: cam (orange-500)
        onColor="#06b6d4"   // Dark mode: xanh cyan (cyan-500)

        /** MÀU NÚT TRÒN */
        offHandleColor="#ffffff"  // Light mode: trắng
        onHandleColor="#0f172a"   // Dark mode: slate đen

        checkedIcon={false}
        uncheckedIcon={false}
        height={22}
        width={44}
        handleDiameter={18}
        boxShadow="0 2px 4px rgba(0,0,0,0.2)"
        activeBoxShadow="0 2px 6px rgba(0,0,0,0.3)"
      />
    </div>
  );
};
