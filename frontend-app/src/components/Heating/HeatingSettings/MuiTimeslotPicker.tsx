import * as React from "react";
import { Slider } from "@mui/material";
import {
  UPDATE_TEMPERATURE,
  UPDATE_TIMES,
  useHeatingSettings,
} from "../../../context/HeatingContext";

export function MuiTimeslotPicker() {
  const { context, dispatch } = useHeatingSettings();

  const formatTime = (time: number) => {
    let digit: string | string[] = time.toFixed(2);
    digit = digit.toString().split(".");
    let minutes: number | string =
      (parseInt(digit as unknown as string) -
        parseInt(digit[0] as unknown as string)) *
      60;
    minutes = minutes.toString();
    if (minutes.length < 2) {
      minutes = "0" + minutes;
    }
    if (digit[0].length < 2) {
      return (("0" + digit[0]) as string) + ":" + minutes;
    }
    return (digit[0] as string) + ":" + minutes;
  };

  const unformatTime = (time: string): number => {
    let hours = time.split(":")[0];
    // let minutes = (parseInt(time.split(":")[0]) / 60) * 100;
    // return parseFloat(`${hours}.${minutes}`);
    return time === "23:59" ? 24 : parseInt(hours);
  };

  const [value, setValue] = React.useState<number[]>([
    context.selectedPeriod ? unformatTime(context.selectedPeriod.time_on) : 0,
    context.selectedPeriod ? unformatTime(context.selectedPeriod.time_off) : 24,
  ]);

  React.useEffect(() => {
    setValue([
      context.selectedPeriod ? unformatTime(context.selectedPeriod.time_on) : 0,
      context.selectedPeriod
        ? unformatTime(context.selectedPeriod.time_off)
        : 24,
    ]);
  }, [context.selectedPeriod?.period_id, context.revert]);

  const handleChange = (event: Event, newValue: number | number[]) => {
    const val = newValue as number[];
    let endVal: string | null = null;
    if (val[0] === 24 || val[1] === 0) return;
    if (val[1] === 24) endVal = "23:59";
    setValue(val);
    dispatch({
      type: UPDATE_TIMES,
      payload: {
        period_id: context.selectedPeriod?.period_id,
        time_on: formatTime(val[0]),
        time_off: endVal || formatTime(val[1]),
      },
    });
  };

  const [marks] = React.useState(
    [...Array(48)]
      .map((nullVal, index) => ({
        value: index / 2,
        label: index % 2 ? "" : `${index / 2}`,
      }))
      .concat([{ value: 24, label: "0" }])
  );

  return (
    <div className="timeslot-picker">
      <Slider
        sx={{ marginLeft: "1rem" }}
        orientation="vertical"
        getAriaLabel={() => "Time slot"}
        value={value}
        max={24}
        disabled={!context.selectedPeriod}
        onChange={handleChange}
        marks={marks}
      />
    </div>
  );
}
