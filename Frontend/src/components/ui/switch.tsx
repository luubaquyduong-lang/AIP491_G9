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
      <span className="text-sm text-gray-500">
        {theme === "light" ? "Light Mode" : "Dark Mode"}
      </span>

      <Switch
        onChange={toggleTheme}
        checked={theme === "dark"}
        /** MÀU NỀN THANH SWITCH */
        offColor="#D1F3EB"      // Light mode: xanh ngọc nhạt (giống nút ChatGPT)
        onColor="#00A67E"       // Dark mode: xanh ngọc đậm (brand ChatGPT)

        /** MÀU NÚT TRÒN */
        offHandleColor="#ffffff"                       // Light mode: trắng
        onHandleColor={theme === "dark" ? "#000000ff" : "#ffffff"}  // Dark mode: xanh sáng

        checkedIcon={false}
        uncheckedIcon={false}
        height={20}
        width={40}
      />
    </div>
  );
};
