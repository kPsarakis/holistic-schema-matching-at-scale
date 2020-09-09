import React, { Component } from 'react'
import axios from 'axios';

import classes from './Results.css'
import Result from './Result/Result'
import Aux from "../../hoc/Aux";
import Modal from "../../components/UI/Modal/Modal";
import Spinner from "../../components/UI/Spinner/Spinner";
import {TableContainer} from "@material-ui/core";
import TablePagination from "@material-ui/core/TablePagination";
import Paper from "@material-ui/core/Paper";
import Table from "@material-ui/core/Table";
import TableBody from "@material-ui/core/TableBody";

class Results extends Component {

    state = {
        page: 0,
        rowsPerPage: 5,
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

    handleChangePage = (event, newPage) => {
        this.setState({page: newPage});
    };

    handleChangeRowsPerPage = (event) => {
        this.setState({rowsPerPage: +event.target.value});
        this.setState({page: 0});
    };

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
                <Paper className={classes.Root}>
                    <TableContainer className={classes.Container}>
                        <Table className={classes.Results}>
                            <TableBody>
                                {this.state.jobs.slice(this.state.page * this.state.rowsPerPage, this.state.page * this.state.rowsPerPage + this.state.rowsPerPage)
                                    .map((job_id, index) =>
                                        (<Result key={index} job_id={job_id} deleteJob={() => this.deleteJob(job_id, index)}/>))}
                            </TableBody>
                        </Table>
                        <TablePagination
                                rowsPerPageOptions={[5, 10, 25]}
                                component="div"
                                count={this.state.jobs.length}
                                rowsPerPage={this.state.rowsPerPage}
                                page={this.state.page}
                                onChangePage={this.handleChangePage}
                                onChangeRowsPerPage={this.handleChangeRowsPerPage}
                        />
                    </TableContainer>
                </Paper>
            </Aux>
        );
    }
}

export default Results;