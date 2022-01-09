import * as React from "react";

export interface TimePeriod {
  time_on: string;
  time_off: string;
  target: number;
  period_id?: number;
  heating_system_id: number;
}

interface IHeatingContext {
  lock: boolean;
  revert: boolean;
  currentSystem: number;
  selectedPeriod: TimePeriod | null;
  allPeriods: TimePeriod[];
  systems: number[];
}

export const LOCK = "LOCK";
export const UNLOCK = "UNLOCK";
export const SELECT = "SELECT";
export const SET_SYSTEM = "SET_SYSTEM";
export const UPDATE_TIMES = "UPDATE_TIMES";
export const UPDATE_TEMPERATURE = "UPDATE_TEMPERATURE";
export const UPDATE_ALL = "UPDATE_ALL";
export const NEW_PERIOD = "NEW_PERIOD"; // TODO: not yet implemented
export const DELETE_PERIOD = "DELETE_PERIOD"; // TODO: not yet implemented

interface Payload {
  period_id?: number;
  time_on?: string;
  time_off?: string;
  target?: number;
  allPeriods?: TimePeriod[];
  currentSystem?: number;
}

type Action =
  | { type: typeof LOCK; payload: Payload }
  | { type: typeof UNLOCK; payload: Payload }
  | { type: typeof SELECT; payload: Payload }
  | { type: typeof SET_SYSTEM; payload: Payload }
  | { type: typeof UPDATE_TIMES; payload: Payload }
  | { type: typeof UPDATE_TEMPERATURE; payload: Payload }
  | { type: typeof UPDATE_ALL; payload: Payload }
  | { type: typeof NEW_PERIOD; payload: Payload }
  | { type: typeof DELETE_PERIOD; payload: Payload };

interface ContextWithReducer {
  heating: IHeatingContext;
  dispatch: React.Dispatch<Action>;
}

const initialContext = {
  lock: false,
  revert: false,
  currentSystem: 3,
  selectedPeriod: null,
  allPeriods: [],
  systems: [],
};

const defaultValue = {
  heating: initialContext,
  dispatch: () => initialContext,
};

const HeatingContext = React.createContext<ContextWithReducer>(defaultValue);

const reducer = (state: IHeatingContext, { payload, type }: Action) => {
  switch (type) {
    case SELECT:
      return {
        ...state,
        selectedPeriod: state.allPeriods.filter(
          (p) => p.period_id === payload.period_id
        )[0],
        revert: !state.revert,
      };
    case SET_SYSTEM:
      return {
        ...state,
        currentSystem: payload.currentSystem,
      };
    case UPDATE_TIMES:
      return {
        ...state,
        selectedPeriod: {
          ...state.selectedPeriod,
          time_on: payload.time_on,
          time_off: payload.time_off,
        },
      };
    case UPDATE_TEMPERATURE:
      return {
        ...state,
        selectedPeriod: { ...state.selectedPeriod, target: payload.target },
      };
    case UPDATE_ALL:
      console.log(payload.allPeriods);
      return {
        ...state,
        allPeriods: payload.allPeriods,
      };
    case LOCK:
      return {
        ...state,
        lock: true,
      };
    case UNLOCK:
      return {
        ...state,
        lock: false,
      };
    default:
      return state;
  }
};

export const HeatingContextProvider: React.FC = ({ children }) => {
  const [heating, dispatch] = React.useReducer(reducer, defaultValue as never);

  return (
    <HeatingContext.Provider value={{ heating, dispatch }}>
      {children}
    </HeatingContext.Provider>
  );
};

export const useHeatingSettings = () => {
  return React.useContext(HeatingContext);
};
