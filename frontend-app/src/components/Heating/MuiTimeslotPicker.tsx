import * as React from "react";
import { TimePeriod } from "./TimeBlock";
import { Box, Slider } from "@mui/material";

interface Props {
  timePeriod: TimePeriod;
  setter: React.Dispatch<any>;
}

export function MuiTimeslotPicker({ timePeriod, setter }: Props) {
  const [value, setValue] = React.useState<number[]>([
    timePeriod ? parseInt(timePeriod.time_on.split(":")[0]) : 0,
    timePeriod ? parseInt(timePeriod.time_off.split(":")[0]) : 24,
  ]);

  React.useEffect(() => {
    setValue([
      timePeriod ? parseInt(timePeriod.time_on.split(":")[0]) : 0,
      timePeriod ? parseInt(timePeriod.time_off.split(":")[0]) : 24,
    ]);
  }, [timePeriod]);

  const handleChange = (event: Event, newValue: number | number[]) => {
    setValue(newValue as number[]);
  };

  function valuetext(value: number) {
    return `${value} o'clock`;
  }

  React.useEffect(()=>{
    if (parseInt(timePeriod?.time_on.split(':')[0] as string) !== value[0])
    setter((p: TimePeriod) => ({
      ...p,
      time_on: value[0] + ':00',
    }))
    if (parseInt(timePeriod?.time_off.split(':')[0] as string) !== value[1])
    setter((p: TimePeriod) => ({
      ...p,
      time_off: value[1] + ':00',
    }))
  }, [setter, value])

  const [marks] = React.useState(
    [...Array(48)]
      .map((nullVal, index) => ({
        value: index / 2,
        label: index % 2 ? "" : `${index / 2}`,
      }))
      .concat([{ value: 24, label: "0" }])
  );

  return (
    <Slider
      sx={{marginLeft: '1rem'}}
      orientation="vertical"
      getAriaLabel={() => "Time slot"}
      value={value}
      max={24}
      onChange={handleChange}
      valueLabelDisplay="off"
      getAriaValueText={valuetext}
      marks={marks}
    />
  );
}
