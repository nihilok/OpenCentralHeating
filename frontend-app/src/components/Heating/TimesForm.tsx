import * as React from "react";
import { TopBar } from "../Custom/TopBar";
import { BackButton } from "../IconButtons/BackButton";
import {TimeBlock, TimePeriod} from "./TimeBlock";
import { useFetchWithToken } from "../../hooks/FetchWithToken";
import {FullScreenComponent} from "../Custom/FullScreenComponent";

interface Props {}

interface TimesResponse {
  periods: TimePeriod[];
}

export function TimesForm(props: Props) {
  const fetch = useFetchWithToken();
  const [timePeriods, setTimePeriods] = React.useState<TimePeriod[]>([]);

  React.useEffect(() => {
    fetch("/v2/heating/times").then((res) =>
      res.json().then((data: TimesResponse) => {
        if (res.status === 200) {
          setTimePeriods(data.periods);
        }
      })
    );
  }, [fetch]);
  return (
    <FullScreenComponent>
      <TopBar>
        <BackButton path={"/"} />
        <div />
      </TopBar>
      {timePeriods ? timePeriods.map((timePeriod: TimePeriod) => (
        <>
          <TimeBlock timePeriod={timePeriod} />
        </>
      )) : ''}
    </FullScreenComponent>
  );
}
