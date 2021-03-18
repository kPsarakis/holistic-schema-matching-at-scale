import React, {Component} from "react";
import {withStyles} from "@material-ui/core/styles";
import TableCell from "@material-ui/core/TableCell";
import TableRow from "@material-ui/core/TableRow";
import Paper from "@material-ui/core/Paper";
import TableContainer from "@material-ui/core/TableContainer";
import classes from "../../../Results/MatchList/ColumnPreview/ColumnPreview.module.css";
import Table from "@material-ui/core/Table";
import TableHead from "@material-ui/core/TableHead";
import TableBody from "@material-ui/core/TableBody";


const StyledTableCell = withStyles((theme) => ({
  head: {
      backgroundColor: "#534bae",
      border: 1,
      borderRadius: 0,
      boxShadow: "1px 1px 1px 1px rgba(0, 0, 0, 1)",
      color: theme.palette.common.white,
      fontWeight: "bold",
      fontSize: 10,
  },
  body: {
    fontSize: 10,
  },
}))(TableCell);


const StyledTableRow = withStyles((theme) => ({
  root: {
    "&:nth-of-type(odd)": {
      backgroundColor: theme.palette.action.hover,
    },
  },
}))(TableRow);


class SampleTable extends Component {
    render(){
        return(
            <Paper>
                <TableContainer className={classes.Container}>
                    <Table className={classes.List} size="small">
                        <TableHead>
                            <TableRow>
                                {this.props.columnNames.map((columnName) => {
                                    return (
                                        <StyledTableCell>
                                            {columnName}
                                        </StyledTableCell>);})
                                }
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {this.props.sampleData.map((row, index) => (
                                <StyledTableRow key={index}>
                                    {row.map((cell) => (
                                        <StyledTableCell className={classes.Cell}>
                                            {cell}
                                        </StyledTableCell>
                                    ))}
                                </StyledTableRow>
                                )
                            )}
                        </TableBody>
                    </Table>
                </TableContainer>
            </Paper>
        );
    }

}

export default SampleTable;