import React, { Component } from 'react'
import axios from 'axios';

import classes from './Results.css'
import Result from './Result/Result'
import Aux from "../../hoc/Aux";
import Modal from "../../components/UI/Modal/Modal";
import Spinner from "../../components/UI/Spinner/Spinner";
import Button from "@material-ui/core/Button";
import {List} from "react-virtualized";

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

    renderRow({ index, key, style }) {
        return (
            <div key={key} style={style} className={classes.Row}>
                <div className={classes.Content}>
                    <Result key={this.state.jobs[index]} job_id={this.state.jobs[index]} />
                    <Button variant="contained" color="primary" onClick={() => this.deleteMatchHandler(index, true)}>Verify Match</Button>
                    <Button color="secondary" onClick={() => this.deleteMatchHandler(index, false)}>Discard Match</Button>
                </div>
            </div>
        );
    }

    render() {
        return (
            <Aux>
                <Modal show={this.state.loading}>
                    <Spinner />
                </Modal>
                <div className={classes.List}>
                    <List
                    width={1400}
                    height={800}
                    rowHeight={80}
                    rowRenderer={this.renderRow.bind(this)}
                    rowCount={this.state.jobs.length} />
                </div>
            </Aux>
        );
    }
}

export default Results;