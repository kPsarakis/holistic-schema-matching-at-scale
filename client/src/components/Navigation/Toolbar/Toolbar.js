import React from "react";

import classes from "./Toolbar.module.css";
import NavigationItems from "../NavigationItems/NavigationItems";

const toolbar = (props) => (
    <header className={classes.Toolbar}>
        {/*<div>*/}
        {/*    MENUE*/}
        {/*</div>*/}
        {/*<div>*/}
        {/*    LOGO*/}
        {/*</div>*/}
        <nav>
            <NavigationItems toolbar_elements={props.toolbar_elements}/>
        </nav>
    </header>
);

export default toolbar;