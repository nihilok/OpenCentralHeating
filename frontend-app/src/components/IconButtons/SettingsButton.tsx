import * as React from "react";
import "./icon-buttons.css";
import { IconButton } from "@mui/material";
import { Settings } from "@mui/icons-material";
import { useHistory } from "react-router-dom";

export function SettingsButton() {
  let history = useHistory();

  const handleClick = () => {
    history.push("/times");
  };

  return (
    <div>
      <IconButton
        onClick={handleClick}
        className={"help-button"}
        aria-label="help"
        component="div"
      >
        <Settings />
      </IconButton>
    </div>
  );
}
