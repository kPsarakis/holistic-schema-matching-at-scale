import React from "react";

import classes from "./NavigationItems.module.css";
import NavigationItem from "./NavgationItem/NavigationItem";

const navigationItems = (props) => (
    <ul className={classes.NavigationItems}>
        <NavigationItem link={"/"} exact>
            &lsaquo;&mdash;
        </NavigationItem>
        {props.toolbar_elements.map((row) => (
            <NavigationItem link={row.link} exact>
                {row.text}
            </NavigationItem>
        ))}
    </ul>
);

export default navigationItems;