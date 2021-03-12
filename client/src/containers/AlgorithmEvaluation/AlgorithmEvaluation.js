import React, {Component} from "react";
import Aux from "../../hoc/Aux";
import classes from "./AlgorithmEvaluation.module.css";
import {Button} from "@material-ui/core";
import FabricatedDatasets from "./FabricatedDatasets/FabricatedDatasets";
import AlgorithmSelection from "../Matcher/AlgorithmSelection/AlgorithmSelection";


class AlgorithmEvaluation extends Component {

    state = {
        selectedDataset: null
    }

    getSelectedDataset = (val) => {
        this.setState({selectedDataset: val})
    }

    render() {
        console.log(this.state.selectedDataset)
        return (
            <Aux>
                <div className={classes.fabDataList}>
                    <FabricatedDatasets
                        sendSelected={(val) => this.getSelectedDataset(val)}
                        />
                </div>
                <div className={classes.AlgorithmSelection}>
                    <AlgorithmSelection />
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

export default AlgorithmEvaluation;
