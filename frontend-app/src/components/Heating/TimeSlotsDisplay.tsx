import * as React from "react";
import { Box, Tab, Tabs } from "@mui/material";

interface Props {
  timeSlots: number[];
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
      {value === index && (
        <Box>
          {children}
        </Box>
      )}
    </div>
  );
}


export function TimeSlotsDisplay({ timeSlots }: Props) {
  const [system, setSystem] = React.useState(1);

  const handleChange = (event: React.SyntheticEvent, newValue: number) => {
    setSystem(newValue);
  };

  return (
    <>
      <div style={{display: "flex", flexDirection: "column", background: 'rgba(0, 0, 0, 0.3)', borderRadius: '5px', boxShadow: 'inset 0 0 10px rgba(0, 15, 0, 0.9)'}}>
        <Tabs
          value={system}
          onChange={handleChange}
          sx={{margin: '0 auto'}}
        >
          <Tab label="Upstairs" sx={{color: 'white'}}/>
          <Tab label="Downstairs" sx={{color: 'white'}}/>
        </Tabs>
        <TabPanel index={0} value={system}>
        <ul className="timeslot-list">
          <li>{"20:00 -> 21:00"}</li>
          <li>{"20:00 -> 21:00"}</li>
          <li>{"20:00 -> 21:00"}</li>
          <li>{"20:00 -> 21:00"}</li>
        </ul>
        </TabPanel>
        <TabPanel index={1} value={system}>
        <ul className="timeslot-list">
          <li>{"06:00 -> 08:00"}</li>
          <li>{"13:00 -> 16:00"}</li>
          <li>{"18:00 -> 19:30"}</li>
        </ul>
        </TabPanel>
      </div>
    </>
  );
}
