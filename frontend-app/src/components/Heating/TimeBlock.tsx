import * as React from "react";
import { useFetchWithToken } from "../../hooks/FetchWithToken";
import { StyledTextField } from "../Custom/StyledTextField";
import { ProgramArrow } from "./ProgramArrow";
import { Slider, Stack } from "@mui/material";
import { systemNames } from "../../constants/systems";
import { ReducedTimeBlock } from "./ReducedTimeBlock";
import { UnfoldMoreOutlined, UnfoldLessOutlined } from "@mui/icons-material";
import { useSnackbar } from "notistack";

export interface TimePeriod {
  time_on: string;
  time_off: string;
  target: number;
  period_id?: number;
  heating_system_id: number;
}

interface Props {
  timePeriod: TimePeriod;
}

export function TimeBlock({ timePeriod }: Props) {
  type Timeout = ReturnType<typeof setTimeout>;

  const fetch = useFetchWithToken();
  const { enqueueSnackbar } = useSnackbar();
  const [error, setError] = React.useState<string | null>(null);
  const [state, setState] = React.useState<TimePeriod>(timePeriod);
  const [expanded, setExpanded] = React.useState<boolean>(false);
  const timeout = React.useRef<Timeout>();
  const lock = React.useRef<boolean>(true);
  const resetState = React.useRef<TimePeriod>(timePeriod);
  const first = React.useRef<boolean>(true);

  const handleTimeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    lock.current = false;
    resetState.current = state;
    setState((p) => ({
      ...p,
      [event.target.name]: event.target.value,
    }));
  };

  const update = React.useCallback(
    async (currentState) => {
      const data = {
        period_id: currentState.period_id,
        time_on: currentState.time_on,
        time_off: currentState.time_off,
        target: currentState.target,
        heating_system_id: currentState.heating_system_id,
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

      fetch("/v2/heating/times", "PUT", data)
        .then((res) => {
          if (res.status === 200) {
            res.json().then((resJson: TimePeriod) => {
              lock.current = true;
              setState(data);
              setError(null);
            });
          } else if (res.status === 422) {
            res.json().then((resJson: { detail: string }) => {
              setError(resJson.detail);
              setState(resetState.current);
            });
          }
        })
        .then(() => (lock.current = false));
    },
    [fetch]
  );

  React.useEffect(() => {
    if (error) {
      enqueueSnackbar(error, { variant: "error" });
    }
  }, [error, enqueueSnackbar]);

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
    resetState.current = state;
    setState((prev) => ({ ...prev, target: newValue as number }));
  }

  const withinLimit = () => {
    const currentDate = new Date();

    const startDate = new Date(currentDate.getTime());
    startDate.setHours(parseInt(state.time_on.split(":")[0]));
    startDate.setMinutes(parseInt(state.time_on.split(":")[1]));

    const endDate = new Date(currentDate.getTime());
    endDate.setHours(parseInt(state.time_off.split(":")[0]));
    endDate.setMinutes(parseInt(state.time_off.split(":")[1]));

    return startDate < currentDate && endDate > currentDate;
  };

  React.useEffect(() => {
    if (!lock.current) debounce(state);
    if (first.current) {
      first.current = false;
      lock.current = false;
    }
    return () => clearTimeout(timeout.current as Timeout);
  }, [debounce, state]);

  return !expanded ? (
    <ReducedTimeBlock timePeriod={timePeriod} setExpanded={setExpanded} />
  ) : (
    <div className={"container time-block"}>
      <div
        style={{
          display: "flex",
          justifyContent: "flex-end",
          cursor: "pointer",
        }}
        onClick={() => setExpanded(false)}
      >
        <UnfoldLessOutlined />
      </div>
      <p className="text-muted no-margin">
        {systemNames[state.heating_system_id]}
      </p>
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
            <ProgramArrow programOn={true} withinLimit={withinLimit()} />
            <ProgramArrow programOn={true} withinLimit={withinLimit()} />
            <ProgramArrow programOn={true} withinLimit={withinLimit()} />
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
