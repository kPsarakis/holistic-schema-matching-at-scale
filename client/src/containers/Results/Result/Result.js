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
                 url: '/api/results/job_results/' + this.props.job_id
            }).then(res => {
                this.setState({loading: false, rankedList: res.data, showRankedList: true})
            }).catch(err => {
                this.setState({loading: false})
                console.log(err)
            })
        }
    }

    deleteJob = () => {
        this.setState({loading: true})
        axios({
             method: 'post',
             url: '/api/results/delete_job/' + this.props.job_id
        }).then(() => {
            this.setState({loading: false, rankedList: []})
        }).catch(err => {
            this.setState({loading: false})
            console.log(err)
        })
    }

    render() {
        const renderedList = this.state.showRankedList ? <MatchList rankedList={this.state.rankedList} jobId={this.props.job_id}/> : null;
        return (
            <Aux>
                <Modal show={this.state.loading}>
                    <Spinner />
                </Modal>
                <div className={classes.Result}>
                    <p>Job with id {this.props.job_id}</p>
                    <Button variant="outlined" color="primary" onClick={this.toggleRankedList}>Show/hide matches</Button>
                    <Button variant="outlined" color="secondary" onClick={this.deleteJob}>Delete job</Button>
                    {renderedList}
                </div>
            </Aux>
        );
    }
}

export default Result;