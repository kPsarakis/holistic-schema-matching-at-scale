import React, { Component } from 'react'
import axios from 'axios';

import classes from './Results.css'
import Result from './Result/Result'
import Aux from "../../hoc/Aux";
import Modal from "../../components/UI/Modal/Modal";
import Spinner from "../../components/UI/Spinner/Spinner";

class Results extends Component {

    state = {
        jobs: [],
        loading: true
    }

    componentDidMount() {
        axios({
             method: 'get',
             url: '/api/results/finished_jobs'
        }).then(res => {
            this.setState({loading: false, jobs: res.data})
        }).catch(err => {
            this.setState({loading: false})
            console.log(err)
        })
    }

    deleteJob = (job_id, index) => {
        const jobs = [...this.state.jobs];
        jobs.splice(index, 1);
        this.setState({jobs: jobs, loading: true})
        axios({
             method: 'post',
             url: '/api/results/delete_job/' + job_id
        }).then(() => {
            this.setState({loading: false, rankedList: []})
        }).catch(err => {
            this.setState({loading: false})
            console.log(err)
        })
    }

    render() {
        return (
            <Aux>
                <Modal show={this.state.loading}>
                    <Spinner />
                </Modal>
                <div className={classes.Results}>
                    {this.state.jobs.map((job_id, index) =>
                        (<Result key={job_id} job_id={job_id} deleteJob={() => this.deleteJob(job_id, index)}/>))}
                </div>
            </Aux>
        );
    }
}

export default Results;