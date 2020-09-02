import React, { Component } from 'react'
import axios from 'axios';

import classes from './Results.css'
import Result from './Result/Result'


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
            console.log(res.data)
            this.setState({loading: false, jobs: ['1']})
        }).catch(err => {
            this.setState({loading: false})
            console.log(err)
        })
    }

    render() {
        return (
            <div className={classes.Results}>
                {this.state.jobs.map(job => (
                    <Result
                        key={job}
                        job_id={job} />
                ))}
            </div>
        );
    }
}

export default Results;