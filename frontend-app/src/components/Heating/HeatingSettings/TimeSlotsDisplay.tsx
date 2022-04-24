import * as React from "react";
import { Box, Tab, Tabs } from "@mui/material";
import {
  useHeatingSettings,
  SELECT,
  LOCK,
  UNLOCK,
  SET_SYSTEM,
} from "../../../context/HeatingContext";
import { leftPad } from "../../../lib/helpers";

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tab-panel"
      hidden={value !== index}
      id={`tab-panel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}
    >
      {value === index && <Box>{children}</Box>}
    </div>
  );
}

export function TimeSlotsDisplay() {
  const { heating, dispatch } = useHeatingSettings();

  const [system, setSystem] = React.useState(
    heating.selectedPeriod?.heating_system_id || heating.currentSystem
  );

  const handleChange = (event: React.SyntheticEvent, newValue: number) => {
    setSystem(newValue + 3);
    dispatch({
      type: SET_SYSTEM,
      payload: {
        currentSystem: newValue + 3,
      },
    });
  };

  const handleClickOnPeriod = (event: React.MouseEvent) => {
    dispatch({
      type: LOCK,
      payload: {},
    });
    const target = event.target as HTMLElement;
    const period = heating.allPeriods.filter(
      (slot) => slot.period_id === parseInt(target.id)
    )[0];
    dispatch({
      type: SELECT,
      payload: {
        period_id: period.period_id as number,
      },
    });
  };

  React.useEffect(() => {
    dispatch({
      type: UNLOCK,
      payload: {},
    });
  }, [dispatch, heating.selectedPeriod?.period_id]);

  React.useEffect(() => {
    let currentTime: Date | number = new Date();
    const hours = currentTime.getHours();
    const minutes = currentTime.getMinutes();
    const timeString = `01 Jan 1970 ${leftPad(hours)}:${leftPad(
      minutes
    )}:00 GMT`;
    currentTime = Date.parse(timeString);
    if (heating.allPeriods) {
      const currentPeriod = heating.allPeriods.filter((period) => {
        const periodSplitTimeOn = period.time_on.split(":");
        const periodSplitTimeOff = period.time_off.split(":");
        const timeOnString = `01 Jan 1970 ${leftPad(
          parseInt(periodSplitTimeOn[0])
        )}:${leftPad(parseInt(periodSplitTimeOn[1]))}:00 GMT`;
        const timeOffString = `01 Jan 1970 ${leftPad(
          parseInt(periodSplitTimeOff[0])
        )}:${leftPad(parseInt(periodSplitTimeOff[1]))}:00 GMT`;
        const timeOn = Date.parse(timeOnString);
        const timeOff = Date.parse(timeOffString);
        return (
          period.heating_system_id === heating.currentSystem &&
          timeOn <= currentTime &&
          currentTime < timeOff
        );
      })[0];
      console.log(currentPeriod);
      if (currentPeriod)
        dispatch({
          type: SELECT,
          payload: {
            period_id: currentPeriod.period_id as number,
          },
        });
    }
  }, []);

  return (
    <>
      <div className={"slots-display-screen"}>
        <Tabs
          value={system - 3}
          onChange={handleChange}
          sx={{ margin: "0 auto" }}
        >
          <Tab label="Upstairs" sx={{ color: "white" }} />
          <Tab label="Downstairs" sx={{ color: "white" }} />
        </Tabs>

        {[3, 4].map((mappedSystem, index) => (
          <TabPanel
            index={index}
            value={system - 3}
            key={`${index}-${mappedSystem}`}
          >
            <ul className="timeslot-list">
              {heating.allPeriods
                ? heating.allPeriods
                    .filter((slot) => slot.heating_system_id === mappedSystem)
                    .map((slot, indx) => (
                      <li
                        className={
                          heating.selectedPeriod?.period_id === slot.period_id
                            ? "selected"
                            : ""
                        }
                        onClick={handleClickOnPeriod}
                        key={`${slot.heating_system_id}-${indx}`}
                        id={`${slot.period_id}`}
                      >{`${slot.time_on} -> ${slot.time_off}`}</li>
                    ))
                : ""}
            </ul>
          </TabPanel>
        ))}
      </div>
    </>
  );
}
