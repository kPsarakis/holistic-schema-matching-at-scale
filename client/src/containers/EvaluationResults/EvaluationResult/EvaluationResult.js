import React, {Component} from "react";
import Aux from "../../../hoc/Aux";
import Modal from "../../../components/UI/Modal/Modal";
import Spinner from "../../../components/UI/Spinner/Spinner";
import classes from "./EvaluationResult.module.css";
import Button from "@material-ui/core/Button";
import GetAppIcon from "@material-ui/icons/GetApp";
import BarChartIcon from '@material-ui/icons/BarChart';
import TestFigure from "../../../assets/Unionable-all-1.png";
import {TableContainer} from "@material-ui/core";
import Table from "@material-ui/core/Table";
import TableBody from "@material-ui/core/TableBody";
import TableFooter from "@material-ui/core/TableFooter";
import TableRow from "@material-ui/core/TableRow";
import TablePagination from "@material-ui/core/TablePagination";


class EvaluationResult extends Component {

    state = {
        loading: false,
        page: 0,
        rowsPerPage: 5,
    }

    downloadDataset = (fabricatedPairId) => {

    }

    showSpuriousResults = () => {

    }

    handleChangePage = (event, newPage) => {
        this.setState({page: newPage});
    };

    handleChangeRowsPerPage = (event) => {
        this.setState({rowsPerPage: +event.target.value});
        this.setState({page: 0});
    };

    render() {
        return(
            <Aux>
                <Modal show={this.state.loading}>
                    <Spinner />
                </Modal>
                <div className={classes.Parent}>
                    <TableContainer className={classes.Container}>
                        <Table className={classes.Results}>
                            <TableBody>
                                {this.props.pairIds.slice(this.state.page * this.state.rowsPerPage,
                                    this.state.page * this.state.rowsPerPage + this.state.rowsPerPage)
                                    .map((datasetId) => {
                                        return (<div className={classes.FabricatedPair}>
                                                    <p>Fabricated pair: {datasetId}</p>
                                                    <Button
                                                        style={{
                                                            borderRadius: 10,
                                                            color: "#016b9f",
                                                            padding: "10px 10px",
                                                            fontSize: "8px"
                                                        }}
                                                        onClick={() => this.downloadDataset(datasetId)}>
                                                        <GetAppIcon/>
                                                    </Button>
                                                    <Button
                                                        style={{
                                                            borderRadius: 10,
                                                            color: "white",
                                                            padding: "10px 10px",
                                                            marginLeft: "10px",
                                                            fontSize: "10px",
                                                            background: "#71100f"
                                                        }}
                                                        onClick={() => this.showSpuriousResults(datasetId)}>
                                                        Show Spurious Results
                                                    </Button>
                                                </div>);
                                        }
                                    )
                                }
                            </TableBody>
                            <TableFooter>
                                <TableRow>
                                    <div className={classes.Pagination}>
                                        <TablePagination
                                        rowsPerPageOptions={[5, 10, 25]}
                                        component="div"
                                        count={this.props.pairIds.length}
                                        rowsPerPage={this.state.rowsPerPage}
                                        page={this.state.page}
                                        onChangePage={this.handleChangePage}
                                        onChangeRowsPerPage={this.handleChangeRowsPerPage}
                                        />
                                    </div>
                                </TableRow>
                            </TableFooter>
                        </Table>
                    </TableContainer>
                </div>
            </Aux>
        );
    }

}

export default EvaluationResult;