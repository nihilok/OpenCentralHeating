import * as React from "react";
import { Slider } from "@mui/material";
import {
  UPDATE_TEMPERATURE,
  useHeatingSettings,
} from "../../../context/HeatingContext";

export function TemperatureControl() {
  const { context, dispatch } = useHeatingSettings();

  const [value, setValue] = React.useState(
    context.selectedPeriod?.target || 20
  );

  const handleChange = (e: Event, newVal: number | number[]) => {
    setValue(newVal as number);
    dispatch({
      type: UPDATE_TEMPERATURE,
      payload: {
        period_id: context.selectedPeriod?.period_id || 3,
        target: newVal as number,
      },
    });
  };

  return (
    <div className={"temperature-control"}>
      <h1>{context.selectedPeriod?.target}°C</h1>
      <Slider
        disabled={!context.selectedPeriod}
        max={30}
        min={10}
        value={value}
        onChange={handleChange}
      />
    </div>
  );
}
