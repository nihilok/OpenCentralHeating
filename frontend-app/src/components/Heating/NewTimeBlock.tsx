import * as React from 'react';
import {TimePeriod} from './TimeBlock';
import {MuiTimeslotPicker} from "./MuiTimeslotPicker";
import {TimeSlotsDisplay} from "./TimeSlotsDisplay";
import {TemperatureControl} from "./TemperatureControl";

interface Props {
  timePeriods: TimePeriod[];
  systems: number[];
}

export function NewTimeBlock({timePeriods, systems}: Props) {
  const [selectedPeriod, setSelectedPeriod] = React.useState<TimePeriod | undefined>(undefined)

  return (
    <div className="time-block__grid">
      <MuiTimeslotPicker timePeriod={selectedPeriod} setter={setSelectedPeriod}/>
      <div className="time-block-right__grid">
        <TimeSlotsDisplay timeSlots={timePeriods} systems={systems} choosePeriod={setSelectedPeriod} selected={selectedPeriod as TimePeriod}/>
        <TemperatureControl timeSlot={selectedPeriod} setValue={setSelectedPeriod}/>
      </div>
    </div>
  );
}