import React, { Component } from "react";
import Aux from "../../hoc/Aux";
import { withRouter } from 'react-router-dom'
import researchLogo from "../../assets/research-svgrepo-com.svg";
import dataLakeLogo from "../../assets/data-lake.svg"

import classes from "./LandingPage.module.css";


const ResearchButton = withRouter(({ history }) => (
    <div className={classes.LandingPageItem} onClick={() => { history.push('/matcher') }}>
        <h3>Research</h3>
        <img src={researchLogo} alt={"Research logo"} width="500px" height="200px"/>
        <p>Evaluate and compare schema matching methods</p>
    </div>
));


const DataLakeButton = withRouter(({ history }) => (
    <div className={classes.LandingPageItem} onClick={() => { history.push('/matcher') }}>
        <h3>Data Lake</h3>
        <img src={dataLakeLogo} alt={"Data lake logo"} width="500px" height="200px"/>
        <p>Capture relevance among datasets in a data lake</p>
    </div>
));


class LandingPage extends Component {

    render(){
        return(
            <Aux>
                <h1 className={classes.LandingPageTitle}>Valentine++</h1>
                <div className={classes.LandingPageItems}>
                    <ResearchButton/>
                    <DataLakeButton/>
                </div>
            </Aux>
        );
    }

}

export default LandingPage;