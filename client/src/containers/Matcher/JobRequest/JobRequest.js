import React, { Component } from 'react'

import classes from './JobRequest.css'
// import axios from '../../../../axios-schema-matching-job'
import Input from '../../../components/Forms/Input/Input'
import Button from '../../../components/UI/Button/Button'


class JobRequest extends Component {

    state = {

        jobForm: {
            dbName: {
                name:'Database Name',
                elementType: 'input',
                elementConfig: {
                    type: 'text',
                    placeholder: 'Database Name'
                },
                value: '',
                show: true
            },
            tableName: {
                name:'Table Name',
                elementType: 'input',
                elementConfig: {
                    type: 'text',
                    placeholder: 'Table Name'
                },
                value: '',
                show: true
            },
            algorithm: {
                name:'Select algorithm',
                elementType: 'select',
                elementConfig: {
                    options: [
                        {value: 'coma', displayValue: 'COMA'},
                        {value: 'cupid', displayValue: 'CUPID'},
                        {value: 'distributionBased', displayValue: 'Distribution Based'},
                        {value: 'jaccardLeven', displayValue: 'Jaccard Levenshtein'},
                        {value: 'similarityFlooding', displayValue: 'Similarity Flooding'}
                        ]
                },
                value: 'coma',
                show: true
            },
            defaultAlgoParams: {
                name:'Default Algorithm Parameters',
                elementType: 'checkbox',
                elementConfig:{
                    type: 'checkbox',
                    defaultChecked: true,
                    name: 'Default Parameters'
                },
                value: true,
                show: true
            },
            // START OF PARAMS
            // COMA params
            coma_strategy: {
                elementType: 'select',
                elementConfig: {
                    options: [
                        {value: 'COMA_OPT', displayValue: 'COMA_OPT'},
                        {value: 'COMA_OPT_INST', displayValue: 'COMA_OPT_INST'}
                        ]
                },
                value: '',
                show: false
            },
            coma_max_n: {
                name: 'max_n',
                elementType: 'input',
                elementConfig: {
                    type: 'number',
                    placeholder: 'max_n'
                },
                value: 0,
                show: false
            },
            // CUPID params
            cupid_leaf_w_struct: {
                elementType: 'range',
                elementConfig : {
                    min: 0.0,
                    max: 1.0,
                    step: 0.05
                },
                value: 0.2,
                show: false
            },
            cupid_w_struct: {
                elementType: 'range',
                elementConfig : {
                    min: 0.0,
                    max: 1.0,
                    step: 0.05
                },
                value: 0.2,
                show: false
            },
            cupid_th_accept: {
                elementType: 'range',
                elementConfig : {
                    min: 0.0,
                    max: 1.0,
                    step: 0.05
                },
                value: 0.7,
                show: false
            },
            cupid_th_high: {
                elementType: 'range',
                elementConfig : {
                    min: 0.0,
                    max: 1.0,
                    step: 0.05
                },
                value: 0.6,
                show: false
            },
            cupid_th_low: {
                elementType: 'range',
                elementConfig : {
                    min: 0.0,
                    max: 1.0,
                    step: 0.05
                },
                value: 0.35,
                show: false
            },
            cupid_th_ns: {
                elementType: 'range',
                elementConfig : {
                    min: 0.0,
                    max: 1.0,
                    step: 0.05
                },
                value: 0.7,
                show: false
            },
            // Distribution Based params
            distributionBased_th1: {
                elementType: 'range',
                elementConfig : {
                    min: 0.0,
                    max: 1.0,
                    step: 0.05
                },
                value: 0.15,
                show: false
            },
            distributionBased_th2: {
                elementType: 'range',
                elementConfig : {
                    min: 0.0,
                    max: 1.0,
                    step: 0.05
                },
                value: 0.15,
                show: false
            },
            distributionBased_quantiles: {
                elementType: 'range',
                elementConfig : {
                    min: 1,
                    max: 1024,
                    step: 1
                },
                value: 256,
                show: false
            },
            // Jaccard Leven params
            jaccardLeven_th_leven: {
                elementType: 'range',
                elementConfig : {
                    min: 0.0,
                    max: 1.0,
                    step: 0.05
                },
                value: 0.8,
                show: false
            },
            // END OF PARAMS
            maxNumberOfMatches: {
                name:'Max number of matches',
                elementType: 'input',
                elementConfig: {
                    type: 'number',
                    placeholder: 'Max number of matches'
                },
                value: '',
                show: true
            },
            mode: {
                name: 'Schema Matching mode',
                elementType: 'select',
                elementConfig: {
                    options: [
                        {value: 'holistic', displayValue: 'Holistic'},
                        {value: 'internal', displayValue: 'Internal'},
                        {value: 'specifyDB', displayValue: 'Specify Database'}
                        ]
                },
                value: 'holistic',
                show: true
            },
            otherDB: {
                name: 'Other Database Name',
                elementType: 'input',
                elementConfig: {
                    type: 'text',
                    placeholder: 'Database Name'
                },
                value: '',
                show: false
            }
        },
        loading: false
    }


    inputChangedHandler = (event, inputIdentifier) => {
        const updatedJobForm = {
            ...this.state.jobForm
        };
        const updatedJobElement = {
            ...updatedJobForm[inputIdentifier]
        };
        if(inputIdentifier === 'defaultAlgoParams') {
            updatedJobElement.value = !updatedJobElement.value;
            this.toggle_show_dynamic_component(updatedJobForm, updatedJobForm.algorithm.value)
        }else if(inputIdentifier === 'algorithm'){
            if(!updatedJobForm.defaultAlgoParams.value){
                this.toggle_show_dynamic_component(updatedJobForm, updatedJobForm.algorithm.value)
                this.toggle_show_dynamic_component(updatedJobForm, event.target.value)
            }
            updatedJobElement.value = event.target.value;
        }else{
            updatedJobElement.value = event.target.value;
            if(inputIdentifier === 'mode' && event.target.value === 'specifyDB'){
                updatedJobForm['otherDB'].show = true
            } else if (inputIdentifier === 'mode' && event.target.value !== 'specifyDB'){
                updatedJobForm['otherDB'].show = false
            }
        }
        updatedJobForm[inputIdentifier] = updatedJobElement;
        this.setState({jobForm: updatedJobForm});
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

    render () {
        const formElementsArray = [];
        for (let key in this.state.jobForm){
            if (this.state.jobForm[key].show){
                formElementsArray.push({
                    id: key,
                    config: this.state.jobForm[key]
                })
            }
        }
        return (
           <div className={classes.JobRequest}>
               <h4>Create a Schema matching job</h4>
                <form>
                    {formElementsArray.map(formElement => (
                        <Input
                            key={formElement.id}
                            elementType={formElement.config.elementType}
                            config={formElement.config.elementConfig}
                            name={formElement.config.name}
                            value={formElement.config.value}
                            changed={(event) => this.inputChangedHandler(event, formElement.id)}/>
                    ))}
                    <Button btnType={"Success"} clicked={this.jobRequestHandler} >Submit</Button>
                </form>
           </div>
        );
    }

}

export default JobRequest;