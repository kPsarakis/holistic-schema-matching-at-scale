import React, {Component} from "react";
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Paper from '@material-ui/core/Paper';

import classes from './VerifiedMatches.css'
import axios from "axios";

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
              <Table className={classes.VerifiedMatches} size="small" aria-label="a dense table">
                <TableHead>
                  <TableRow>
                    <TableCell align="right">Source table name</TableCell>
                    <TableCell align="right">Source table guid</TableCell>
                    <TableCell align="right">Source column name</TableCell>
                    <TableCell align="right">Source column guid</TableCell>
                    <TableCell align="right">Target table name</TableCell>
                    <TableCell align="right">Target table guid</TableCell>
                    <TableCell align="right">Target column name</TableCell>
                    <TableCell align="right">Target column guid</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {this.state.verifiedMatches.map((row) => (
                    <TableRow key={row.name}>
                      <TableCell component="th" scope="row">
                        {row.name}
                      </TableCell>
                      <TableCell align="right">{row['source']['tbl_nm']}</TableCell>
                      <TableCell align="right">{row['source']['tbl_guid']}</TableCell>
                      <TableCell align="right">{row['source']['clm_nm']}</TableCell>
                      <TableCell align="right">{row['source']['clm_guid']}</TableCell>
                      <TableCell align="right">{row['target']['tbl_nm']}</TableCell>
                      <TableCell align="right">{row['target']['tbl_guid']}</TableCell>
                      <TableCell align="right">{row['target']['clm_nm']}</TableCell>
                      <TableCell align="right">{row['target']['clm_guid']}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
        );
    }
}

export default VerifiedMatches;