import * as React from "react";
import { Slider } from "@mui/material";
import {
  UPDATE_TEMPERATURE,
  useHeatingSettings,
} from "../../../context/HeatingContext";

export function TemperatureControl() {
  const { heating, dispatch } = useHeatingSettings();

  const [value, setValue] = React.useState(
    heating.selectedPeriod?.target || 20
  );

  const handleChange = (e: Event, newVal: number | number[]) => {
    setValue(newVal as number);
    dispatch({
      type: UPDATE_TEMPERATURE,
      payload: {
        period_id: heating.selectedPeriod?.period_id || 3,
        target: newVal as number,
      },
    });
  };

  React.useEffect(() => {
    setValue(heating.selectedPeriod?.target as number)
  }, [heating.revert])

  return (
    <div className={"temperature-control"}>
      <h1>{heating.selectedPeriod?.target}°C</h1>
      <Slider
        disabled={!heating.selectedPeriod}
        max={30}
        min={10}
        value={value}
        onChange={handleChange}
      />
    </div>
  );
}
