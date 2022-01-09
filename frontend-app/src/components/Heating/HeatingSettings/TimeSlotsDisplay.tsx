import * as React from "react";
import { Box, Tab, Tabs } from "@mui/material";
import {
  useHeatingSettings,
  SELECT,
  LOCK,
  UNLOCK, SET_SYSTEM,
} from "../../../context/HeatingContext";

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
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
