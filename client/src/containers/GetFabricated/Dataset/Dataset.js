import React, {Component} from "react";
import FabricatedDataPreview from "../FabricatedDataPreview/FabricatedDataPreview";
import classes from "../GetFabricated.module.css";
import Button from "@material-ui/core/Button";
import GetAppIcon from "@material-ui/icons/GetApp";
import DeleteIcon from "@material-ui/icons/Delete";

class Dataset extends Component {

    state = {
        showSample: false,
        sample: {}
    }

    render() {
        const fabricatedDataPreview = this.state.showSample ?
            <FabricatedDataPreview sample={this.state.sample}/>
            : null;
        return (
            <div className={classes.Result}>
                <p className={classes.Paragraph}>Dataset: {this.props.datasetId}</p>
                <div className={classes.Buttons}>
                    <Button
                        style={{
                            borderRadius: 10,
                            backgroundColor: "#016b9f",
                            color: "white",
                            padding: "10px 10px",
                            fontSize: "11px"
                        }}
                        onClick={() => this.showSample(this.props.datasetId)}>
                        Show Sample
                    </Button>
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
                            color: "#71100f",
                            padding: "10px 10px",
                            fontSize: "8px"
                        }}
                        onClick={() => this.deleteDataset(datasetId)}>
                        <DeleteIcon/>
                    </Button>
                </div>
                <div className={classes.Sample}>
                    {fabricatedDataPreview}
                </div>
            </div>);
    }

}

export default Dataset;