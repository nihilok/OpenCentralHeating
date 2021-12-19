import * as React from "react";
import { TopBar } from "../Custom/TopBar";
import { BackButton } from "../IconButtons/BackButton";
import { TimeBlock, TimePeriod } from "./TimeBlock";
import { useFetchWithToken } from "../../hooks/FetchWithToken";
import { FullScreenComponent } from "../Custom/FullScreenComponent";
import { Button } from "@mui/material";

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
          console.log(systemsArr);
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
      <div className={"times-container"}>
        {allSystems.map((id) =>
          timePeriods
            .filter((period) => period.heating_system_id === id)
            .map((timePeriod: TimePeriod) => (
              <TimeBlock timePeriod={timePeriod} />
            ))
        )}
      </div>
      <div>
        <Button
          onClick={() => alert("New Timeblock!")}
          variant={"contained"}
          color={"primary"}
        >
          New
        </Button>
      </div>
    </FullScreenComponent>
  );
}
