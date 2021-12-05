import * as React from "react";
import "./heating.css";
import classNames from "classnames";
import { StyledTooltip } from "../Custom/StyledTooltip";
import { TEMPERATURE_INTERVAL } from "../../constants/constants";
import { useFetchWithToken } from "../../hooks/FetchWithToken";
import { checkResponse } from "../../lib/helpers";
import { FullScreenLoader } from "../Loaders/FullScreenLoader";
import { FullScreenComponent } from "../Custom/FullScreenComponent";
import { WeatherButton } from "../WeatherButton/WeatherButton";
import { Barometer } from "../Barometer/Barometer";
import { TopBar } from "../Custom/TopBar";
import { TimePeriod } from "./TimeBlock";
import { ProgramOnOffSwitch } from "./ProgramOnOffSwitch";
import {SettingsButton} from "../IconButtons/SettingsButton";

interface Sensors {
  temperature: number;
  pressure: number;
  humidity: number;
}

export interface APIResponse {
  sensor_readings: Sensors;
  relay_on: boolean;
  program_on: boolean;
  target: number;
}

export function SettingsForm() {

  const fetch = useFetchWithToken();
  const [readings, setReadings] = React.useState({
    temperature: 0,
    pressure: 0,
    humidity: 0,
  });
  const [isLoading, setIsLoading] = React.useState(true);
  const [helpMode, setHelpMode] = React.useState(false);
  const [currentTemp, setCurrentTemp] = React.useState<number>();
  const [relayOn, setRelayOn] = React.useState(false);
  const [programOn, setProgramOn] = React.useState(false);
  const [target, setTarget] = React.useState(20);
  const [systemId, setSystemId] = React.useState(3);

  const handleSystemChange = () => {
    if (systemId === 3) setSystemId(4);
    else setSystemId(3);
  };

  const parseData = React.useCallback((data: APIResponse) => {
    checkResponse(data.sensor_readings, setReadings);
    checkResponse(data.program_on, setProgramOn);
    checkResponse(data.target, setTarget);
    checkResponse(data.sensor_readings.temperature, setCurrentTemp);
    checkResponse(data.relay_on, setRelayOn);
  }, []);

  const getInfo = React.useCallback(async () => {
    fetch(`/v2/heating?system_id=${systemId}`).then((res) =>
      res.json().then((data: APIResponse) => {
        if (res.status !== 200) {
          console.log(data);
          return;
        }
        parseData(data);
      }).finally(()=>setIsLoading(false))
    );
  }, [fetch, parseData, systemId]);

  React.useEffect(() => {
    getInfo().catch((error) => console.log(error));
  }, [systemId, getInfo]);

  React.useEffect(() => {
    let interval = setInterval(getInfo, TEMPERATURE_INTERVAL);
    return () => clearInterval(interval);
  }, [fetch, parseData, getInfo]);

  return (
    <FullScreenComponent>
      <TopBar>
        <WeatherButton />
        <SettingsButton helpMode={helpMode} setHelpMode={setHelpMode} />
      </TopBar>
      <form className="heating-settings">
        {isLoading ? (
          <FullScreenLoader />
        ) : (
          <>
            <button type="button" onClick={handleSystemChange}>
              {systemId === 3 ? "Upstairs:" : "Downstairs:"}
            </button>
            <div className="flex flex-col space-evenly">
              <div>
                <p>Target: {target}&deg;C</p>
                {currentTemp && (
                  <StyledTooltip
                    title={`Indoor Temperature. Relay is currently ${
                      relayOn ? "on" : "off"
                    }`}
                    placement="top"
                    disabled={!helpMode}
                  >
                    <h1
                      className={classNames("TempDisplay", {
                        TempDisplay__On: relayOn,
                      })}
                    >
                      {readings.temperature.toFixed(1)}&deg;C
                    </h1>
                  </StyledTooltip>
                )}
              </div>
              <Barometer readings={readings} />
            </div>
          </>
        )}
      </form>
      <ProgramOnOffSwitch
        state={programOn}
        systemId={systemId}
        parseResponse={parseData}
      />
    </FullScreenComponent>
  );
}
