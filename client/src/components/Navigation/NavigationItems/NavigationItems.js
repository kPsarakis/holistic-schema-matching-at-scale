import React from "react";

import classes from "./NavigationItems.module.css";
import NavigationItem from "./NavgationItem/NavigationItem";

const navigationItems = () => (
    <ul className={classes.NavigationItems}>
        <NavigationItem link={"/"} exact>
            Matcher
        </NavigationItem>
        <NavigationItem link={"/results"}>
            Finished Jobs
        </NavigationItem>
        <NavigationItem link={"/verified_matches"}>
            Verified Matches
        </NavigationItem>
    </ul>
);

export default navigationItems;