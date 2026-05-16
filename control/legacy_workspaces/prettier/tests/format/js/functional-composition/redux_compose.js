import { applyMiddleware, compose, createStore } from "redux";
import thunk from "redux-thunk";
import reducer from "../reducers";
import DevTools from "./containers/DevTools";

const store = createStore(reducer, compose(applyMiddleware(thunk), DevTools.instrument()));
