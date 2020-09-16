import React, { Component } from 'react';

import Aux from '../../hoc/Aux';
import JobRequest from './JobRequest/JobRequest'
import ListSource from './ListSource/ListSource'
import classes from './Matcher.css'

class Matcher extends Component {
    render() {
        return(
            <Aux>
                <div className={classes.DbList}>
                    <ListSource header={"Select Source Tables"}/>
                </div>
                <div className={classes.DbList}>
                    <ListSource header={"Select Target Tables"}/>
                </div>
                <div>
                    <JobRequest/>
                </div>
            </Aux>
        );
    }
}

export default Matcher;