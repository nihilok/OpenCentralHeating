import * as React from "react";
import "./icon-buttons.css";
import { IconButton } from "@mui/material";
import { Settings } from "@mui/icons-material";
import { useHistory } from "react-router-dom";

interface Props {
  helpMode: boolean;
  setHelpMode: (state: boolean) => void;
}

export function SettingsButton({ helpMode, setHelpMode }: Props) {
  let history = useHistory();

  const handleClick = () => {
    history.push("/times");
  };

  return (
    <div>
      <IconButton
        onClick={handleClick}
        className={"help-button"}
        color={helpMode ? "primary" : "default"}
        aria-label="help"
        component="div"
      >
        <Settings />
      </IconButton>
    </div>
  );
}
