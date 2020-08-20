import React from 'react'

import classes from './Input.css'
import Aux from '../../../hoc/Aux'
import TextField from '@material-ui/core/TextField';
import Checkbox from '@material-ui/core/Checkbox';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import { makeStyles } from '@material-ui/core/styles';

const input = (props) => {
    let inputElement;

    const useStyles = makeStyles((theme) => ({
  formControl: {
    margin: theme.spacing(1),
    minWidth: 200,
  },
  selectEmpty: {
    marginTop: theme.spacing(2),
  },
}));
    const mat_classes = useStyles();


    switch (props.elementType){
        case('input'):
            inputElement = <TextField  label={props.name} variant="outlined" {...props.config} value={props.value}
                                       onChange={props.changed} />;
            break;
        case('textarea'):
            inputElement = <textarea className={classes.InputElement} {...props.config} value={props.value}
                                     onChange={props.changed} />;
            break;
        case('select'):
            inputElement =
                <FormControl className={mat_classes.formControl}>
                    <InputLabel>{props.name}</InputLabel>
                    <Select
                            value={props.value}
                            onChange={props.changed}>
                        {props.config.options.map(option => (
                            <MenuItem key={option.value} value={option.value}>
                                {option.displayValue}
                            </MenuItem>))}
                    </Select>
                </FormControl>
            break;
        case('checkbox'):
            inputElement = <FormControlLabel
                control={<Checkbox {...props.config} onChange={props.changed} name={props.name} color="primary"/>}
                label={props.name} />
            break;
        case('range'):
            inputElement =
                <Aux>
                    <label>{props.name}</label>
                    <input type="range" {...props.config} onChange={props.changed}/>
                    <label>Value: {props.value}</label>
                </Aux>
            break;
        default:
            inputElement = null
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