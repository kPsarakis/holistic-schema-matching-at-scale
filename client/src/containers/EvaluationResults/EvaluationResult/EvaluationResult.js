import React, {Component} from "react";
import Aux from "../../../hoc/Aux";
import Modal from "../../../components/UI/Modal/Modal";
import Spinner from "../../../components/UI/Spinner/Spinner";
import classes from "./EvaluationResult.module.css";
import Button from "@material-ui/core/Button";
import GetAppIcon from "@material-ui/icons/GetApp";
import BarChartIcon from '@material-ui/icons/BarChart';
import TestFigure from "../../../assets/Unionable-all-1.png";


class EvaluationResult extends Component {

    state = {
        loading: false,
        showPlot: false
    }

    displayBoxplot = (fabricatedPairId) => {
        this.setState({showPlot: true});
    }

    downloadDataset = (fabricatedPairId) => {

    }

    closeShowDataHandler = () => {
        this.setState({showPlot: false});
    }

    render() {
        return(
            <Aux>
                <Modal show={this.state.loading} figure={false}>
                    <Spinner />
                </Modal>
                <Modal show={this.state.showPlot} modalClosed={this.closeShowDataHandler} figure={true}>
                    <img src={TestFigure} alt={"figure"} className={classes.Modal}/>
                </Modal>
                <div className={classes.FabricatedPair}>
                    <p>Fabricated pair id: {this.props.fabricatedPairId}</p>
                    <Button
                        color="primary"
                        onClick={() => this.displayBoxplot(this.props.fabricatedPairId)}>
                        <BarChartIcon/>
                    </Button>
                    <Button
                        color="primary"
                        onClick={() => this.downloadDataset(this.props.fabricatedPairId)}>
                        <GetAppIcon/>
                    </Button>
                </div>
            </Aux>
        );
    }

}

export default EvaluationResult;