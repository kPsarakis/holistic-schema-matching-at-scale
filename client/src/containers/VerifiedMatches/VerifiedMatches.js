import React, {Component} from "react";
import { withStyles, makeStyles } from '@material-ui/core/styles';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Paper from '@material-ui/core/Paper';

import classes from './VerifiedMatches.css'
import axios from "axios";


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

    render() {
        return (
             <TableContainer component={Paper}>
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
                  {this.state.verifiedMatches.map((row) => (
                    <StyledTableRow key={row.name}>
                      <StyledTableCell align="center">{row['source']['tbl_nm']}</StyledTableCell>
                      <StyledTableCell align="center">{row['source']['tbl_guid']}</StyledTableCell>
                      <StyledTableCell align="center">{row['source']['clm_nm']}</StyledTableCell>
                      <StyledTableCell align="center">{row['source']['clm_guid']}</StyledTableCell>
                      <StyledTableCell align="center">{row['target']['tbl_nm']}</StyledTableCell>
                      <StyledTableCell align="center">{row['target']['tbl_guid']}</StyledTableCell>
                      <StyledTableCell align="center">{row['target']['clm_nm']}</StyledTableCell>
                      <StyledTableCell align="center">{row['target']['clm_guid']}</StyledTableCell>
                    </StyledTableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
        );
    }
}

export default VerifiedMatches;