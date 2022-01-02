import * as React from "react";
import { TimePeriod } from "./TimeBlock";
import {Box, Slider} from "@mui/material";

interface Props {
  timePeriod?: TimePeriod;
}

export function MuiTimeslotPicker(props: Props) {
  const [value, setValue] = React.useState<number[]>([20, 37]);

  const handleChange = (event: Event, newValue: number | number[]) => {
    setValue(newValue as number[]);
  };

  function valuetext(value: number) {
    return `${value}°C`;
  }

  const [marks] = React.useState([...Array(48)]
    .map((nullVal, index) => ({
      value: index / 2,
      label: index % 2 ? "" : `${index / 2}`,
    }))
    .concat([{ value: 24, label: "0" }]))

  return (
    <Box sx={{ height: '80vh', padding: '1rem 2rem' }}>
      <Slider
        orientation="vertical"
        getAriaLabel={() => "Time slot"}
        value={value}
        max={24}
        step={0.5}
        onChange={handleChange}
        valueLabelDisplay="off"
        getAriaValueText={valuetext}
        marks={marks}
      />
    </Box>
  );
}
