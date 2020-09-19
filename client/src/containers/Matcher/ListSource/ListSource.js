import React, {Component} from "react";
import ExpandMoreIcon from "@material-ui/icons/ExpandMore";
import ChevronRightIcon from "@material-ui/icons/ChevronRight";
import StorageIcon from '@material-ui/icons/Storage';
import TableChartIcon from '@material-ui/icons/TableChart';
import TreeView from "@material-ui/lab/TreeView";
import TreeItem from "@material-ui/lab/TreeItem";
import Checkbox from "@material-ui/core/Checkbox";
import { blue, indigo } from '@material-ui/core/colors';
import classes from './ListSource.css'
import Aux from "../../../hoc/Aux";
import Modal from "../../../components/UI/Modal/Modal";
import Spinner from "../../../components/UI/Spinner/Spinner";
import axios from "axios";
import Typography from "@material-ui/core/Typography";

class Database {
    constructor(id, name, tables) {
        this.id = id;
        this.name = name;
        this.tables = [];
        this.selected = false;
        this.add_tables(tables);
    }
    add_tables(tables){
        tables.map((tableName, index) => this.tables.push(new Table(index, tableName)));
    }
}

class Table {
    constructor(id, name) {
        this.id = id;
        this.name = name;
        this.selected = false;
    }
}


class ListSource extends Component {

    state = {
        dbTree: [],
        loading: false
    }

    componentDidMount() {
        this.setState({loading: true})
        axios({
            method: 'get',
            url: "http://127.0.0.1:5000/matches/minio/ls"
             // url: '/api/matches/minio/ls'
        }).then(res => {
            const dbTree = [];
            res.data.map((dbInfo, index) => dbTree.push(new Database(index, dbInfo['db_name'], dbInfo['tables'])));
            this.setState({loading: false, dbTree: dbTree});
        }).catch(err => {
            this.setState({loading: false});
            console.log(err);
        })
    }

    sendSelectedToParent = () => {
        const selectedTables = [];
        this.state.dbTree.map(db =>
            db.tables.map(table =>
                (table.selected) ? selectedTables.push({"db_name": db.name, "table_name": table.name}) : null))
        this.props.sendSelected(selectedTables);
    }

    handleCheckDB = (dbIdx) => {
        const updatedDBTree = [...this.state.dbTree];
        const dbToUpdate = updatedDBTree.slice(dbIdx, dbIdx+1)[0];
        dbToUpdate.selected = !dbToUpdate.selected
        dbToUpdate.tables.map(table => table.selected = dbToUpdate.selected)
        updatedDBTree[dbIdx] = dbToUpdate
        this.setState({dbTree: updatedDBTree},() => this.sendSelectedToParent());
    }

    handleCheckTbl = (dbIdx, tblIdx) => {
        const updatedDBTree = [...this.state.dbTree];
        const dbToUpdate = updatedDBTree.slice(dbIdx, dbIdx+1)[0];
        dbToUpdate.tables[tblIdx].selected = !dbToUpdate.tables[tblIdx].selected
        updatedDBTree[dbIdx] = dbToUpdate
        this.setState({dbTree: updatedDBTree}, () => this.sendSelectedToParent());
    }

    renderTree = (dbInfo, index) => {
        return(
            <TreeItem
                key={"d"+dbInfo.id}
                nodeId={"d"+dbInfo.id}
                label={
                    <div className={classes.labelRoot}>
                        <Checkbox
                            checked={dbInfo.selected}
                            onChange={() => this.handleCheckDB(index)}
                            onClick={e => e.stopPropagation()}
                            color="primary"
                        />
                        <StorageIcon style={{ color: indigo[500] }} className={classes.labelIcon}/>
                        <Typography variant="body2" className={classes.labelText}>
                            {dbInfo.name}
                        </Typography>
                    </div>
                }
            >
                {dbInfo.tables.map((table, tblIdx) =>
                    < TreeItem
                    key = {"t"+table.id}
                    nodeId = {"t"+table.id}
                    label = {
                        <div className={classes.labelRoot}>
                            <Checkbox
                                checked={table.selected}
                                onChange={() => this.handleCheckTbl(index, tblIdx)}
                                onClick={e => e.stopPropagation()}
                                color="primary"
                            />
                            <TableChartIcon style={{ color: blue[400] }} className={classes.labelIcon}/>
                            <Typography variant="body2" className={classes.labelText}>
                                {table.name}
                            </Typography>
                        </div>
                    }
                    />
                )}
            </TreeItem>
        );
    }

    render() {
        return(
            <Aux>
                <Modal show={this.state.loading}>
                    <Spinner />
                </Modal>
                <div className={classes.ListSource}>
                    <h5>{this.props.header}</h5>
                    <TreeView defaultCollapseIcon={<ExpandMoreIcon />} defaultExpandIcon={<ChevronRightIcon />}>
                        {this.state.dbTree.map((dbInfo, index) => this.renderTree(dbInfo, index))}
                    </TreeView>
                </div>
            </Aux>
        );
    }
}

export default ListSource;
