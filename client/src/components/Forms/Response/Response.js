import React from "react";

import Aux from '../../../hoc/Aux';

const response = (props) => {
    return(
        <Aux>
            <h3>Response</h3>
            <p>Job {props.response} received from server</p>
        </Aux>
    );
};

export default response;