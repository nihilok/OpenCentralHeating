import React from 'react';
import GaugeChart from 'react-gauge-chart'


interface Props {
  pressure: number;
}

function PressureGauge({pressure}: Props) {

  const minMax = {
    min: 900,
    max: 1100
  }

  const range = minMax.max - minMax.min

  const percentCalc = React.useCallback((p: number) => {
    const position = p - minMax.min
    return position / range
  }, [minMax.min, range])

  const reversePercent = React.useCallback((p: number) => {
    if (p < 1) {
      return p * range + minMax.min
    } else {
      return (p / 100 * range) + minMax.min
    }
  }, [minMax.min, range])

  const [percent, setPercent] = React.useState(() => percentCalc(pressure))

  React.useEffect(() => {
    setPercent(percentCalc(pressure))
  }, [percentCalc, pressure])

  const formatTextValue = React.useCallback((value: string) => {
    const p = reversePercent(parseInt(value))
    return p + ' hPa'
  }, [reversePercent])

  return (
    <GaugeChart id="pressure" percent={percent} nrOfLevels={30} colors={["#FF5F6D"]} arcWidth={0.3}
                formatTextValue={formatTextValue} animate={false} style={{height: '9rem'}}/>
  );
}

export default PressureGauge;