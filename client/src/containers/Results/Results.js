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
             url: 'http://127.0.0.1:5000/results/finished_jobs'
        }).then(res => {
            this.setState({loading: false, jobs: res.data})
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
                    {this.state.jobs.map(job_id => (<Result key={job_id} job_id={job_id} />))}
                </div>
            </Aux>
        );
    }
}

export default Results;