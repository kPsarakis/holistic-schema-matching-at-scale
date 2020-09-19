import React, { Component } from 'react';

import Aux from '../../hoc/Aux';
import ListSource from './ListSource/ListSource'
import AlgorithmSelection from './AlgorithmSelection/AlgorithmSelection'
import classes from './Matcher.css'
import {Button} from "@material-ui/core";

class Matcher extends Component {

    state = {
        sourceSelectedTables: [],
        targetSelectedTables: [],
        selectedAlgorithms: []
    }

    getSelectedTables(val, mode){
        if(mode==="source"){
            this.setState({sourceSelectedTables: [...val]})
        }else if(mode==="target") {
            this.setState({targetSelectedTables: [...val]})
        }else if(mode==="algorithms"){
            this.setState({selectedAlgorithms: [...val]})
        }
    }

    sendJob = () => {
        console.log("Submit")
        console.log("Source", this.state.sourceSelectedTables)
        console.log("Target", this.state.targetSelectedTables)
        console.log("Algorithms", this.state.selectedAlgorithms)
    }

    render() {
        return(
            <Aux>
                <div className={classes.DbList}>
                    <ListSource
                        header={"Select Source Tables"}
                        sendSelected={(val) => this.getSelectedTables(val, "source")}
                    />
                </div>
                <div className={classes.DbList}>
                    <ListSource
                        header={"Select Target Tables"}
                        sendSelected={(val) => this.getSelectedTables(val, "target")}
                    />
                </div>
                <div className={classes.AlgorithmSelection}>
                    <AlgorithmSelection
                        sendSelected={(val) => this.getSelectedTables(val, "algorithms")}
                    />
                </div>
                <div className={classes.submitButtonFooter}>
                    <Button className={classes.submitButton} variant="contained" color="primary" onClick={this.sendJob}>
                        SUBMIT JOB
                    </Button>
                </div>
            </Aux>
        );
    }
}

export default Matcher;