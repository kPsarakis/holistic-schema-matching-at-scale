import React, { Component } from 'react';

import Aux from '../../hoc/Aux';
import JobRequest from './JobRequest/JobRequest'

class Matcher extends Component {
    render() {
        return(
            <Aux>
                <JobRequest />
            </Aux>
        );
    }
}

export default Matcher;