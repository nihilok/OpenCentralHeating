import * as React from "react";
import { useFetchWithToken } from "../../hooks/FetchWithToken";
import { StyledTextField } from "../Custom/StyledTextField";
import { ProgramArrow } from "./ProgramArrow";
import { Slider, Stack } from "@mui/material";

export interface TimePeriod {
  time_on: string;
  time_off: string;
  target: number;
  period_id?: number;
  heating_system: { system_id: number };
}

interface Props {
  timePeriod: TimePeriod;
}

export function TimeBlock({ timePeriod }: Props) {
  type Timeout = ReturnType<typeof setTimeout>;

  const fetch = useFetchWithToken();

  const [state, setState] = React.useState<TimePeriod>(timePeriod);
  const timeout = React.useRef<Timeout>();
  const lock = React.useRef<boolean>(true);
  const first = React.useRef<boolean>(true);

  const handleTimeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    lock.current = false;
    setState((p) => ({
      ...p,
      [event.target.name]: event.target.value,
    }));
  };

  const update = React.useCallback(
    async (currentState) => {
      const data = {
        time_on: currentState.time_on,
        time_off: currentState.time_off,
        target: currentState.target,
        heating_system_id: currentState.heating_system.system_id,
        days: {
          monday: true,
          tuesday: true,
          wednesday: true,
          thursday: true,
          friday: true,
          saturday: true,
          sunday: true,
        },
      };

      fetch(
        "/v2/heating/times?period_id=" + currentState.period_id,
        "PUT",
        data
      )
        .then((res) => {
          if (res.status === 200) {
            res.json().then((data: TimePeriod) => {
              lock.current = true;
              setState(data);
            });
          }
        })
        .then(() => (lock.current = false));
    },
    [fetch]
  );

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    lock.current = false;

    update(state).catch((err) => console.log(err));
  };

  const debounce = React.useCallback(
    (currentState) => {
      clearTimeout(timeout.current as Timeout);
      timeout.current = setTimeout(() => update(currentState), 1000);
    },
    [update]
  );

  function handleSliderChange(event: Event, newValue: number | number[]) {
    lock.current = false;
    setState((prev) => ({ ...prev, target: newValue as number }));
  }

  React.useEffect(() => {
    if (!lock.current) debounce(state);
    if (first.current) {
      first.current = false;
      lock.current = false;
    }
    return () => clearTimeout(timeout.current as Timeout);
  }, [debounce, state]);

  return (
    <div className={"container"}>
      <Stack
        spacing={2}
        direction="row"
        sx={{ mb: 1 }}
        alignItems="center"
        justifyContent="center"
      >
        <h2>Target:</h2>
        <Slider
          aria-label="Target Temperature"
          value={state.target}
          onChange={handleSliderChange}
          min={12}
          max={26}
        />
        <h2>{state.target}&deg;C</h2>
      </Stack>
      <Stack>
        <div />
        <form onSubmit={handleSubmit} className={"time-grid"}>
          <StyledTextField
            label="On"
            name="time_on"
            type="time"
            required={true}
            value={state.time_on || ""}
            InputLabelProps={{
              shrink: true,
            }}
            onChange={handleTimeChange}
          />
          <span>
            <ProgramArrow programOn={true} withinLimit={true} />
            <ProgramArrow programOn={true} withinLimit={true} />
            <ProgramArrow programOn={true} withinLimit={true} />
          </span>
          <StyledTextField
            label="Off"
            type="time"
            name="time_off"
            required={true}
            value={state.time_off || ""}
            InputLabelProps={{
              shrink: true,
            }}
            onChange={handleTimeChange}
          />
        </form>
      </Stack>
    </div>
  );
}
