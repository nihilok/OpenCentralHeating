import * as React from "react";
import { Slider } from "@mui/material";
import {TimePeriod} from "./TimeBlock";

interface Props {
  timeSlot?: TimePeriod;
  setValue: React.Dispatch<any>;
}

export function TemperatureControl({ timeSlot, setValue }: Props) {
  const [value, setState] = React.useState(timeSlot?.target || 20)

  React.useEffect(()=>{
    setState(timeSlot?.target || 20)
  }, [timeSlot])
  return (
    <div>
      <div className={"temperature-control"}>
        <h1>{timeSlot?.target}°C</h1>
        <Slider
          orientation={"vertical"}
          max={30}
          min={10}
          value={value}
          onChange={(e, newVal) => setValue((prev: TimePeriod)=>({
            ...prev,
            target: newVal,
          }))}
        />
      </div>
    </div>
  );
}
