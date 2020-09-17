import React, { Component } from 'react';

import Aux from '../../hoc/Aux';
import ListSource from './ListSource/ListSource'
import AlgorithmSelection from './AlgorithmSelection/AlgorithmSelection'
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
                <div className={classes.AlgorithmSelection}>
                    <AlgorithmSelection />
                </div>
            </Aux>
        );
    }
}

export default Matcher;