import React from 'react'

import classes from './Result.css'

const result = (props) => (
    <div className={classes.Result}>
        <p>Job with id {props.job_id}</p>
    </div>
);

export default result;
