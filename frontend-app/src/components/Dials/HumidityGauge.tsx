import React from "react";
import GaugeChart from "react-gauge-chart";
interface Props {
  humidity: number;
}

function HumidityGauge({ humidity }: Props) {
  return (
    <div className="gauge-container">
      <GaugeChart
        id="gauge-chart2"
        percent={humidity}
        nrOfLevels={30}
        colors={["#6C4FF3"]}
        arcWidth={0.3}
        animate={false}
        className="gauge-chart"
      />
      <p>Humidity</p>
    </div>
  );
}

export default HumidityGauge;
