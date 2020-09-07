import React, {Component} from "react";
import Button from '@material-ui/core/Button';
import axios from "axios";

import classes from './MatchList.css';
import Modal from "../../../components/UI/Modal/Modal";
import Spinner from "../../../components/UI/Spinner/Spinner";
import Aux from "../../../hoc/Aux";
import Paper from "@material-ui/core/Paper";
import TableContainer from "@material-ui/core/TableContainer";
import TablePagination from "@material-ui/core/TablePagination";
import TableBody from "@material-ui/core/TableBody";
import Table from "@material-ui/core/Table";
import TableRow from "@material-ui/core/TableRow";
import TableHead from "@material-ui/core/TableHead";
import TableCell from "@material-ui/core/TableCell";
import {withStyles} from "@material-ui/core/styles";


const StyledTableCell = withStyles((theme) => ({
  head: {
    backgroundColor: theme.palette.common.black,
    color: theme.palette.common.white,
      fontSize: 10,
  },
  body: {
    fontSize: 14,
  },
}))(TableCell);


const StyledTableRow = withStyles((theme) => ({
  root: {
    '&:nth-of-type(odd)': {
      backgroundColor: theme.palette.action.hover,
    },
  },
}))(TableRow);


class MatchList extends Component {

    state = {
        page: 0,
        rowsPerPage: 10,
        rankedList: [],
        jobId: "",
        loading: false
    }

    componentDidMount() {
        this.setState({rankedList: this.props.rankedList, jobId: this.props.jobId})
    }

    deleteMatchHandler = (matchIndex, save) => {
        const rankedList = [...this.state.rankedList];
        rankedList.splice(matchIndex, 1);
        this.setState({rankedList: rankedList, loading: true})
        if(save){
            axios({
                 method: 'post',
                 url: '/api/results/save_verified_match/' + this.state.jobId + '/' + matchIndex
            }).then(() => {
                this.setState({loading: false})
            }).catch(err => {
                this.setState({loading: false})
                console.log(err)
            })
        }else{
            axios({
                 method: 'post',
                 url: '/api/results/discard_match/' + this.state.jobId + '/' + matchIndex
            }).then(() => {
                this.setState({loading: false})
            }).catch(err => {
                this.setState({loading: false})
                console.log(err)
            })
        }
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
                <Paper>
                    <TableContainer className={classes.Container}>
                        <Table className={classes.List} size="small">
                            <TableHead>
                              <TableRow>
                                <StyledTableCell className={classes.Cell} align="center">Source table name</StyledTableCell>
                                <StyledTableCell className={classes.Cell} align="center">Source table guid</StyledTableCell>
                                <StyledTableCell className={classes.Cell} align="center">Source column name</StyledTableCell>
                                <StyledTableCell className={classes.Cell} align="center">Source column guid</StyledTableCell>
                                <StyledTableCell className={classes.Cell} align="center">Target table name</StyledTableCell>
                                <StyledTableCell className={classes.Cell} align="center">Target table guid</StyledTableCell>
                                <StyledTableCell className={classes.Cell} align="center">Target column name</StyledTableCell>
                                <StyledTableCell className={classes.Cell} align="center">Target column guid</StyledTableCell>
                                <StyledTableCell className={classes.Cell} align="center">Similarity</StyledTableCell>
                                <StyledTableCell className={classes.Cell} align="center"> </StyledTableCell>
                              </TableRow>
                            </TableHead>
                            <TableBody>
                            {this.state.rankedList.slice(this.state.page * this.state.rowsPerPage, this.state.page * this.state.rowsPerPage + this.state.rowsPerPage)
                                .map((item, index) => (
                                    <StyledTableRow key={index}>
                                        <StyledTableCell className={classes.Cell} align="center">{item.source['tbl_nm']}</StyledTableCell>
                                        <StyledTableCell className={classes.Cell} align="center">{item.source['tbl_guid']}</StyledTableCell>
                                        <StyledTableCell className={classes.Cell} align="center">{item.source['clm_nm']}</StyledTableCell>
                                        <StyledTableCell className={classes.Cell} align="center">{item.source['clm_guid']}</StyledTableCell>
                                        <StyledTableCell className={classes.Cell} align="center">{item.target['tbl_nm']}</StyledTableCell>
                                        <StyledTableCell className={classes.Cell} align="center">{item.target['tbl_guid']}</StyledTableCell>
                                        <StyledTableCell className={classes.Cell} align="center">{item.target['clm_nm']}</StyledTableCell>
                                        <StyledTableCell className={classes.Cell} align="center">{item.target['clm_guid']}</StyledTableCell>
                                        <StyledTableCell className={classes.Cell} align="center">{item['sim']}</StyledTableCell>
                                        <StyledTableCell className={classes.Cell} align="center">
                                            <Button variant="contained" color="primary" onClick={() => this.deleteMatchHandler(index, true)}>Verify</Button>
                                            <Button color="secondary" onClick={() => this.deleteMatchHandler(index, false)}>Discard</Button>
                                        </StyledTableCell>
                                    </StyledTableRow>
                                )
                            )}
                            </TableBody>
                        </Table>
                    </TableContainer>
                    <TablePagination
                    rowsPerPageOptions={[10, 25, 100]}
                    component="div"
                    count={this.state.rankedList.length}
                    rowsPerPage={this.state.rowsPerPage}
                    page={this.state.page}
                    onChangePage={this.handleChangePage}
                    onChangeRowsPerPage={this.handleChangeRowsPerPage}
                    />
                </Paper>
            </Aux>
        );
    }
}

export default MatchList;