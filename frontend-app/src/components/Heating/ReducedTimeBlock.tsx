import * as React from "react";
import { TimePeriod } from "./TimeBlock";

interface Props {
  timePeriod: TimePeriod;
  setExpanded: React.Dispatch<any>;
}

export function ReducedTimeBlock({ timePeriod, setExpanded }: Props) {
  return (
    <div className="reduced-timeblock" onClick={() => setExpanded(true)}>
      {timePeriod.time_on} {">>>"} {timePeriod.time_off}
    </div>
  );
}
