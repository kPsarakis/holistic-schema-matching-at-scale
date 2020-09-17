import React, {Component} from "react";
import classes from "./Algorithm.css";
import Checkbox from "@material-ui/core/Checkbox";
import Input from "../../../../components/Forms/Input/Input";

class Coma extends Component{
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
            Coma_strategy: {
                name: 'Strategy',
                elementType: 'select',
                elementConfig: {
                    options: [
                        {value: 'COMA_OPT', displayValue: 'Schema'},
                        {value: 'COMA_OPT_INST', displayValue: 'Schema + Instances'}
                        ]
                },
                value: 'COMA_OPT',
                show: false
            },
            Coma_max_n: {
                name: 'max_n',
                elementType: 'range',
                elementConfig : {
                    min: 0,
                    max: 10,
                    step: 1,
                    defaultValue: 0
                },
                value: 0,
                show: false
            }
        }
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
            this.toggle_show_dynamic_component(updatedJobForm, 'Coma');
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

    toggleSelected = () => {
        this.setState({selected: !this.state.selected})
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
                    <h4>Coma</h4>
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

export default Coma;