import * as React from "react";
import "./icon-buttons.css";
import { IconButton } from "@mui/material";
import { ArrowBack } from "@mui/icons-material";
import { useHistory } from "react-router-dom";

interface Props {
  path: string;
}

export function BackButton(props: Props) {
  let history = useHistory();

  const handleClick = () => {
    history.push(props.path);
  };

  return (
    <div>
      <IconButton
        onClick={handleClick}
        className={"back-button"}
        aria-label="back"
        component="div"
      >
        <ArrowBack />
      </IconButton>
    </div>
  );
}
