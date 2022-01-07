import * as React from "react";
import { Route, Switch } from "react-router-dom";
import { HeatingSettingsContainer } from "./Heating/HeatingSettings/HeatingSettingsContainer";
import { SettingsForm } from "./Heating/SettingsForm";

export default function RouterSwitch() {
  return (
    <Switch>
      <Route exact path="/" component={SettingsForm} />
      <Route exact path="/times" component={HeatingSettingsContainer} />
    </Switch>
  );
}
