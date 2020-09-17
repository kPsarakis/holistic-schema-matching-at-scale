import React, {Component} from "react";
import classes from "./Algorithm.css";
import Checkbox from "@material-ui/core/Checkbox";

class SimilarityFlooding extends Component{
    state = {
        selected: false
    }

    toggleSelected = () => {
        this.setState({selected: !this.state.selected})
    }

    render() {
        return(
             <div>
                <div className={classes.Header}>
                    <Checkbox
                        checked={this.state.selected}
                        onChange={() => this.toggleSelected()}
                        color="primary"
                    />
                    <h4>Similarity Flooding</h4>
                </div>
            </div>
        );
    }
}

export default SimilarityFlooding;