import React, {Component} from "react";
import Checkbox from "@material-ui/core/Checkbox";
import Input from "../../../../components/Forms/Input/Input";

import classes from './Algorithm.css'

class Cupid extends Component{

    state = {
        selected: false,
        params: {
             defaultAlgoParams: {
                name:'Default Params',
                elementType: 'checkbox',
                elementConfig:{
                    type: 'checkbox',
                    defaultChecked: true,
                    name: 'Default Parameters'
                },
                value: true,
                show: true
             },
            Cupid_leaf_w_struct: {
                name: 'leaf_w_struct',
                elementType: 'range',
                elementConfig : {
                    min: 0.0,
                    max: 1.0,
                    step: 0.01,
                    defaultValue: 0.2
                },
                value: 0.2,
                show: false
            },
            Cupid_w_struct: {
                name: 'w_struct',
                elementType: 'range',
                elementConfig : {
                    min: 0.0,
                    max: 1.0,
                    step: 0.01,
                    defaultValue: 0.2
                },
                value: 0.2,
                show: false
            },
            Cupid_th_accept: {
                name: 'th_accept',
                elementType: 'range',
                elementConfig : {
                    min: 0.0,
                    max: 1.0,
                    step: 0.01,
                    defaultValue: 0.7
                },
                value: 0.7,
                show: false
            },
            Cupid_th_high: {
                name: 'th_high',
                elementType: 'range',
                elementConfig : {
                    min: 0.0,
                    max: 1.0,
                    step: 0.01,
                    defaultValue: 0.6
                },
                value: 0.6,
                show: false
            },
            Cupid_th_low: {
                name: 'th_low',
                elementType: 'range',
                elementConfig : {
                    min: 0.0,
                    max: 1.0,
                    step: 0.01,
                    defaultValue: 0.35
                },
                value: 0.35,
                show: false
            },
            Cupid_th_ns: {
                name: 'th_ns',
                elementType: 'range',
                elementConfig : {
                    min: 0.0,
                    max: 1.0,
                    step: 0.01,
                    defaultValue: 0.7
                },
                value: 0.7,
                show: false
            }
        }
    }

    toggleSelected = () => {
        this.setState({selected: !this.state.selected})
    }

    toggle_show_dynamic_component = (updatedJobForm, name) => {
        for (let key in updatedJobForm) {
            if (updatedJobForm.hasOwnProperty(key)){
                if (key.startsWith(name)) {
                    updatedJobForm[key].show = !updatedJobForm[key].show
                }
            }
        }
    }

    inputChangedHandler = (event, inputIdentifier) => {
        const updatedJobForm = {
            ...this.state.params
        };
        const updatedJobElement = {
            ...updatedJobForm[inputIdentifier]
        };
        if(inputIdentifier === 'defaultAlgoParams') {
            updatedJobElement.value = !updatedJobElement.value;
            this.toggle_show_dynamic_component(updatedJobForm, 'Cupid');
        }else{
            if (event.target.textContent){
                updatedJobElement.value = parseFloat(event.target.textContent);
            } else {
                 updatedJobElement.value = event.target.value;
            }
        }
        updatedJobForm[inputIdentifier] = updatedJobElement;
        this.setState({params: updatedJobForm});
    }

    render() {
        const formElementsArray = [];
        for (let key in this.state.params){
            if (this.state.params[key].show){
                formElementsArray.push({
                    id: key,
                    config: this.state.params[key]
                })
            }
        }
        return(
            <div>
                <div className={classes.Header}>
                    <Checkbox

                        checked={this.state.selected}
                        onChange={() => this.toggleSelected()}
                        color="primary"
                    />
                    <h4>Cupid</h4>
                </div>
                {formElementsArray.map(formElement => (
                            <Input
                                key={formElement.id}
                                elementType={formElement.config.elementType}
                                config={formElement.config.elementConfig}
                                name={formElement.config.name}
                                value={formElement.config.value}
                                changed={(event) => this.inputChangedHandler(event, formElement.id)}/>
                                ))
                }
            </div>
        );
    }
}

export default Cupid;