import * as React from "react";
import { Slider } from "@mui/material";

interface Props {
  value: number;
  setValue: React.Dispatch<any>;
}

export function TemperatureControl({ value, setValue }: Props) {
  return (
    <div>
      <div className={"temperature-control"}>
        <h1>{value}°C</h1>
        <Slider
          orientation={"vertical"}
          max={30}
          min={10}
          value={value}
          onChange={(e, newVal) => setValue(newVal)}
        />
      </div>
    </div>
  );
}
