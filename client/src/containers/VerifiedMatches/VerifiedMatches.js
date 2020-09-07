import React, {Component} from "react";
import { withStyles } from '@material-ui/core/styles';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Paper from '@material-ui/core/Paper';

import classes from './VerifiedMatches.css'
import axios from "axios";
import TablePagination from "@material-ui/core/TablePagination";


const StyledTableCell = withStyles((theme) => ({
  head: {
    backgroundColor: theme.palette.common.black,
    color: theme.palette.common.white,

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


class VerifiedMatches extends Component {


    state = {
        page: 0,
        rowsPerPage: 10,
        loading: false,
        verifiedMatches: []
    }

    componentDidMount() {
        this.setState({loading: true})
        axios({
                 method: 'get',
                 url: '/api/results/verified_matches'
            }).then(res => {
                this.setState({loading: false, verifiedMatches: res.data})
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

    render() {
        return (
            <Paper className={classes.Root}>
             <TableContainer className={classes.Container}>
              <Table className={classes.VerifiedMatches} size="small">
                <TableHead>
                  <TableRow>
                    <StyledTableCell align="center">Source table name</StyledTableCell>
                    <StyledTableCell align="center">Source table guid</StyledTableCell>
                    <StyledTableCell align="center">Source column name</StyledTableCell>
                    <StyledTableCell align="center">Source column guid</StyledTableCell>
                    <StyledTableCell align="center">Target table name</StyledTableCell>
                    <StyledTableCell align="center">Target table guid</StyledTableCell>
                    <StyledTableCell align="center">Target column name</StyledTableCell>
                    <StyledTableCell align="center">Target column guid</StyledTableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {this.state.verifiedMatches
                      .slice(this.state.page * this.state.rowsPerPage, this.state.page * this.state.rowsPerPage + this.state.rowsPerPage)
                      .map((row, index) => (
                            <StyledTableRow key={index}>
                              <StyledTableCell align="center">{row['source']['tbl_nm']}</StyledTableCell>
                              <StyledTableCell align="center">{row['source']['tbl_guid']}</StyledTableCell>
                              <StyledTableCell align="center">{row['source']['clm_nm']}</StyledTableCell>
                              <StyledTableCell align="center">{row['source']['clm_guid']}</StyledTableCell>
                              <StyledTableCell align="center">{row['target']['tbl_nm']}</StyledTableCell>
                              <StyledTableCell align="center">{row['target']['tbl_guid']}</StyledTableCell>
                              <StyledTableCell align="center">{row['target']['clm_nm']}</StyledTableCell>
                              <StyledTableCell align="center">{row['target']['clm_guid']}</StyledTableCell>
                            </StyledTableRow>
                        ))
                  }
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination
                rowsPerPageOptions={[10, 25, 100]}
                component="div"
                count={this.state.verifiedMatches.length}
                rowsPerPage={this.state.rowsPerPage}
                page={this.state.page}
                onChangePage={this.handleChangePage}
                onChangeRowsPerPage={this.handleChangeRowsPerPage}
              />
              </Paper>
        );
    }
}

export default VerifiedMatches;