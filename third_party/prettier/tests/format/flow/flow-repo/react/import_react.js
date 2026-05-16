/* @flow */

import react, { Component } from "react";

var a: Component<*,*,*> = new react.Component();
var b: number = new react.Component(); // Error: ReactComponent ~> number
