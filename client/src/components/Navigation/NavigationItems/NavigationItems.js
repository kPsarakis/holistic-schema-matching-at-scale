import React from 'react';

import classes from './NavigationItems.css'
import NavigationItem from "./NavgationItem/NavigationItem"

const navigationItems = () => (
    <ul className={classes.NavigationItems}>
        <NavigationItem link={"/"} active>
            Matcher
        </NavigationItem>
        <NavigationItem link={"/"}>
            Results
        </NavigationItem>
    </ul>
);

export default navigationItems;