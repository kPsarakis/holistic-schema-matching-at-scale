import React from 'react'

import classes from './Input.css'
import Aux from '../../../hoc/Aux'

const input = (props) => {
    let inputElement = null;

    switch (props.elementType){
        case('input'):
            inputElement = <input className={classes.InputElement} {...props.config} value={props.value} />;
            break;
        case('textarea'):
            inputElement = <textarea className={classes.InputElement} {...props.config} value={props.value} />;
            break;
        case('select'):
            inputElement = <select
                className={classes.InputElement}
                value={props.value}>
                {props.config.options.map(option => (
                    <option key={option.value} value={option.value}>
                        {option.displayValue}
                    </option>
                ))}
            </select>
            break;
        case('checkbox'):
            inputElement =
                <Aux>
                    <label>
                        Default Algorithm Parameters
                    </label>
                    <input id="cb" type="checkbox"/>
                </Aux>
            break;
        default:
            inputElement = <input className={classes.InputElement} {...props.config} value={props.value} />;
            break;
    }
    return(
        <div className={classes.Input}>
            <label className={classes.Label}>{props.label}</label>
            {inputElement}
        </div>
    );
};

export default input;