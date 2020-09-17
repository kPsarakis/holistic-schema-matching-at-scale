import React from "react";

import classes from './Algorithm.css'

const algorithm = (props) => (
    <div className={classes.Algorithm}>
        <h6>{props.algoName}</h6>
    </div>
);

export default algorithm;