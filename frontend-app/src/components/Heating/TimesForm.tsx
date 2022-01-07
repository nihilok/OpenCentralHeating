import * as React from "react";
import { TopBar } from "../Custom/TopBar";
import { BackButton } from "../IconButtons/BackButton";
import { TimePeriod } from "./TimeBlock";
import { useFetchWithToken } from "../../hooks/FetchWithToken";
import { FullScreenComponent } from "../Custom/FullScreenComponent";

interface Props {}

interface TimesResponse {
  periods: TimePeriod[];
}

export function TimesForm(props: Props) {
  const fetch = useFetchWithToken();
  const [timePeriods, setTimePeriods] = React.useState<TimePeriod[]>([]);
  const [allSystems, setAllSystems] = React.useState<number[]>([]);

  React.useEffect(() => {
    fetch("/v2/heating/times").then((res) =>
      res.json().then((data: TimesResponse) => {
        if (res.status === 200) {
          let systemsArr: number[] = [];
          data.periods.forEach((period) => {
            const system_id = period.heating_system_id;
            if (!systemsArr.includes(system_id as number)) {
              systemsArr.push(system_id as number);
            }
          });
          setAllSystems(systemsArr);
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
    </FullScreenComponent>
  );
}
