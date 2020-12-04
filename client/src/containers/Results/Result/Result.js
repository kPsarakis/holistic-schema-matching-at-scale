import React, {Component} from 'react'

import classes from './Result.css'
import axios from "axios";
import MatchList from "../MatchList/MatchList";
import Aux from '../../../hoc/Aux'
import Button from "@material-ui/core/Button";
import Spinner from "../../../components/UI/Spinner/Spinner";
import Modal from "../../../components/UI/Modal/Modal";


class Result extends Component{

    state = {
        loading: false,
        rankedList: [],
        showRankedList: false
    }

    toggleRankedList = () => {
        if(this.state.showRankedList){
            this.setState({showRankedList: false})
        }else if(this.state.rankedList.length !== 0){
            this.setState({showRankedList: true})
        }else{
            this.setState({loading: true})
            axios({
                 method: 'get',
                 url: process.env.REACT_APP_SERVER_ADDRESS + '/results/job_results/' + this.props.job_id
            }).then(res => {
                this.setState({loading: false, rankedList: res.data, showRankedList: true})
            }).catch(err => {
                this.setState({loading: false})
                console.log(err)
            })
        }
    }

    render() {
        const renderedList = this.state.showRankedList ? <MatchList rankedList={this.state.rankedList} jobId={this.props.job_id}/> : null;
        const splitJobId = this.props.job_id.split("_")
        const id = splitJobId[0]
        const algorithmName = splitJobId[1]
        return (
            <Aux>
                <Modal show={this.state.loading}>
                    <Spinner />
                </Modal>
                <div className={classes.Result}>
                    <p>Job: {id}</p>
                    <p>Algorithm: {algorithmName}</p>
                    <Button variant="contained" color="primary" onClick={this.toggleRankedList}>Show/hide matches</Button>
                    <Button color="secondary" onClick={this.props.deleteJob}>Delete job</Button>
                    {renderedList}
                </div>
            </Aux>
        );
    }
}

export default Result;