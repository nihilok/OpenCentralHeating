import * as React from 'react';
import {TimePeriod} from './TimeBlock';
import {MuiTimeslotPicker} from "./MuiTimeslotPicker";
import {TimeSlotsDisplay} from "./TimeSlotsDisplay";
import {TemperatureControl} from "./TemperatureControl";

interface Props {
  timePeriod?: TimePeriod;
}

export function NewTimeBlock({timePeriod}: Props) {
  const [temperature, setTemperature] = React.useState(20)

  return (
    <div className="time-block__grid">
      <MuiTimeslotPicker timePeriod={timePeriod}/>
      <div className="time-block-right__grid">
        <TimeSlotsDisplay timeSlots={[1, 2]}/>
        <TemperatureControl value={temperature} setValue={setTemperature}/>
      </div>
    </div>
  );
}