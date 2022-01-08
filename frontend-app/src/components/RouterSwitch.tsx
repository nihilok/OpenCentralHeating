import * as React from "react";
import { Route, Switch } from "react-router-dom";
import { HeatingSettingsContainer } from "./Heating/HeatingSettings/HeatingSettingsContainer";
import { MainScreen } from "./Heating/MainScreen";
import { HeatingContextProvider } from "../context/HeatingContext";

export default function RouterSwitch() {
  return (
    <Switch>
      <Route exact path="/" component={MainScreen} />
      <HeatingContextProvider>
        <Route exact path="/times" component={HeatingSettingsContainer} />
      </HeatingContextProvider>
    </Switch>
  );
}
