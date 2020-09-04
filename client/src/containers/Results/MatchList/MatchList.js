import React, {Component} from "react";
import { List } from "react-virtualized";
import Button from '@material-ui/core/Button';

import classes from './MatchList.css';

class MatchList extends Component {

    renderRow({ index, key, style }) {
        return (
            <div key={key} style={style} className={classes.Row}>
                <div className={classes.Content}>
                    <p>Source
                        table's {this.props.rankedList[index].source['tbl_nm']} column {this.props.rankedList[index].source['clm_nm']}</p>
                    <p>Target
                        table's {this.props.rankedList[index].target['tbl_nm']} column {this.props.rankedList[index].target['clm_nm']}</p>
                    <p>Similarity {this.props.rankedList[index]['sim']}</p>
                    <Button variant="contained" color="primary" type="submit">Verify Match</Button>
                    <Button color="secondary" type="submit">Discard Match</Button>
                </div>
            </div>
        );
    }

    render() {
        return (
            <div className={classes.List}>
                <List
                width={1300}
                height={300}
                rowHeight={60}
                rowRenderer={this.renderRow.bind(this)}
                rowCount={this.props.rankedList.length} />
            </div>
        );
    }
}

export default MatchList;