import React from 'react';

import classes from './NavigationItems.css'
import NavigationItem from "./NavgationItem/NavigationItem"

const navigationItems = () => (
    <ul className={classes.NavigationItems}>
        <NavigationItem link={"/"} exact>
            Matcher
        </NavigationItem>
        <NavigationItem link={"/results"}>
            Results
        </NavigationItem>
    </ul>
);

export default navigationItems;