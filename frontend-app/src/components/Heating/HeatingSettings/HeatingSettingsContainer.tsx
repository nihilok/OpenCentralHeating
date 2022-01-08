import * as React from "react";
import { TimePeriod } from "../TimeBlock";
import "./heating-settings.css";
import { MuiTimeslotPicker } from "./MuiTimeslotPicker";
import { TimeSlotsDisplay } from "./TimeSlotsDisplay";
import { TemperatureControl } from "./TemperatureControl";
import { useFetchWithToken } from "../../../hooks/FetchWithToken";
import { useSnackbar } from "notistack";
import { TopBar } from "../../Custom/TopBar";
import { BackButton } from "../../IconButtons/BackButton";

interface Props {
  currentSystem: number;
}

type Timeout = ReturnType<typeof setTimeout>;

interface TimesResponse {
  periods: TimePeriod[];
}

export interface IContainerState {
  currentSystem: number;
  selectedPeriod: TimePeriod | null;
  allPeriods: TimePeriod[];
  systems: number[];
}

export function HeatingSettingsContainer({ currentSystem }: Props) {
  const fetch = useFetchWithToken();
  const { enqueueSnackbar } = useSnackbar();
  const [getPeriods, setGetPeriods] = React.useState(false);
  const lock = React.useRef(false);
  const mouseDown = React.useRef(0);

  const [containerState, setContainerState] = React.useState<IContainerState>({
    currentSystem,
    selectedPeriod: null,
    allPeriods: [],
    systems: [],
  });

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
          setContainerState((p) => ({
            ...p,
            allPeriods: data.periods,
            systems: systemsArr,
          }));
        }
      })
    );
  }, [fetch, getPeriods]);

  const debounceTimeout = React.useRef<Timeout | null>(null);

  const update = React.useCallback(
    async (frozenState) => {
      console.log("updating period");
      const data = {
        period_id: frozenState.period_id,
        time_on: frozenState.time_on,
        time_off: frozenState.time_off,
        target: frozenState.target,
        heating_system_id: frozenState.heating_system_id,
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
            setGetPeriods(p => !p);
          } else if (res.status === 422) {
            res.json().then((resJson: { detail: string | { msg: string } }) => {
              setContainerState((p) => ({
                ...p,
                selectedPeriod: p.allPeriods.filter(
                  (period) => period.period_id === data.period_id
                )[0],
              }));
              typeof resJson.detail === "string" ||
              resJson.detail.msg?.length > 0
                ? enqueueSnackbar(
                    typeof resJson.detail === "string"
                      ? resJson.detail
                      : resJson.detail.msg,
                    { variant: "error" }
                  )
                : console.log(resJson);
            });
          }
        })
        .finally(() => {
          console.log("freeing lock (done)");
          lock.current = false;
          console.groupEnd();
        });
    },
    [enqueueSnackbar, fetch]
  );

  const debounce = React.useCallback(
    (period: TimePeriod | null) => {
      lock.current = true;
      clearTimeout(debounceTimeout.current as Timeout);
      if (period) {
        debounceTimeout.current = setTimeout(() => update(period), 1000);
      }
    },
    [update]
  );

  function selectPeriod(period: TimePeriod) {
    setContainerState({
      ...containerState,
      selectedPeriod: period,
    });
  }

  function setTarget(target: number) {
    setContainerState({
      ...containerState,
      selectedPeriod: {
        ...containerState.selectedPeriod,
        target: target,
      } as TimePeriod,
    });
  }

  interface StateCheck {
    time_on: string;
    time_off: string;
    target: number;
    heating_system_id: number;
  }

  const mapCheckers = React.useCallback(function (
    period: TimePeriod
  ): StateCheck {
    return {
      time_on: period.time_on,
      time_off: period.time_off,
      target: period.target,
      heating_system_id: period.heating_system_id,
    };
  },
  []);

  React.useEffect(() => {
    if (containerState.selectedPeriod) {
      const selectedPeriod = containerState.selectedPeriod as TimePeriod;
      const stateCheck = mapCheckers(selectedPeriod);
      const allPeriods = containerState.allPeriods.map((p) => mapCheckers(p));
      const diff = allPeriods.filter(
        (obj) =>
          obj.time_on === stateCheck.time_on &&
          obj.time_off === stateCheck.time_off &&
          obj.target === stateCheck.target &&
          obj.heating_system_id === stateCheck.heating_system_id
      );

      if (diff.length === 0 && !lock.current) {
        console.group("Update Flow:");
        console.log("debouncing");
        console.log(selectedPeriod);
        debounce(selectedPeriod);
      } else if (!lock.current) {
        clearTimeout(debounceTimeout.current as Timeout);
      }
    }
  }, [debounce, mapCheckers, containerState.selectedPeriod]);

  return (
    <>
      <TopBar>
        <BackButton path={"/"} />
        <div />
      </TopBar>
      <div className="heating-settings-container">
        <MuiTimeslotPicker
          timePeriod={containerState.selectedPeriod}
          setter={setContainerState}
        />
        <TimeSlotsDisplay
          timeSlots={containerState.allPeriods}
          choosePeriod={selectPeriod}
          selected={containerState.selectedPeriod}
          systems={containerState.systems}
        />
        <TemperatureControl
          timeSlot={containerState.selectedPeriod}
          setter={setTarget}
        />
      </div>
    </>
  );
}
