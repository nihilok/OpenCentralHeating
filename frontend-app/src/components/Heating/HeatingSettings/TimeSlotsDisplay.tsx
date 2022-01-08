import * as React from "react";
import { Box, Tab, Tabs } from "@mui/material";
import { TimePeriod } from "../TimeBlock";

interface Props {
  timeSlots: TimePeriod[];
  choosePeriod: React.Dispatch<any>;
  selected: TimePeriod | null;
  systems: number[];
}

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
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && <Box>{children}</Box>}
    </div>
  );
}

export function TimeSlotsDisplay({ timeSlots, choosePeriod, selected, systems }: Props) {
  const [system, setSystem] = React.useState(selected?.heating_system_id || 3);

  const handleChange = (event: React.SyntheticEvent, newValue: number) => {
    setSystem(newValue + 3);
  };

  const handleClickOnPeriod = (event: React.MouseEvent) => {
    const target = event.target as HTMLElement;
    const systemIndex = [
      parseInt(target.id.split(" ")[0]),
      parseInt(target.id.split(" ")[1]),
    ];
    const period = timeSlots.filter(
      (slot) => slot.heating_system_id === systemIndex[0]
    )[systemIndex[1]];
    choosePeriod(period);
  };

  return (
    <>
      <div
        className={"slots-display-screen"}
      >
        <Tabs
          value={system - 3}
          onChange={handleChange}
          sx={{ margin: "0 auto" }}
        >
          <Tab label="Upstairs" sx={{ color: "white" }} />
          <Tab label="Downstairs" sx={{ color: "white" }} />
        </Tabs>

        {[3, 4].map((mappedSystem, index) => (
          <TabPanel index={index} value={system - 3} key={`${index}-${mappedSystem}`}>
            <ul className="timeslot-list">
              {timeSlots
                .filter((slot) => slot.heating_system_id === mappedSystem)
                .map((slot, indx) => (
                  <li
                    className={selected?.period_id === slot.period_id ? "selected" : ''}
                    onClick={handleClickOnPeriod}
                    key={`${slot.heating_system_id}-${indx}`}
                    id={`${slot.heating_system_id} ${indx}`}
                  >{`${slot.time_on} -> ${slot.time_off}`}</li>
                ))}
            </ul>
          </TabPanel>
        ))}
      </div>
    </>
  );
}
