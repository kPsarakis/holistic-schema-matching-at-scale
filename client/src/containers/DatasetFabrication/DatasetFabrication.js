import React, {Component} from "react";
import classes from "./DatasetFabrication.module.css";
import {Button} from "@material-ui/core";
import Aux from "../../hoc/Aux";
import UploadDataset from "./UploadDataset/UploadDataset";
import FabricationParameters from "./FabricationParameters/FabricationParameters";


class DatasetFabrication extends Component {

    state = {
        loading: false
    }

    sendJob = () => {}


    render() {
        return (
            <Aux>
                <div className={classes.selectFile}>
                    <UploadDataset/>
                </div>
                <div className={classes.FabricationMethods}>
                    <h5>Select Fabrication Variant(s)</h5>
                    <FabricationParameters/>
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

export default DatasetFabrication;