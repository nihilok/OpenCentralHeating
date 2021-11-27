import * as React from "react";
import { useFetchWithToken } from "../../hooks/FetchWithToken";

export interface TimePeriod {
  time_on: string;
  time_off: string;
  temperature: number;
  period_id: number;
}

interface Props {
  timePeriod: TimePeriod;
}

export function TimeBlock({ timePeriod }: Props) {
  type Timeout = ReturnType<typeof setTimeout>;

  const fetch = useFetchWithToken();

  const [state, setState] = React.useState<TimePeriod>(timePeriod);
  const timeout = React.useRef<Timeout>();

  const update = React.useCallback(
    async (currentState) => {
      fetch("/heating/times/", "POST", currentState).then((res) => {
        if (res.status === 200) {
          res.json().then((data: TimePeriod) => {
            setState(data);
          });
        }
      });
    },
    [fetch]
  );

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    update(state).catch((err) => console.log(err));
  };

  const debounce = React.useCallback(
    (currentState) => {
      clearTimeout(timeout.current as Timeout);
      timeout.current = setTimeout(() => update(currentState), 2000);
    },
    [update]
  );

  React.useEffect(() => {
    debounce(state);
    return () => clearTimeout(timeout.current as Timeout);
  }, [debounce, state]);

  return (
    <form onSubmit={handleSubmit}>
      <input type="time" value={state.time_on} />
      <input type="time" value={state.time_off} />
    </form>
  );
}
