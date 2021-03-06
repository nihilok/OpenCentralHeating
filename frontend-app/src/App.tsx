import * as React from "react";
import useAuthContext from "./context/AuthContext";
import RouterSwitch from "./components/RouterSwitch";
import LoginForm from "./components/Login/LoginForm";

export default function App() {
  const { context } = useAuthContext();
  return context.isAuthenticated ? <RouterSwitch /> : <LoginForm />;
}
