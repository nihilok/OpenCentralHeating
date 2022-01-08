import * as React from "react";
import "./heating-settings.css";
import { MuiTimeslotPicker } from "./MuiTimeslotPicker";
import { TimeSlotsDisplay } from "./TimeSlotsDisplay";
import { TemperatureControl } from "./TemperatureControl";
import { useFetchWithToken } from "../../../hooks/FetchWithToken";
import { useSnackbar } from "notistack";
import { TopBar } from "../../Custom/TopBar";
import { BackButton } from "../../IconButtons/BackButton";
import {
  TimePeriod,
  LOCK,
  SELECT,
  UNLOCK,
  UPDATE_ALL,
  useHeatingSettings,
} from "../../../context/HeatingContext";

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

export function HeatingSettingsContainer() {
  const fetch = useFetchWithToken();
  const { enqueueSnackbar } = useSnackbar();
  const [getPeriods, setGetPeriods] = React.useState(false);
  const lock = React.useRef(false);

  const { context: heatingContext, dispatch: heatingDispatch } =
    useHeatingSettings();

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
          heatingDispatch({
            type: UPDATE_ALL,
            payload: {
              allPeriods: data.periods,
            },
          });
        }
      })
    );
  }, [fetch, getPeriods, heatingDispatch]);

  const debounceTimeout = React.useRef<Timeout | null>(null);

  const update = React.useCallback(
    async (frozenState) => {
      console.log("engaging lock");
      heatingDispatch({
        type: LOCK,
        payload: {},
      });
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
            setGetPeriods((p) => !p);
          } else if (res.status === 422) {
            res.json().then((resJson: { detail: string | { msg: string } }) => {
              heatingDispatch({
                type: SELECT,
                payload: {
                  period_id: data.period_id,
                },
              });
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
          console.log("freeing lock");
          heatingDispatch({
            type: UNLOCK,
            payload: {},
          });
          console.log("done");
          console.groupEnd();
        });
    },
    [enqueueSnackbar, fetch, heatingDispatch]
  );

  const debounce = React.useCallback(
    (period: TimePeriod | null) => {
      if (heatingContext.lock) return;
      clearTimeout(debounceTimeout.current as Timeout);
      if (period) {
        debounceTimeout.current = setTimeout(() => update(period), 1000);
      }
    },
    [update]
  );

  React.useEffect(() => {
    if (!heatingContext.lock) debounce(heatingContext.selectedPeriod);
  }, [heatingContext.selectedPeriod, debounce]);

  return (
    <>
      <TopBar>
        <BackButton path={"/"} />
        <div />
      </TopBar>
      <div className="heating-settings-container">
        <MuiTimeslotPicker />
        <TimeSlotsDisplay />
        <TemperatureControl />
      </div>
    </>
  );
}
