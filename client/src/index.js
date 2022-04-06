const App = require("./components/App.js");
import "./index.scss";

const $app = document.getElementsByClassName("app")[0];
const app = new App($app);
app.$render();

const wsURL =
  process.env.NODE_ENV === "production"
    ? "ws://dadescomunals.tk/hemeroteca-oberta/ws"
    : "ws://localhost:8000/ws";
