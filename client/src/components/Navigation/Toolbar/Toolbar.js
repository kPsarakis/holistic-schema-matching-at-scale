import React from 'react';

import classes from './Toolbar.module.css';
import NavigationItems from '../NavigationItems/NavigationItems';

const toolbar = (props) => (
    <header className={classes.Toolbar}>
        {/*<div>*/}
        {/*    MENUE*/}
        {/*</div>*/}
        {/*<div>*/}
        {/*    LOGO*/}
        {/*</div>*/}
        <nav>
            <NavigationItems />
        </nav>
    </header>
);

export default toolbar;