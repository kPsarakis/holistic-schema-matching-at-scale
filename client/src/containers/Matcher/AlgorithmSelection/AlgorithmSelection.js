import React, {Component} from "react";

import classes from './AlgorithmSelection.css'
import Algorithm from "./Algorithm/Algorithm";
import Cupid from "./Algorithm/Cupid";
import Coma from "./Algorithm/Coma";
import SimilarityFlooding from "./Algorithm/SimilarityFlooding";
import JaccardLevenshtein from "./Algorithm/JaccardLevenshtein";
import DistributionBased from "./Algorithm/DistributionBased";

class AlgorithmSelection extends Component {

    state = {
        algorithms: ["Coma", "cupid", "sf", "db", "jl"],
    }

    render() {
        return(
            <div className={classes.Algorithms}>
                <h5>Select algorithms to run</h5>
                <div className={classes.Algorithms}>
                    <Coma />
                </div>
                <div className={classes.Algorithms}>
                    <Cupid />
                </div>
                <div className={classes.Algorithms}>
                    <DistributionBased />
                </div>
                <div className={classes.Algorithms}>
                    <JaccardLevenshtein />
                </div>
                <div className={classes.Algorithms}>
                    <SimilarityFlooding />
                </div>
            </div>
        );
    }
}

export default AlgorithmSelection;