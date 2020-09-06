import React, {Component} from "react";
import { List } from "react-virtualized";
import Button from '@material-ui/core/Button';
import axios from "axios";

import classes from './MatchList.css';
import Modal from "../../../components/UI/Modal/Modal";
import Spinner from "../../../components/UI/Spinner/Spinner";
import Aux from "../../../hoc/Aux";

class MatchList extends Component {

    state = {
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

    renderRow({ index, key, style }) {
        return (
            <div key={key} style={style} className={classes.Row}>
                <div className={classes.Content}>
                    <p>Source
                        table's {this.state.rankedList[index].source['tbl_nm']} column {this.state.rankedList[index].source['clm_nm']}</p>
                    <p>Target
                        table's {this.state.rankedList[index].target['tbl_nm']} column {this.state.rankedList[index].target['clm_nm']}</p>
                    <p>Similarity {this.state.rankedList[index]['sim']}</p>
                    <Button variant="contained" color="primary" onClick={() => this.deleteMatchHandler(index, true)}>Verify Match</Button>
                    <Button color="secondary" onClick={() => this.deleteMatchHandler(index, false)}>Discard Match</Button>
                </div>
            </div>
        );
    }

    render() {
        return (
            <Aux>
                <Modal show={this.state.loading}>
                    <Spinner />
                </Modal>
                <div className={classes.List}>
                    <List
                    width={1300}
                    height={300}
                    rowHeight={60}
                    rowRenderer={this.renderRow.bind(this)}
                    rowCount={this.state.rankedList.length} />
                </div>
            </Aux>
        );
    }
}

export default MatchList;