import * as React from "react";
import { Slider } from "@mui/material";
import {TimePeriod} from "../TimeBlock";
import {IContainerState} from "./HeatingSettingsContainer";

interface Props {
  timeSlot: TimePeriod | null;
  setter: React.Dispatch<any>;
}

export function TemperatureControl({ timeSlot, setter }: Props) {

  return (
      <div className={"temperature-control"}>
        <h1>{timeSlot?.target}°C</h1>
        <Slider
          disabled={!timeSlot}
          max={30}
          min={10}
          value={timeSlot?.target || 20}
          onChange={(e, newVal) => setter(newVal)}
        />
      </div>
  );
}
