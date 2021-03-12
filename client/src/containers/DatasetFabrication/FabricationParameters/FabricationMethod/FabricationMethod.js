import React, {Component} from "react";
import classes from "./FabricationMethod.module.css";
import Checkbox from "@material-ui/core/Checkbox";
import {TextField} from "@material-ui/core";


class FabricationMethod extends Component{

    state = {
        selected: false,
        params: {}
    }

    componentDidMount() {
        this.setState({params: {...this.props.params}})
    }


    toggleSelected = () => {
         this.setState({selected: !this.state.selected})
        // this.setState({selected: !this.state.selected}, () => this.sendSelectedToParent());
    }


    render() {

        const joinable = (this.props.methodName !== "Joinable") ?
            <div className={classes.Choice}>
                <Checkbox
                    checked={this.state.selected}
                    onChange={() => this.toggleSelected()}
                    color="primary"
                />
                <p>Noisy instances</p>
            </div> : null;

        const semanticallyJoinable = (this.props.methodName !== "Semantically Joinable") ?
            <div className={classes.Choice}>
                <Checkbox
                    checked={this.state.selected}
                    onChange={() => this.toggleSelected()}
                    color="primary"
                />
                <p>Verbatim instances</p>
            </div>: null;

        return(
            <div className={classes.FabricationMethod}>
                <div className={classes.Header}>
                    <Checkbox
                        checked={this.state.selected}
                        onChange={() => this.toggleSelected()}
                        color="primary"
                    />
                    <h4>{this.props.methodName}</h4>
                </div>
                <div>
                    <div className={classes.TextField}>
                        <TextField id="standard-basic" label="Number of pairs" />
                    </div>
                    <div className={classes.IncludeHeader}>
                        <h5> Include: </h5>
                    </div>
                    {joinable}
                    <div className={classes.Choice}>
                        <Checkbox
                            checked={this.state.selected}
                            onChange={() => this.toggleSelected()}
                            color="primary"
                        />
                        <p>Noisy schemata</p>
                    </div>
                    {semanticallyJoinable}
                    <div className={classes.Choice}>
                        <Checkbox
                            checked={this.state.selected}
                            onChange={() => this.toggleSelected()}
                            color="primary"
                        />
                        <p>Verbatim schemata</p>
                    </div>
                </div>
            </div>

        );
    }


}

export default FabricationMethod;