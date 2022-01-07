import * as React from "react";
import { TimePeriod } from "../TimeBlock";
import { Slider } from "@mui/material";
import {IContainerState} from "./HeatingSettingsContainer";

interface Props {
  timePeriod: TimePeriod | null;
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

  const formatTime = (time: number) => {
    let digit: string | string[] = time.toFixed(2)
    digit = digit.toString().split('.')
    const minutes = (parseInt(digit as unknown as string) - parseInt((digit[0] as unknown as string))) * 60
    if (digit[0].length < 2) {
      return '0' + digit[0] as string + ':' + minutes
    }
    return digit[0] as string + ':' + minutes
  }

  const handleChange = (event: Event, newValue: number | number[]) => {
    const val = newValue as number[];
    setValue(val);
    setter((p: IContainerState) => ({
    ...p,
    selectedPeriod: {...p.selectedPeriod, time_on: formatTime(val[0]), time_off: formatTime(val[1])}
    }))
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
    <div className="timeslot-picker"><Slider
      sx={{marginLeft: '1rem'}}
      orientation="vertical"
      getAriaLabel={() => "Time slot"}
      value={value}
      step={0.5}
      max={24}
      disabled={!timePeriod}
      onChange={handleChange}
      valueLabelDisplay="off"
      getAriaValueText={valuetext}
      marks={marks}
    /></div>
  );
}
