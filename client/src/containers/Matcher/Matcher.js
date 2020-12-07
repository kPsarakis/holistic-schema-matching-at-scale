import React, { Component } from "react";

import Aux from "../../hoc/Aux";
import ListSource from "./ListSource/ListSource";
import AlgorithmSelection from "./AlgorithmSelection/AlgorithmSelection";
import classes from "./Matcher.module.css";
import {Button} from "@material-ui/core";
import axios from "axios";
import Modal from "../../components/UI/Modal/Modal";
import Spinner from "../../components/UI/Spinner/Spinner";
import Response from "../../components/Forms/Response/Response";

class Matcher extends Component {

    state = {
        sourceSelectedTables: [],
        targetSelectedTables: [],
        selectedAlgorithms: [],
        loading: false,
        responseReceived: false,
        latestResponse: ""
    }

    getSelectedTables(val, mode){
        if(mode==="source"){
            this.setState({sourceSelectedTables: [...val]});
        }else if(mode==="target") {
            this.setState({targetSelectedTables: [...val]});
        }else if(mode==="algorithms"){
            this.setState({selectedAlgorithms: [...val]});
        }
    }

    sendJob = () => {
        if(this.state.sourceSelectedTables.length === 0){
            alert("No selected tables for source!");
            return;
        }
        if(this.state.targetSelectedTables.length === 0){
            alert("No selected tables for target!");
            return;
        }
        if(this.state.selectedAlgorithms.length === 0){
            alert("No selected algorithms!");
            return;
        }
        this.setState({loading: true});
        const requestBody = {
            "source_tables": this.state.sourceSelectedTables,
            "target_tables": this.state.targetSelectedTables,
            "algorithms": this.state.selectedAlgorithms
        };
        axios({
          method: "post",
          url:  process.env.REACT_APP_SERVER_ADDRESS + "/matches/minio/submit_batch_job",
          headers: {},
          data: requestBody})
            .then(response => {this.setState({loading: false, responseReceived: true, latestResponse: response.data});})
            .catch(error => {this.setState( {loading: false} ); console.log(error);})
    }

    closeResponseHandler = () => {
        this.setState({responseReceived: false})
    }

    render() {
        return(
            <Aux>
                <Modal show={this.state.loading}>
                    <Spinner />
                </Modal>
                <Modal show={this.state.responseReceived} modalClosed={this.closeResponseHandler}>
                    <Response response={this.state.latestResponse}/>
                </Modal>
                <div className={classes.DBView}>
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