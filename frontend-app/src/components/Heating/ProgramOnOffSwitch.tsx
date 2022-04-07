import * as React from "react";
import { Stack, Switch } from "@mui/material";
import AcUnitIcon from "@mui/icons-material/AcUnit";
import { StyledTooltip } from "../Custom/StyledTooltip";
import { useFetchWithToken } from "../../hooks/FetchWithToken";
import { APIResponse } from "./SettingsForm";

interface Props {
  state: boolean;
  systemId: number;
  parseResponse: (response: APIResponse) => void;
}

export function ProgramOnOffSwitch({ state, systemId, parseResponse }: Props) {
  const fetch = useFetchWithToken();

  const programLabel = {
    inputProps: {
      "aria-label": "Switch between timer program and frost stat mode",
    },
  };

  async function programOnOff() {
    await fetch(`/v2/heating/program?system_id=${systemId}`).then((res) =>
      res.json().then((data) => {
        if (res.status !== 200) return console.log(data);
        parseResponse(data);
      })
    );
  }

  function handleProgramChange(event: React.ChangeEvent<HTMLInputElement>) {
    programOnOff().catch((error) => console.log(error));
  }

  return (
    <Stack
      spacing={2}
      direction="row"
      sx={{
        position: "absolute",
        bottom: 0,
      }}
      alignItems="center"
      justifyContent="center"
    >
      <h2>Program:</h2>
      <Switch
        {...programLabel}
        onChange={handleProgramChange}
        checked={state}
      />
      <h2>
        {state ? (
          "On"
        ) : (
          <div className="flex">
            {"Off "}
            <AcUnitIcon style={{ marginTop: "2px", display: "block" }} />
          </div>
        )}
      </h2>
    </Stack>
  );
}
