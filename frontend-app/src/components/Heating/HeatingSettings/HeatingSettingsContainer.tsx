import * as React from "react";
import { TimePeriod } from "../TimeBlock";
import "./heating-settings.css";

interface Props {
  currentSystem: number;
}

interface IContainerState {
  currentSystem: number;
  selectedPeriod: TimePeriod | null;
  allPeriods: TimePeriod[];
}

export function HeatingSettingsContainer({ currentSystem }: Props) {
  const [containerState, setContainerState] = React.useState<IContainerState>({
    currentSystem,
    selectedPeriod: null,
    allPeriods: [],
  });

  const debounceTimeout = React.useRef<ReturnType<typeof setTimeout> | null>(
    null
  );

  const debounce = React.useCallback((period: TimePeriod | null) => {
    function fetchUpdate(period: TimePeriod) {}
    clearTimeout(debounceTimeout.current as ReturnType<typeof setTimeout>);
    if (period) {
      debounceTimeout.current = setTimeout(
        () => fetchUpdate(period),
        1000
      );
    }
  }, []);

  React.useEffect(() => {
    if (containerState.selectedPeriod) {
      debounce(containerState.selectedPeriod);
    }
  }, [debounce, containerState.selectedPeriod]);

  return <div className="heating-settings"></div>;
}
