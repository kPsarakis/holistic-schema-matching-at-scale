import React, {Component} from "react";
import Aux from "../../hoc/Aux";
import Modal from "../../components/UI/Modal/Modal";
import Spinner from "../../components/UI/Spinner/Spinner";
import classes from "./EvaluationResults.module.css";
import Paper from "@material-ui/core/Paper";
import {TableContainer} from "@material-ui/core";
import Table from "@material-ui/core/Table";
import TableBody from "@material-ui/core/TableBody";
import TablePagination from "@material-ui/core/TablePagination";
import axios from "axios";
import EvaluationResult from "./EvaluationResult/EvaluationResult";


class EvaluationResults extends Component {

    state = {
        evaluationResults: {"Job1": ["fabricated1", "fabricated2"], "Job2": ["fabricated1", "fabricated2"]},
        page: 0,
        rowsPerPage: 5,
        loading: false
    }

    componentDidMount() {
        this.setState({loading: true})
        axios({
             method: "get",
             url: process.env.REACT_APP_SERVER_ADDRESS + "/valentine/results/get_evaluation_results"
        }).then(res => {
            this.setState({loading: false, evaluationResults: res.data});
        }).catch(err => {
            this.setState({loading: false});
            console.log(err);
        })
    }

    handleChangePage = (event, newPage) => {
        this.setState({page: newPage});
    };

    handleChangeRowsPerPage = (event) => {
        this.setState({rowsPerPage: +event.target.value});
        this.setState({page: 0});
    };

    render() {
        return (
            <Aux>
                <Modal show={this.state.loading}>
                    <Spinner />
                </Modal>
                <div className={classes.Parent}>
                    <Paper className={classes.Root}>
                        <TableContainer className={classes.Container}>
                            <Table className={classes.Results}>
                                <TableBody>
                                    {Object.keys(this.state.evaluationResults).slice(this.state.page * this.state.rowsPerPage,
                                        this.state.page * this.state.rowsPerPage + this.state.rowsPerPage)
                                        .map((datasetId) => {
                                            return (<div className={classes.Result}>
                                                        <p className={classes.Paragraph}>Job: {datasetId}</p>
                                                        {this.state.evaluationResults[datasetId].map((fabricatedPairId) => {
                                                            return (
                                                                <EvaluationResult fabricatedPairId={fabricatedPairId}/>
                                                            );
                                                        })}
                                                    </div>);
                                            }
                                        )
                                    }
                                </TableBody>
                            </Table>
                            <TablePagination
                                rowsPerPageOptions={[5, 10, 25]}
                                component="div"
                                count={Object.keys(this.state.evaluationResults).length}
                                rowsPerPage={this.state.rowsPerPage}
                                page={this.state.page}
                                onChangePage={this.handleChangePage}
                                onChangeRowsPerPage={this.handleChangeRowsPerPage}
                            />
                        </TableContainer>
                    </Paper>
                </div>
            </Aux>
        );
    }

}

export default EvaluationResults;